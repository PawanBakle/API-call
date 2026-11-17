import anthropic

client = anthropic.Anthropic()
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for",
                }
            },
            "required": ["city"],
        },
    }
]

def run_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['city']}: 95F, sunny"
    raise ValueError(f"Unknown tool: {name}")

messages = [
    {"role": "user", "content": "What should I wear in Mumbai today?"}
]

# The agent loop. Each iteration sends messages to Claude 
while True:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        # Claude is done. Print the final text and break 
        for block in response.content:
            if block.type == "text":
                print(block.text)
        break

    elif response.stop_reason == "tool_use":
        # Find the tool use blocks in the response and run each one
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    else:
        print(f"Stopped early: {response.stop_reason}")
        break