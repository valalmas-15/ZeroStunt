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
    if combinations_df.shape[0] < 3:
        return "Not enough valid combinations to provide three unique recommendations."

    random_combinations = combinations_df.sample(n=3).reset_index(drop=True)
    recommendation_summary = "## Rekomendasi Tiga Kombinasi Makanan :\n"
    for i in range(3):
        recommendation_summary += f"\n### Combination {i + 1}:\n"
        recommendation_summary += f"- **Food 1**: {random_combinations.loc[i, 'Food 1']}\n"
        recommendation_summary += f"- **Food 2**: {random_combinations.loc[i, 'Food 2']}\n"
        recommendation_summary += f"- **Food 3**: {random_combinations.loc[i, 'Food 3']}\n"
        
        try:
            total_nutrition_dict = json.loads(random_combinations.loc[i, "Total Nutrition"])
        except json.JSONDecodeError:
            total_nutrition_dict = {}

        recommendation_summary += "\n**Total Nutrisi**:\n"
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

    nutrient_info = {
        row['Nutrisi']: {
            "excess_impact": row["Dampak Kelebihan"],
            "deficiency_impact": row["Dampak Kekurangan"],
            "function": row["Fungsi Zat"]
        } for _, row in standard_nutrition.iterrows()
    }

    for nutrient, status in evaluation.items():
        if "Deficiency" in status:
            recommendations["increase"].append(nutrient)
        elif "Excess" in status:
            recommendations["moderate"].append(nutrient)
        elif status == "Sufficient":
            recommendations["maintain"].append(nutrient)

    summary += "## Ringkasan Status Gizi\n"
    summary += "### Total Nutrisi dari Makanan yang Diinput:\n"
    for nutrient, value in total_nutrition.items():
        status = evaluation.get(nutrient, "Tidak Diketahui")
        summary += f"{nutrient}: {value} ({status})\n"

    summary += "\n### Rekomendasi:\n"
    if recommendations["increase"]:
        summary += f"- **Tingkatkan** makanan yang kaya akan: " + ", ".join(recommendations["increase"]) + " untuk memenuhi kebutuhan harian.\n"
    if recommendations["moderate"]:
        summary += f"- **Kurangi** asupan: " + ", ".join(recommendations["moderate"]) + " untuk menghindari kelebihan.\n"
    if recommendations["maintain"]:
        summary += f"- **Pertahankan** tingkat saat ini dari: " + ", ".join(recommendations["maintain"]) + ".\n"

    return summary

@app.route('/detect_and_evaluate', methods=['POST'])
def detect_and_evaluate():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Tidak ada data JSON yang ditemukan dalam permintaan"}), 400
        
        input_foods = data.get('foods', [])
        if not input_foods:
            return jsonify({"error": "Kunci 'foods' hilang atau kosong dalam permintaan"}), 400

        input_features = tfidf.transform(input_foods).toarray()
        predictions = model.predict(input_features)
        predicted_classes = [foods_df.iloc[np.argmax(pred)] for pred in predictions]

        total_nutrition = {col: 0 for col in foods_df.columns if 'g' in col or 'mg' in col or 'µg' in col}

        for food in predicted_classes:
            for nutrient in total_nutrition.keys():
                total_nutrition[nutrient] += food.get(nutrient, 0)

        evaluation = {}
        for nutrient, value in total_nutrition.items():
            if value < standard_nutrition_df.loc[standard_nutrition_df['Nutrisi'] == nutrient, 'Minimum'].values[0]:
                evaluation[nutrient] = "Kekurangan"
            elif value > standard_nutrition_df.loc[standard_nutrition_df['Nutrisi'] == nutrient, 'Maximum'].values[0]:
                evaluation[nutrient] = "Kelebihan"
            else:
                evaluation[nutrient] = "Cukup"

        summary = generate_summary(evaluation, total_nutrition, standard_nutrition_df)
        response = {"summary": summary}

        recommendation_food = choose_three_random_combinations(combinations_df)
        response["recommendations"] = recommendation_food
        response["success"] = True

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
