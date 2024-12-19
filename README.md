# Spy Cat Agency API

The Spy Cat Agency API is a FastAPI application designed to manage spy cats, their missions, and associated targets. This API supports CRUD operations, breed validation through TheCatAPI, and robust mission assignment functionalities.

---

## Features

- **Spy Cat Management**:
  - Create, retrieve, update, and delete spy cats.
  - Validate cat breeds using TheCatAPI.

- **Mission Management**:
  - Create missions with multiple targets.
  - Update, retrieve, and delete missions.
  - Assign missions to spy cats with validation.

- **Target Management**:
  - Add targets to missions.
  - Manage target completion status.

---

## Prerequisites

- Python 3.8+
- SQLite (bundled with Python)
- Recommended: A virtual environment for dependency isolation.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Coin-Gulter/Spy_Cat_Agency_REST_api.git
   cd spy-cat-agency
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   python -m main
   ```

---

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access API documentation**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

### Spy Cats
- **POST** `/spy_cats/`: Create a new spy cat (validates breed with TheCatAPI).
- **GET** `/spy_cats/`: List all spy cats.
- **GET** `/spy_cats/{spy_cat_id}`: Retrieve a specific spy cat.
- **PUT** `/spy_cats/{spy_cat_id}`: Update a spy cat (validates breed).
- **DELETE** `/spy_cats/{spy_cat_id}`: Delete a spy cat.
- **POST** `/spy_cats/{spy_cat_id}/assign_mission/`: Assign a mission to a spy cat.

### Missions
- **POST** `/missions/`: Create a new mission with targets.
- **GET** `/missions/`: List all missions.
- **GET** `/missions/{mission_id}`: Retrieve a specific mission (includes assigned spy cats).
- **PUT** `/missions/{mission_id}`: Update mission details.
- **DELETE** `/missions/{mission_id}`: Delete a mission.

---

## Project Structure

```
spy-cat-agency/
├── main.py            # Main application code
├── requirements.txt   # Dependencies
├── README.md          # Documentation
└── spy_cat_agency.db  # SQLite database (auto-created)
```

---

## Notes

- The application integrates TheCatAPI to validate breeds during spy cat creation and updates.
- Testing includes edge cases, such as invalid breeds and restricted operations.
- Use Swagger UI for interactive API exploration.

---

## License

This project is licensed under the MIT License.

