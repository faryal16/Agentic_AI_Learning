import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    #Reference: https://ai.google.dev/gemini-api/docs/openai
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    
    cl.user_session.set("chat_history", [])
    
    cl.user_session.set("config", config)
    
    agent = Agent(
        name="chatbot",
        instructions="You are a helpful assistant.",
        model=model
    )
    
    cl.user_session.set("agent", agent)
    await cl.Message(content="Welcome to the Panaversity AI Assistant! How can I help you today?").send()
    
@cl.on_message
async def main(message: cl.Message):
     
    msg = cl.Message(content= "Thinking..")
    await msg.send()

    agent : Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig ,cl.user_session.get("config"))
     
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content":message.content})
    
    try:
        
        result = Runner.run_sync(
            starting_agent= agent,
            run_config=config,
            input=history
        )
        
        #  ----------------- run_streamed -------------------
        # async for event in result.stream_events():
        #     if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
        #         token = event.data.delta
        #         await msg.stream_token(token)
        
        #  ----------------- run_sync -------------------
        response = result.final_output
        msg.content =response
        await msg.update()
        # -----------------------------------------------
        
        cl.user_session.set("chat_history", result.to_input_list())
        
        print(f"User: {message.content}")
        print(f"Assistant: {response}")
        
    except Exception as e:
        msg.content= f"An error occurred: {str(e)}"
        await msg.update()
        
        print(f"Error: {str(e)}")