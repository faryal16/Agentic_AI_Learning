import os
from dotenv import load_dotenv


from agents import (
    Agent, Runner, AsyncOpenAI, set_tracing_disabled,OpenAIChatCompletionsModel,
    RunContextWrapper
)
from pydantic import BaseModel
import rich



load_dotenv()
set_tracing_disabled(disabled=True)
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

provider =AsyncOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


# ------------- Pydandic class --------------
class UserInfo(BaseModel):
    name: str

user_input  = input("Enter your name:")
user_info_obj = UserInfo(name= user_input)
#  --------------- dynmic instruction function --------

# def dyn_inst(
#     ctx:RunContextWrapper[UserInfo],
#     agent: Agent
# ) :
#     rich.print(f"dynamic instruction: {ctx}")
#     # rich.print(f"agent: {agent}")
#     return f"The user's name is {ctx.context.name}. Help them with their questions."
    
# ----------dynamic instruction function--------
class DayInst():
    def __init__(self):
        pass
    
    # make a callable function
    def __call__(self, ctx:RunContextWrapper[UserInfo], agent: Agent):
        # ctx.context.name = "junaid" 
        return f"Your are a helpfull assistance.{ctx.context.name} is your user name. Help them with their questions."

dyn_inst = DayInst()
# ------------- Agent ---------------
agent = Agent(
    name="Gemini Agent",
    # instructions="You are a helpful agent.", # fix instruction 
    instructions=dyn_inst, # dynamic instruction function
    
    model= OpenAIChatCompletionsModel(model="openai/gpt-3.5-turbo", openai_client=provider)
)

# ------------- Run the agent ---------------

result = Runner.run_sync(agent, input= "hi, do you know my name?", context=user_info_obj)
print(result.final_output)