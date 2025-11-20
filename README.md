# FastAPI Secure User Service

This project is a FastAPI application that implements a **secure user model** using SQLAlchemy and Pydantic, with password hashing, validation, automated tests, and a full CI/CD pipeline using GitHub Actions and Docker Hub.

It is built as part of **Module 10: Secure User Model, Pydantic Validation, Database Testing, and Docker Deployment**.

---

## Features

- **FastAPI** application with automatic OpenAPI docs (`/docs`).
- **SQLAlchemy `User` model** with:
  - `id` (primary key)
  - `username` (unique, indexed)
  - `email` (unique, indexed)
  - `password_hash`
  - `created_at` (timestamp with time zone)
- **Pydantic schemas**:
  - `UserCreate` → used for incoming data (`username`, `email`, `password`)
  - `UserRead` → used for responses (`id`, `username`, `email`, `created_at`), no password fields.
- **Secure password hashing** using PBKDF2-HMAC-SHA256:
  - `hash_password(plain_password)`
  - `verify_password(plain_password, hashed_password)`
- **Unit tests** (hashing + schema validation).
- **Integration tests** using a real Postgres database.
- **Docker & Docker Compose** for running app + database.
- **GitHub Actions CI/CD**:
  - Starts a Postgres service.
  - Installs dependencies and runs `pytest`.
  - On push to `main`, builds the Docker image and pushes it to Docker Hub.

---

## Tech Stack

- **Language:** Python 3.12
- **Web Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Validation:** Pydantic v2
- **Database:** PostgreSQL
- **Testing:** pytest, httpx (via FastAPI `TestClient`)
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions → Docker Hub

---

## Project Structure

```text
fastapi-secure-user/
  app/
    __init__.py
    main.py          # FastAPI app and routes
    database.py      # SQLAlchemy engine, SessionLocal, Base
    models.py        # User model
    schemas.py       # Pydantic schemas (UserCreate, UserRead)
    auth.py          # Password hashing & verification helpers
    crud.py          # User CRUD helpers
  tests/
    __init__.py
    conftest.py               # Test DB setup & TestClient fixture
    test_auth.py              # Unit tests for hashing
    test_schemas.py           # Unit tests for Pydantic schemas
    test_users_integration.py # Integration tests against API + DB
  .github/
    workflows/
      ci.yml         # GitHub Actions: tests + Docker Hub deploy
  Dockerfile
  docker-compose.yml
  requirements.txt
  pytest.ini
  .env.example
  README.md
  reflection.md
```

---

## Prerequisites

- Python 3.12
- Git
- Docker Desktop (for running Postgres and the app in containers)
- A Docker Hub account (for CI/CD image push)

---

## Setup & Local Development (without app Docker container)

These steps run FastAPI directly with Uvicorn, while Postgres runs in Docker.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/fastapi-secure-user.git
cd fastapi-secure-user
```

### 2. Create and activate virtual environment

**Windows PowerShell:**

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start Postgres via Docker Compose (db service only)

The `docker-compose.yml` defines a Postgres service mapped to host port **5433**.

```bash
docker compose up -d db
```

This runs a Postgres container with:

- user: `postgres`
- password: `postgres`
- database: `secure_user_db`
- port: `5433` on your local machine

By default, `app/database.py` uses:

```text
postgresql://postgres:postgres@localhost:5433/secure_user_db
```

so no extra env vars are required for local dev.

### 5. Run the FastAPI app

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- Swagger UI: http://127.0.0.1:8000/docs

---

## Local API Usage

### Create a user

`POST /users/`

Example JSON body:

```json
{
  "username": "pavan",
  "email": "pavan@example.com",
  "password": "secret123"
}
```

Successful response (`201 Created`) looks like:

```json
{
  "id": 1,
  "username": "pavan",
  "email": "pavan@example.com",
  "created_at": "2025-01-01T12:34:56.789012+00:00"
}
```

Notice that **no password** or `password_hash` is returned.

### Get a user by ID

`GET /users/{user_id}`

Example:

```text
GET /users/1
```

Returns the same fields as `UserRead`.

---

## Running Tests Locally

There are both **unit tests** and **integration tests**. Integration tests require a real Postgres database.

1. Make sure your virtualenv is active and dependencies are installed.
2. Start the db service:

```bash
docker compose up -d db
```

3. Run tests with pytest:

```bash
pytest
```

You should see all tests passing, for example:

```text
9 passed in 0.84s
```

---

## Running the App with Docker Compose (app + db)

You can run both Postgres and the FastAPI app as containers using `docker compose`.

From the project root:

```bash
docker compose up --build
```

This will:

- Build the app image from the `Dockerfile`.
- Start:
  - `db`   → Postgres (inside the compose network)
  - `app`  → FastAPI app container

The app container uses an environment variable:

```text
DATABASE_URL=postgresql://postgres:postgres@db:5432/secure_user_db
```

so it connects to the `db` service by hostname inside the compose network.

The app is exposed on your host at:

- Swagger UI: http://127.0.0.1:8001/docs

To stop containers:

```bash
docker compose down
```

---

## Docker Hub Image

The CI/CD pipeline builds and pushes the app image to Docker Hub whenever changes are pushed to the `main` branch and tests pass.

Docker Hub repository (example):

```text
https://hub.docker.com/r/pavankumarnagarju/fastapi-secure-user
```

You can pull the image with:

```bash
docker pull pavankumarnagarju/fastapi-secure-user:latest
```

### Running the Docker Hub image manually

If you already have a Postgres instance accessible from your host (for example the `db` service from `docker compose` using port `5433`), you can run just the app image:

```bash
docker run --rm -p 8002:8000 ^
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5433/secure_user_db" ^
  pavankumarnagarju/fastapi-secure-user:latest
```

Then open:

- http://127.0.0.1:8002/docs

> `host.docker.internal` allows the container to reach Postgres running on the host (Windows/macOS Docker Desktop).

---

## CI/CD Pipeline (GitHub Actions → Docker Hub)

The workflow is defined in:

```text
.github/workflows/ci.yml
```

### What the pipeline does

On each **push** or **pull request** to the `main` branch:

1. Start a **Postgres service** (Docker container) inside the runner.
2. Set `DATABASE_URL` to point to that service.
3. Check out the code.
4. Set up Python 3.12.
5. Install dependencies from `requirements.txt`.
6. Run the full test suite with `pytest`.

On **pushes to `main`** (and only if tests pass):

7. Log in to Docker Hub using GitHub Secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN` (Docker Hub access token).
8. Build the Docker image from the `Dockerfile`.
9. Push the image to Docker Hub tagged as:

```text
pavankumarnagarju/fastapi-secure-user:latest
```

This satisfies the assignment requirement for a **working CI/CD pipeline** that tests, builds, and deploys a Docker image.

---

## Environment Variables

The application uses a `DATABASE_URL` environment variable when available.

- **Local development** (no env needed, default is used):

  ```text
  postgresql://postgres:postgres@localhost:5433/secure_user_db
  ```

- **Docker Compose app service**:

  ```yaml
  environment:
    DATABASE_URL: postgresql://postgres:postgres@db:5432/secure_user_db
  ```

You can also create your own `.env` file based on `.env.example` if you want a different configuration.

---



