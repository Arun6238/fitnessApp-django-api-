from django.db import models,transaction
from django.contrib.auth.models import User
from django.utils import timezone


BODY_PART_CHOICES = [
        ("None",'None'),
        ("Core","Core"),
        ("Arms","Arms"),
        ("Back","Back"),
        ("Chest","Chest"),
        ("Legs","Legs"),
        ("Shoulders","Shoulders"),
        ("Other","Other"),
        ("Olympic","Olympic"),
        ("Full body","Full body"),
        ("Cardio","Cardio"),
    ]

CATEGORY_CHOICES = [
        ("Barbell","Barbell"),
        ("Dumbbell","Dumbbell"),
        ("Machine/Other","Machine/Other"),
        ("Weighted bodyweight","Weighted bodyweight"),
        ("Assisted body","Assisted body"),
        ("Reps only","Reps only"),
        ("Cardio exercice","Cardio exercice"),
        ("Duration","Duration"),
    ]

# model to save all the default exercises  exercises
class Exercise(models.Model):
    name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=50, choices= BODY_PART_CHOICES)
    category = models.CharField(max_length=50, choices= CATEGORY_CHOICES)
    image = models.URLField()

    def __str__(self):
        return self.name
    
# model to save all the exercise instrucitons
class Instruction(models.Model):
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    text = models.TextField(max_length=500)


class CustomeExercise(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=50, choices= BODY_PART_CHOICES)
    category = models.CharField(max_length=50, choices= CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class TrainingSession(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    name = models.CharField(max_length= 150, null= True, blank= True)
    note = models.TextField(max_length=1000,null=True,blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def move_session_to_history(self):
        from .models import TrainingHistory,WorkoutSet
        with transaction.atomic():
            # Inside this block, all database operations will be executed atomically
            
            # calculates the workout duration 
            duration = self.started_at - timezone.now()
            duration_in_seconds = duration.total_seconds()
            
            # Create a TrainingHistory entry from the TrainingSession data
            training_history = TrainingHistory.objects.create(
                name=self.name,
                duration=duration_in_seconds
            )
            # Get the associated WorkoutSet instances
            workout_sets = WorkoutSet.objects.filter(training_session=self)
            
            # Update the WorkoutSet instances to link to the TrainingHistory
            workout_sets.update(training_session=None, training_history=training_history)
            
            # Delete the TrainingSession
            self.delete()
            
        # Once the block exits, the transaction is either committed (if no exceptions occurred)
        # or rolled back (if an exception occurred)
        
        return training_history



class TrainingHistory(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()

class WorkoutSet(models.Model):
    training_session = models.ForeignKey(TrainingSession, on_delete=models.SET_NULL, null= True)
    training_history = models.ForeignKey(TrainingHistory, on_delete=models.SET_NULL, null= True)
    default_exercise = models.ForeignKey(Exercise, on_delete= models.CASCADE, null=True)
    custome_exercise = models.ForeignKey(CustomeExercise, on_delete=models.CASCADE ,null=True)
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField(null= True, blank= True )
    distance = models.FloatField(null= True, blank= True)
    duration = models.DurationField(null= True ,blank= True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(default_exercise__isnull= False) & models.Q(custome_exercise__isnull= True)) |
                    (models.Q(default_exercise__isnull= True) & models.Q(custome_exercise__isnull= False))
                ),
                name="check_single_exercise_field"
            )
        ]


class MeasurementType(models.Model):
    CHOICES_NAME = [
        ("Weight","Weight"),
        ("Caloric intake","Caloric intake"),
        ("Fat_percentage","Fat_percentage"),

        ("Neck","Neck"),
        ("Shoulders","Shoulders"),
        ("Chest","Chest"),
        ("Left bicep","Left bicep"),
        ("Right bicep","Right bicep"),
        ("Left forearm","Left forearm"),
        ("Right forearm","Right forearm"),
        ("Upper abs","Upper abs"),
        ("Waist","Waist"),
        ("Lower abs","Lower abs"),
        ("Hips","Hips"),
        ("Left thigh","Left thigh"),
        ("Right thigh","Right thigh"),
        ("Left calf","Left calf"),
        ("Right calf","Right calf"),
    ]

    CHOICES_TYPE = [
        ("length","length"),
        ("weight","weight"),
        ("percentage","percentage"),
        ("kcal","kcal")
    ]

    name = models.CharField(max_length=50,choices=CHOICES_NAME)
    type = models.CharField(max_length=20,choices =CHOICES_TYPE)

    def __str__(self):
        return f"{self.name} ({self.unit})"


class BodyMeasurement(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    date = models.DateField()
    measurement_type = models.ForeignKey(MeasurementType, on_delete = models.CASCADE)
    value = models.DecimalField(max_digits=6, decimal_places=2)
