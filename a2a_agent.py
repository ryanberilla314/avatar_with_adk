import vertexai
from google.adk.agents import Agent
from vertexai.agent_engines import AdkApp

PROJECT_ID = "prj-ryan-mgmt-tools"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://prj-ryan-mgmt-tools-agent-staging"

# Initialize Vertex AI SDK with the staging bucket
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

def get_account_info(account_id: int) -> str:
    """Queries BigQuery for customer account information and balance based on a provided account ID.
    
    Args:
        account_id: The integer ID of the account to query (e.g., 10001).
    """
    from google.cloud import bigquery
    import json
    
    try:
        bq_client = bigquery.Client(project="prj-ryan-mgmt-tools", location="US")
        
        query = """
            SELECT *
            FROM `prj-ryan-mgmt-tools.customer_payment_portal.accounts`
            WHERE Account_ID = @account_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("account_id", "INT64", account_id)
            ]
        )
        
        query_job = bq_client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job]
        
        if not results:
            return "No account found with that ID."
            
        return json.dumps(results, default=str)
        
    except Exception as e:
        return f"Database query failed: {str(e)}"

# Construct the ADK Agent
# This definition acts as the exact blueprint for your automatically generated AgentCard!
bq_agent = Agent(
    model="gemini-2.5-flash",
    # Maps directly to the AgentCard's "name" property
    name="customer_account_agent",
    # Maps directly to the AgentCard's "description" property
    description="Agent that retrieves customer account balances and information from BigQuery.",
    instruction="You are a helpful financial data assistant. Use the get_account_info tool to retrieve customer account records and answer user queries accurately based on the returned data, such as providing their current balance or due date.",
    # The functions passed here are parsed into the AgentCard's "skills" array
    tools=[get_account_info],
)

# Wrap the agent for Agent Engine deployment
# AdkApp automatically handles the A2A plumbing and exposes the /.well-known/agent.json endpoint
app = AdkApp(agent=bq_agent)

print("Deploying agent to Agent Engine. This may take a few minutes...")

# Deploy to Vertex AI Agent Engine
remote_app = client.agent_engines.create(
    agent=app,
    config={
        "staging_bucket": "gs://prj-ryan-mgmt-tools-agent-staging",
        "display_name": "Customer Account A2A Agent Card 2",
        "description": "ADK Agent exposed via A2A protocol to fetch BigQuery account info.",
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]>=1.126.1", 
            "google-cloud-bigquery",
            "google-adk[a2a]>=1.18.0",
            "google-genai>=2.4,<3",
            "cloudpickle",
            "pydantic"
        ],
    },
)

print(f"Agent successfully deployed!\nDeployment Details: {remote_app}")