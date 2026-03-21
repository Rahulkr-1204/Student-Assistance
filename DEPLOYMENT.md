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

## Public Hosting (Render)

### 1) Push latest code to GitHub
Your repo is already connected:
- `https://github.com/Rahulkr-1204/Student-Assistance`

### 2) Create services from `render.yaml`
1. Open Render Dashboard
2. Click `New +` -> `Blueprint`
3. Connect your GitHub repo and select `Student-Assistance`
4. Render will detect `render.yaml` and propose:
   - `student-assistance-backend` (Python web service)
   - `student-assistance-frontend` (Static site)

### 3) Set backend environment variables (Render -> backend -> Environment)
Add the same values from `student-support-backend/.env` except local-only values:
- `MONGO_URI`
- `MONGO_DB_NAME`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `TELEGRAM_BOT_TOKEN` (only if needed in production)
- `TELEGRAM_WEBHOOK_SECRET` (only if needed in production)

Set:
- `FRONTEND_BASE_URL=https://<your-frontend-onrender-domain>`

### 4) Set frontend API URL
In Render -> frontend -> Environment:
- `VITE_API_BASE_URL=https://<your-backend-onrender-domain>/api`

### 5) Deploy and test
- Frontend URL: `https://<frontend>.onrender.com`
- Backend health: `https://<backend>.onrender.com/`
- DB status: `https://<backend>.onrender.com/api/db-status`

### 6) Optional custom domain
- Add your domain in each Render service settings.
- Update `FRONTEND_BASE_URL` and `VITE_API_BASE_URL` to final domains.
