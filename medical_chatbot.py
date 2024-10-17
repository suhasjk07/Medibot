import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from PIL import Image
import io
import os
import PyPDF2
import docx
import json
import random

# Initialize Gemini AI
genai.configure(api_key="AIzaSyAqLgulBNIV689k89u8cQcvO9RekyMJ7rk")
model = genai.GenerativeModel('gemini-pro')

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to process voice input
def process_voice_input():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except:
            return "Sorry, I couldn't understand that."

# Function to generate AI response
def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

# Function for text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to analyze files
def analyze_file(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    elif file_extension == 'docx':
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        text = file.read().decode('utf-8')
    
    summary = generate_response(f"Summarize the following medical document: {text}")
    return summary

# Streamlit UI
st.title("Advanced AI-Powered Medical Chatbot: Namma Sakhi")

# Sidebar for features
st.sidebar.title("Features")
feature = st.sidebar.selectbox("Select a feature", 
    ["Chat", "File Analysis", "Symptom Checker", "Health Advice", "Voice Interaction", "Diet Plan Creator", "Predictive Health", "Appointment Scheduling"])

if feature == "Chat":
    st.header("Medical Chat")
    user_input = st.text_input("Ask a medical question or request a drug photo:")
    if user_input:
        response = generate_response(user_input)
        st.write("Namma Sakhi:", response)
        if "drug photo" in user_input.lower():
            st.image("https://www.shutterstock.com/search/medications/300x200.png?text=Drug+Photo+Placeholder", caption="Requested Drug Photo")

elif feature == "File Analysis":
    st.header("File Analysis")
    uploaded_file = st.file_uploader("Upload a medical document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        summary = analyze_file(uploaded_file)
        st.write("Document Summary:", summary)
        
        if st.button("Start Voice-over"):
            speak(summary)
        if st.button("Stop Voice-over"):
            engine.stop()

elif feature == "Symptom Checker":
    st.header("Symptom Checker")
    symptoms = st.multiselect("Select your symptoms:", 
        ["Fever", "Cough", "Headache", "Fatigue", "Nausea", "Shortness of breath", "Chest pain", "Abdominal pain", "Diarrhea", "Vomiting", "Muscle aches", "Sore throat"])
    if st.button("Check Symptoms"):
        symptom_text = ", ".join(symptoms)
        diagnosis = generate_response(f"Based on these symptoms: {symptom_text}, what could be the possible conditions? Provide a detailed explanation.")
        st.write("Possible Conditions:", diagnosis)

elif feature == "Health Advice":
    st.header("Personalized Health Advice")
    age = st.number_input("Age", min_value=0, max_value=120)
    weight = st.number_input("Weight (kg)", min_value=0.0)
    height = st.number_input("Height (cm)", min_value=0.0)
    if st.button("Get Advice"):
        advice = generate_response(f"Provide health advice for a {age}-year-old person weighing {weight} kg and {height} cm tall.")
        st.write("Health Advice:", advice)
        
        if st.button("Start Voice Interaction"):
            speak(advice)
        if st.button("Stop Voice Interaction"):
            engine.stop()

elif feature == "Voice Interaction":
    st.header("Voice Interaction with Namma-Sakhi AI")
    
    # Create a placeholder for the stop button
    stop_button_placeholder = st.empty()
    
    # Use session state to track if voice interaction is active
    if 'voice_interaction_active' not in st.session_state:
        st.session_state.voice_interaction_active = False

    if st.button("Start Voice Interaction"):
        st.session_state.voice_interaction_active = True

    # Display stop button when voice interaction is active
    if st.session_state.voice_interaction_active:
        if stop_button_placeholder.button("Stop Voice Interaction"):
            st.session_state.voice_interaction_active = False
            st.experimental_rerun()

    if st.session_state.voice_interaction_active:
        user_speech = process_voice_input()
        st.write("You said:", user_speech)
        if user_speech != "Sorry, I couldn't understand that.":
            ai_response = generate_response(user_speech)
            st.write("Namma Sakhi:", ai_response)
            speak(ai_response)
    else:
        st.write("Voice interaction is not active. Press 'Start Voice Interaction' to begin.")


elif feature == "Diet Plan Creator":
    st.header("Diet Plan Creator")
    age = st.number_input("Age", min_value=0, max_value=120, key="diet_age")
    weight = st.number_input("Weight (kg)", min_value=0.0, key="diet_weight")
    height = st.number_input("Height (cm)", min_value=0.0, key="diet_height")
    diet_preference = st.selectbox("Diet Preference", ["Vegetarian", "Non-vegetarian", "Vegan"])
    health_goal = st.selectbox("Health Goal", ["Weight loss", "Weight gain", "Maintenance"])
    if st.button("Generate Diet Plan"):
        diet_plan = generate_response(f"Create a 7-day diet plan for a {age}-year-old {diet_preference} person weighing {weight} kg and {height} cm tall, with a goal of {health_goal}.")
        st.write("Your Personalized Diet Plan:", diet_plan)

elif feature == "Predictive Health":
    st.header("Predictive Health Analysis")
    st.write("Please provide your health information for a predictive analysis:")
    age = st.number_input("Age", min_value=0, max_value=120, key="pred_age")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    family_history = st.multiselect("Family History of Diseases", ["Diabetes", "Heart Disease", "Cancer", "Hypertension"])
    lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Moderately Active", "Very Active"])
    if st.button("Generate Predictive Health Report"):
        prediction = generate_response(f"Provide a predictive health analysis for a {age}-year-old {gender} with family history of {', '.join(family_history)} and a {lifestyle} lifestyle.")
        st.write("Predictive Health Report:", prediction)

elif feature == "Appointment Scheduling":
    st.header("Appointment Scheduling")
    patient_name = st.text_input("Patient Name")
    appointment_date = st.date_input("Preferred Date")
    appointment_time = st.time_input("Preferred Time")
    doctor_specialty = st.selectbox("Doctor Specialty", ["General Physician", "Cardiologist", "Dermatologist", "Orthopedic", "Pediatrician"])
    if st.button("Schedule Appointment"):
        st.success(f"Appointment scheduled for {patient_name} with a {doctor_specialty} on {appointment_date} at {appointment_time}")

    st.subheader("Doctor Registration")
    doctor_name = st.text_input("Doctor Name")
    medical_degree = st.text_input("Medical Degree")
    specialization = st.text_input("Specialization")
    if st.button("Register Doctor"):
        st.success(f"Dr. {doctor_name} registered successfully with {medical_degree} in {specialization}")

# Medical Information Database
st.sidebar.header("Medical Information Database")
if st.sidebar.button("View Admission Requirements"):
    admission_req = generate_response("Provide a list of common admission requirements for hospitals.")
    st.sidebar.write(admission_req)

# Multilingual support
languages = ["English", "Hindi", "Kannada", "Telugu", "Tamil", "Bengali", "Nepali", "Marathi", "Korean", "Spanish", "French", "German", "Chinese"]
selected_language = st.sidebar.selectbox("Select Language", languages)

# Feedback system
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("Please provide your feedback:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

# Disclaimer
st.markdown("**Disclaimer:** This is a prototype. Always consult with a qualified healthcare professional for medical advice.")