from langchain.prompts import ChatPromptTemplate
from octoai.text_gen import ChatCompletionResponseFormat

from dotenv import load_dotenv
load_dotenv()
import os


from octoai.client import OctoAI
from octoai.text_gen import ChatMessage
from fetchpr import get_pr_data
import json
from pydantic import BaseModel, Field
from typing import List



promt_template = """
You are a tool which helps in Resolving merge conflicts. Use the following pieces of conflicting files to answer the question. If you cant do it, just say that you cant. Provide the response in the following structure so we can automate our process.\n

[
    {
        path_to_file: <path>
        content: <content>
    }
]

Example: \n

1. \n

Project: \n

{
    conflicting_files: [
        {
            path: "/Users/bhargavparsi/projects/text.txt"
            content: "<<<<<<< HEAD\nThis is the content in the main branch.\nWe added this line in the main branch.\n=======\nThis is the conflicting content in the feature branch.\nWe added this line in the feature branch.\n>>>>>>> feature-branch\n\n"
        }
    ],
    master_files: [
        {
            path: "/Users/bhargavparsi/projects/text.txt"
            content: "This is the content in the main branch.\nWe added this line in the main branch."
        }
    ],
    pr_files: [
        {
            path: "/Users/bhargavparsi/projects/text.txt"
            content: "This is the conflicting content in the feature branch.\nWe added this line in the feature branch."
        }
    ],
    added_files: [
        {
            path: "/Users/bhargavparsi/projects/text1.txt"
            content: "something"
        }
    ],
    deleted_files: [
        {
            path: "/Users/bhargavparsi/projects/text2.txt"
            content: "something2"
        }
    ]
}

Answer: 
[
    {
        path_to_file: "/Users/bhargavparsi/projects/text.txt"
        content: "This is the conflicting content in the feature branch.\n
        We added this line in the feature branch."
    }
]
"""


client = OctoAI()


class FileEdit(BaseModel):
    path_to_file: str
    content: str
    
    
    
class Output(BaseModel):
    files: List[FileEdit]
    

def generate_test_content():
    return get_pr_data("bhargav265/takenote", 1)
    
content = str(generate_test_content())
# print(content)
completion = client.text_gen.create_chat_completion(
    model="meta-llama-3-70b-instruct",
    messages=[
        ChatMessage(
            role="system",
            content=promt_template,
        ),
        ChatMessage(role="user", content=content),
    ],
    max_tokens=500,
    response_format=ChatCompletionResponseFormat(
        type="json_object",
        schema=Output.model_json_schema(),
    )
)

print(json.loads(completion.choices[0].message.content))

