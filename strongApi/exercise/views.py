from django.core.exceptions import ValidationError
from django.db import transaction

import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes,throttle_classes

from home.models import Exercise,Instruction,CustomeExercise,TrainingSession,WorkoutSet,TrainingTemplate,TrainingTemplateExercise,CATEGORY_CHOICES,BODY_PART_CHOICES
from .serializer import AllExerciseSerializer,InstructionSerializer,TrainingSessionSerializer

def validate_exercise(exercise):
    name = exercise.get("name")
    image = exercise.get("image")
    body_part = exercise.get("bodyPart")
    category = exercise.get("category")

    if not name and not image:
        raise ValidationError("Exercise name and image URL cannot be empty")
    if not name:
        raise ValidationError("Name cannot be empty")
    if not image:
        raise ValidationError("Image URL cannot be empty")
    if body_part not in dict(BODY_PART_CHOICES):
        raise ValidationError("Invalid body_part")
    if category not in dict(CATEGORY_CHOICES):
        raise ValidationError("Invalid category")

# function to merge and sort Exercise and CustomExercise query set based on name (exercise name)
def merge_sort_exercise(list1,list2,sliceValue):
    result = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i].name < list2[j].name:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1   
        # set next as last name of 
    if len(list1)<sliceValue and len(list2)<sliceValue:
        result.extend(list1[i:])
        result.extend(list2[j:])
    return result



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def add_default_exercise(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        exercise = data['exercise']
        instruction = data['instruction']

        # Validate the exercise data
        validate_exercise(exercise)

        # Check if at least one instruction is present
        if len(instruction) == 0:
            raise ValidationError("at least one instruction is required")

        # Create an Exercise instance
        newExercise = Exercise(
            name=exercise['name'],
            body_part=exercise['bodyPart'],
            category=exercise["category"],
            image=exercise["image"]
        )

        # Loop through instructions
        lastIndex = len(instruction) - 1
        instructions_to_create = []
        for index, value in enumerate(instruction):
            # Check if the current instruction is empty and not the last one
            if index != lastIndex and value == "":
                raise ValidationError(f"instruction {index + 1} is empty")
            # If the last instruction is empty, exit the loop
            elif index == lastIndex and value == "":
                break
            instructions_to_create.append(Instruction(
                exercise=newExercise,
                step_number=index + 1,
                text=value
            ))

        # Save the newExercise instance
        newExercise.save()

        # Bulk create Instruction instances
        Instruction.objects.bulk_create(instructions_to_create)

        # Return success message
        return Response({"detail": "Data received successfully.."})
    
    # Handle JSON decoding error
    except json.JSONDecodeError:
        return Response({"detail": "invalid json data"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle validation error
    except ValidationError as e:
        print(e.args[0])
        return Response({"detail": "invalid category"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list(request):
    user = request.user
    try:
        next_exercise= request.GET.get('next') if request.GET.get('next') else ""
        name = request.GET.get('name') if request.GET.get('name') else ""
        category = request.GET.get('category') if request.GET.get('category') else ""
        body_part =request.GET.get('body_part') if request.GET.get('body_part') else ""
        combined_array= []
        next= ""
        has_next = True
        sliceValue = 10
        
        # Query for Exercise objects with name greater than 'next'
        standard_exercise = Exercise.objects.filter(
            name__gt=next_exercise,                
            name__icontains=name,
            category__icontains=category,
            body_part__icontains=body_part
        ).order_by('name')[:sliceValue]
        # Query for CustomeExercise objects with name greater than 'next' for a specific user
        custom_exercise = CustomeExercise.objects.filter(
            user=user,
            name__gt=next_exercise,
            name__icontains=name,
            category__icontains=category,
            body_part__icontains=body_part
        ).order_by('name')[:sliceValue]
        standard_exercise_length = len(standard_exercise)
        custom_exercise_length = len(custom_exercise)
        if custom_exercise_length < 10 and standard_exercise_length < 10:
            has_next = False
        if custom_exercise_length != 0 or standard_exercise_length != 0:
            if custom_exercise_length == 0:
                combined_array = standard_exercise 
            elif standard_exercise_length == 0:
                combined_array = custom_exercise
            else:
                combined_array = merge_sort_exercise(standard_exercise,custom_exercise,sliceValue)
    # if combined array is not empty then set next as the name of last exercise in compined_exercise array
        if len(combined_array)>0:
            next = combined_array[len(combined_array)-1].name

        serializer = AllExerciseSerializer(combined_array,many = True)
        return Response({"exercise":serializer.data,"next":next,"has_next":has_next})
    except Exception as e:
        print(e.args[0])
        return Response({"detail": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# returns information about a given exercise 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_exercise(request):
    is_custom = request.GET.get('isCustom') == "true"
    exercise_id = request.GET.get('exercise_id')

    print(f"is_custom:{is_custom} \n exercise_id: {exercise_id}")
    result = {
        "exercise":{},
        "instructions":[],
        "history":None,
    }
    try:
        if is_custom:
            exercise =  CustomeExercise.objects.get(id=exercise_id)        
        else:
            exercise = Exercise.objects.get(id=exercise_id)
            instruction  = Instruction.objects.filter(exercise = exercise).order_by("step_number")
            instruction_serializer = InstructionSerializer(instruction,many=True)
            result['instructions'] = instruction_serializer.data
        exercise_serializer = AllExerciseSerializer(exercise)
        result['exercise'] = exercise_serializer.data
        return Response(result)
    
    except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Workout
# -------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_templates(request):
    user  = request.user
    result = []
    try:
        templates = TrainingTemplate.objects.filter(user=user).order_by("-id")
        if templates is not None:
            for i in templates:
                template = {}
                template["id"] = i.id
                template["name"] = i.name
                template["exercises"] = []

                exercises = TrainingTemplateExercise.objects.filter(training_template = i)
                if exercises.exists():
                    for exercise in exercises:

                        value = {
                            "id":exercise.id,
                            "name":exercise.exercise.name if exercise.exercise is not None else exercise.custom_exercise.name,
                            "is_custom":False if exercise.exercise is not None else True,
                            "sets":exercise.sets
                        }
                        template["exercises"].append(value)
                result.append(template)
        return Response({"data":result})
    except Exception as e:
        print(e.args[0])
        return Response({"error":e.args[0]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_new_training_session(request):
    user = request.user
    new_training_session_data = json.loads(request.body)

    # Check if there is a workout session already in progress
    existing_session = TrainingSession.objects.filter(user=user).first()
    if existing_session:
        return Response({"error": f"You are currently performing '{existing_session.name}'"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        new_training_session = TrainingSession.objects.create(
            user=user,
            name=new_training_session_data.get("name")
        )
        exercises = new_training_session_data.get("exercises")
        # create workout set only if the there is an exercies list present and list is not empty
        if exercises is not None and len(exercises)>0:
            for i in exercises:
                id = i["id"]
                number_of_sets = i["sets"]
                is_custom = i["is_custom"]

                # create new Workout set ony if number of sets is greater than 0
                if number_of_sets > 0:
                    # check if the exercise is a custom_exercise
                    if is_custom:
                        exercise = CustomeExercise.objects.get(id=id)
                        for num  in range(number_of_sets):
                            WorkoutSet.objects.create(
                                training_session = new_training_session,
                                custome_exercise = exercise,
                                set_number = num + 1
                            )
                    else:
                        exercise = Exercise.objects.get(id=id)
                        for num in range(number_of_sets):
                            WorkoutSet.objects.create(
                                training_session = new_training_session,
                                default_exercise = exercise,
                                set_number = num + 1
                            )
        serializer = TrainingSessionSerializer(new_training_session)
        data = serializer.data
        return Response({"data":data,"message": "New training session started successfully"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_new_template(request):
    user  = request.user
    try:
        template = json.loads(request.body)
        template_name = template.get("name")

        new_template = TrainingTemplate.objects.create(user=user,name=template_name)

        for i in template["exercises"]:
            exercise = i["exercise"]
            exercise_id = exercise["id"]
            new_exercise = None
            if(exercise["is_custom"]):
                new_exercise = CustomeExercise.objects.get(id =exercise_id)
                TrainingTemplateExercise.objects.create(
                training_template=new_template,
                custom_exercise=new_exercise,
                sets=i["sets"])
            else:
                new_exercise = Exercise.objects.get(id=exercise_id)
                TrainingTemplateExercise.objects.create(
                training_template=new_template,
                exercise=new_exercise,
                sets=i["sets"])
    except KeyError as e:
        print(e.args[1])
        return Response({"error":e.args[1]},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e.args[1])
        return Response({"error",e.args[1]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"success":"template saved succesfully"})













@api_view(['GET'])
@permission_classes([AllowAny])
@transaction.atomic
def addDefault(request):
    return Response({"detail","remove this return to make this funtion work"})
    # change this exercise list to avoid duplicate exercise save on database on funtion call
    exercises = [
    {
        'exercise': {
            'name': 'Overhead Press (Barbell)',
            'image': '',
            'bodyPart': 'Shoulders',
            'category': 'Barbell',
        },
        'instructions': [
            'Stand with your feet shoulder-width apart.',
            'Hold a barbell at shoulder height with an overhand grip.',
            'Press the barbell overhead by extending your arms.',
            'Lower the barbell back down to shoulder height and repeat the movement.',
            'Engage your core and keep your back straight.',
        ]
    },
    {
        'exercise': {
            'name': 'Lateral Raises (Dumbbell)',
            'image': '',
            'bodyPart': 'Shoulders',
            'category': 'Dumbbell',
        },
        'instructions': [
            'Hold a dumbbell in each hand by your sides.',
            'Raise your arms out to the sides until they are parallel to the ground.',
            'Lower the dumbbells back down and repeat the movement.',
            'Keep a slight bend in your elbows throughout.',
        ]
    },
    {
        'exercise': {
            'name': 'Front Raises (Barbell)',
            'image': '',
            'bodyPart': 'Shoulders',
            'category': 'Barbell',
        },
        'instructions': [
            'Stand with your feet shoulder-width apart.',
            'Hold a barbell with an overhand grip in front of your thighs.',
            'Raise the barbell straight in front of you until it reaches shoulder height.',
            'Lower the barbell back down and repeat the movement.',
            'Keep a slight bend in your elbows throughout.',
        ]
    },
    {
        'exercise': {
            'name': 'Seated Dumbbell Press (Dumbbell)',
            'image': '',
            'bodyPart': 'Shoulders',
            'category': 'Dumbbell',
        },
        'instructions': [
            'Sit on a bench with back support and hold a dumbbell in each hand at shoulder height.',
            'Press the dumbbells overhead until your arms are fully extended.',
            'Lower the dumbbells back down to shoulder height and repeat the movement.',
            'Engage your core and keep your back against the bench.',
        ]
    },
    {
        'exercise': {
            'name': 'Upright Rows (Barbell)',
            'image': '',
            'bodyPart': 'Shoulders',
            'category': 'Barbell',
        },
        'instructions': [
            'Stand with your feet shoulder-width apart.',
            'Hold a barbell with an overhand grip in front of your thighs.',
            'Raise the barbell towards your chin by lifting your elbows.',
            'Lower the barbell back down and repeat the movement.',
            'Keep the barbell close to your body throughout.',
        ]
    }
]
    try:
        for element in exercises:
            exercise = element['exercise']
            newExercise = Exercise.objects.create(
                name=exercise['name'],
                body_part=exercise['bodyPart'],
                category=exercise["category"],
                image=exercise["image"]
            )

            instruction = element['instructions']
            for index, value in enumerate(instruction):
                Instruction.objects.create(
                    exercise=newExercise,
                    step_number=index + 1,
                    text=value
                )
        return Response({'details',"success"})
    except Exception as e:
        print(e.args[0])
        return Response({'details':"something went wrong"},status=status.HTTP_401_UNAUTHORIZED)

