# Smart Agriculture Assistant - Final Version
# Modules: Face Authentication, Disease Prediction, Feedback (NLP), Voice Output

import cv2
import numpy as np
import sqlite3
import pyttsx3
import os
from textblob import TextBlob

# ===============================
# Database & Voice Setup
# ===============================
conn = sqlite3.connect('ams.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS FARMER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT,
    face_encoding BLOB,
    password TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS FEEDBACK (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER,
    feedback TEXT,
    sentiment TEXT,
    FOREIGN KEY(farmer_id) REFERENCES FARMER(id)
)''')

conn.commit()

tts = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    tts.say(text)
    tts.runAndWait()

# ===============================
# Farmer Registration
# ===============================
def register_farmer(name, contact, password):
    cam = cv2.VideoCapture(0)
    speak("Please look at the camera to capture your face")

    ret, frame = cam.read()
    if ret:
        face_encoding = cv2.imencode('.jpg', frame)[1].tobytes()
        cursor.execute("INSERT INTO FARMER (name, contact, face_encoding, password) VALUES (?, ?, ?, ?)",
                       (name, contact, face_encoding, password))
        conn.commit()
        speak("Farmer registered successfully")
    else:
        speak("Camera error during registration.")
    cam.release()
    cv2.destroyAllWindows()

# ===============================
# Face Login
# ===============================
def face_login():
    cam = cv2.VideoCapture(0)
    speak("Please look at the camera for authentication")

    ret, frame = cam.read()
    if not ret:
        speak("Camera error. Try again.")
        return None

    cursor.execute("SELECT id, name, face_encoding FROM FARMER")
    farmers = cursor.fetchall()

    for farmer in farmers:
        saved_image = np.frombuffer(farmer[2], np.uint8)
        saved_decoded = cv2.imdecode(saved_image, cv2.IMREAD_COLOR)

        if saved_decoded is None:
            continue

        # Simple MSE comparison
        diff = np.sum((frame.astype("float") - saved_decoded.astype("float")) ** 2)
        if diff < 1e7:
            speak(f"Welcome back {farmer[1]}")
            cam.release()
            cv2.destroyAllWindows()
            return farmer[0]

    cam.release()
    cv2.destroyAllWindows()
    speak("Authentication failed")
    return None

# ===============================
# Password Login
# ===============================
def password_login(name, password):
    cursor.execute("SELECT id FROM FARMER WHERE name=? AND password=?", (name, password))
    result = cursor.fetchone()
    if result:
        speak(f"Welcome {name}")
        return result[0]
    else:
        speak("Invalid credentials")
        return None

# ===============================
# Predict Crop Disease
# ===============================
def predict_disease(image_path):
    try:
        # Placeholder logic
        speak("Analyzing the crop image for disease")
        if not os.path.exists(image_path):
            speak("Image not found.")
            return "Unknown", "No treatment available"

        # Dummy prediction
        return "Leaf Blight", "Use Mancozeb fungicide"
    except Exception as e:
        speak("Error in disease prediction")
        return "Unknown", "No treatment available"

# ===============================
# Feedback NLP
# ===============================
def analyze_feedback(farmer_id, feedback_text):
    sentiment = TextBlob(feedback_text).sentiment.polarity
    sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

    cursor.execute("INSERT INTO FEEDBACK (farmer_id, feedback, sentiment) VALUES (?, ?, ?)",
                   (farmer_id, feedback_text, sentiment_label))
    conn.commit()

    speak("Thank you for your feedback")
    if sentiment_label != "Positive":
        speak("We will try to improve our system")

# ===============================
# Main Program
# ===============================
def main():
    speak("Welcome to Smart Agriculture Assistant")
    print("\n1. Register\n2. Login with Face\n3. Login with Password\n4. Exit")
    choice = input("Enter your choice: ").strip()

    user_id = None

    if choice == '1':
        name = input("Enter Name: ").strip()
        contact = input("Enter Contact: ").strip()
        password = input("Set Password: ").strip()
        register_farmer(name, contact, password)
        return

    elif choice == '2':
        user_id = face_login()

    elif choice == '3':
        name = input("Enter Name: ").strip()
        password = input("Enter Password: ").strip()
        user_id = password_login(name, password)

    elif choice == '4':
        speak("Thank you for using the assistant.")
        return

    else:
        speak("Invalid option.")
        return

    # User logged in
    if user_id:
        while True:
            print("\n1. Predict Crop Disease\n2. Submit Feedback\n3. Exit")
            inner_choice = input("Enter choice: ").strip()

            if inner_choice == '1':
                image_path = input("Enter image path of crop leaf: ").strip()
                disease, treatment = predict_disease(image_path)
                speak(f"Disease detected: {disease}")
                speak(f"Recommended treatment: {treatment}")

            elif inner_choice == '2':
                feedback_text = input("Enter your feedback: ").strip()
                analyze_feedback(user_id, feedback_text)

            elif inner_choice == '3':
                speak("Logging out. Take care!")
                break

            else:
                speak("Invalid option.")

        # Tip after session
        speak("Here is a tip: Use drip irrigation to save water.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        speak("Session ended.")
    finally:
        conn.close()
        cv2.destroyAllWindows()
