import streamlit as st
import tensorflow as tf
import pandas as pd
import numpy as np
import tensorflow_decision_forests as tfdf

# Load Model TensorFlow Decision Forests
model = tf.saved_model.load("model")  # Pastikan path sudah sesuai

# Nilai min dan max dari data training
min_age = 0
max_age = 1
min_birth_weight = 0
max_birth_weight = 1
min_birth_length = 0
max_birth_length = 1
min_body_weight = 0
max_body_weight = 1
min_body_length = 0
max_body_length = 1

# Fungsi normalisasi
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

# Fungsi prediksi
def predict_stunting(data):
    # Menyesuaikan DataFrame dengan nama kolom yang benar
    df = pd.DataFrame([data])
    
    # Memisahkan kolom-kolom input dan mengonversinya menjadi tensor
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
    
    # Menyusun input dalam format yang sesuai dengan signature
    infer_fn = model.signatures["serving_default"]
    
    # Melakukan prediksi dengan model
    predictions = infer_fn(**input_data)  # Menggunakan input sebagai keyword arguments
    
    # Mengambil hasil prediksi (sesuaikan dengan nama output model Anda)
    stunting_prediction = int(predictions["output_1"][0] > 0.7)  # Sesuaikan nama output
    return "stunting" if stunting_prediction == 1 else "tidak stunting"


# Streamlit App
st.title("Prediksi Stunting dengan GradientBoostedTree Model")

# Input dari pengguna
gender = st.selectbox("Jenis Kelamin", ["Male", "Female"])
age = st.number_input("Usia (dalam bulan)",step=1)
birth_weight = st.number_input("Berat Lahir (kg)",step=0.1)
birth_length = st.number_input("Panjang Lahir (cm)",step=0.5)
body_weight = st.number_input("Berat Badan (kg)", step=0.1)
body_length = st.number_input("Panjang Badan (cm)",step=0.5)

if st.button("Prediksi"):
    # Normalisasi input sesuai skala data training
    data_baru = {
        "Gender": 0 if gender == "Male" else 1,
        "Age": normalize(age, min_age, max_age),
        "Birth_Weight": normalize(birth_weight, min_birth_weight, max_birth_weight),
        "Birth_Length": normalize(birth_length, min_birth_length, max_birth_length),
        "Body_Weight": normalize(body_weight, min_body_weight, max_body_weight),
        "Body_Length": normalize(body_length, min_body_length, max_body_length)
    }
    
    # Menghitung BMI
    data_baru["BMI"] = data_baru["Body_Weight"] / ((data_baru["Body_Length"]/100) ** 2)

    # Menghitung Weight_Diff dan Length_Diff
    data_baru["Weight_Diff"] = data_baru["Body_Weight"] - data_baru["Birth_Weight"]
    data_baru["Length_Diff"] = data_baru["Body_Length"] - data_baru["Birth_Length"]
    
    # Prediksi stunting
    hasil_prediksi = predict_stunting(data_baru)
    st.write("Prediksi Stunting:", hasil_prediksi)
