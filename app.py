from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def calculate_macros(calories, weight):
    """
    Calculate recommended macronutrients:
    Protein: 1.5g/kg weight
    Fat: 25% of goal calories, 9 cal/g
    Carbs: Remaining calories, 4 cal/g
    """
    protein_grams = int(1.5 * weight)
    protein_cals = protein_grams * 4
    fat_cals = int(0.25 * calories)
    fat_grams = fat_cals // 9
    carb_cals = max(0, calories - (protein_cals + fat_cals))
    carb_grams = carb_cals // 4
    return {
        "protein_g": protein_grams,
        "fat_g": fat_grams,
        "carb_g": carb_grams
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    height = float(data['height'])
    weight = float(data['weight'])
    age = int(data['age'])
    gender = data['gender']
    activity = float(data['activity'])

    # BMI calculation
    bmi = round(weight / ((height / 100) ** 2), 1)

    # Basal Metabolic Rate (Mifflin-St Jeor)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = int(bmr * activity)

    # BMI goals
    min_bmi = 18.5
    max_bmi = 24.9
    min_weight = min_bmi * ((height / 100) ** 2)
    max_weight = max_bmi * ((height / 100) ** 2)

    # Recommendations
    if bmi < 18.5:
        category = "Underweight"
        calorie_goal = f"Gain {round(min_weight - weight, 1)} kg to reach healthy BMI"
        goal_calories = tdee + 400
    elif bmi < 25:
        category = "Normal Weight"
        calorie_goal = "Maintain Weight"
        goal_calories = tdee
    elif bmi < 30:
        category = "Overweight"
        calorie_goal = f"Lose {round(weight - max_weight, 1)} kg to reach healthy BMI"
        goal_calories = tdee - 500
    else:
        category = "Obese"
        calorie_goal = f"Lose {round(weight - max_weight, 1)} kg to reach healthy BMI"
        goal_calories = tdee - 600

    # Ensure minimum healthy calories
    goal_calories = max(goal_calories, 1500 if gender == "male" else 1200)

    macros = calculate_macros(goal_calories, weight)

    # Return data to frontend
    return jsonify({
        'bmi': bmi,
        'category': category,
        'calories': tdee,
        'goal_calories': goal_calories,
        'calorie_goal': calorie_goal,
        'macros': macros
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)