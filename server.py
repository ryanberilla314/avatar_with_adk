import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from google.adk.cli.fast_api import get_fast_api_app

# Define the directory containing your agents
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure and create the ADK FastAPI application
# This automatically registers the App from agent.py
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True
)

# Route the root url "/" to serve the custom frontend client
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(AGENT_DIR, "avatar_client.html"))

if __name__ == "__main__":
    # Cloud Run populates the PORT environment variable, defaulting to 8000 for local testing
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
