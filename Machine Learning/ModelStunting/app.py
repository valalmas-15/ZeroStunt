from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
import random

app = Flask(__name__)

# Load Model TensorFlow Decision Forests
model = tf.saved_model.load("model")  # Pastikan path sudah sesuai

# Nilai min dan max dari data training
min_age, max_age = 0, 1
min_birth_weight, max_birth_weight = 0, 1
min_birth_length, max_birth_length = 0, 1
min_body_weight, max_body_weight = 0, 1
min_body_length, max_body_length = 0, 1

# Fungsi normalisasi
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

# Fungsi prediksi
def predict_stunting(data):
    df = pd.DataFrame([data])
    input_data = {
        "Age": tf.convert_to_tensor(df["Age"], dtype=tf.float32),
        "BMI": tf.convert_to_tensor(df["BMI"], dtype=tf.float32),
        "Birth_Length": tf.convert_to_tensor(df["Birth_Length"], dtype=tf.float32),
        "Birth_Weight": tf.convert_to_tensor(df["Birth_Weight"], dtype=tf.float32),
        "Body_Length": tf.convert_to_tensor(df["Body_Length"], dtype=tf.float32),
        "Body_Weight": tf.convert_to_tensor(df["Body_Weight"], dtype=tf.float32),
        "Gender": tf.convert_to_tensor(df["Gender"], dtype=tf.int64),
        "Length_Diff": tf.convert_to_tensor(df["Length_Diff"], dtype=tf.float32),
        "Weight_Diff": tf.convert_to_tensor(df["Weight_Diff"], dtype=tf.float32)
    }
    infer_fn = model.signatures["serving_default"]
    predictions = infer_fn(**input_data)
    stunting_prediction = int(predictions["output_1"][0] > 0.7)  # Sesuaikan nama output
    return "stunting" if stunting_prediction == 1 else "tidak stunting"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        gender = 0 if data["Gender"].lower() == "male" else 1
        age = normalize(data["Age"], min_age, max_age)
        birth_weight = normalize(data["Birth_Weight"], min_birth_weight, max_birth_weight)
        birth_length = normalize(data["Birth_Length"], min_birth_length, max_birth_length)
        body_weight = normalize(data["Body_Weight"], min_body_weight, max_body_weight)
        body_length = normalize(data["Body_Length"], min_body_length, max_body_length)
        
        bmi = body_weight / ((body_length / 100) ** 2)
        weight_diff = body_weight - birth_weight
        length_diff = body_length - birth_length
        
        input_data = {
            "Gender": gender,
            "Age": age,
            "Birth_Weight": birth_weight,
            "Birth_Length": birth_length,
            "Body_Weight": body_weight,
            "Body_Length": body_length,
            "BMI": bmi,
            "Weight_Diff": weight_diff,
            "Length_Diff": length_diff
        }
        prediction = predict_stunting(input_data)
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
