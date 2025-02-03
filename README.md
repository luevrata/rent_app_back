# Rent App Backend

This repository contains the backend service for the Rent App. It is built with Flask and includes functionality for user authentication, property management, and rent-related features.

---

## Table of Contents

- [Features developed so far](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Notes for Setup](#notes-for-setup)
- [Running Tests](#running-tests)

---

## Features

- **User Management**: Register, login, and manage landlord/tenant roles.
- **Property Management**: CRUD operations for properties with pagination and filtering.
- **Authentication**: JWT-based authentication for secure API access.
- **Error Handling**: Consistent and descriptive error responses across endpoints.

---

## Tech Stack

- **Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Migrations**: Flask-Migrate
- **Testing**: Pytest

---

## Setup Instructions

### Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Up the Database

Start the PostgreSQL service:
   ```bash
   brew services start postgresql
   ```
### Run Database Migrations
```bash
flask db init
flask db migrate -m "Add models"
flask db upgrade
```

### Set the Environment
```bash
export FLASK_ENV=development
```

### Run the Application
```bash
python3 app.py
```

---

## API Endpoints

### Authentication
- **POST** `/api/auth/register` - Register a new user
- **POST** `/api/auth/login` - Login and get a JWT token

### Property Management
- **POST** `/api/landlords/properties` - Create a property
- **GET** `/api/landlords/properties` - Retrieve properties with optional filters and pagination

---

## Notes for Setup

### Virtual Environment
- Activate the virtual environment:
  ```bash
  source venv/bin/activate
  ```
- Deactivate the virtual environment:
  ```bash
  deactivate
  ```

### Updating Requirements
- After installing new packages, update `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```

### Database Connection
- Connect to the development database:
  ```bash
  psql -U rent_app_dev_user -d rent_app_dev
  ```
- Connect to the production database:
  ```bash
  psql -U rent_app_prod_user -d rent_app_prod
  ```

---

## Running Tests

To run the test suite, use:
```bash
python3 -m pytest tests/test_auth_routes.py -v
python3 -m pytest tests/test_landlords_routes.py -v
```
