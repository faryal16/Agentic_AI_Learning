import os
from dotenv import load_dotenv


from agents import (
    Agent, Runner, AsyncOpenAI, set_tracing_disabled,OpenAIChatCompletionsModel
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

agent = Agent(
    name="Gemini Agent",
    instructions="You are a helpful agent.",
    
    model= OpenAIChatCompletionsModel(model="openai/gpt-3.5-turbo", openai_client=provider)
)

    
result = Runner.run_sync(agent, input="hi")
print(result.final_output)