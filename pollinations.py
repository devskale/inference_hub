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
                user_provided_object_name = object_name_for_filename
            elif loaded_object_name and "[OBJECT]" in final_prompt:
                final_prompt = final_prompt.replace(
                    "[OBJECT]", loaded_object_name)
                user_provided_object_name = loaded_object_name
            elif "[OBJECT]" in final_prompt:
                logger.warning(
                    "Default prompt contains [OBJECT] but no object_name provided. Using default.")
                final_prompt = final_prompt.replace(
                    "[OBJECT]", "object")
                user_provided_object_name = "object"
        else:
            logger.info("Using default prompt")
            final_prompt = "A beautiful abstract design"
            user_provided_object_name = "generic_design"
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

                # Always use first prompt by default
                choice_index = 0
                logger.info(
                    f"Using prompt 1: {prompt_library[choice_index]['description']}")
                selected_prompt_from_lib = prompt_library[choice_index]['prompt']
                current_object_name_for_file = prompt_library[choice_index].get(
                    'object_name', 'custom_prompt')
            else:  # No prompt library loaded
                selected_prompt_from_lib = None
                current_object_name_for_file = "custom_prompt"

            final_generation_prompt = selected_prompt_from_lib
            object_name_input_str = ""

            if selected_prompt_from_lib and "[OBJECT]" in selected_prompt_from_lib:
                try:
                    raw_object_input = input(
                        f"Prompt '{selected_prompt_from_lib.split('[OBJECT]')[0].strip()}' requires an object. Enter object (or p# object to change prompt): "
                    ).strip()

                    if not raw_object_input:
                        logger.warning(
                            "No object name provided, using 'item'.")
                        object_name_input_str = "item"
                        final_generation_prompt = selected_prompt_from_lib.replace(
                            "[OBJECT]", object_name_input_str)
                        current_object_name_for_file = object_name_input_str
                    elif raw_object_input.startswith('p') and len(raw_object_input) > 1 and raw_object_input[1].isdigit():
                        parts = raw_object_input.split(' ', 1)
                        prompt_choice_str = parts[0][1:]
                        if prompt_choice_str.isdigit():
                            prompt_choice_idx = int(prompt_choice_str) - 1
                            if 0 <= prompt_choice_idx < len(prompt_library):
                                selected_prompt_from_lib = prompt_library[prompt_choice_idx]['prompt']
                                current_object_name_for_file = prompt_library[prompt_choice_idx].get(
                                    'object_name', 'custom_prompt')
                                logger.info(
                                    f"Switched to prompt {prompt_choice_idx + 1}: {prompt_library[prompt_choice_idx]['description']}")
                                if "[OBJECT]" in selected_prompt_from_lib:
                                    if len(parts) > 1 and parts[1].strip():
                                        object_name_input_str = parts[1].strip(
                                        )
                                        final_generation_prompt = selected_prompt_from_lib.replace(
                                            "[OBJECT]", object_name_input_str)
                                        current_object_name_for_file = object_name_input_str
                                    else:
                                        logger.warning(
                                            f"Prompt {prompt_choice_idx + 1} requires an object, but none provided after p#. Using 'item'.")
                                        object_name_input_str = "item"
                                        final_generation_prompt = selected_prompt_from_lib.replace(
                                            "[OBJECT]", object_name_input_str)
                                        current_object_name_for_file = "item_from_p_reselect"
                                else:  # Selected prompt does not need an object
                                    final_generation_prompt = selected_prompt_from_lib
                                    object_name_input_str = ""
                                    # current_object_name_for_file is already set from prompt library
                            else:
                                logger.warning(
                                    f"Invalid prompt number p{prompt_choice_str}. Using default prompt 1 and full input as object.")
                                # Fallback to default prompt 1 and use full input as object
                                choice_index = 0  # Default to first prompt
                                selected_prompt_from_lib = prompt_library[choice_index]['prompt']
                                current_object_name_for_file = prompt_library[choice_index].get(
                                    'object_name', 'custom_prompt')
                                # use the whole "pX object" as the object
                                object_name_input_str = raw_object_input
                                final_generation_prompt = selected_prompt_from_lib.replace(
                                    "[OBJECT]", object_name_input_str)
                                current_object_name_for_file = object_name_input_str
                        else:
                            # 'p' followed by non-digit, treat as normal object name
                            object_name_input_str = raw_object_input
                            final_generation_prompt = selected_prompt_from_lib.replace(
                                "[OBJECT]", object_name_input_str)
                            current_object_name_for_file = object_name_input_str
                    else:
                        object_name_input_str = raw_object_input
                        final_generation_prompt = selected_prompt_from_lib.replace(
                            "[OBJECT]", object_name_input_str)
                        current_object_name_for_file = object_name_input_str
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
