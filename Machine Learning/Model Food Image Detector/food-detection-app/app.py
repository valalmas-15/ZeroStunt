import os
import numpy as np
from flask import Flask, request, render_template, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input

app = Flask(__name__)

# Load the pre-trained model
MODEL_PATH = 'model_makanan.h5'
model = load_model(MODEL_PATH)

CLASS_LABELS = [
  'air', 'anggur', 'apel', 'ayam', 'bakso', 'bakwan', 'batagor',
  'bubur', 'burger', 'cakwe', 'capcay', 'crepes', 'cumi', 'donat',
  'durian', 'es_krim', 'fu_yung_hai', 'gudeg', 'ikan', 'jeruk',
  'kacang', 'kebab', 'kentang', 'kerupuk', 'kopi'
]

def prepare_image(img_path):
    """Mempersiapkan gambar untuk prediksi"""
    img = image.load_img(img_path, target_size=(100, 100))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

@app.route('/', methods=['GET'])
def index():
    """Halaman utama untuk upload gambar"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint untuk prediksi gambar makanan"""
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diunggah'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Tidak ada file yang dipilih'})
    
    # Simpan file sementara
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    
    try:
        # Persiapkan gambar
        processed_image = prepare_image(file_path)
        
        # Prediksi
        predictions = model.predict(processed_image)
        
        # Dapatkan label dengan probabilitas tertinggi
        top_prediction_index = np.argmax(predictions[0])
        top_label = CLASS_LABELS[top_prediction_index]
        confidence = float(predictions[0][top_prediction_index])
        
        # Hapus file sementara
        os.remove(file_path)
        
        return jsonify({
            'prediction': top_label,
            'confidence': confidence
        })
    
    except Exception as e:
        # Hapus file jika terjadi kesalahan
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Buat direktori uploads jika belum ada
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)