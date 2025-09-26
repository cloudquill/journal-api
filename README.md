# Journal API

This project is a RESTful API for managing personal journal entries, built with FastAPI. It includes robust features such as user authentication, persistent data storage using Azure Cosmos DB, and a structured logging system for improved reliability and debugging.

## 🚀 Features

The API provides core CRUD (Create, Read, Update, Delete) operations for journal entries. But users must authenticate to perform any of these actions:

- ✅ **Create Entry**: Add a new journal entry
- ✅ **Get Entries**: Retrieve a summary list of all entries or fetch full details of a specific entry by ID
- ✅ **Update Entry**: Modify an existing journal entry
- ✅ **Delete Entry**: Remove a journal entry
- ✅ **User Authentication**: Secure JWT-based authentication system
- ✅ **Persistent Storage**: Azure Cosmos DB integration
- ✅ **Structured Logging**: Comprehensive logging for debugging and monitoring

## 🛠️ Technologies Used

- **Python**
- **FastAPI** - Modern web framework for building APIs
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for running the application
- **Azure Cosmos DB** - NoSQL database for persistent storage
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing

## 📋 Prerequisites

- Python 3.8 or higher
- Azure Cosmos DB Emulator (for local development)
- Git (for cloning the repository)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd journal-api
```

### 2. Set Up Virtual Environment

```python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```python
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the `.env.example` file to `.env` and update the values:

```env
COSMOS_ENDPOINT=https://localhost:8081
COSMOS_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
ENTRY_DB=journal
ENTRY_CONTAINER=entries
USER_DB=users
USER_CONTAINER=users
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

Note: The Cosmos endpoint and key are the default for the emulator.
```

**Generate a secure SECRET_KEY:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Run the Application

```python
cd api
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation at:

**http://127.0.0.1:8000/docs**

The Swagger UI allows you to view all endpoints, understand request/response structures, and test the API directly from your browser.

## 🔗 API Endpoints

### Authentication

#### Register User
- **POST** `/users/me/register`
- **Description**: Register a new user account
- **Authentication**: None required
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: Success or error message

#### Login
- **POST** `/users/me/token`
- **Description**: Authenticate user and receive access token
- **Authentication**: None required
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: JWT access token

#### Get Current User
- **GET** `/users/me/`
- **Description**: Get current authenticated user information
- **Authentication**: Required
- **Response**: User information

### Journal Entries

#### Create Entry
- **POST** `/users/me/entries/create`
- **Description**: Create a new journal entry
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "intention": "string",
    "work": "string",
    "struggle": "string"
  }
  ```
- **Response**: A success or error message.

#### Get All Entries
- **GET** `/users/me/entries/all`
- **Description**: Retrieve all journal entries for the authenticated user
- **Authentication**: Required
- **Response**: List of journal entries

#### Get Single Entry
- **GET** `/users/me/entries/{entry_id}`
- **Description**: Retrieve details of a specific entry
- **Authentication**: Required
- **Path Parameters**: `entry_id` (string) - Unique entry identifier
- **Response**: Full entry details

#### Update Entry
- **PUT** `/users/me/entries/update/{entry_id}`
- **Description**: Update an existing journal entry
- **Authentication**: Required
- **Path Parameters**: `entry_id` (string) - Unique entry identifier
- **Request Body** (partial updates supported):
  ```json
  {
    "intention": "string",
    "work": "string",
    "struggle": "string"
  }
  ```
- **Response**: A success or error message.

#### Delete Entry
- **DELETE** `/users/me/entries/delete/{entry_id}`
- **Description**: Delete a journal entry
- **Authentication**: Required
- **Path Parameters**: `entry_id` (string) - Unique entry identifier
- **Response**: A success or error message

## 🗄️ Database Setup

### Azure Cosmos DB Integration

The API uses Azure Cosmos DB for persistent data storage. The Cosmos DB Emulator provides a local development environment.

#### Setup Instructions

1. Download and install the [Azure Cosmos DB Emulator](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-develop-emulator?tabs=windows%2Ccsharp&pivots=api-nosql#install-the-emulator)
2. Start the emulator
3. The default connection details are already configured in the `.env` file

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `COSMOS_ENDPOINT` | Azure Cosmos DB endpoint URL | `https://localhost:8081` |
| `COSMOS_KEY` | Primary key for Cosmos DB | `C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==` |
| `ENTRY_DB` | Database name for entries | `journal` |
| `ENTRY_CONTAINER` | Container name for entries | `entries` |
| `USER_DB` | Database name for users | `users` |
| `USER_CONTAINER` | Container name for users | `users` |
| `SECRET_KEY` | Secret key for JWT signing | `your-secret-key-here` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |


## 🔮 Next Steps

- Implement testing
- Cloud deployment
- Add rate limiting for API endpoints
- Create frontend client application

## 📖 Resources
This project was developed with the help of several resources. Special thanks to the following for their invaluable guidance:
- Project idea and outline: This project was inspired by Learn To Cloud. It is a useful resource for studying and becoming a cloud engineer.
  - Link: [Learn To Cloud](https://learntocloud.guide/)

- JSON-Formatted Logging: The MyJSONFormatter class structure and approach was lifted from a tutorial by mCoding. This resource was crucial for understanding how to log properly and implement JSON-formatted logs.
  - Video Link: [Modern Python Logging](https://www.youtube.com/watch?v=9L77QExPmI0)