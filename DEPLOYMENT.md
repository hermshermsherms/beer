# Beer App Deployment Guide

## 🚀 Quick Deploy

### Backend (Railway)
1. Create account at [Railway](https://railway.app)
2. Connect your GitHub repository
3. Deploy from `backend/` directory
4. Set environment variables:
   - `SUPABASE_URL` = your_supabase_url
   - `SUPABASE_ANON_KEY` = your_supabase_key
5. Railway will auto-deploy using the Dockerfile

### Frontend (Vercel)
1. Push code to GitHub
2. Create account at [Vercel](https://vercel.com)
3. Import your repository
4. Build settings (auto-detected from vercel.json):
   - Build command: `cd frontend && npm install && npm run build`
   - Output directory: `frontend/dist`
5. Update API URLs in frontend code to point to your Railway backend

## 🔧 Manual Steps

### 1. Create GitHub Repository
```bash
# Push to GitHub
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Backend Deployment (Railway)
- Sign up at railway.app
- "New Project" → "Deploy from GitHub"
- Select your repo
- Choose `backend/` as root directory
- Add environment variables in Railway dashboard
- Deploy will start automatically

### 3. Frontend Deployment (Vercel)
- Sign up at vercel.com
- "New Project" → Import from GitHub
- Select your repository
- Vercel auto-detects settings from vercel.json
- Deploy

### 4. Update Frontend Config
After backend is deployed, update the API URL in your React components:
```typescript
// Replace localhost:8000 with your Railway URL
const API_BASE = 'https://your-app.railway.app/api';
```

## 🌐 Production URLs
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

## ✅ Post-Deployment Checklist
- [ ] Backend API accessible at /docs
- [ ] Frontend loads without errors
- [ ] User registration works
- [ ] Beer posting with images works
- [ ] All pages navigate correctly
- [ ] Leaderboard displays charts
- [ ] Delete functionality works

## 🔒 Security Notes
- Environment variables are set in hosting platforms
- Supabase RLS policies protect data
- CORS configured for production domains
- No sensitive data in git repository

Your Beer App is now ready for the world! 🍺