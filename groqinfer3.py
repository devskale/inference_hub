import argparse
from groq import Groq
import json
from getparams import load_api_credentials, load_model_parameters


def process_question(client, model_parameters, question):
    """
    Sends a user question to the Groq client and prints the response.

    Parameters:
    - client: The initialized Groq client.
    - question: The user's question as a string.
    """
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a helpful assistant."},
            {"role": "user", "content": question},
        ],
        **model_parameters
    )

    for chunk in stream:
        # Check if the content is not None before printing
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")


def main(question=None, model="mixtral-8x7b-32768"):
    """
    Main routine that initializes the Groq client and processes user questions.
    Allows for back-to-back questions from the user.

    Parameters:
    - question: An optional initial question provided as a script argument.
    """
    hoster = 'groq'
    api_key = load_api_credentials(hoster)
    model_parameters, api_url = load_model_parameters(hoster, model)

    client = Groq(api_key=api_key)

    # If an initial question is provided, process it first.
    if question is not None:
        process_question(client, model_parameters, question)
        print("\nYou can continue asking questions. Type 'exit' to quit.")

    while True:
        user_input = input("\nq: ")
        print("\n--\n\na: ", end='')
        if user_input.lower() == 'exit':
            break  # Exit the loop and program if the user types 'exit'.
        process_question(client, model_parameters, user_input)
        print("\n.")




if __name__ == "__main__":
    # Parse command-line arguments for a question.
    parser = argparse.ArgumentParser(
        description='Process a provided question or interactively ask questions.')
    parser.add_argument('-q', '--question', type=str,
                        help='A question to ask the model', default=None)
    parser.add_argument('-m', '--model', type=str,
                        help='model', default="mixtral")
    args = parser.parse_args()

    # Run the main routine with the provided question, if any.
    main(question=args.question, model=args.model)
