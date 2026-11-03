import os

# Must be set before importing app so tests use a throwaway in-memory database
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

from datetime import date

import pytest

from app import app
from models import db, Exercise, Workout, WorkoutExercise


@pytest.fixture(autouse=True)
def database():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    return app.test_client()


def make_exercise(client, name='Squat'):
    return client.post(
        '/exercises', json={'name': name, 'category': 'Legs', 'equipment_needed': True}
    )


def make_workout(client):
    return client.post(
        '/workouts', json={'date': '2026-11-03', 'duration_minutes': 45, 'notes': 'Leg day'}
    )


def add_link(client, workout_id, exercise_id, **body):
    return client.post(
        f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises', json=body
    )


def test_create_exercise(client):
    res = make_exercise(client)
    assert res.status_code == 201
    assert res.get_json()['name'] == 'Squat'


def test_duplicate_exercise_name_rejected(client):
    make_exercise(client)
    assert make_exercise(client).status_code == 409


def test_exercise_missing_category_rejected(client):
    res = client.post('/exercises', json={'name': 'Plank'})
    assert res.status_code == 400
    assert 'category' in res.get_json()['errors']


def test_workout_negative_duration_rejected(client):
    res = client.post('/workouts', json={'date': '2026-11-03', 'duration_minutes': -5})
    assert res.status_code == 400


def test_list_endpoints(client):
    make_workout(client)
    make_exercise(client)
    assert len(client.get('/workouts').get_json()) == 1
    assert len(client.get('/exercises').get_json()) == 1


def test_add_exercise_to_workout_and_view(client):
    workout = make_workout(client).get_json()
    exercise = make_exercise(client).get_json()
    res = add_link(client, workout['id'], exercise['id'], reps=10, sets=3)
    assert res.status_code == 201

    detail = client.get(f"/workouts/{workout['id']}").get_json()
    assert detail['workout_exercises'][0]['reps'] == 10
    assert detail['workout_exercises'][0]['exercise']['name'] == 'Squat'

    ex_detail = client.get(f"/exercises/{exercise['id']}").get_json()
    assert ex_detail['workout_exercises'][0]['workout']['duration_minutes'] == 45


def test_add_exercise_needs_a_measure(client):
    workout = make_workout(client).get_json()
    exercise = make_exercise(client).get_json()
    assert add_link(client, workout['id'], exercise['id']).status_code == 400


def test_same_exercise_twice_in_workout_rejected(client):
    workout = make_workout(client).get_json()
    exercise = make_exercise(client).get_json()
    add_link(client, workout['id'], exercise['id'], reps=5)
    assert add_link(client, workout['id'], exercise['id'], reps=5).status_code == 409


def test_delete_workout_deletes_workout_exercises(client):
    workout = make_workout(client).get_json()
    exercise = make_exercise(client).get_json()
    add_link(client, workout['id'], exercise['id'], sets=2)
    assert client.delete(f"/workouts/{workout['id']}").status_code == 204
    assert WorkoutExercise.query.count() == 0


def test_delete_exercise_deletes_workout_exercises(client):
    workout = make_workout(client).get_json()
    exercise = make_exercise(client).get_json()
    add_link(client, workout['id'], exercise['id'], sets=2)
    assert client.delete(f"/exercises/{exercise['id']}").status_code == 204
    assert WorkoutExercise.query.count() == 0


def test_missing_records_return_404(client):
    assert client.get('/workouts/999').status_code == 404
    assert client.get('/exercises/999').status_code == 404
    assert client.delete('/workouts/999').status_code == 404
    assert client.delete('/exercises/999').status_code == 404


def test_model_validations():
    with pytest.raises(ValueError):
        Workout(date=date.today(), duration_minutes=-1)
    with pytest.raises(ValueError):
        Exercise(name='   ', category='Core')
    with pytest.raises(ValueError):
        WorkoutExercise(reps=-3)