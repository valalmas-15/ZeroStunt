# ZeroStunt: Machine Learning for Stunting Prediction

ZeroStunt is a machine learning project aimed at predicting stunting conditions in Indonesian children by utilizing datasets of Indonesian food images, food nutrition, and factors contributing to stunting. This project is built using **TensorFlow Lite** and **TensorFlow.js** for model building and deployment.

## Datasets

The datasets used for this project are sourced from Kaggle and include various aspects of Indonesian food and nutrition, as well as factors contributing to stunting. You can access the datasets via the following links:

1. [Indonesian Food Image Dataset](https://www.kaggle.com/datasets/robertusbagaskara/indonesian-food-image)
2. [Data Makanan Stunting](https://www.kaggle.com/datasets/nauvalalmas/data-makanan-stunting/data)
3. [Faktor Stunting](https://www.kaggle.com/datasets/harnelia/faktor-stunting)

## Notebooks

Each case in this project is accompanied by a Jupyter Notebook or Kaggle notebook for better understanding and experimentation:

1. [Google Colab Notebook for Stunting Prediction](https://colab.research.google.com/drive/1bUixYgK8wd7uBsUeYnyWjt4swATlwmVy?usp=sharing)
2. [Kaggle Notebook for Stunting Prediction](https://www.kaggle.com/code/muisnasrul/stunting-prediction)
3. [Kaggle Notebook for Food Nutrition Analysis](https://www.kaggle.com/code/nauvalalmas/food-nutrition-indonesian)

## Prerequisites

To run this project, ensure that you have the following installed:

- **Jupyter Notebook** or **Google Colab**
- **Kaggle API Token**: [Generate your Kaggle API token](https://www.kaggle.com/docs/api)
- Python version **3.6** or above
- Latest version of **TensorFlow 2.5** (or you can update it by rerunning the `.ipynb` and updating the models)

## How to Use

Follow these steps to get started with the project:

1. **Create Kaggle API Token**:
   - Go to your [Kaggle profile](https://www.kaggle.com/account) and download your Kaggle API token:
     - Navigate to "My Account" → Look for the "API" section → Click on "Create New API Token".
   - This will download a `kaggle.json` file.

2. **Open Notebook in Google Colab**:
   - Click the **Open in Colab** link for the respective notebook.
   - In Google Colab, click on **File** > **Save a copy in Drive** to run and edit the notebook with your Google account.

3. **Upload Kaggle API Token**:
   - If prompted, upload your `kaggle.json` to enable dataset download.

4. **Dataset Download**:
   - The notebook will automatically download the datasets from Kaggle.

5. **Google Drive Dataset (Optional)**:
   - If you are using Google Drive for dataset storage, click on the provided GoogleAuth link, sign in with your Google account, and grant the necessary permissions.

6. **Done**:
   - You are now ready to run the project, train models, and perform stunting predictions using the provided datasets.

## Model Building

This project leverages **TensorFlow Lite** and **TensorFlow.js** to build and deploy machine learning models for stunting prediction. TensorFlow Lite is used for efficient model deployment on mobile and embedded devices, while TensorFlow.js allows for running models directly in the browser.

---

Feel free to modify or expand this as needed!
