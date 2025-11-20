# FastAPI Secure User Service (Module 10 & 11)

This project is a FastAPI application that implements a **secure user model** and a **calculation model** using SQLAlchemy and Pydantic, with password hashing, validation, automated tests, and a full CI/CD pipeline using GitHub Actions and Docker Hub.

It is built as part of:

- **Module 10:** Secure User Model, Pydantic Validation, Database Testing, and Docker Deployment  
- **Module 11:** Calculation Model with Validation, Optional Factory Pattern, and Extended Testing

---

## Features

### User Model (Module 10)

- **FastAPI** application with automatic OpenAPI docs (`/docs`).
- **SQLAlchemy `User` model** with:
  - `id` (primary key)
  - `username` (unique, indexed)
  - `email` (unique, indexed)
  - `password_hash`
  - `created_at` (timestamp with time zone)
- **Pydantic user schemas**:
  - `UserCreate` → used for incoming data (`username`, `email`, `password`)
  - `UserRead` → used for responses (`id`, `username`, `email`, `created_at`), no password fields.
- **Secure password hashing** using PBKDF2-HMAC-SHA256:
  - `hash_password(plain_password)`
  - `verify_password(plain_password, hashed_password)`
- **User tests**:
  - Unit tests for hashing and schema validation.
  - Integration tests for user creation and uniqueness with a real PostgreSQL database.

### Calculation Model (Module 11)

- **SQLAlchemy `Calculation` model** with:
  - `id`
  - `a` (operand)
  - `b` (operand)
  - `type` (one of `add`, `sub`, `multiply`, `divide`)
  - `result` (optional)
  - `user_id` (optional foreign key to `User`)
  - `created_at` (timestamp with time zone)
- **Pydantic calculation schemas**:
  - `CalculationCreate` → validates `a`, `b`, and `type` using `CalculationType` enum.
  - `CalculationRead` → serializes `id`, `a`, `b`, `type`, `result`, `user_id`, and `created_at`.
  - Validation to **prevent division by zero** when `type == divide`.
- **Factory Pattern** (optional but implemented):
  - `CalculationFactory` that returns a strategy class based on `CalculationType`:
    - `AddCalculation`
    - `SubtractCalculation`
    - `MultiplyCalculation`
    - `DivideCalculation`
  - Each strategy has a `compute(a, b)` method that performs the operation.
- **Calculation tests**:
  - Unit tests verifying:
    - Factory returns the correct strategy for each type.
    - Each operation computes the correct result.
    - Division by zero raises an error.
    - Pydantic rejects invalid types and zero divisors.
  - Integration tests:
    - Insert a calculation, compute result via the factory, and verify it is stored correctly in PostgreSQL.

### CI/CD and Docker

- **Docker & Docker Compose** for running the app + database.
- **GitHub Actions CI/CD**:
  - Starts a PostgreSQL service.
  - Installs dependencies and runs `pytest` on every push / PR to `main`.
  - On push to `main`, builds the Docker image and pushes it to Docker Hub if tests pass.

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
fastapi-secure-user-m11/
  app/
    __init__.py
    main.py                  # FastAPI app and routes
    database.py              # SQLAlchemy engine, SessionLocal, Base
    models.py                # User and Calculation models
    schemas.py               # Pydantic schemas (User*, Calculation*)
    auth.py                  # Password hashing & verification helpers
    crud.py                  # User CRUD helpers
    calculation_factory.py   # Factory pattern for calculations
  tests/
    __init__.py
    conftest.py                      # Test DB setup & TestClient fixture
    test_auth.py                     # Unit tests for hashing
    test_schemas.py                  # Unit tests for user schemas
    test_users_integration.py        # Integration tests for users
    test_calculation_factory.py      # Unit tests for calculation factory
    test_calculation_schemas.py      # Unit tests for calculation schemas
    test_calculation_integration.py  # Integration tests for calculations
  .github/
    workflows/
      ci.yml                 # GitHub Actions: tests + Docker Hub deploy
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

These steps run FastAPI directly with Uvicorn, while PostgreSQL runs in Docker.

### 1. Clone the repository

```bash
git clone https://github.com/pavankumarNagaraju/fastapi-secure-user-m11.git
cd fastapi-secure-user-m11
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

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

### 4. Start PostgreSQL via Docker Compose (db service only)

The `docker-compose.yml` defines a PostgreSQL service mapped to host port **5433**.

```bash
docker compose up -d db
```

This runs a PostgreSQL container with:

- user: `postgres`
- password: `postgres`
- database: `secure_user_db`
- port: `5433` on your local machine

By default, `app/database.py` uses:

```text
postgresql://postgres:postgres@localhost:5433/secure_user_db
```

so no extra env vars are required for local development.

### 5. Run the FastAPI app

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- Swagger UI: http://127.0.0.1:8000/docs

---

## Local API Usage (User Model)

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

> Note: Calculation endpoints are not yet exposed; in Module 11 the focus is on **modeling and validation**. BREAD routes will be added in Module 12.

---

## Running Tests Locally

There are both **unit tests** and **integration tests** (for users and calculations). Integration tests require a real PostgreSQL database.

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
22 passed in X.XXs
```

---

## Running the App with Docker Compose (app + db)

You can run both PostgreSQL and the FastAPI app as containers using `docker compose`.

From the project root:

```bash
docker compose up --build
```

This will:

- Build the app image from the `Dockerfile`.
- Start:
  - `db`   → PostgreSQL (inside the compose network)
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
https://hub.docker.com/r/pavankumarnagaraju/fastapi-secure-user-m11
```

You can pull the image with:

```bash
docker pull pavankumarnagaraju/fastapi-secure-user-m11:latest
```

### Running the Docker Hub image manually

If you already have a PostgreSQL instance accessible from your host (for example, the `db` service from `docker compose` using port `5433`), you can run just the app image:

```bash
docker run --rm -p 8002:8000 ^
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5433/secure_user_db" ^
  pavankumarnagaraju/fastapi-secure-user-m11:latest
```

Then open:

- http://127.0.0.1:8002/docs

> `host.docker.internal` allows the container to reach PostgreSQL running on the host (Windows/macOS Docker Desktop).

---

## CI/CD Pipeline (GitHub Actions → Docker Hub)

The workflow is defined in:

```text
.github/workflows/ci.yml
```

### What the pipeline does

On each **push** or **pull request** to the `main` branch:

1. Start a **PostgreSQL service** (Docker container) inside the GitHub Actions runner.
2. Set `DATABASE_URL` to point to that service.
3. Check out the code.
4. Set up Python 3.12.
5. Install dependencies from `requirements.txt`.
6. Run the full test suite with `pytest` (user + calculation tests).

On **pushes to `main`** (and only if tests pass):

7. Log in to Docker Hub using GitHub Secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN` (Docker Hub access token).
8. Build the Docker image from the `Dockerfile`.
9. Push the image to Docker Hub tagged as:

```text
pavankumarnagaraju/fastapi-secure-user-m11:latest
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

## Reflection

A detailed reflection on the implementation, challenges, and learnings across Module 10 and Module 11 is provided in:

```text
reflection.md
```

---

