import os

from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Schema instances
workout_schema = WorkoutSchema()  # single workout, includes its exercises
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))  # list view
workout_summary_schema = WorkoutSchema(exclude=('workout_exercises',))  # create/response
exercise_schema = ExerciseSchema()  # single exercise, includes its workouts
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises',))  # list view
exercise_summary_schema = ExerciseSchema(exclude=('workout_exercises',))  # create/response
workout_exercise_schema = WorkoutExerciseSchema()


def error(message, status):
    return make_response({'errors': message}, status)


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json(silent=True) or {}
    try:
        validated = workout_summary_schema.load(data)
        workout = Workout(**validated)
        db.session.add(workout)
        db.session.commit()
    except ValidationError as err:
        return error(err.messages, 400)
    except ValueError as err:
        db.session.rollback()
        return error([str(err)], 400)
    except IntegrityError:
        db.session.rollback()
        return error('Could not save workout.', 400)
    return make_response(workout_summary_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error('Workout not found.', 404)
    db.session.delete(workout)  # cascade also deletes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json(silent=True) or {}
    try:
        validated = exercise_summary_schema.load(data)
        exercise = Exercise(**validated)
        db.session.add(exercise)
        db.session.commit()
    except ValidationError as err:
        return error(err.messages, 400)
    except ValueError as err:
        db.session.rollback()
        return error([str(err)], 400)
    except IntegrityError:
        db.session.rollback()
        return error('An exercise with that name already exists.', 409)
    return make_response(exercise_summary_schema.dump(exercise), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error('Exercise not found.', 404)
    db.session.delete(exercise)  # cascade also deletes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------- Add an exercise to a workout ----------

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST'],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if not workout:
        return error('Workout not found.', 404)
    if not exercise:
        return error('Exercise not found.', 404)

    data = request.get_json(silent=True) or {}
    try:
        validated = workout_exercise_schema.load(data)
        workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **validated)
        db.session.add(workout_exercise)
        db.session.commit()
    except ValidationError as err:
        return error(err.messages, 400)
    except ValueError as err:
        db.session.rollback()
        return error([str(err)], 400)
    except IntegrityError:
        db.session.rollback()
        return error('That exercise is already in this workout.', 409)
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)