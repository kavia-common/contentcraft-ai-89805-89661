# ContentCraft AI Backend

FastAPI backend for AI-powered blog generation and management.

## Run

- Install dependencies: `pip install -r requirements.txt`
- Start dev server: `uvicorn src.api.main:app --reload --port 3001`
- Generate OpenAPI (optional): `python -m src.api.generate_openapi`

## Environment

Copy `.env.example` to `.env` and set:
- SECRET_KEY
- DATABASE_URL (default: sqlite:///./contentcraft.db)
- CORS_ALLOW_ORIGINS (optional, CSV)

## Endpoints (summary)

- Health: `GET /`
- Auth:
  - `POST /auth/signup` {email, password, full_name?}
  - `POST /auth/login` (OAuth2 form: username=email, password=pass) -> {access_token}
  - `GET /auth/me` (Bearer auth)
- Generate:
  - `POST /generate` {prompt} -> {title, content} (also saves a draft)
- Blogs (Bearer auth):
  - `POST /blogs`
  - `GET /blogs?skip=0&limit=20&status_filter=draft`
  - `GET /blogs/{id}`
  - `PUT /blogs/{id}`
  - `PATCH /blogs/{id}`
  - `DELETE /blogs/{id}`

Use `Authorization: Bearer <token>` for protected routes.
