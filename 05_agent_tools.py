import os
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, RunConfig, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from openai.types.responses import ResponseTextDeltaEvent
from agents.tool import function_tool
import requests

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# step 1 : Provider

provider = AsyncOpenAI(
    api_key= gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

# Step 2 : Model

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

# Step 3 Config
config = RunConfig(
    model = model,
    model_provider=provider,
    tracing_disabled=True,
)

@function_tool("get weather")
def get_weather(location:str, unit: str = "C") -> str:
    """
    Fetch the weather for a given location, returning a short description.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "error" in data:
            return f"❌ Eror: {data['error']['message']}"
        
        temp_c = data['current']['temp_c']
        temp_f = data['current']['temp_f']
        condition = data['current']['condition']['text']
        city = data['location']['name']
        # country= data['location']['country']
        
        temperature = f"{temp_c}°C" if unit.upper() == "C" else f"{temp_f}°F"

        return f"🌤️ The current weather in {city} is {temperature} with {condition}."
    
    except Exception as e:
        return f"❌ Failed to fetch weather: {str(e)}"


@function_tool("piaic_student_finder")
def student_finder(student_roll : list) -> str:
    """
    find the PIAIC student based on the roll number
    """
    
    data = {1:"Qasim", 2: "Sir Zia", 3: "Daniyal"}
    
    return data.get(student_roll, "Not Found")


# Step 4 Agent
agent = Agent(
    name= "Support Agent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    tools=[get_weather, student_finder],
    model=model,
)

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
    author="Support Agent 🤖",
    content="👋 **Hi!** I'm your assistant.\n\nHow can I help you today?").send()
    
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    msg = cl.Message(
    
    content="🧠 Thinking...",
    
    )

    await msg.send()

    history.append({"role": "user", "content": message.content})
    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=config,
    )
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()