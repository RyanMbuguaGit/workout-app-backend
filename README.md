# Workout Application Backend

## Description
A Flask REST API for a workout tracking app used by personal trainers. It tracks
workouts and reusable exercises, and links them through a join table (WorkoutExercises)
that stores reps, sets, and duration. Built with Flask, SQLAlchemy, Flask-Migrate,
and Marshmallow.

## Installation
1. Clone the repo and enter it:
   ```
   git clone https://github.com/RyanMbuguaGit/workout-app-backend.git
   cd workout-app-backend
   ```
2. Install dependencies and activate the virtual environment (Python 3.8 to 3.11):
   ```
   pipenv install
   pipenv shell
   ```
3. Create the database tables:
   ```
   cd server
   flask db upgrade head
   ```
4. Seed example data:
   ```
   python seed.py
   ```

## Running the app
From the `server/` folder:
```
flask run -p 5555
```
(or `python app.py`). The API runs at http://127.0.0.1:5555.

## Running tests
From the `server/` folder:
```
pytest -v
```

## Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration |
| POST | `/workouts` | Create a workout (`date`, `duration_minutes`, optional `notes`) |
| DELETE | `/workouts/<id>` | Delete a workout and its associated WorkoutExercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show an exercise and its associated workouts |
| POST | `/exercises` | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated WorkoutExercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout (`reps`, `sets`, and/or `duration_seconds`) |

## Validations
- **Table constraints:** unique exercise names, non-blank names and categories, positive workout duration, non-negative reps/sets/duration, one entry per exercise per workout.
- **Model validations:** type and value checks using `@validates`.
- **Schema validations:** required fields, length and range checks, and at least one of reps/sets/duration when adding an exercise to a workout.