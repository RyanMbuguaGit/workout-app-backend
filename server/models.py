import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    # Table constraints
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_exercises_name'),
        db.CheckConstraint('length(trim(name)) > 0', name='ck_exercises_name_not_blank'),
        db.CheckConstraint('length(trim(category)) > 0', name='ck_exercises_category_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    workouts = association_proxy('workout_exercises', 'workout')

    # Model validations
    @validates('name', 'category')
    def validate_text(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'Exercise {key} must be a non-empty string.')
        return value.strip()

    @validates('equipment_needed')
    def validate_equipment(self, key, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be true or false.')
        return value

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    # Table constraints
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workouts_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    exercises = association_proxy('workout_exercises', 'exercise')

    # Model validations
    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, datetime.date):
            raise ValueError('date must be a valid date.')
        return value

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError('duration_minutes must be a positive integer.')
        return value

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    # Table constraints
    __table_args__ = (
        db.UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise_pair'),
        db.CheckConstraint('reps IS NULL OR reps >= 0', name='ck_we_reps_nonnegative'),
        db.CheckConstraint('sets IS NULL OR sets >= 0', name='ck_we_sets_nonnegative'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds >= 0',
            name='ck_we_duration_nonnegative',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validations
    @validates('reps', 'sets', 'duration_seconds')
    def validate_non_negative(self, key, value):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise ValueError(f'{key} must be a non-negative integer.')
        return value

    def __repr__(self):
        return f'<WorkoutExercise {self.id}: workout={self.workout_id} exercise={self.exercise_id}>'