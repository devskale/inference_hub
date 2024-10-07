import ollama
import os

dir = './data'

# load all image files into a list
endings = ['jpg', 'jpeg', 'png']
images = [f'{dir}/{f}' for f in os.listdir(dir) if f.split('.')[-1].lower() in endings]

for image in images:
    total_images = len(images)
    for idx, image in enumerate(images, start=1):
        action = input(f"{idx}/{total_images}     {image}? (Describe/Query/Skip/Exit): ").strip().lower()
        if action == 'd':
            print(f"Describing {image}...")
            res = ollama.chat(
                model="moondream",
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe the image:',
                        'images': [image]
                    }
                ]
            )
            description = res['message']['content']
            print(f"Description for {image}: {description}")
        elif action == 'q':
            query = input("Enter your query about the image: ")
            print(f"Querying about {image}...")
            res = ollama.chat(
                model="moondream",
                messages=[
                    {
                        'role': 'user',
                        'content': query,
                        'images': [image]
                    }
                ]
            )
            answer = res['message']['content']
            print(f"Answer: {answer}")
        elif action == 's':
            continue
        elif action == 'e' or action == 'exit':
            exit()
        else:
            print("Invalid input. Please enter 'Describe', 'Query', 'Skip', or 'Quit'.")