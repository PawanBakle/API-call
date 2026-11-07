import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv() 
print(os.environ.get("GROQ_API_KEY"))   

# create a client object
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# send ai server with message's content
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "just say hi",
        }
    ],
    model="openai/gpt-oss-120b",
)

print(f'Type 1 = {type(chat_completion)} \n {chat_completion} \n')
print(f'Type 2 = {type(chat_completion.choices)} \n {chat_completion.choices}\n')
print(f'Type 3 = {type(chat_completion.choices[0])} \n {chat_completion.choices[0]}\n')
print(f'Type 4 = {type(chat_completion.choices[0].message)} \n {chat_completion.choices[0].message}\n')
print(f'Response = \n {chat_completion.choices[0].message.content}\n')