# 📘 BookIt API

A **production-ready REST API** built with **FastAPI** for a simple booking platform — **BookIt**.  
Users can browse services, make bookings, and leave reviews, while admins can manage users, services, and bookings.

This project follows clean, modular architecture with **JWT authentication**, **role-based access control**, **PostgreSQL database**, and **Alembic migrations**.

---

## 🧾 Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Tech Stack](#tech-stack)
- [Database Choice & Justification](#database-choice--justification)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Endpoints Overview](#endpoints-overview)
- [Contributors](#contributors)
- [License](#license)

---

## 🧠 Project Overview
BookIt API provides an efficient way to manage bookings for various services.  

### Key Functionalities:
- Users can:
  - Register, login, and manage their accounts.
  - Book available services and leave reviews.
- Admins can:
  - Manage users and services.
  - View and update bookings.
  - Moderate reviews.

The API enforces **role-based permissions** and returns appropriate **HTTP status codes** for every operation.

---

## 🏗️ Architecture & Design Decisions
- **Framework:** FastAPI – chosen for its asynchronous capabilities, data validation (Pydantic), and built-in docs (Swagger).  
- **Architecture Pattern:** Layered architecture separating:
  - `routers/` → API route handlers  
  - `schemas/` → Pydantic models for request/response validation  
  - `services/` → Business logic and data processing  
  - `models.py` → SQLAlchemy ORM models  
  - `utils/` → Configuration, database, and security utilities  
- **Authentication:** JWT-based (Access + Refresh tokens)  
- **Authorization:** Role-based (User, Admin)  
- **Security:** Passwords hashed with `bcrypt`  
- **Migrations:** Managed with Alembic  
- **Deployment:** Configurable via environment variables and ready for production deployment on **Render**  

---

## ⚙️ Tech Stack
| Layer            | Technology            |
| ---------------- | --------------------- |
| Language         | Python 3.11+          |
| Framework        | FastAPI               |
| Database         | PostgreSQL            |
| ORM              | SQLAlchemy            |
| Migrations       | Alembic               |
| Authentication   | JWT (via python-jose) |
| Password Hashing | bcrypt                |
| Deployment       | PipeOps / Render      |
| Testing          | Pytest                |

---

## 🗄️ Database Choice & Justification
**PostgreSQL** was selected because it provides:
- Strong relational integrity between users, services, and bookings.
- Support for advanced constraints (e.g., unique and foreign keys) that prevent invalid data (like overlapping bookings).
- Excellent support with SQLAlchemy and Alembic migrations.
- ACID compliance — ensuring data consistency even during concurrent operations.

---

## ✨ Features
✅ User registration, login, and logout  
✅ JWT authentication (Access + Refresh)  
✅ Role-based access control  
✅ CRUD operations for services, bookings, and reviews  
✅ Booking conflict prevention  
✅ Structured logging  
✅ Auto-generated API documentation  
✅ Environment-based configuration for production readiness  

---

## 🧩 Project Structure
```
BOOKIT/
│
├── alembic/                     # Database migration folder
│
├── app/
│   ├── routers/                 # Route handlers (API endpoints)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bookings.py
│   │   ├── reviews.py
│   │   ├── services.py
│   │   └── users.py
│   │
│   ├── schemas/                 # Pydantic models for request/response validation
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bookings.py
│   │   ├── reviews.py
│   │   ├── services.py
│   │   └── users.py
│   │
│   ├── services/                # Business logic and CRUD operations
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bookings.py
│   │   ├── reviews.py
│   │   ├── services.py
│   │   └── users.py
│   │
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   └── enums.py
│   │
│   ├── __init__.py                
│   ├── database.py                  
│   └── logger.py
│   ├── main.py                  # Application entry point
│   ├── models.py                # SQLAlchemy ORM models
│   └── requirements.py          # Project dependencies
│   └── security.py
│
├── .env                         # Environment configuration file
├── .gitignore                   # Git ignore rules
├── alembic.ini                  # Alembic configuration file
├── app.log                      # Application log file
├── README.md                    # Project documentation
└── venv/                        # Virtual environment
```

---

## 🧰 Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/OnyekachiEzeala/BookIT.git
cd BookIT
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate     # For macOS/Linux
venv\Scripts\activate        # For Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create the database
Create a PostgreSQL database named `bookit_db`.

### 5️⃣ Apply migrations
```bash
alembic upgrade head
```

---

## ⚙️ Environment Variables
Create a `.env` file in the root directory with the following keys:

| Variable                       | Description                | Example                                                   |
| ------------------------------ | -------------------------- | --------------------------------------------------------- |
| `DATABASE_URL`                 | PostgreSQL database URL    | `postgresql+psycopg2://user:password@localhost/bookit_db` |
| `SECRET_KEY`                   | Secret key for JWT signing | `super_secret_key_here`                                   |
| `ALGORITHM`                    | JWT algorithm              | `HS256`                                                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Access token validity      | `30`                                                      |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token validity     | `60`                                                      |
| `APP_ENV`                      | Environment mode           | `development` / `production`                              |

---

## 🚀 Running the Application
### Run locally with Uvicorn:
```bash
uvicorn app.main:app --reload
```

Visit the API at  
👉 **http://127.0.0.1:8000**

---

## 📚 API Documentation
Auto-generated documentation is available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌐 Deployment
Deployed to **Render** for production hosting.

| Item          | URL                                   |
| ------------- | ------------------------------------- |
| **Base URL**  | `https://bookit-api.render.app`      |
| **Live Docs** | `https://bookit-api.render.app/docs` |

Environment variables and secrets are managed through the Render dashboard.

---

## 🧪 Testing
Run tests using `pytest`:

```bash
pytest -v
```

### Tests to be made
- ✅ Authentication flow (register, login, refresh, unauthorized access)  
- ✅ Booking conflict logic (prevent overlapping bookings)  
- ✅ Permissions (user vs admin routes)  
- ✅ Happy & unhappy paths with correct status codes  

---

## 🔗 Endpoints Overview
| Method   | Endpoint                 | Description               | Access        |
| -------- | ------------------------ | ------------------------- | ------------- |
| `POST`   | `/auth/register`         | Register new user         | Public        |
| `POST`   | `/auth/login`            | Login user                | Public        |
| `POST`   | `/auth/refresh`          | Refresh token             | Authenticated |
| `POST`   | `/auth/logout`           | Logout user               | Authenticated |
| `GET`    | `/me`                    | Get current user profile  | Authenticated |
| `PATCH`  | `/me`                    | Update profile            | Authenticated |
| `GET`    | `/services`              | List available services   | Public        |
| `POST`   | `/services`              | Create service            | Admin         |
| `PATCH`  | `/services/{id}`         | Update service            | Admin         |
| `DELETE` | `/services/{id}`         | Delete service            | Admin         |
| `POST`   | `/bookings`              | Create booking            | User          |
| `GET`    | `/bookings`              | View bookings             | User/Admin    |
| `PATCH`  | `/bookings/{id}`         | Update/reschedule booking | Owner/Admin   |
| `DELETE` | `/bookings/{id}`         | Delete booking            | Owner/Admin   |
| `POST`   | `/reviews`               | Add review                | User          |
| `GET`    | `/services/{id}/reviews` | Get service reviews       | Public        |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📫 Contact

For any questions or support:

* Email: [ezesam227@gmail.com](mailto:ezesam227@gmail.com)
* GitHub: OnyekachiEzeala
