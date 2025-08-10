import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,RunConfig,set_tracing_disabled

load_dotenv()
set_tracing_disabled(disabled=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

provider =AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=provider
)

config =RunConfig(
    model=model,
    model_provider=provider
)
