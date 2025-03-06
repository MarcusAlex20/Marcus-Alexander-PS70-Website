import os
import json
import random
import pandas as pd

# ---------------------- MEMORY SYSTEM (Workout Tracking) ----------------------

LOG_FILE = "workout_log.json"

def load_log():
    """Load workout history from a JSON file."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            return json.load(file)
    return {"previous_workouts": []}  # If no log exists, create a fresh start

def save_log(log_data):
    """Save workout history to a JSON file."""
    with open(LOG_FILE, "w") as file:
        json.dump(log_data, file, indent=4)

# ---------------------- USER QUESTIONNAIRE ----------------------

def get_user_info():
    """Collect user input for training program customization."""
    print("\nPlease answer the following questions:\n")

    # Age & Position
    age = int(input("Enter your age: ").strip())
    position = input("What position do you play? (Linemen, Skill Player, Linebacker/TE): ").strip().lower()

    # Gym & Equipment Access
    has_gym = input("Do you have access to a gym nearby? (yes/no): ").strip().lower() == "yes"

    equipment = {
        "barbell": input("Do you have a barbell? (yes/no): ").strip().lower() == "yes" and has_gym,
        "dumbbells": input("Do you have dumbbells? (yes/no): ").strip().lower() == "yes" and has_gym,
        "squat_rack": input("Do you have a squat rack? (yes/no): ").strip().lower() == "yes" and has_gym,
        "sled": input("Do you have a sled? (yes/no): ").strip().lower() == "yes",
        "resistance_bands": input("Do you have resistance bands? (yes/no): ").strip().lower() == "yes",
        "pull_up_bar": input("Do you have a pull-up bar? (yes/no): ").strip().lower() == "yes"
    }

    environment = {
        "grass": input("Do you have access to a grass field? (yes/no): ").strip().lower() == "yes",
        "turf": input("Do you have access to a turf field? (yes/no): ").strip().lower() == "yes",
        "track": input("Do you have access to a running track? (yes/no): ").strip().lower() == "yes",
        "gym_floor": input("Do you have access to a gym floor? (yes/no): ").strip().lower() == "yes"
    }

    return age, position, has_gym, equipment, environment

# ---------------------- POSITION-BASED EXERCISE SELECTION ----------------------

EXERCISE_DATABASE = {
    "Linemen": ["Squat", "Deadlift", "Sled Push", "Trap Bar Deadlift", "Power Cleans"],
    "Skill Player": ["Sprints", "Shuttle Runs", "Broad Jumps", "Bounding", "DB Lunges"],
    "Linebacker/TE": ["Squat", "Power Cleans", "Sprints", "Box Jumps", "Agility Drills"]
}

def get_position_exercises(position):
    """Return exercises based on position group."""
    return EXERCISE_DATABASE.get(position.capitalize(), ["General Strength Training"])

# ---------------------- WORKOUT PLAN GENERATION ----------------------

def generate_weekly_plan(position, log_data):
    """Generate a 7-day training plan with memory to avoid duplicate workouts."""
    
    past_workouts = log_data["previous_workouts"]
    
    # Load position-based exercises
    base_exercises = get_position_exercises(position)

    # Shuffle but maintain some consistency
    new_week_exercises = random.sample(base_exercises, min(4, len(base_exercises)))
    
    plan = {
        "Monday": {"Focus": "Strength & Power", "Exercises": new_week_exercises},
        "Tuesday": {"Focus": "Speed & Agility", "Exercises": random.sample(base_exercises, min(4, len(base_exercises)))},
        "Wednesday": {"Focus": "Recovery & Mobility", "Exercises": ["Foam Rolling", "Yoga", "Stretching"]},
        "Thursday": {"Focus": "Explosiveness & Hypertrophy", "Exercises": new_week_exercises},
        "Friday": {"Focus": "Off (Active Recovery)", "Exercises": ["Swimming", "Bike Work", "Light Jog"]},
        "Saturday": {"Focus": "Full-Body Power", "Exercises": random.sample(base_exercises, min(4, len(base_exercises)))},
        "Sunday": {"Focus": "Conditioning & Core", "Exercises": ["Shuttle Runs", "Planks", "Hill Sprints"]}
    }
    
    # Save new plan to memory
    log_data["previous_workouts"] = plan
    save_log(log_data)

    return plan

# ---------------------- WORKOUT COMPLETION TRACKING ----------------------

def mark_workout_completed(log_data):
    """Allow user to mark workouts as complete."""
    print("\nMark workouts as completed:\n")
    
    for day, details in log_data["previous_workouts"].items():
        print(f"{day}: {details['Focus']}")
        completed = input(f"Did you complete {day}'s workout? (yes/no): ").strip().lower()
        if completed == "yes":
            log_data["previous_workouts"][day]["Completed"] = True
        else:
            log_data["previous_workouts"][day]["Completed"] = False

    save_log(log_data)
    print("\nWorkout completion recorded!\n")

# ---------------------- RUNNING THE PROGRAM ----------------------

# Load past log
log_data = load_log()

# Collect user info
user_age, user_position, user_gym, user_equipment, user_environment = get_user_info()

# Generate a new weekly plan
weekly_plan = generate_weekly_plan(user_position, log_data)

# Convert to DataFrame for better visualization
df_plan = pd.DataFrame.from_dict(weekly_plan, orient='index')

# Display the plan
print("\nGenerated Training Plan:\n")
print(df_plan)

# Mark workouts as completed
mark_workout_completed(log_data)
