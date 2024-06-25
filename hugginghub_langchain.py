from langchain_community.llms import HuggingFaceEndpoint
from getparams import load_api_credentials, load_model_parameters

api_token = load_api_credentials('huggingface')
#HUGGINGFACEHUB_API_TOKEN = "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"


repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
#repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
#repo_id="stabilityai/stablelm-zephyr-3b"
#repo_id="01-ai/Yi-1.5-34B-Chat"
#repo_id="microsoft/Phi-3-mini-4k-instruct"

""" llm = HuggingFaceEndpoint(
                endpoint_url=repo_id,
                max_new_tokens=512,
                top_k=10,
                top_p=0.95,
                typical_p=0.95,
                temperature=0.01,
                repetition_penalty=1.03,
                huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
            )

print(llm.invoke("What is Deep Learning?"))
 """

from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

print(f"loading {repo_id}")

callbacks = [StreamingStdOutCallbackHandler()]
llm = HuggingFaceEndpoint(
    endpoint_url=repo_id,
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
    callbacks=callbacks,
    streaming=True,
    huggingfacehub_api_token=api_token
    )


#llm.invoke("What is Deep Learning?")

while True:
    user_input = input("\nq: ")
    if user_input.lower() == 'exit':
        break  # Exit the loop and program if the user types 'exit'.
    print("\n--\n\na: ", end='')
    llm.invoke(user_input)
#    print(output[0]['generated_text'])
