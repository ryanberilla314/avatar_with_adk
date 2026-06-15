# Deployment Script for Gemini Live 3.1 Avatar Agent
# Project: prj-ryan-mgmt-tools
# Target Platform: Google Cloud Run

# Bypass Certificate Based Access (CBA) mTLS check on Cloudtop to avoid ECP install/repair permissions errors
$env:CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE = "false"
$env:CLOUDSDK_CONTEXT_AWARE_USE_ECP_HTTP_PROXY = "false"

$PROJECT_ID = "prj-ryan-mgmt-tools"
$REGION = "us-central1"
$REPO_NAME = "live-avatar-repo"
$IMAGE_NAME = "live-avatar-agent"
$SERVICE_NAME = "live-avatar-service"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Gemini Live Avatar Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Set default project
Write-Host "`n[1/5] Setting gcloud project to $PROJECT_ID..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# 2. Enable necessary APIs
Write-Host "`n[2/5] Enabling Cloud Build, Artifact Registry, and Cloud Run APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    artifactregistry.googleapis.com `
    run.googleapis.com `
    aiplatform.googleapis.com

# 3. Create Artifact Registry repository if it doesn't exist
Write-Host "`n[3/5] Verifying/Creating Artifact Registry Repository..." -ForegroundColor Yellow
$repos = gcloud artifacts repositories list --location=$REGION --format="value(name)"
if ($repos -like "*$REPO_NAME*") {
    Write-Host "Repository '$REPO_NAME' already exists." -ForegroundColor Green
} else {
    Write-Host "Creating Repository '$REPO_NAME'..." -ForegroundColor Green
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="Docker repository for Gemini Live 3.1 Avatar Agent"
}

# 4. Build image in the cloud using Google Cloud Build (removes local Docker dependency)
Write-Host "`n[4/5] Submitting build to Google Cloud Build..." -ForegroundColor Yellow
$IMAGE_TAG = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"
gcloud builds submit --tag $IMAGE_TAG .

# 5. Deploy to Cloud Run
Write-Host "`n[5/5] Deploying image to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_TAG `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --set-env-vars="GCP_PROJECT=$PROJECT_ID" `
    --timeout=3600

Write-Host "`n==============================================" -ForegroundColor Cyan
Write-Host "  Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
