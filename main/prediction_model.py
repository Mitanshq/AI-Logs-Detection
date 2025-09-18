import os
import pickle
import re
import joblib
import numpy as np
from app import *
from keras.models import load_model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from model import predict

# Define model file paths
NN_MODEL_PATH = "model_file/tf_model.keras"
ENSEMBLE_MODEL_PATH = "model_file/ensemble.pkl"
VECTORIZER_PATH = "model_file/vectorizer.pkl"
PCA_PATH = "model_file/pca.pkl"

# Load pre-trained models and vectorizer
if not os.path.exists(NN_MODEL_PATH) or not os.path.exists(ENSEMBLE_MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError("One or more model files are missing!")

print("Loading AI models...")
nn_model = load_model(NN_MODEL_PATH)
ensemble_model = pickle.load(open(ENSEMBLE_MODEL_PATH, 'rb'))
vectorizer = pickle.load(open(VECTORIZER_PATH, 'rb'))
pca = pickle.load(open(PCA_PATH, 'rb')) if os.path.exists(PCA_PATH) else None

# Preprocessing function
def process_log(log):
    """Clean and preprocess log data"""
    log = re.sub(r'\[\d{1,2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}]', ' ', log)  # Remove timestamps
    log = re.sub(r'[^a-zA-Z0-9.\s:/_-]', ' ', log)  # Keep IPs, URLs, special characters
    log = log.lower().split()
    return " ".join(log)

# Feature extraction
def extract_features(log):
    """Convert log text into numerical features for model prediction"""
    processed_log = process_log(log)
    log_vector = vectorizer.transform([processed_log]).toarray()
    if pca:
        log_vector = pca.transform(log_vector)  # Apply PCA if available
    log_vector = MinMaxScaler().fit_transform(log_vector)  # Normalize features
    return log_vector

# Prediction function
def predict_log(log_content):
    """Predicts if a log entry is scam or genuine"""
    return predict(log_content, nn_model, ensemble_model, vectorizer, pca)

# Example usage
if __name__ == "__main__":
    sample_log = "User login failed from IP 192.168.1.1 with multiple attempts."
    result, confidence = predict_log(sample_log)
    print(f"Prediction: {result} (Confidence: {confidence:.2f})")
