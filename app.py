from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def calculate_macros(calories, weight):
    # Macronutrients as per generic guidelines
    # Protein: 1.5g per kg, Fat: 25% of calories, Carbs: rest
    protein_grams = round(1.5 * weight)
    protein_cals = protein_grams * 4
    fat_cals = int(0.25 * calories)
    fat_grams = fat_cals // 9
    remaining_cals = calories - (protein_cals + fat_cals)
    carb_grams = max(0, remaining_cals // 4)
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

    # BMI
    bmi = weight / ((height / 100) ** 2)
    bmi = round(bmi, 1)

    # BMR (Mifflin-St Jeor)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = int(bmr * activity)

    # Recommendation based on BMI
    category = ""
    goal_cals = tdee
    calorie_goal = ""
    min_bmi = 18.5
    max_bmi = 24.9
    min_weight = min_bmi * ((height/100) ** 2)
    max_weight = max_bmi * ((height/100) ** 2)

    if bmi < 18.5:
        category = "Underweight"
        kilograms = round(min_weight - weight, 1)
        goal_cals = tdee + 400
        calorie_goal = f"Gain {kilograms} kg to reach healthy BMI"
    elif 18.5 <= bmi < 25:
        category = "Normal Weight"
        calorie_goal = "Maintain Weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
        kilograms = round(weight - max_weight, 1)
        goal_cals = tdee - 500
        calorie_goal = f"Lose {kilograms} kg to reach healthy BMI"
    else:
        category = "Obese"
        kilograms = round(weight - max_weight, 1)
        goal_cals = tdee - 600
        calorie_goal = f"Lose {kilograms} kg to reach healthy BMI"

    # Minimum safe goal calories
    goal_cals = max(goal_cals, 1200 if gender == 'female' else 1500)

    macros = calculate_macros(goal_cals, weight)

    return jsonify({
        'bmi': bmi,
        'category': category,
        'calories': tdee,
        'goal_calories': goal_cals,
        'calorie_goal': calorie_goal,
        'macros': macros
    })

if __name__ == '__main__':
    app.run(debug=True)