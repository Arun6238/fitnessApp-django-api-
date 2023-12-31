# Generated by Django 4.2.3 on 2023-08-22 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomeExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('body_part', models.CharField(choices=[('None', 'None'), ('Core', 'Core'), ('Arms', 'Arms'), ('Back', 'Back'), ('Chest', 'Chest'), ('Legs', 'Legs'), ('Shoulders', 'Shoulders'), ('Other', 'Other'), ('Olympic', 'Olympic'), ('Full body', 'Full body'), ('Cardio', 'Cardio')], max_length=50)),
                ('category', models.CharField(choices=[('Barbell', 'Barbell'), ('Dumbbell', 'Dumbbell'), ('Machine/Other', 'Machine/Other'), ('Weighted bodyweight', 'Weighted bodyweight'), ('Assisted body', 'Assisted body'), ('Reps only', 'Reps only'), ('Cardio exercice', 'Cardio exercice'), ('Duration', 'Duration')], max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('body_part', models.CharField(choices=[('None', 'None'), ('Core', 'Core'), ('Arms', 'Arms'), ('Back', 'Back'), ('Chest', 'Chest'), ('Legs', 'Legs'), ('Shoulders', 'Shoulders'), ('Other', 'Other'), ('Olympic', 'Olympic'), ('Full body', 'Full body'), ('Cardio', 'Cardio')], max_length=50)),
                ('category', models.CharField(choices=[('Barbell', 'Barbell'), ('Dumbbell', 'Dumbbell'), ('Machine/Other', 'Machine/Other'), ('Weighted bodyweight', 'Weighted bodyweight'), ('Assisted body', 'Assisted body'), ('Reps only', 'Reps only'), ('Cardio exercice', 'Cardio exercice'), ('Duration', 'Duration')], max_length=50)),
                ('image', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Weight', 'Weight'), ('Caloric intake', 'Caloric intake'), ('Fat_percentage', 'Fat_percentage'), ('Neck', 'Neck'), ('Shoulders', 'Shoulders'), ('Chest', 'Chest'), ('Left bicep', 'Left bicep'), ('Right bicep', 'Right bicep'), ('Left forearm', 'Left forearm'), ('Right forearm', 'Right forearm'), ('Upper abs', 'Upper abs'), ('Waist', 'Waist'), ('Lower abs', 'Lower abs'), ('Hips', 'Hips'), ('Left thigh', 'Left thigh'), ('Right thigh', 'Right thigh'), ('Left calf', 'Left calf'), ('Right calf', 'Right calf')], max_length=50)),
                ('type', models.CharField(choices=[('length', 'length'), ('weight', 'weight'), ('percentage', 'percentage'), ('kcal', 'kcal')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('note', models.TextField(blank=True, max_length=1000, null=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_number', models.PositiveIntegerField()),
                ('reps', models.PositiveIntegerField(blank=True, null=True)),
                ('distance', models.FloatField(blank=True, null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('custome_exercise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.customeexercise')),
                ('default_exercise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.exercise')),
                ('training_history', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.traininghistory')),
                ('training_session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.trainingsession')),
            ],
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.PositiveIntegerField()),
                ('text', models.TextField(max_length=500)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='BodyMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                ('measurement_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.measurementtype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='workoutset',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('default_exercise__isnull', False), ('custome_exercise__isnull', True)), models.Q(('default_exercise__isnull', True), ('custome_exercise__isnull', False)), _connector='OR'), name='check_single_exercise_field'),
        ),
    ]
