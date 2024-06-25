import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64

from custom_package import ChatModel


PROMPT = """
You are an excellent planner. You take the user query and identify steps necessary to complete the query.
Each step is an API call and must exclusively use the list of endpoints provided to you.

Each plan is a list of steps necessary to complete the query. Each step is a dictionary containing 3 keys:
- "step": representing the step's number, e.g., 1,
- "description": a brief description of the action being performed in this step,
- "endpoint": the endpoint of the API to be called during the current step, e.g., "POST /v1/delete/id".

When making your choice among the endpoints, consider the description, requirements, and what the endpoint returns.

Below is the list of the endpoints you can use to create your plan.

endpoints = [
    {
        "endpoint": "POST /v1/images/generations",
        "description": "This API is used to generate an image based on a given query. It then returns the URL of that image.",
        "required": "a query",
        "return": "It returns the URL of the image that was generated."
    },
    {
        "endpoint": "POST /v1/chat/completions",
        "description": "This API is used to generate text content based on a given query.",
        "required": "a query",
        "return": "It returns the text that was generated."
    },
    {
        "endpoint": "POST /v20.0/331866956681863/photos",
        "description": "This API is used to post content containing both an image and text as a single post on a Facebook page. The context is only used when an image is present in the post.",
        "required": "a URL",
        "return": "It returns a dictionary containing the ID of the Facebook page and the ID of the post on that Facebook page."
    },
    {
        "endpoint": "POST /v20.0/331866956681863/feed",
        "description": "This API is used to post text-only content on a Facebook page. The context is only for text.",
        "required": "a query",
        "return": "It returns the ID of the post that was made on the Facebook page."
    }
]

If the current information does not allow you to create a plan that can complete the user request, then return "No plan can be found".

Example:

{"role": "user", "content": "Create text post about lemons and post it on my Facebook page"}
{"role": "assistant", "content": [
    {
        "step": 1,
        "description": "Generate a text about lemons",
        "parameters": {
            "message": "Generate a text about lemons"
        },
        "endpoint": "POST /v1/chat/completions",
        "output": "Lemons are extremely acidic"
    },
    {
        "step": 2,
        "description": "Post the generated text about lemons on the Facebook page.",
        "parameters": {
            "message": "Lemons are extremely acidic"
        }
        "endpoint": "POST /v20.0/331866956681863/feed",
        "output": "successful"
    }
]}

Create a plan to complete the following request from the user:
"""



def main():
    llm = ChatModel(
        prompt=PROMPT
    )

    while True:
        user_query = input("Enter your query:")

        llm.user_content = user_query

        result = llm.get_response()

        print(f"result: {result}")



if __name__ == '__main__':
    main()
