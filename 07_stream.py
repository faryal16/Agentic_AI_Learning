import os

from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
import chainlit as cl

load_dotenv()
set_tracing_disabled(disabled=True)

api_key= os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API missing..")

provider =AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    
)

agent = Agent(
    name="simple agent",
    instructions="You are a helpful assistant.",
    model= OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=provider
    )
)


@cl.on_message
async def my_message(msg: cl.Message):
    
    user_input= msg.content
    message = cl.Message(content="")
    
    
    result = Runner.run_streamed(agent, user_input)
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            await message.stream_token(event.data.delta)
    
    
    
    
    
    
    
    # print(result.final_output)