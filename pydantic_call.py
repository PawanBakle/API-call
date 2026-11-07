## Basically same sequence
## init groq
## pass the intent(question) with format requst as JSON
## before sending creating/request to AI. have a specific JSON format to check the response
## check the response against the format. 

import json
import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

# - data contract 
class CodeAnalysis(BaseModel):
  summary: str = Field(description="One sentence summary of what the code does")
  language: str = Field(description="Programming language detected")
  complexity_score: int = Field(
      description="Complexity rating from 1 (simple) to 10 (complex)"
  )


# - init client
response = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# -Make request in  JSON mode
completion = response.chat.completions.create(
    model="openai/gpt-oss-120b",  
    messages=[{
        "role": "user",
        "content": (
            "Analyze this Python snippet: 'def fib(n): return fib(n-1) + fib(n-2)"
            " if n > 1 else n'. Return ONLY a JSON object with keys: summary,"
            " language, complexity_score."
        ),
    }],
    response_format={"type": "json_object"},  
)

raw_json_str = completion.choices[0].message.content
print(f"1. Raw JSON string from AI:\n{raw_json_str}\n")

# - validate
try:
  validated_data = CodeAnalysis.model_validate_json(raw_json_str)

  print(f"2. Successfully validated into type: {type(validated_data)}")
  print(f"3. Strongly typed access - Language: {validated_data.language}")
  print(
      f"4. Strongly typed access-Complexity (Int):"
      f" {validated_data.complexity_score} (Type: {type(validated_data.complexity_score)})"
  )

except Exception as e:
  print(f"Pydantic Validation Error: {e}")
