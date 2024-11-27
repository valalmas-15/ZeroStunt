from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
import random

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

    # Create a summary for each selected combination
    recommendation_summary = "### Three Randomly Selected Food Combinations:\n"
    for i in range(3):
        recommendation_summary += f"\n**Combination {i + 1}:**\n"
        recommendation_summary += f"- {random_combinations.loc[i, 'Food 1']}\n"
        recommendation_summary += f"- {random_combinations.loc[i, 'Food 2']}\n"
        recommendation_summary += f"- {random_combinations.loc[i, 'Food 3']}\n"
        recommendation_summary += "\nTotal Nutrition:\n"
        for nutrient, value in random_combinations.loc[i, "Total Nutrition"].items():
            recommendation_summary += f"{nutrient}: {value}\n"

    return recommendation_summary

def generate_summary(evaluation, standard_nutrition):
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
    
    # Generate the summary
    summary += "### Summary of Nutritional Status:\n"
    
    # Sufficient Nutrients
    if recommendations["maintain"]:
        summary += f"\nSufficient Nutrients:\n"
        summary += ", ".join(recommendations["maintain"]) + " levels are adequate, indicating the current diet meets the minimum requirements for these nutrients.\n"
    
    # Excess Nutrients
    if recommendations["moderate"]:
        summary += f"\nExcess Nutrients:\n"
        for nutrient in recommendations["moderate"]:
            impact = nutrient_info.get(nutrient, {}).get("excess_impact", "Consider reducing intake to avoid potential health risks.")
            summary += f"- {nutrient}: {impact}\n"
    
    # Deficient Nutrients
    if recommendations["increase"]:
        summary += f"\nDeficient Nutrients:\n"
        for nutrient in recommendations["increase"]:
            impact = nutrient_info.get(nutrient, {}).get("deficiency_impact", "Increase intake to meet daily requirements.")
            summary += f"- {nutrient}: {impact}\n"

    # Generate Overall Recommendations
    summary += "\n### Recommendations:\n"
    if recommendations["increase"]:
        summary += "- **Increase** foods rich in: " + ", ".join(recommendations["increase"]) + " to meet daily requirements.\n"
    if recommendations["moderate"]:
        summary += "- **Moderate** intake of: " + ", ".join(recommendations["moderate"]) + " to avoid potential excesses.\n"
    if recommendations["maintain"]:
        summary += "- **Maintain** current levels of: " + ", ".join(recommendations["maintain"]) + ".\n"
    
    return summary

@app.route('/detect_and_evaluate', methods=['POST'])

def detect_and_evaluate():
    try:
        data = request.get_json()
        input_foods = data.get('foods', [])

        # Convert input foods to TF-IDF features
        input_features = tfidf.transform(input_foods).toarray()
        
        # Predict food names
        predictions = model.predict(input_features)
        predicted_classes = [foods_df.iloc[np.argmax(pred)] for pred in predictions]
        
        # Initialize total_nutrition with zero for each nutrient column in standard_nutrition
        total_nutrition = {nutrient: 0 for nutrient in standard_nutrition_df['Nutrisi'] if nutrient in foods_df.columns}

        # Sum nutrition values for detected foods
        for food in predicted_classes:
            for nutrient in total_nutrition.keys():
                total_nutrition[nutrient] += food.get(nutrient, 0)  # Safely sum nutrient values

        # Evaluate nutrition (dummy function, replace with actual)
        evaluation = {nutrient: "Sufficient" for nutrient in total_nutrition.keys()}

        # Generate summary
        summary = generate_summary(evaluation, standard_nutrition_df)
        response = {"summary": summary}

        recommendation_food = choose_three_random_combinations(combinations_df)
        response["recommendations"] = recommendation_food

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
