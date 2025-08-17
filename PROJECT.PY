# data_preparation.py
import pandas as pd

def prepare_data():
    data = pd.read_csv('scrub_typhus_data.csv')
    X = data.drop('Outcome', axis=1)
    y = data['Outcome']
    X.to_csv('X_processed.csv', index=False)
    y.to_csv('y_processed.csv', index=False)

if __name__ == "__main__":
    prepare_data()
# model_training.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    X = pd.read_csv('X_processed.csv')
    y = pd.read_csv('y_processed.csv')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    joblib.dump(model, 'scrub_typhus_model.pkl')

if __name__ == "__main__":
    train_model()
# app.py
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('scrub_typhus_model.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    features = [
        int(request.json['fever']),
        int(request.json['headache']),
        int(request.json['myalgia']),
        int(request.json['eschar']),
        int(request.json['chills']),
        int(request.json['sweating']),
        int(request.json['vomiting']),
        int(request.json['rash']),
        int(request.json['lymph_gland_swelling'])
    ]
    prediction = model.predict([features])
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)