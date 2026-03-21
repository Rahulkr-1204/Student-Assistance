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
