import json
import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

tool_funcs = [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location"]
        }
      }
    }
  ]

'''
  "messages": [
    {
      "role": "system",
      "content": "You are a weather assistant. Respond to the user question and use tools if needed to answer the query."
    },
'''

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def get_weather(location):
    return f'Temperature is 32C for {location}'
og_message = [
                       {
                        "role": "user",
                        "content": "What's the weather in Mumbai today?" 
                        },   
                        {
                        "role": "system",
                        "content": "You are a weather assistant. Respond to the user question and use tools if needed to answer the query."
                        }
        ]
while True:
    # run the first message
    response = client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        messages = og_message,
        # response_format = {"type": "json_object"},
        tools = tool_funcs,
        # tool_choice = "auto"
    )
    tool = response.choices[0].message.tool_calls 
    mesg = response.choices[0].message.content
    print(f' finish reason - {response.choices[0].finish_reason}')
    
    if response.choices[0].finish_reason != 'tool_calls':
        print(f'final message {mesg}')
        break
    else:
        print(f'{mesg} message sent by AI')
        for each_tool in tool:
            print(f' each tool sent \n {each_tool}')
            if each_tool.function.name == 'get_weather':
                # print(f'this needs to be used here {each_tool.function.name}, and arguments {each_tool.function.arguments}')
                locate = json.loads(each_tool.function.arguments)
                location = locate['location']
                # unit = each_tool.function.arguments['unit']
                result = get_weather(location)
                messaged = {
                            "role": "tool",
                            # must match the `id` from the assistant's `tool_calls`
                            "tool_call_id": each_tool.id,
                            "name": "get_weather",
                            "content": result
                            }

                print(f'returned by {result}')
        og_message.append(messaged)
    # break
    



# response will be present in response.content[0].message.content = str
# but then this changes while using agent loop
