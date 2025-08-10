import os
from dotenv import load_dotenv

import rich
from agents import (
    Agent, Runner,function_tool, AsyncOpenAI, set_tracing_disabled,OpenAIChatCompletionsModel
)

load_dotenv()
set_tracing_disabled(disabled=True)
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

provider =AsyncOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

@function_tool
def karachi_weather(city: str) -> str:
    """
    Get the current weather of karachi.
    """
    return f"The current weather in {city} is sunny with a temperature of 30°C." 
    
@function_tool
def solve_math_problem(a:int , b: int, operation: str = "+") -> str:
    """Solve simple math problems"""
    print("\nTool Called:")
    
   

    if operation == "+":
        return f"\nThe result of {a} + {b} is {a + b}."
    elif operation == "-":
        return f"\nThe result of {a} - {b} is {a-b}."
    elif operation == "*":
        return f"\nThe result of {a} * {b} is {a * b}."
    elif operation == "/":
        if b == 0:
            return "\nDivision by zero is not allowed."
        else:
            return f"\nThe result of {a} / {b} is {a / b}."
            
    else:
        "\nUnsupported operation. Please use +, -, *, or /."
    

agent = Agent(
    name="Gemini Agent",
    instructions="You are a helpful agent. Use the 'karachi_weather' tool to answer questions about Karachi's weather.",
    # tools=[karachi_weather],
    tools=[solve_math_problem],
    model= OpenAIChatCompletionsModel(model="openai/gpt-3.5-turbo", openai_client=provider)
)




while True:
    user_query = input("Enter your query (type 'exit' to quit): ").strip()
    if user_query.lower() == "exit":
        break
    
    result = Runner.run_sync(agent, user_query)
    rich.print(result.final_output)