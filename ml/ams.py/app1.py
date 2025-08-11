# app.py
import streamlit as st
import mysql.connector
import cv2
import numpy as np
import face_recognition
import os
import pyttsx3
from PIL import Image

# ---------- DATABASE CONNECTION ---------- #
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ams"
)
cursor = conn.cursor()

# ---------- TEXT-TO-SPEECH ENGINE ---------- #
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------- FACE DATASET DIR ---------- #
FARMER_FACES_DIR = "farmer_faces"
os.makedirs(FARMER_FACES_DIR, exist_ok=True)

# ---------- LOAD KNOWN FACES ---------- #
known_face_encodings = []
known_face_names = []

def load_known_faces():
    known_face_encodings.clear()
    known_face_names.clear()
    for name in os.listdir(FARMER_FACES_DIR):
        path = os.path.join(FARMER_FACES_DIR, name)
        for filename in os.listdir(path):
            image_path = os.path.join(path, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)

load_known_faces()

# ---------- MAIN INTERFACE ---------- #
st.title("🌾 Agriculture Management System")
menu = ["Register Farmer", "Login (Face)", "Login (Password)", "Disease Prediction", "Exit"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------- REGISTER FARMER ---------- #
if choice == "Register Farmer":
    st.subheader("📸 Register Farmer with Face & Password")
    name = st.text_input("Enter Farmer Name")
    password = st.text_input("Create Password", type="password")
    if st.button("Capture Face and Register"):
        if name and password:
            farmer_dir = os.path.join(FARMER_FACES_DIR, name)
            os.makedirs(farmer_dir, exist_ok=True)

            cap = cv2.VideoCapture(0)
            st.info("Capturing 5 Face Samples... Look at the Camera")
            count = 0
            while count < 5:
                ret, frame = cap.read()
                if not ret:
                    break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb)
                if boxes:
                    encoding = face_recognition.face_encodings(rgb, boxes)[0]
                    img_path = os.path.join(farmer_dir, f"face_{count}.jpg")
                    cv2.imwrite(img_path, frame)
                    count += 1
            cap.release()
            load_known_faces()
            cursor.execute("INSERT INTO farmer (name, password) VALUES (%s, %s)", (name, password))
            conn.commit()
            st.success("Farmer Registered Successfully!")
            speak("Farmer registered successfully")
        else:
            st.warning("Please fill in all fields")

# ---------- FACE LOGIN ---------- #
elif choice == "Login (Face)":
    st.subheader("🔐 Farmer Login via Face Recognition")
    if st.button("Start Face Login"):
        cap = cv2.VideoCapture(0)
        st.info("Looking for a registered face...")
        matched_name = None
        for _ in range(50):
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)
            for encoding in encodings:
                matches = face_recognition.compare_faces(known_face_encodings, encoding)
                if True in matches:
                    matched_name = known_face_names[matches.index(True)]
                    break
            if matched_name:
                break
        cap.release()
        if matched_name:
            st.success(f"Welcome {matched_name}")
            speak(f"Welcome {matched_name}")
        else:
            st.error("Face not recognized. Try again.")
            speak("Face not recognized")

# ---------- PASSWORD LOGIN ---------- #
elif choice == "Login (Password)":
    st.subheader("🔐 Farmer Login via Password")
    uname = st.text_input("Enter Name")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        cursor.execute("SELECT * FROM farmer WHERE name=%s AND password=%s", (uname, pwd))
        if cursor.fetchone():
            st.success(f"Welcome {uname}")
            speak(f"Welcome {uname}")
        else:
            st.error("Invalid Credentials")
            speak("Invalid credentials")

# ---------- DISEASE PREDICTION ---------- #
elif choice == "Disease Prediction":
    st.subheader("🌿 Plant Disease Prediction")
    image_file = st.file_uploader("Upload Image of Leaf", type=['jpg', 'png', 'jpeg'])
    if image_file is not None:
        img = Image.open(image_file)
        st.image(img, caption="Uploaded Leaf Image", use_column_width=True)
        st.info("Loading Model...")
        # Placeholder prediction logic
        predicted_disease = "Leaf Blight"
        cure = "Use Mancozeb 75% WP fungicide"
        st.success(f"Predicted Disease: {predicted_disease}")
        st.info(f"Recommended Cure: {cure}")
        speak(f"Disease detected: {predicted_disease}. Recommended cure is {cure}")

# ---------- EXIT ---------- #
elif choice == "Exit":
    st.warning("Thank you for using AMS!")
    speak("Thank you for using Agriculture Management System")
