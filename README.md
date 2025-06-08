# Journal API
This project is a simple RESTful API for managing personal journal entries, built with FastAPI. Currently, all data is stored in-memory, meaning it will be lost whenever the application restarts. Persistent storage will be added shortly.

Technologies used are Python, FastAPI, Pydantic and Uvicorn.

## Features
The API provides core CRUD (Create, Read, Update, Delete) operations for journal entries:

1. Create Entry: Add a new journal entry.

2. Get Entries: Retrieve a summary list of all entries. Also supports fetching the full details of a specific entry by its ID.

3. Update Entry: Modify an existing journal entry.

4. Delete Entry: Remove a journal entry.

## Technologies Used
1. Python

2. FastAPI: A web framework for building APIs with Python.

3. Pydantic: Used by FastAPI for data validation and serialization.

4. Uvicorn: An ASGI server that runs the FastAPI application.

## Setup & Running the Application
Follow these steps to run the API on your local machine:

- Clone the repository (if applicable, otherwise, ensure you have the main.py file).

- Create a virtual environment (recommended):

 ```python
python -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`
```

- Install dependencies:
 ```python
pip install fastapi uvicorn[standard]
```

- Run the application:
Navigate to the directory containing your main.py file in your terminal and run:
```python
uvicorn main:app --reload
# The --reload flag will automatically restart the server when you make changes to your code.
```

## API Endpoints
Once the server is running, you can access the interactive API documentation at:

http://127.0.0.1:8000/docs

This Swagger UI allows you to:

- View all available endpoints (/).

- Understand the expected request bodies and response structures for each endpoint.

- "Try it out" by sending sample requests directly from your browser.



Here's a quick overview of the main journal entry endpoints:

- POST /entries/: Create a new journal entry.

**Request Body**: {"intention": "str", "work": "str", "struggle": "str"}

**Response**: The full EntryResponse including generated id, created_at, and updated_at.

- GET /entries/: Retrieve a summary list of all journal entries.

**Response**: List[EntrySummary] (each with id and intention).

- GET /entries/{entry_id}: Retrieve the details of a single entry.

**Path Parameter**: entry_id (the unique ID of the entry).

**Response**: The full EntryResponse for the matching entry. Returns 404 Not Found if the ID doesn't exist.

- PUT /entries/{entry_id}: Update an existing journal entry.

**Path Parameter**: entry_id.

**Request Body**: {"intention": "str" (optional), "work": "str" (optional), "struggle": "str" (optional)}

**Response**: The updated EntryResponse. Returns 404 Not Found if the ID doesn't exist.

- DELETE /entries/{entry_id}: Delete a journal entry.

**Path Parameter**: entry_id.

**Response**: A confirmation message. Returns 404 Not Found if the ID doesn't exist.


## Next steps
- Database Integration: Connecting to a persistent database (like Azure Cosmos DB, PostgreSQL, or SQLite) to store data permanently.

- Testing: Writing automated tests to ensure API reliability.