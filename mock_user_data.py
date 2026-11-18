import json
import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()
# sample data
users_db = {
    "U001": {
        "user_id": "U001",
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "age": 28,
        "city": "Bengaluru",
        "role": "Software Engineer",
        "department": "Engineering",
        "join_date": "2022-03-15",
        "status": "active"
    },
    "U002": {
        "user_id": "U002",
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "age": 34,
        "city": "Mumbai",
        "role": "Product Manager",
        "department": "Product",
        "join_date": "2020-07-01",
        "status": "active"
    },
    "U003": {
        "user_id": "U003",
        "name": "Rohan Mehta",
        "email": "rohan.mehta@example.com",
        "age": 25,
        "city": "Pune",
        "role": "Data Analyst",
        "department": "Analytics",
        "join_date": "2023-01-10",
        "status": "on_leave"
    },
    "U004": {
        "user_id": "U004",
        "name": "Ananya Iyer",
        "email": "ananya.iyer@example.com",
        "age": 31,
        "city": "Chennai",
        "role": "UX Designer",
        "department": "Design",
        "join_date": "2021-11-22",
        "status": "active"
    },
    "U005": {
        "user_id": "U005",
        "name": "Vikram Singh",
        "email": "vikram.singh@example.com",
        "age": 42,
        "city": "Delhi",
        "role": "Engineering Manager",
        "department": "Engineering",
        "join_date": "2018-05-08",
        "status": "active"
    }
}   


# tool which groq gotta refer to get user info - 
# so properties is basically what groq sends as parameter which is used by backend to get data based on the properties
tool_funcs = [
    {
      "type": "function",
      "function": {
        "name": "get_user_profile",
        "description": "Get database data based on a user ID",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "user id of the student"
            }
            # "email": {
            #   "type": "string",
            #   "description":"mail id of the user"
            # },
            # "age": {
            #   "type": "int",
            #   "description": "age of the user"
            # },
            # "department": {
            #   "type": "string",
            #   "description": "department that the user belongs to, e.g. Analytics, Design"
            # }
          },
          "required": ["user_id"]
        }
      }
    }
  ]


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# actual code run by backend to retrieve based on what groq asked
def get_user_profile(user_id):
    data = users_db.get(user_id, None)
    print(data)
    if data:
        result = {
        "name": data.get('name'),
        "email": data.get('email'),
        "age": data.get('age'),
        "department": data.get('department'),
        }
        return result
    else:
        # groq returns no records in db
        return "User not found"
messages = [
                       {
                        "role": "user",
                        "content": "get the user data based on the user-id- U100 and give greetings to the user with the information received" 
                        },   
                        {
                        "role": "system",
                        "content": "You are a University assistant. Respond to the user question and use tools if needed to answer the query."
                        }
        ]
while True:
    # run the first message
    response = client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        messages = messages,
        # response_format = {"type": "json_object"},
        tools = tool_funcs,
        # tool_choice = "auto"
    )
    tool = response.choices[0].message.tool_calls 
    mesg = response.choices[0].message.content
    print(f' finish reason - {response.choices[0].finish_reason}')
    
    if response.choices[0].finish_reason != 'tool_calls':
        print(f'{mesg}')
        break
    else:
        # assistant's message (which contains the tool_calls request)
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls
        })
        # print(f'{mesg} message sent by AI')
        for each_tool in tool:
            print(f' each tool sent \n {each_tool}')
            # what groq asked match with what functions/API is present in backend
            if each_tool.function.name == 'get_user_profile':
                
                user_data = json.loads(each_tool.function.arguments)
                user_info = user_data['user_id']
                # unit = each_tool.function.arguments['unit']
                result = get_user_profile(user_info)
                result = json.dumps(result)
                messaged = {
                            "role": "tool",
                            # must match the id from the assistant's tool_calls
                            "tool_call_id": each_tool.id,
                            "name": "get_user_profile",
                            "content": result # convert to string
                            }

                print(f'API/Database returned - {result}')
        # append the message to original list since http (stateless so groq needs context)
        messages.append(messaged)
    # break
    



# response will be present in response.content[0].message.content = str
# but then this changes while using agent loop
