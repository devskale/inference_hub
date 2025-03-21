# main.py
from openrouter import OpenRouter


def main():
    user_message = input("Please enter your message: ")
    print('\n\n--')

    open_router = OpenRouter()
    response = open_router.get_inference(user_message)
    print(response)


if __name__ == "__main__":
    main()
