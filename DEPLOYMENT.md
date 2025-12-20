# Deployment Guide

## Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB Atlas Account

## 1. Environment Variables

### Backend (`backend/.env`)
```bash
MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0"
MONGO_PASSWORD="your_password"
BACKEND_CORS_ORIGINS="http://localhost:5173,https://your-frontend-domain.com"
```

### Frontend (`frontend/.env`)
```bash
VITE_API_URL="https://your-backend-domain.com/api/v1"
```

## 2. Build & Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run preview
```

## 3. Render Deployment (Backend)

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- **Root Directory**: `backend`
- **Environment Variables**:
    - `PYTHON_VERSION`: `3.11.0` (or your local version)
    - `MONGO_URI`: ...
    - `BACKEND_CORS_ORIGINS`: ...
