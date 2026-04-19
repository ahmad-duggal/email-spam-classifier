# Production Deployment Guide: Digital Sentinel AI

This document provides step-by-step instructions for deploying your Full-Stack Machine Learning Architecture into a true SAAS production environment.

## 1. Backend Deployment (Render.com)

Render is the preferred platform for hosting our highly-concurrent FastAPI inference engine.

1. Create a [Render.com](https://render.com) account and connect your GitHub repository.
2. Click **New +** and select **Web Service**.
3. Choose your repository.
4. Fill in the deployment criteria:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - (Optional) Set up any variables if needed in the future.
6. Click **Create Web Service**. 
   Render will provide an active URL (e.g., `https://digital-sentinel-api.onrender.com`).

*(Ensure you copy this URL for the frontend step).*

## 2. Frontend Deployment (Streamlit Cloud)

Streamlit Community Cloud is optimized for hosting our heavily customized SAAS dashboard.

1. Navigate to [share.streamlit.io](https://share.streamlit.io/) and link your GitHub.
2. Click **New app**.
3. Provide the repository details:
   - **Main file path**: `app/streamlit_app.py`
4. Click **Advanced Settings**.
5. Under "Secrets" or "Environment Variables", inject the connection to your Render Backend to decouple the ML load:
   ```toml
   FASTAPI_URL = "https://digital-sentinel-api.onrender.com"
   ```
6. Click **Deploy!**

## 3. Architecture Benefits
Because we modified `app/streamlit_app.py` to natively listen to `FASTAPI_URL`, the moment you inject it into the Streamlit server settings, the dashboard will automatically stop processing ML requests locally, and will instead dynamically route all heavy AI inferences (like bulk REST checks and Bayesian evaluation) exclusively to your dedicated Render container over HTTP!

If no variable is provided, it safely falls back to native local execution.
