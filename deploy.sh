#!/bin/bash
# Deployment Script for Gemini Live 3.1 Avatar Agent
# Project: prj-ryan-mgmt-tools
# Target Platform: Google Cloud Run

PROJECT_ID="prj-ryan-mgmt-tools"
REGION="us-central1"
REPO_NAME="live-avatar-repo"
IMAGE_NAME="live-avatar-agent"
SERVICE_NAME="live-avatar-service"

echo "=============================================="
echo "  Gemini Live Avatar Cloud Run Deployment"
echo "=============================================="

# 1. Set default project
echo -e "\n[1/5] Setting gcloud project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# 2. Enable necessary APIs
echo -e "\n[2/5] Enabling Cloud Build, Artifact Registry, and Cloud Run APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com

# 3. Create Artifact Registry repository if it doesn't exist
echo -e "\n[3/5] Verifying/Creating Artifact Registry Repository..."
REPOS=$(gcloud artifacts repositories list --location=$REGION --format="value(name)" 2>/dev/null)
if [[ $REPOS == *"$REPO_NAME"* ]]; then
    echo "Repository '$REPO_NAME' already exists."
else
    echo "Creating Repository '$REPO_NAME'..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Gemini Live 3.1 Avatar Agent"
fi

# 4. Build image in the cloud using Google Cloud Build
echo -e "\n[4/5] Submitting build to Google Cloud Build..."
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"
gcloud builds submit --tag $IMAGE_TAG .

# 5. Deploy to Cloud Run
echo -e "\n[5/5] Deploying image to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT=$PROJECT_ID" \
    --timeout=3600

echo -e "\n=============================================="
echo "  Deployment Completed Successfully!"
echo "=============================================="
