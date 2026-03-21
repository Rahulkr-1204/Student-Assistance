# Deployment Guide (Docker)

## 1) Prerequisites
- Install Docker Desktop
- Ensure ports `80` and `5000` are free on your machine/server

## 2) Configure backend environment
- Update `student-support-backend/.env` with production values
- Keep `MONGO_URI`, `SMTP_*`, and tokens valid for your server environment

## 3) Build and start containers
From project root (`d:\Student_Assistance`):

```bash
docker compose up --build -d
```

## 4) Verify
- Frontend: `http://localhost`
- Backend health: `http://localhost:5000/`
- Backend DB status: `http://localhost:5000/api/db-status`

## 5) Logs and restart
```bash
docker compose logs -f
docker compose restart backend
docker compose restart frontend
```

## 6) Stop
```bash
docker compose down
```

## Notes
- Frontend uses Nginx and proxies `/api/*` to backend service inside Docker network.
- Frontend API base URL now defaults to `/api` (production-friendly).
- If you deploy on a cloud VM, open inbound ports `80` and `5000` in firewall/security group.

## Public Hosting (Railway + Vercel)

### 1) Backend on Railway (free-friendly)
1. Open Railway dashboard and click `New Project` -> `Deploy from GitHub repo`.
2. Select `Student-Assistance`.
3. Set `Root Directory` to `student-support-backend`.
4. Railway will install dependencies and run:
   - `gunicorn --bind 0.0.0.0:$PORT app:app`

### 2) Backend environment variables on Railway
Add these in Railway service variables:
- `MONGO_URI`
- `MONGO_DB_NAME`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `TELEGRAM_BOT_TOKEN` (optional)
- `TELEGRAM_WEBHOOK_SECRET` (optional)

Keep this for now (update after frontend is live):
- `FRONTEND_BASE_URL=https://<your-vercel-frontend-domain>`

### 3) Frontend on Vercel (free)
1. Open Vercel dashboard and click `Add New...` -> `Project`.
2. Import `Student-Assistance` from GitHub.
3. Set `Root Directory` to `student-support-frontend`.
4. Build settings:
- Build Command: `npm run build`
- Output Directory: `dist`

### 4) Frontend environment variable on Vercel
Set:
- `VITE_API_BASE_URL=https://<your-railway-backend-domain>/api`

### 5) Deploy order
1. Deploy backend first (Railway), copy backend URL.
2. Deploy frontend (Vercel) with `VITE_API_BASE_URL`.
3. Update backend `FRONTEND_BASE_URL` to your Vercel URL.
4. Redeploy backend once.

### 6) Verify
- Frontend: `https://<your-vercel-domain>`
- Backend health: `https://<your-railway-domain>/`
- Backend DB check: `https://<your-railway-domain>/api/db-status`
