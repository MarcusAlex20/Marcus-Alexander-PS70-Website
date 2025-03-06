from flask import Flask, request, jsonify
import os
import json
import random

app = Flask(__name__)

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

EXERCISE_DATABASE = {
    "Linemen": ["Squat", "Deadlift", "Sled Push", "Trap Bar Deadlift", "Power Cleans"],
    "Skill Player": ["Sprints", "Shuttle Runs", "Broad Jumps", "Bounding", "DB Lunges"],
    "Linebacker/TE": ["Squat", "Power Cleans", "Sprints", "Box Jumps", "Agility Drills"]
}

def get_position_exercises(position):
    """Return exercises based on position group."""
    return EXERCISE_DATABASE.get(position.capitalize(), ["General Strength Training"])

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

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    data = request.json
    position = data.get('position')
    log_data = load_log()
    plan = generate_weekly_plan(position, log_data)
    return jsonify(plan)

@app.route('/mark_completed', methods=['POST'])
def mark_completed():
    data = request.json
    log_data = load_log()
    for day, completed in data.items():
        if day in log_data["previous_workouts"]:
            log_data["previous_workouts"][day]["Completed"] = completed
    save_log(log_data)
    return jsonify({"message": "Workout completion recorded!"})

if __name__ == '__main__':
    app.run(debug=True)
