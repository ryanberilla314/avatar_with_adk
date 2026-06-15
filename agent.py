import os
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin
from google.genai import types

# System Prompt for Kira
PROMPT_DEV = """
You are Kira, a professional conversational financial assistant.
Tone: Concise, professional, and helpful. Optimize responses to be SHORT and direct for voice/audio.

## TOOL SELECTION & BEHAVIORS
- Direct Execution: When a user query requires a tool call (such as querying an account ID), invoke that tool immediately. Do not stream or generate any introductory text, pleasantries, or placeholders (such as "Let me look that up for you") before invoking the tool.
- Customer Accounts: If the user asks for their account information, details, balance, or provides an account number/ID, use the `query_customer_account` tool to retrieve their account records and answer their queries accurately based on the returned data.
- Speak results: Speak the results clearly and concisely to the user.
"""

# ---------------------------------------------------------
# A2A INTEGRATION TOOL
# ---------------------------------------------------------

async def query_customer_account(account_id: int) -> str:
    """Queries the remote customer account A2A agent to get account info and balance.
    
    Args:
        account_id: The integer ID of the account to query (e.g., 10001).
    """
    import vertexai
    
    try:
        PROJECT_ID = "prj-ryan-mgmt-tools"
        LOCATION = "us-central1"
        client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
        
        # Resource Name of the deployed A2A agent
        a2a_agent_resource = "projects/419844573156/locations/us-central1/reasoningEngines/6766173005740507136"
        
        # Load the remote A2A agent
        remote_app = client.agent_engines.get(name=a2a_agent_resource)
        
        # Send the query to retrieve the account details
        prompt = f"Retrieve information for account number {account_id}"
        response = remote_app.query(input=prompt)
        
        # Return the string of the response
        return str(response)
        
    except Exception as e:
        return f"Failed to retrieve account details from A2A agent: {str(e)}"

# ---------------------------------------------------------
# CONFIG PLUGIN
# ---------------------------------------------------------

class AvatarConfigPlugin(BasePlugin):
  """Plugin to inject Avatar configuration and dynamic prompts before the run starts."""

  def __init__(self):
    super().__init__(name='avatar_config_plugin')

  async def before_run_callback(self, *, invocation_context) -> None:
    # Initialize avatar options
    avatar_name = 'Kira'
    invocation_context.run_config.avatar_config = types.AvatarConfig(
        avatar_name=avatar_name,
    )
    
    # Establish connection params
    invocation_context.run_config.response_modalities = ['VIDEO']
    invocation_context.run_config.enable_affective_dialog = True
    invocation_context.run_config.realtime_input_config = types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            prefix_padding_ms=0,
            silence_duration_ms=0,
        )
    )
    invocation_context.run_config.context_window_compression = (
        types.ContextWindowCompressionConfig(
            trigger_tokens=12800,
            sliding_window=types.SlidingWindow(target_tokens=10240),
        )
    )

    # Set dynamic instructions
    invocation_context.agent.instruction = PROMPT_DEV

# ---------------------------------------------------------
# AGENT DEFINITION
# ---------------------------------------------------------

project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "prj-ryan-mgmt-tools"

root_agent = Agent(
    model=f'projects/{project_id}/locations/global/publishers/google/models/gemini-3.1-flash-live-preview-04-2026',
    name='Kira',
    description='Conversational Financial Assistant Kira',
    instruction='',  # Handled dynamically by AvatarConfigPlugin
    tools=[
        query_customer_account,
    ],
)

app = App(
    name='live_avatar_agent',
    root_agent=root_agent,
    plugins=[
        AvatarConfigPlugin(),
    ],
)
