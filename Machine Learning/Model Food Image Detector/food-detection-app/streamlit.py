import os
import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the pre-trained models
model = load_model('model_makanan.h5')
model_2 = load_model('model_rekomendasi.h5')
foods_df = pd.read_csv('foods.csv')
standard_nutrition_df = pd.read_csv('standard-nutrition.csv')

# Initialize TF-IDF
tfidf = TfidfVectorizer()
tfidf.fit(foods_df['Menu'])

CLASS_LABELS = [
    'air', 'anggur', 'apel', 'ayam', 'bakso', 'bakwan', 'batagor',
    'bubur', 'burger', 'cakwe', 'capcay', 'crepes', 'cumi', 'donat',
    'durian', 'es_krim', 'fu_yung_hai', 'gudeg', 'ikan', 'jeruk',
    'kacang', 'kebab', 'kentang', 'kerupuk', 'kopi'
]

def prepare_image(img):
    """Mempersiapkan gambar untuk prediksi"""
    img = img.resize((100, 100))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

st.title("Deteksi Makanan dan Nutrisi")

# Upload image
uploaded_file = st.file_uploader("Unggah gambar makanan", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Prepare image
    img = image.load_img(uploaded_file)
    processed_image = prepare_image(img)

    # Predict food type
    predictions = model.predict(processed_image)
    top_prediction_index = np.argmax(predictions[0])
    top_label = CLASS_LABELS[top_prediction_index]

    st.image(uploaded_file, caption='Gambar yang diunggah', use_column_width=True)
    st.write(f"Prediksi jenis makanan: {top_label}")

    # Convert input foods to TF-IDF features
    input_features = tfidf.transform([top_label]).toarray()

    # Predict food names
    predictions = model_2.predict(input_features)
    predicted_classes = [foods_df.iloc[np.argmax(pred)] for pred in predictions]

    # Initialize total_nutrition with zero for each nutrient column in standard_nutrition
    total_nutrition = {nutrient: 0 for nutrient in standard_nutrition_df['Nutrisi'] if nutrient in foods_df.columns}

    # Sum nutrition values for detected foods
    for food in predicted_classes:
        for nutrient in total_nutrition.keys():
            total_nutrition[nutrient] += food.get(nutrient, 0)  # Safely sum nutrient values

    # Display total nutrition
    st.write("Total Nutrisi:")
    for nutrient, value in total_nutrition.items():
        st.write(f"{nutrient}: {value}")

    # Evaluate nutrition (dummy function, replace with actual)
    evaluation = {nutrient: "Sufficient" for nutrient in total_nutrition.keys()}
    st.write("Evaluasi Nutrisi:")
    for nutrient, status in evaluation.items():
        st.write(f"{nutrient}: {status}")