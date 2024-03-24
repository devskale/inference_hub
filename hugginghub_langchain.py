from langchain_community.llms import HuggingFaceEndpoint

HUGGINGFACEHUB_API_TOKEN = "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"

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

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
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

llm.invoke("What is Deep Learning?")