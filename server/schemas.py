from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    category = fields.String(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Boolean(load_default=False)

    # Shown when viewing one exercise with its workouts
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True, exclude=('exercise',)
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(
        required=True, strict=True, validate=validate.Range(min=1, max=600)
    )
    notes = fields.String(allow_none=True, validate=validate.Length(max=500))

    # Shown when viewing one workout with its exercises
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True, exclude=('workout',)
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Integer(strict=True, validate=validate.Range(min=1))
    sets = fields.Integer(strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(strict=True, validate=validate.Range(min=1))

    exercise = fields.Nested('ExerciseSchema', dump_only=True, exclude=('workout_exercises',))
    workout = fields.Nested('WorkoutSchema', dump_only=True, exclude=('workout_exercises',))

    @validates_schema
    def require_one_measure(self, data, **kwargs):
        """At least one of reps, sets, or duration_seconds must be given."""
        if not any(data.get(key) is not None for key in ('reps', 'sets', 'duration_seconds')):
            raise ValidationError('Provide at least one of reps, sets, or duration_seconds.')