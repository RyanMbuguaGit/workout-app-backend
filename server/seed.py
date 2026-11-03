#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    squat = Exercise(name='Squat', category='Legs', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='Chest', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    deadlift = Exercise(name='Deadlift', category='Back', equipment_needed=True)
    db.session.add_all([squat, pushup, plank, deadlift])

    print('Creating workouts...')
    leg_day = Workout(date=date(2026, 11, 2), duration_minutes=60, notes='Heavy leg day')
    home_workout = Workout(date=date(2026, 11, 3), duration_minutes=30, notes='No equipment')
    db.session.add_all([leg_day, home_workout])

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, reps=8, sets=4),
        WorkoutExercise(workout=leg_day, exercise=deadlift, reps=5, sets=3),
        WorkoutExercise(workout=home_workout, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=home_workout, exercise=plank, duration_seconds=60),
    ])

    db.session.commit()
    print('Done seeding!')