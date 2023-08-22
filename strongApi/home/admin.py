from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([
    Exercise,
    Instruction,
    CustomeExercise,
    TrainingSession,
    TrainingHistory,
    WorkoutSet,
    MeasurementType,
    BodyMeasurement
    ])