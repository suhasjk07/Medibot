import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
from PIL import Image
import io
import uuid
import os
import PyPDF2
import docx
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pygame
from gtts import gTTS
from googletrans import Translator

# Download NLTK data
nltk.download('vader_lexicon', quiet=True)

# Initialize Gemini AI
genai.configure(api_key="AIzaSyAqLgulBNIV689k89u8cQcvO9RekyMJ7rk")
model = genai.GenerativeModel('gemini-pro')

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Initialize Pygame for audio playback
pygame.mixer.init()

# Initialize translator
translator = Translator()

# Function to process voice input and perform sentiment analysis
def process_voice_input():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            sentiment = analyze_sentiment(text)
            return text, sentiment
        except:
            return "Sorry, I could not understand that.", None

# Function to analyze sentiment
def analyze_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Function to generate AI response
def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

# Function for text-to-speech (avoiding symbols and supporting multiple languages)
def speak(text, lang='en'):
    # Replace common symbols with their spoken equivalents
    text = text.replace('%', ' percent ')
    text = text.replace('&', ' and ')
    text = text.replace('$', ' dollars ')
    text = text.replace('@', ' at ')
    text = text.replace('*', '  ')
    
    # Translate text if not in English
    if lang != 'en':
        text = translator.translate(text, dest=lang).text

    # Create a directory to store audio files if it doesn't exist
    audio_dir = "audio_files"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    
    # Save the text as a temporary audio file
    tts = gTTS(text=text, lang=lang)
    tts.save("temp_audio.mp3")

    # Generate a unique filename for the audio file
    filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(audio_dir, filename)
    
    # Play the audio file
    pygame.mixer.music.load("temp_audio.mp3")
    pygame.mixer.music.play()

# Function to stop audio playback
def stop_audio():
    pygame.mixer.music.stop()


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
st.title("Advanced AI-Powered Medical Chatbot")

# Sidebar for feature selection
st.sidebar.title("Features")
feature = st.sidebar.radio("Select a feature", 
    ["Patient Interface", "Doctor Registration"])

# Language selection
languages = {
    "English": "en", "Hindi": "hi", "Kannada": "kn", "Telugu": "te", "Tamil": "ta",
    "Bengali": "bn", "Nepali": "ne", "Marathi": "mr", "Korean": "ko", "Spanish": "es",
    "French": "fr", "German": "de", "Chinese": "zh-cn"
}
selected_language = st.sidebar.selectbox("Select Language", list(languages.keys()))
lang_code = languages[selected_language]

if feature == "Patient Interface":
    st.header("Patient Interface")
    
    sub_feature = st.selectbox("Choose a service", 
        ["Chat", "File Analysis", "Symptom Checker", "Health Advice", "Voice Interaction", "Diet Plan Creator", "Predictive Health", "Appointment Scheduling"])

    if sub_feature == "Chat":
        user_input = st.text_input("Ask a medical question:")
        if user_input:
            response = generate_response(user_input)
            st.write("Namma Sakhi:", response)
            if st.button("Read Response"):
                speak(response, lang_code)
            if "drug photo" in user_input.lower():
                st.image("https://via.placeholder.com/300x200.png?text=Drug+Photo+Placeholder", caption="Requested Drug Photo")

    elif sub_feature == "File Analysis":
        uploaded_file = st.file_uploader("Upload a medical document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            summary = analyze_file(uploaded_file)
            st.write("Document Summary:", summary)
            if st.button("Read Summary"):
                speak(summary, lang_code)

    elif sub_feature == "Symptom Checker":
        symptoms = st.multiselect("Select your symptoms:", 
            ["Fever", "Cough", "Headache", "Fatigue", "Nausea", "Shortness of breath", "Chest pain", "Abdominal pain", "Diarrhea", "Vomiting", "Muscle aches", "Sore throat"])
        if st.button("Check Symptoms"):
            symptom_text = ", ".join(symptoms)
            diagnosis = generate_response(f"Based on these symptoms: {symptom_text}, what could be the possible conditions? Provide a concise explanation.")
            st.write("Possible Conditions:", diagnosis)
            if st.button("Read Diagnosis"):
                speak(diagnosis, lang_code)

    elif sub_feature == "Health Advice":
        age = st.number_input("Age", min_value=0, max_value=120)
        weight = st.number_input("Weight (kg)", min_value=0.0)
        height = st.number_input("Height (cm)", min_value=0.0)
        if st.button("Get Advice"):
            advice = generate_response(f"Provide brief health advice for a {age}-year-old person weighing {weight} kg and {height} cm tall.")
            st.write("Health Advice:", advice)
            if st.button("Read Advice"):
                speak(advice, lang_code)

    elif sub_feature == "Voice Interaction":
        if st.button("Start Voice Interaction"):
            user_speech, sentiment = process_voice_input()
            st.write("You said:", user_speech)
            if sentiment:
                st.write("Detected Sentiment:", sentiment)
            if user_speech != "Sorry, I could not understand that.":
                ai_response = generate_response(user_speech)
                st.write("Namma Sakhi:", ai_response)
                speak(ai_response, lang_code)

    elif sub_feature == "Diet Plan Creator":
        age = st.number_input("Age", min_value=0, max_value=120, key="diet_age")
        weight = st.number_input("Weight (kg)", min_value=0.0, key="diet_weight")
        height = st.number_input("Height (cm)", min_value=0.0, key="diet_height")
        diet_preference = st.selectbox("Diet Preference", ["Vegetarian", "Non-vegetarian", "Vegan"])
        health_goal = st.selectbox("Health Goal", ["Weight loss", "Weight gain", "Maintenance"])
        if st.button("Generate Diet Plan"):
            diet_plan = generate_response(f"Create a brief 7-day diet plan for a {age}-year-old {diet_preference} person weighing {weight} kg and {height} cm tall, with a goal of {health_goal}.")
            st.write("Your Personalized Diet Plan:", diet_plan)
            if st.button("Read Diet Plan"):
                speak(diet_plan, lang_code)

    elif sub_feature == "Predictive Health":
        st.write("Please provide your health information for a predictive analysis:")
        age = st.number_input("Age", min_value=0, max_value=120, key="pred_age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        family_history = st.multiselect("Family History of Diseases", ["Diabetes", "Heart Disease", "Cancer", "Hypertension"])
        lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Moderately Active", "Very Active"])
        if st.button("Generate Predictive Health Report"):
            prediction = generate_response(f"Provide a concise predictive health analysis for a {age}-year-old {gender} with family history of {', '.join(family_history)} and a {lifestyle} lifestyle.")
            st.write("Predictive Health Report:", prediction)
            if st.button("Read Health Report"):
                speak(prediction, lang_code)

    elif sub_feature == "Appointment Scheduling":
        patient_name = st.text_input("Patient Name")
        appointment_date = st.date_input("Preferred Date")
        appointment_time = st.time_input("Preferred Time")
        doctor_specialty = st.selectbox("Doctor Specialty", ["General Physician", "Cardiologist", "Dermatologist", "Orthopedic", "Pediatrician"])
        if st.button("Schedule Appointment"):
            confirmation = f"Appointment scheduled for {patient_name} with a {doctor_specialty} on {appointment_date} at {appointment_time}"
            st.success(confirmation)
            if st.button("Read Confirmation"):
                speak(confirmation, lang_code)

    if st.button("Stop Audio"):
        stop_audio()

elif feature == "Doctor Registration":
    st.header("Doctor Registration")
    doctor_name = st.text_input("Full Name")
    medical_degree = st.text_input("Medical Degree")
    specialization = st.text_input("Specialization")
    license_number = st.text_input("Medical License Number")
    years_of_experience = st.number_input("Years of Experience", min_value=0, max_value=70)
    hospital_affiliation = st.text_input("Hospital Affiliation")
    
    if st.button("Register"):
        # In a real application, you would validate and store this information securely
        registration_info = f"Dr. {doctor_name} registered successfully with {medical_degree} in {specialization}. License: {license_number}, Experience: {years_of_experience} years, Affiliated with: {hospital_affiliation}"
        st.success(registration_info)
        if st.button("Read Registration Info"):
            speak(registration_info, lang_code)

# Feedback system
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("Please provide your feedback:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")
    speak("Thank you for your feedback!", lang_code)

# Disclaimer
disclaimer = "This is a prototype. Always consult with a qualified healthcare professional for medical advice."
st.sidebar.markdown(f"**Disclaimer:** {disclaimer}")
if st.sidebar.button("Read Disclaimer"):
    speak(disclaimer, lang_code)
