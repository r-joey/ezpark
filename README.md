# EZPark API Backend

This is the backend for the EZPark parking reservation application. It provides APIs for user authentication, managing parking locations, slots, and reservations. It also uses WebSockets for real-time updates (e.g., slot availability).

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python (3.x recommended)
*   pip (Python package installer) 

## Project Setup

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/r-joey/ezpark.git
    cd ezpark
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv .venv
    .venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory. Add the following environment variables.  

    ```env
    FLASK_ENV=development
    DATABASE_URL_DEV='sqlite:///ezpark.db'  
    JWT_SECRET_KEY=your_strong_jwt_secret_key_here # Replace with a strong, random secret key
    PORT=5000  
    ```
    Refer to <mcfile name="config.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\ezpark\config.py"></mcfile> for how these are used.

5.  **Database Migrations:**
    This project uses Flask-Migrate for database schema management.
    ```bash
    # Initialize migrations (only if not already done - check for a 'migrations' folder)
    flask db init 

    # Create a new migration script after making changes to models.py
    flask db migrate -m "Initial migration or descriptive message for changes"

    # Apply the migrations to the database
    flask db upgrade
    ```

6.  **Running the Application:**
    ```bash
    python run.py
    ```
    The application will start, and by default, it should be accessible at `http://localhost:5000` (or the port specified in your `.env` file). The <mcsymbol name="run.py" filename="run.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\run.py" startline="1" type="file"></mcsymbol> script handles running the Flask app with SocketIO.

## API Endpoints

The API endpoints are defined in the `routes` directory:
*   <mcfile name="auth.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\ezpark\routes\auth.py"></mcfile>: Handles user registration, login, profile updates, and admin functionalities.
*   <mcfile name="locations.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\ezpark\routes\locations.py"></mcfile>: Manages parking locations.
*   <mcfile name="slots.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\ezpark\routes\slots.py"></mcfile>: Manages parking slots within locations.
*   <mcfile name="reservations.py" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\ezpark\routes\reservations.py"></mcfile>: Handles parking reservations.

A Postman collection <mcfile name="EZPark API.postman_collection.json" path="d:\PROJECTS\Ingenuity_trial_parking_reservation_app\backend\EZPark API.postman_collection.json"></mcfile> is available in the project root to test the API endpoints.

## Key Technologies Used

*   **Flask:** Web framework.
*   **Flask-SQLAlchemy:** ORM for database interaction.
*   **Flask-Migrate:** Handles database migrations.
*   **Flask-JWT-Extended:** For JWT authentication.
*   **Flask-SocketIO:** For WebSocket communication (real-time updates).
*   **Flask-CORS:** Handles Cross-Origin Resource Sharing.
*   **psycopg2-binary:** PostgreSQL adapter for Python (if using PostgreSQL).
*   **python-dotenv:** For managing environment variables.

## Project Structure