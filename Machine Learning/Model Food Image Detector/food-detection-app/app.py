import os
import numpy as np
import pandas as pd
import logging
from flask import Flask, request, render_template, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from werkzeug.utils import secure_filename

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load models and data
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepare_image(img_path):
    """Prepare image for prediction."""
    img = image.load_img(img_path, target_size=(100, 100))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

@app.route('/', methods=['GET'])
def index():
    """Render upload page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict food and nutrition."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg'})

    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    try:
        # Process image for prediction
        processed_image = prepare_image(file_path)

        # Model 1 Prediction
        predictions = model.predict(processed_image)
        top_prediction_index = np.argmax(predictions[0])
        top_label = CLASS_LABELS[top_prediction_index]

        # Model 2 Recommendation
        input_features = tfidf.transform([top_label]).toarray()
        recommendations = model_2.predict(input_features)
        recommended_foods = [foods_df.iloc[np.argmax(rec)] for rec in recommendations]

        # Calculate total nutrition
        total_nutrition = {nutrient: 0 for nutrient in standard_nutrition_df['Nutrisi'] if nutrient in foods_df.columns}
        for food in recommended_foods:
            for nutrient in total_nutrition.keys():
                total_nutrition[nutrient] += int(food.get(nutrient, 0))  # Convert to int

        # Example nutrition evaluation (dummy logic)
        evaluation = {nutrient: "Sufficient" if value > 0 else "Deficient" for nutrient, value in total_nutrition.items()}

        # Convert all values in total_nutrition to JSON-serializable types
        total_nutrition = {key: int(value) for key, value in total_nutrition.items()}

        # Clean up file
        os.remove(file_path)

        return jsonify({'prediction': top_label, 'nutrition': total_nutrition, 'evaluation': evaluation})

    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
