import argparse
import ollama
import os
import json
import time

# Initialize Ollama client with custom host
client = ollama.Client(host="http://localhost:11434")


def describe_image(image_path, idx=None, total=None):
    """
    Describe the content of an image using the Ollama model.

    :param image_path: Path to the image file
    :param idx: Current image index (optional)
    :param total: Total number of images (optional)
    :return: Description of the image
    """
    progress = f"{idx}/{total} " if idx and total else ""
    print(f"{progress}Describing {image_path}...")

    res = client.chat(
        #        model="moondream:v2",
        model="moondream:v2",
        messages=[
            {
                'role': 'user',
                'content': 'Describe the image:',
                'images': [image_path]
            }
        ]
    )
    description = res['message']['content']
    print(f"Description for {image_path}: {description}")
    return description


def main():
    parser = argparse.ArgumentParser(
        description='Interact with Ollama model to describe or query images')
    parser.add_argument(
        'path', type=str, help='path to the image or directory containing images')
    parser.add_argument(
        '--mode', type=str, choices=['d', 'q', 'i'], default='q',
        help='action to perform (d: describe, q: query, i: interactive)')
    args = parser.parse_args()

    if os.path.isfile(args.path):
        # Single image mode
        if args.mode == 'd':
            image_descriptions = {args.path: describe_image(args.path)}
            # Save single image description
            output_dir = os.path.dirname(args.path)
            output_file = os.path.join(output_dir, 'image_descriptions.json')
            with open(output_file, 'w') as f:
                json.dump(image_descriptions, f, indent=4)
            print(f"Image description saved to {output_file}")
        elif args.mode == 'q':
            query = input(
                f"Enter your query about {os.path.basename(args.path)}: ")
            print(f"Querying about {os.path.basename(args.path)}...")
            res = client.chat(
                model="moondream:v2",
                messages=[
                    {
                        'role': 'user',
                        'content': query,
                        'images': [args.path]
                    }
                ]
            )
            answer = res['message']['content']
            print(f"Answer: {answer}")
        else:  # Interactive mode
            action = input(
                f"{os.path.basename(args.path)}? (Describe/Query/Skip/Exit): ").strip().lower()
            if action == 'd':
                image_descriptions = {args.path: describe_image(args.path)}
                # Save single image description
                output_dir = os.path.dirname(args.path)
                output_file = os.path.join(
                    output_dir, 'image_descriptions.json')
                with open(output_file, 'w') as f:
                    json.dump(image_descriptions, f, indent=4)
                print(f"Image description saved to {output_file}")
            elif action == 'q':
                query = input("Enter your query about the image: ")
                print(f"Querying about {os.path.basename(args.path)}...")
                res = client.chat(
                    model="moondream:v2",
                    messages=[
                        {
                            'role': 'user',
                            'content': query,
                            'images': [args.path]
                        }
                    ]
                )
                answer = res['message']['content']
                print(f"Answer: {answer}")
    elif os.path.isdir(args.path):
        # Directory mode
        endings = ['jpg', 'jpeg', 'png']
        images = [f for f in os.listdir(
            args.path) if f.split('.')[-1].lower() in endings]
        image_descriptions = {}
        total_images = len(images)

        for idx, image in enumerate(images, start=1):
            image_path = os.path.join(args.path, image)

            if args.mode == 'd':
                # Describe mode
                description = describe_image(image_path, idx, total_images)
                image_descriptions[image_path] = description
            elif args.mode == 'q':
                # Query mode
                query = input(
                    f"{idx}/{total_images} Enter your query about {image}: ")
                print(f"Querying about {image}...")
                res = client.chat(
                    model="moondream:v2",
                    messages=[
                        {
                            'role': 'user',
                            'content': query,
                            'images': [image_path]
                        }
                    ]
                )
                answer = res['message']['content']
                print(f"Answer: {answer}")
            else:
                # Interactive mode
                action = input(
                    f"{idx}/{total_images} {image}? (Describe/Query/Skip/Exit): ").strip().lower()
                if action == 'd':
                    description = describe_image(image_path)
                    image_descriptions[image_path] = description
                elif action == 'q':
                    query = input("Enter your query about the image: ")
                    print(f"Querying about {image}...")
                    res = client.chat(
                        model="moondream:v2",
                        messages=[
                            {
                                'role': 'user',
                                'content': query,
                                'images': [image_path]
                            }
                        ]
                    )
                    answer = res['message']['content']
                    print(f"Answer: {answer}")
                elif action == 's':
                    continue
                elif action == 'e' or action == 'exit':
                    break
                else:
                    print(
                        "Invalid input. Please enter 'Describe', 'Query', 'Skip', or 'Exit'.")

            time.sleep(1)  # Add a small delay between requests

        # Save the image descriptions to a JSON file if any were collected
        if image_descriptions and args.mode == 'd':
            output_dir = args.path
            output_file = os.path.join(output_dir, 'image_descriptions.json')
            with open(output_file, 'w') as f:
                json.dump(image_descriptions, f, indent=4)
            print(f"Image descriptions saved to {output_file}")
    else:
        print(f"Error: {args.path} is neither a file nor a directory")
        return


if __name__ == "__main__":
    main()
