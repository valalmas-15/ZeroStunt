from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
import random
import json

# Initialize Flask app
app = Flask(__name__)

# Load required files (model, TF-IDF, datasets)
model = load_model('model_rekomendasi.h5')  # Path to the saved TensorFlow model
foods_df = pd.read_csv('Datasets/foods.csv')  # Food dataset
standard_nutrition_df = pd.read_csv('Datasets/standard-nutrition.csv')  # Nutrition standards
combinations_df = pd.read_csv('Datasets/food-combinations.csv')  # Food combinations

# Initialize and fit TF-IDF
tfidf = TfidfVectorizer()
tfidf.fit(foods_df['Menu'])

def choose_three_random_combinations(combinations_df):
    # Check if there are enough combinations to select three
    if combinations_df.shape[0] < 3:
        return "Not enough valid combinations to provide three unique recommendations."

    # Randomly sample three unique combinations
    random_combinations = combinations_df.sample(n=3).reset_index(drop=True)

    # Create a formatted summary for each selected combination
    recommendation_summary = "## Three Randomly Selected Food Combinations:\n"
    for i in range(3):
        recommendation_summary += f"\n### Combination {i + 1}:\n"
        recommendation_summary += f"- **Food 1**: {random_combinations.loc[i, 'Food 1']}\n"
        recommendation_summary += f"- **Food 2**: {random_combinations.loc[i, 'Food 2']}\n"
        recommendation_summary += f"- **Food 3**: {random_combinations.loc[i, 'Food 3']}\n"
        
        # Assuming "Total Nutrition" is a string that can be converted to a dictionary
        try:
            total_nutrition_dict = json.loads(random_combinations.loc[i, "Total Nutrition"])
        except json.JSONDecodeError:
            total_nutrition_dict = {}  # Fallback if the string is not valid JSON

        recommendation_summary += "\n**Total Nutrition**:\n"
        for nutrient, value in total_nutrition_dict.items():
            recommendation_summary += f"- {nutrient}: {value}\n"

    return recommendation_summary

def generate_summary(evaluation, total_nutrition, standard_nutrition):
    summary = ""
    recommendations = {
        "increase": [],
        "moderate": [],
        "maintain": []
    }

    # Convert standard_nutrition DataFrame into a dictionary for quick lookup
    nutrient_info = {
        row['Nutrisi']: {
            "excess_impact": row["Dampak Kelebihan"],
            "deficiency_impact": row["Dampak Kekurangan"],
            "function": row["Fungsi Zat"]
        } for _, row in standard_nutrition.iterrows()
    }

    # Categorize nutrients based on their evaluation status
    for nutrient, status in evaluation.items():
        if "Deficiency" in status:
            recommendations["increase"].append(nutrient)
        elif "Excess" in status:
            recommendations["moderate"].append(nutrient)
        elif status == "Sufficient":
            recommendations["maintain"].append(nutrient)

    # Start creating the formatted summary
    summary += "## Nutritional Status Summary\n"

    # Nutritional Data
    summary += "### Total Nutrition from Detected Foods:\n"
    summary += f"Energy (kJ): {total_nutrition['Energy (kJ)']}\n"
    summary += f"Protein (g): {total_nutrition['Protein (g)']}\n"
    summary += f"Fat (g): {total_nutrition['Fat (g)']}\n"
    summary += f"Carbohydrates (g): {total_nutrition['Carbohydrates (g)']}\n"
    summary += f"Dietary Fiber (g): {total_nutrition['Dietary Fiber (g)']}\n"
    summary += f"PUFA (g): {total_nutrition['PUFA (g)']}\n"
    summary += f"Cholesterol (mg): {total_nutrition['Cholesterol (mg)']}\n"
    summary += f"Vitamin A (mg): {total_nutrition['Vitamin A (mg)']}\n"
    summary += f"Vitamin E (eq.) (mg): {total_nutrition['Vitamin E (eq.) (mg)']}\n"
    summary += f"Vitamin B1 (mg): {total_nutrition['Vitamin B1 (mg)']}\n"
    summary += f"Vitamin B2 (mg): {total_nutrition['Vitamin B2 (mg)']}\n"
    summary += f"Vitamin B6 (mg): {total_nutrition['Vitamin B6 (mg)']}\n"
    summary += f"Total Folic Acid (µg): {total_nutrition['Total Folic Acid (µg)']}\n"
    summary += f"Vitamin C (mg): {total_nutrition['Vitamin C (mg)']}\n"
    summary += f"Sodium (mg): {total_nutrition['Sodium (mg)']}\n"
    summary += f"Potassium (mg): {total_nutrition['Potassium (mg)']}\n"
    summary += f"Calcium (mg): {total_nutrition['Calcium (mg)']}\n"
    summary += f"Magnesium (mg): {total_nutrition['Magnesium (mg)']}\n"
    summary += f"Phosphorus (mg): {total_nutrition['Phosphorus (mg)']}\n"
    summary += f"Iron (mg): {total_nutrition['Iron (mg)']}\n"
    summary += f"Zinc (mg): {total_nutrition['Zinc (mg)']}\n"

    # Nutrient Evaluation
    summary += "\n### Nutrition Evaluation:\n"
    for nutrient, value in total_nutrition.items():
        if nutrient in evaluation:
            status = evaluation[nutrient]
            if "Deficiency" in status:
                summary += f"- {nutrient}: Deficiency of {value} {nutrient}\n"
            elif "Excess" in status:
                summary += f"- {nutrient}: Excess of {value} {nutrient}\n"
            else:
                summary += f"- {nutrient}: Sufficient\n"

    # Generate Overall Recommendations
    summary += "\n### Recommendations:\n"
    if recommendations["increase"]:
        summary += f"- **Increase** foods rich in: " + ", ".join(recommendations["increase"]) + " to meet daily requirements.\n"
    if recommendations["moderate"]:
        summary += f"- **Moderate** intake of: " + ", ".join(recommendations["moderate"]) + " to avoid potential excesses.\n"
    if recommendations["maintain"]:
        summary += f"- **Maintain** current levels of: " + ", ".join(recommendations["maintain"]) + ".\n"

    return summary

@app.route('/detect_and_evaluate', methods=['POST'])
def detect_and_evaluate():
    try:
        data = request.get_json()

        # If no JSON data is found
        if not data:
            return jsonify({"error": "No JSON data found in the request"}), 400
        
        input_foods = data.get('foods', [])
        if not input_foods:
            return jsonify({"error": "'foods' key is missing or empty in the request"}), 400

        # Convert input foods to TF-IDF features
        input_features = tfidf.transform(input_foods).toarray()

        # Predict food names
        predictions = model.predict(input_features)
        predicted_classes = [foods_df.iloc[np.argmax(pred)] for pred in predictions]

        # Initialize total_nutrition with zero for each nutrient column in foods_df
        total_nutrition = {col: 0 for col in foods_df.columns if 'g' in col or 'mg' in col or 'µg' in col}

        # Sum nutrition values for detected foods
        for food in predicted_classes:
            for nutrient in total_nutrition.keys():
                total_nutrition[nutrient] += food.get(nutrient, 0)  # Safely sum nutrient values

        # Dummy evaluation function (replace with actual logic)
        evaluation = {nutrient: "Sufficient" for nutrient in total_nutrition.keys()}

        # Generate summary
        summary = generate_summary(evaluation, total_nutrition, standard_nutrition_df)
        response = {"summary": summary}

        # Get recommendations from food combinations
        recommendation_food = choose_three_random_combinations(combinations_df)
        response["recommendations"] = recommendation_food

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
