import streamlit as st
import numpy as np
import pickle

# Correctly open and load the model
with open(r'C:\Users\shubh\OneDrive\Desktop\nlp.py\ml\linear_regression.pkl', 'rb') as file:
    lr = pickle.load(file)

# Prediction function
def predict_sales(tv, radio, newspaper, online_ad):
    features = np.array([[tv, radio, newspaper, online_ad]])
    result = lr.predict(features)
    return result[0]

# Streamlit app UI
st.title("📈 Sales Prediction App using Linear Regression")

tv = st.number_input("Enter TV advertisement budget:", value=230.1)
radio = st.number_input("Enter Radio advertisement budget:", value=37.8)
newspaper = st.number_input("Enter Newspaper advertisement budget:", value=69.2)
online_ad = st.number_input("Enter Online advertisement budget:", value=50.0)

if st.button("Predict"):
    sales = predict_sales(tv, radio, newspaper, online_ad)
    st.subheader("📊 Predicted Sale:")
    st.success(f"{sales:.3f}")
