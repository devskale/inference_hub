import requests
import os
import json
import logging
import time
from typing import List, Dict, Optional, Any

# --- Constants ---
BASE_API_URL = "https://image.pollinations.ai"  # Aligning with API documentation
MODELS_ENDPOINT = f"{BASE_API_URL}/models"  # Consistent with API documentation
# Aligning with API documentation for image generation
IMAGE_GENERATION_ENDPOINT = f"{BASE_API_URL}/prompt/"
DEFAULT_SAVE_DIR = "/Users/johannwaldherr/code/Inference/inference_hub/images"
PROMPT_LIBRARY_FILE = "/Users/johannwaldherr/code/Inference/inference_hub/prompt_library.json"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


defaults = {
    "model": "flux",
    "prompt": "a beautiful landscape",
    # Consolidated negative prompts
    "negative_prompt": "worst quality, blurry, ugly, deformed",
    "steps": 25,
    "nologo": True,
    "private": False,
    "enhance": False,
    "safe": False
}

# --- Helper Functions ---


def load_prompt_library(file_path: str) -> List[Dict[str, str]]:
    """Loads the prompt library from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Prompt library file not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(
            f"Error decoding JSON from prompt library file: {file_path}")
        return []


def get_pollinations_models(timeout: int = 10) -> Optional[List[str]]:
    """
    Fetch available image models from pollinations.ai.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        List of model names or None if an error occurs.
    """
    try:
        response = requests.get(MODELS_ENDPOINT, timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(
            f"Timeout occurred while fetching models from {MODELS_ENDPOINT}")
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching models: {e}")
        return None


def generate_image(
    prompt: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
    seed: int = -1,
    model: str = "flux",
    save_path: Optional[str] = None,
    object_name_for_filename: Optional[str] = None,
    test_mode: bool = False,
    negative_prompt: Optional[str] = None,
    nologo: Optional[bool] = None,
    private: Optional[bool] = None,
    enhance: Optional[bool] = None,
    safe: Optional[bool] = None,
    referrer: Optional[str] = None
) -> Optional[str]:
    """
    Generate an image using pollinations.ai API and save it.

    Args:
        prompt: Text prompt for image generation. If None, prompts user.
        width: Image width in pixels.
        height: Image height in pixels.
        seed: Random seed for generation.
        model: Model to use for generation.
        save_path: Full path to save the generated image. If None, a default path is constructed.
        object_name_for_filename: Optional name to include in the filename for better description.
        test_mode: If True, only logs API call details without executing the request.

    Returns:
        Path to saved image or None if an error occurs.
    """
    final_prompt = prompt
    user_provided_object_name = ""
    loaded_object_name = ""

    if final_prompt is None:
        prompt_library = load_prompt_library(PROMPT_LIBRARY_FILE)
        default_prompt_data = next(
            (p for p in prompt_library if p.get("default") is True), None)

        if default_prompt_data:
            logger.info(
                f"Using default prompt from library: {default_prompt_data.get('description')}")
            final_prompt = default_prompt_data.get(
                "prompt", "A beautiful abstract design")
            loaded_object_name = default_prompt_data.get("object_name", "")
            if object_name_for_filename and "[OBJECT]" in final_prompt:
                final_prompt = final_prompt.replace(
                    "[OBJECT]", object_name_for_filename)
                # Use the user-provided name for the filename if [OBJECT] was replaced
                user_provided_object_name = object_name_for_filename
            # If no user object name, but prompt has [OBJECT]
            elif loaded_object_name and "[OBJECT]" in final_prompt:
                # This case might need refinement: what should [OBJECT] be if not provided by user?
                # For now, let's assume it might be replaced by a generic term or removed.
                # Or, we could prompt the user if a default prompt with [OBJECT] is selected.
                # As a simple first step, we'll use the loaded_object_name if available.
                final_prompt = final_prompt.replace(
                    "[OBJECT]", loaded_object_name)
                user_provided_object_name = loaded_object_name  # for filename consistency
            elif "[OBJECT]" in final_prompt:  # [OBJECT] present but no replacement found
                logger.warning(
                    "Default prompt contains [OBJECT] but no object_name_for_filename or library object_name provided. [OBJECT] will remain.")
                # If user_provided_object_name is still empty, the generic filename logic will apply

        else:  # No default prompt in library or library not loaded
            logger.info(
                "No default prompt found in library or library not loaded. Falling back to user input or hardcoded default.")
            try:
                user_provided_object_name_input = input(
                    "Enter the object you want to generate (e.g. 'coffee mug', 'robot', 'house'): "
                ).strip()
                if not user_provided_object_name_input:
                    logger.warning(
                        "No object name provided, using a generic prompt.")
                    final_prompt = "A beautiful abstract design"
                    user_provided_object_name = "generic_design"  # for filename
                else:
                    user_provided_object_name = user_provided_object_name_input
                    # Using a default prompt structure if none is selected from library later
                    final_prompt = (
                        f"A {user_provided_object_name} in orthographic style, plain white background, "
                        f"a highly detailed isometric 3D illustration in orthographic view, "
                        f"featuring smooth, rounded edges and realistic miniature plastic-like materials. "
                        f"Uses a soft pastel color palette with subtle gradients and gentle shadows. "
                        f"Rendered in a clean, modern Apple-style aesthetic."
                    )
            except KeyboardInterrupt:
                logger.info(
                    "Image generation cancelled by user during object input.")
                return None
    elif object_name_for_filename:  # Prompt is provided, but also object_name_for_filename for filename
        user_provided_object_name = object_name_for_filename

    # Construct save_path if not provided
    if save_path is None:
        # Sanitize object_name for filename
        name_part = "generic"
        # Prioritize user_provided_object_name (which could come from input, object_name_for_filename, or loaded_object_name)
        if user_provided_object_name:
            name_part = "".join(
                c if c.isalnum() else '_' for c in user_provided_object_name.lower())
        elif object_name_for_filename:  # Fallback if user_provided_object_name wasn't set but this was
            name_part = "".join(
                c if c.isalnum() else '_' for c in object_name_for_filename.lower())
        elif loaded_object_name:  # Fallback to loaded_object_name if others weren't set
            name_part = "".join(
                c if c.isalnum() else '_' for c in loaded_object_name.lower())

        filename = f"{name_part}_{model}_{int(time.time())}.jpg"
        save_path = os.path.join(DEFAULT_SAVE_DIR, filename)

    # Ensure the directory for save_path exists
    save_dir = os.path.dirname(save_path)
    if save_dir and not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            logger.info(f"Created directory: {save_dir}")
        except OSError as e:
            logger.error(f"Could not create directory {save_dir}: {e}")
            return None

    import urllib.parse
    encoded_prompt = urllib.parse.quote(final_prompt)

    # Use provided negative_prompt or fallback to defaults
    final_negative_prompt = negative_prompt if negative_prompt is not None else defaults[
        "negative_prompt"]

    # Build query parameters from defaults and overrides
    params = {
        "width": width,
        "height": height,
        "seed": seed,
        "model": model,
        "negative_prompt": final_negative_prompt,
        "nologo": "true" if (nologo if nologo is not None else defaults["nologo"]) else None,
        "private": "true" if (private if private is not None else defaults["private"]) else None,
        "enhance": "true" if (enhance if enhance is not None else defaults["enhance"]) else None,
        "safe": "true" if (safe if safe is not None else defaults["safe"]) else None
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    # Add referrer if provided
    if referrer:
        params["referrer"] = referrer

    # The prompt itself is part of the URL path, not a query parameter for this API
    api_url_with_prompt = f"{IMAGE_GENERATION_ENDPOINT}{encoded_prompt}"
    logger.info(
        f"Requesting image from: {api_url_with_prompt} with params: {params}")

    if test_mode:
        logger.info("TEST MODE: Would request image from:")
        logger.info(f"URL: {api_url_with_prompt}")
        logger.info(f"Params: {params}")
        logger.info(f"Would save to: {save_path}")
        return save_path

    try:
        # Increased timeout for image generation
        # Pass parameters directly to requests.get()
        response = requests.get(api_url_with_prompt, params=params, timeout=60)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            file.write(response.content)

        logger.info(f"Image successfully saved to {save_path}")
        return save_path
    except requests.exceptions.Timeout:
        logger.error(
            f"Timeout occurred while generating image from {image_url}")
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"HTTP error during image generation: {http_err} - {response.text}")
        return None
    except IOError as e:
        logger.error(f"Could not save image to {save_path}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating image: {e}")
        return None
    except Exception as e:  # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred: {e}")
        return None


# --- Main Execution ---
if __name__ == "__main__":
    prompt_library = load_prompt_library(PROMPT_LIBRARY_FILE)
    if not prompt_library:
        logger.warning(
            "Prompt library is empty or could not be loaded. Proceeding without predefined prompts.")

    models = get_pollinations_models()
    if models:
        logger.info(f"Available Image Models: {', '.join(models)}")
        flux_found = "flux" in models

        if flux_found:
            logger.info("'flux' model found and selected as default.")
            chosen_model = "flux"  # Default model

            if prompt_library:
                logger.info("\nAvailable Prompts from library:")
                for i, p_info in enumerate(prompt_library):
                    logger.info(f"{i + 1}: {p_info['description']}")

                use_library_prompt = input(
                    "Do you want to use a prompt from the library? (yes/no, default: yes): ").strip().lower()
                if use_library_prompt in ["yes", "y", ""]:
                    while True:
                        try:
                            choice_str = input(
                                f"Enter the number of the prompt you want to use (1-{len(prompt_library)}), or 0 to enter custom prompt: "
                            ).strip()
                            if not choice_str:  # Default to first prompt if empty
                                choice_index = 0
                                logger.info(
                                    f"No input, defaulting to prompt 1: {prompt_library[choice_index]['description']}")
                                break
                            choice_index = int(choice_str) - 1
                            if choice_index == -1:  # User chose 0 for custom prompt
                                selected_prompt_from_lib = None
                                break
                            if 0 <= choice_index < len(prompt_library):
                                selected_prompt_from_lib = prompt_library[choice_index]['prompt']
                                current_object_name_for_file = prompt_library[choice_index].get(
                                    'object_name', 'custom_prompt')
                                break
                            else:
                                logger.warning(
                                    "Invalid choice. Please enter a number within the range or 0.")
                        except ValueError:
                            logger.warning(
                                "Invalid input. Please enter a number.")
                        except KeyboardInterrupt:
                            logger.info("Operation cancelled by user.")
                            exit()
                else:
                    selected_prompt_from_lib = None  # User chose not to use library
                    current_object_name_for_file = "custom_prompt"
            else:  # No prompt library loaded
                selected_prompt_from_lib = None
                current_object_name_for_file = "custom_prompt"

            final_generation_prompt = selected_prompt_from_lib
            object_name_input = ""

            if selected_prompt_from_lib and "[OBJECT]" in selected_prompt_from_lib:
                try:
                    object_name_input = input(
                        "This prompt requires an object. Enter the object (e.g. 'coffee mug', 'robot'): "
                    ).strip()
                    if not object_name_input:
                        logger.warning(
                            "No object name provided for template, using 'item'.")
                        object_name_input = "item"
                    final_generation_prompt = selected_prompt_from_lib.replace(
                        "[OBJECT]", object_name_input)
                    current_object_name_for_file = object_name_input  # Update for filename
                except KeyboardInterrupt:
                    logger.info("Operation cancelled by user.")
                    exit()
            elif selected_prompt_from_lib is None:  # Custom prompt or no library
                # generate_image will handle prompting if final_generation_prompt is None
                pass

            logger.info(
                f"Preparing to generate image... Prompt: {'User will be prompted' if final_generation_prompt is None else final_generation_prompt}")

            try:
                # Pass object_name_input to be used for filename if relevant
                generated_image_path = generate_image(
                    prompt=final_generation_prompt,
                    model=chosen_model,
                    object_name_for_filename=current_object_name_for_file
                )
                if generated_image_path:
                    logger.info(
                        f"Success! Image saved to: {generated_image_path}")
                else:
                    logger.error("Image generation failed.")
            except KeyboardInterrupt:
                logger.info("Image generation process cancelled by user.")
        else:
            logger.warning(
                "'flux' model not found. Please check available models or API.")
    else:
        logger.error(
            "Could not fetch models. Please check your internet connection or the API status.")
