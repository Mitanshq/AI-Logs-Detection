import os
import re
import pickle
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

try:
    lemmatizer = WordNetLemmatizer()
except LookupError:
    nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()
    

def process(log):
    log = re.sub(r'\[\d{1,2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}]', ' ', log)
    log = re.sub(r'[^a-zA-Z0-9.\s:/_-]', ' ', log)  # Allows IPs, URLs, etc.
    log = log.lower().split()
    log = ' '.join(lemmatizer.lemmatize(word) for word in log if word not in stop_words)
    return log

genuine_folder = ['All_logs/genuine_app_logs.txt', 'All_logs/genuine_firewall_logs.txt', 'All_logs/genuine_network_logs.txt', 'All_logs/genuine_web_logs.txt']
scam_folder = ['All_logs/scam_app_logs.txt', 'All_logs/scam_firewall_logs.txt', 'All_logs/scam_network_logs.txt', 'All_logs/scam_web_logs.txt']

def load_logs():
    all_logs = []
    
    for file_path in genuine_folder:
        with open(file_path, 'r', encoding='utf-8') as file:
            log = process(file.read())
            all_logs.append((log, 0))  # 0 for genuine

    for file_path in scam_folder:
        with open(file_path, 'r', encoding='utf-8') as file:
            log = process(file.read())
            all_logs.append((log, 1))  # 1 for scam
            
    return all_logs

def extract_features(all_logs):
    logs, labels = zip(*all_logs)
    if os.path.exists("model_file/vectorizer.pkl"):
        with open("model_file/vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        features = vectorizer.transform(logs).toarray()
    else:
        vectorizer = TfidfVectorizer(max_features=1000)
        features = vectorizer.fit_transform(logs).toarray()
        with open("model_file/vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)
    return features, np.array(labels), vectorizer

def train_or_load_model():
    required_files = ["model_file/tf_model.keras", "model_file/vectorizer.pkl", "model_file/pca.pkl", "model_file/ensemble.pkl"]
    if all(os.path.exists(f) for f in required_files):
        print("Loading existing model, vectorizer, and PCA...")
        model = tf.keras.models.load_model("model_file/tf_model.keras")
        with open("model_file/vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open("model_file/pca.pkl", "rb") as f:
            pca = pickle.load(f)
        with open("model_file/ensemble.pkl", 'rb') as f:
            ensemble_model = pickle.load(f)
        return model, vectorizer, pca, ensemble_model

    print("Training TensorFlow model...")
    all_logs = load_logs()
    features, labels, vectorizer = extract_features(all_logs)

    # Apply PCA
    pca = PCA(n_components=0.95)
    features_pca = pca.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(features_pca, labels, test_size=0.2, random_state=42)


    # Define a simple neural network
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train model using GPU
    with tf.device('/GPU:0'):
        model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)
        

    # ensemble training
    
    ensemble_model = VotingClassifier(
        estimators=[('nb', GaussianNB()), ('svm', SVC(probability=True, kernel='linear'))],
        voting='soft'
    )
    ensemble_model.fit(X_train, y_train)
    
    # Save model
    model.save("model_file/tf_model.keras")
    with open('model_file/ensemble.pkl', 'wb') as f:
        pickle.dump(ensemble_model, f)
    with open("model_file/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("model_file/pca.pkl", "wb") as f:
        pickle.dump(pca, f)

    return model, vectorizer, pca, ensemble_model

def predict(log, model, ensemble_model, vectorizer, pca):
    log = process(log)
    log_vector = vectorizer.transform([log]).toarray()
    log_vector_pca = pca.transform(log_vector)

    nn_confidence = model.predict(log_vector_pca)[0][0]
    
    # ensemble model prediction
    ensmb_pred = ensemble_model.predict_proba(log_vector_pca)[0][1]
    
    # weighted decision
    
    final_confidence = (nn_confidence + ensmb_pred) / 2
    return ('Scam Log' if final_confidence > 0.5 else 'Genuine Log', final_confidence)

def main():
    # test = []
    # with open('logs/test_genuine_app_logs.txt', 'r', encoding='utf-8') as f:
    #     test_logs = f.read().splitlines()
    #     for log in test_logs:
    #         test.append(log)
    # with open('logs/test_scam_app_logs.txt', 'r', encoding='utf-8') as f:
    #     test_logs = f.read().splitlines()
    #     for log in test_logs:
    #         test.append(log)
    model, vectorizer, pca, ensemble_model = train_or_load_model()
    file_path = 'test_logs/test_scam_firewall_logs.txt'
    scam, genuine = 0, 0
    total = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        test_logs = f.read().splitlines()
        for log in test_logs:
            result, confidence = predict(log, model, ensemble_model, vectorizer, pca)
            total += confidence
            if result == "Scam Log":
                scam += 1
            else:
                genuine += 1
    
    # for log in test:
    #         result, confidence = predict(log, model, ensemble_model, vectorizer, pca)
    #         total += confidence
    #         if result == "Scam Log":
    #             scam += 1
    #         else:
    #             genuine += 1

    print(f'Scam: {scam}, Genuine: {genuine}')
    # print(float(total) / len(test_logs))

if __name__ == "__main__":
    main()