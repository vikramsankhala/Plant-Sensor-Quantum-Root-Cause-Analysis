# Deployment Guide

## Streamlit Community Cloud Deployment

### Prerequisites
- GitHub account
- Repository pushed to GitHub (✅ Already done: https://github.com/vikramsankhala/Plant-Sensor-Quantum-Root-Cause-Analysis)

### Steps to Deploy

1. **Go to Streamlit Community Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy Your App**
   - Click "New app" button
   - Select your GitHub account
   - Choose repository: `vikramsankhala/Plant-Sensor-Quantum-Root-Cause-Analysis`
   - Set main file path: `streamlit_app.py`
   - Click "Deploy!"

3. **Wait for Deployment**
   - Streamlit will automatically:
     - Install dependencies from `requirements.txt`
     - Build your app
     - Deploy it to a public URL

4. **Access Your App**
   - Once deployed, you'll get a URL like: `https://plant-sensor-quantum-root-cause-analysis.streamlit.app`
   - Share this URL with others!

### Environment Variables (Optional)

If you need to set environment variables (e.g., IBM Quantum credentials):

1. Go to your app's settings in Streamlit Community Cloud
2. Click "Secrets" tab
3. Add your secrets in TOML format:
   ```toml
   IBM_QUANTUM_TOKEN = "your_token_here"
   IBM_QUANTUM_INSTANCE = "your_instance_here"
   ```

### Troubleshooting

- **Build fails**: Check that `requirements.txt` includes all dependencies
- **Import errors**: Ensure all Python packages are listed in `requirements.txt`
- **App not loading**: Check the logs in Streamlit Community Cloud dashboard

### Local Testing

Before deploying, test locally:
```bash
streamlit run streamlit_app.py
```

## FastAPI Deployment (Alternative)

If you prefer to deploy the FastAPI service instead:

### Option 1: Railway
1. Go to https://railway.app/
2. Connect GitHub repository
3. Select the repository
4. Railway will auto-detect FastAPI and deploy

### Option 2: Render
1. Go to https://render.com/
2. Create new Web Service
3. Connect GitHub repository
4. Set build command: `pip install -e .`
5. Set start command: `uvicorn psq.api.fastapi_app:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku
1. Create `Procfile` with: `web: uvicorn psq.api.fastapi_app:app --host 0.0.0.0 --port $PORT`
2. Deploy via Heroku CLI or GitHub integration

