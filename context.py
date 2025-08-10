import os
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig ,enable_verbose_stdout_logging
from agents.tool import function_tool
from pydantic import BaseModel

load_dotenv()
enable_verbose_stdout_logging()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# -------------step 1 : Provider

provider = AsyncOpenAI(
    api_key= gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

# -------------Step 2 : Model

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

# -------------Step 3 Config
config = RunConfig(
    model = model,
    model_provider=provider,
    tracing_disabled=True,
)

# ------------- local context
class UserInfo(BaseModel):
    name: str

@function_tool
def greet(wrapper:RunContextWrapper[UserInfo]) -> str:
    """
    Greet the user with their name.
    
    """
    print("Greeting", wrapper.context.name)
    return f"Hello, {wrapper.context.name}! How can I assist you today?"





# -------------tool----------
# @function_tool
# def greet(name: str) -> str:
#     """
#     Greet the user with their name.
    
#     """
#     print("Greeting", name)
#     return f"Hello, {name}! How can I assist you today?"

agent = Agent(
    name="Suppport Agent",
    instructions="You are support agent. Help the user with their queries",
    tools=[greet]
)

user_context = UserInfo(name= "Noor Fatima")
prompt = input("Enter your query: ")

result = Runner.run_sync(
    agent, prompt, run_config=config,
    context=user_context  # for local context
)

print(result.final_output)