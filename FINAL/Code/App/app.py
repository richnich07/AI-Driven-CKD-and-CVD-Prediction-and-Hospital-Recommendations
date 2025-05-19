import streamlit as st
import requests
import pickle
import json
from datetime import datetime
import numpy as np
import streamlit as st
import json
import hashlib

# Function to load user credentials (from file)
def load_user_credentials():
    try:
        with open('user_credentials.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Create the file if it doesn't exist
        with open('user_credentials.json', 'w') as file:
            json.dump({}, file)  # Initialize with an empty dictionary
        return {}  # Return an empty dictionary if the file didn't exist
    except json.JSONDecodeError:
        # Handle the case where the file exists but isn't valid JSON
        st.sidebar.error("Error reading credentials. The file might be corrupted.")
        return {}

# Function to save user credentials (to file)
def save_user_credentials(credentials):
    with open('user_credentials.json', 'w') as file:
        json.dump(credentials, file)

# Function to hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate the user
def authenticate(username, password, user_credentials):
    hashed_password = hash_password(password)
    if username in user_credentials and user_credentials[username] == hashed_password:
        return True
    return False

# Function to handle login
def login():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if st.session_state['authenticated']:
        return True

    st.sidebar.header("Login")
    option = st.sidebar.selectbox("Select option", ["Login", "Register"])

    username = st.sidebar.text_input("Username", "")
    password = st.sidebar.text_input("Password", "", type='password')

    if option == "Login":
        if st.sidebar.button("Login"):
            user_credentials = load_user_credentials()
            if authenticate(username, password, user_credentials):
                st.session_state['authenticated'] = True
                st.sidebar.success("Successfully logged in!")
                return True
            else:
                st.sidebar.error("Invalid credentials. Please try again.")
                return False
    
    elif option == "Register":
        if st.sidebar.button("Register"):
            user_credentials = load_user_credentials()

            if username in user_credentials:
                st.sidebar.error("Username already exists. Please choose a different one.")
            else:
                hashed_password = hash_password(password)
                user_credentials[username] = hashed_password
                save_user_credentials(user_credentials)
                st.sidebar.success(f"Account created for {username}! You can now log in.")
                return False
    
    return False

# If the user is not authenticated, prompt login
if not login():
    st.stop()  # Stop further execution if not authenticated

# If authenticated, proceed with the rest of the app
st.title("")

# Load models and scaler
heart_model = pickle.load(open('heart_model.pkl', 'rb'))
kidney_model = pickle.load(open('kidney.pkl', 'rb'))
heart_scaler = pickle.load(open('scaler.pkl', 'rb'))
kidney_scaler = pickle.load(open('kidney_scaler_14.pkl', 'rb'))

# Hospital data (Mocked, add more real data as needed)
hospital_data = {
    "mumbai": {
        "Heart Disease": [
            "Kokilaben Dhirubhai Ambani Hospital",
            "Asian Heart Institute",
            "Lilavati Hospital",
            "Hiranandani Hospital",
            "Tata Memorial Hospital"
        ],
        "Kidney Disease": [
            "S.L. Raheja Hospital",
            "Bombay Hospital & Medical Research Centre",
            "Nanavati Max Super Speciality Hospital",
            "Global Hospitals",
            "Wockhardt Hospitals"
        ]
    },
    "delhi": {
        "Heart Disease": [
            "AIIMS Delhi",
            "Fortis Escorts Heart Institute",
            "Max Super Speciality Hospital",
            "Indraprastha Apollo Hospitals",
            "Sir Ganga Ram Hospital"
        ],
        "Kidney Disease": [
            "Medanta Kidney Institute",
            "BLK Super Speciality Hospital",
            "Sir Ganga Ram Hospital",
            "Primus Super Speciality Hospital",
            "Batra Hospital & Medical Research Centre"
        ]
    },
    "bangalore": {
        "Heart Disease": [
            "Narayana Health",
            "Apollo Hospitals Bannerghatta",
            "Sakra World Hospital",
            "Fortis Hospital Cunningham Road",
            "Manipal Hospital Old Airport Road"
        ],
        "Kidney Disease": [
            "Manipal Hospital",
            "St. John’s Medical College Hospital",
            "BGS Global Hospitals",
            "Vikram Hospital",
            "Columbia Asia Hospital"
        ]
    },
    "chennai": {
        "Heart Disease": [
            "Apollo Hospital",
            "Fortis Malar Hospital",
            "MIOT International",
            "Sri Ramachandra Medical Centre",
            "Global Hospitals"
        ],
        "Kidney Disease": [
            "Madras Medical Mission",
            "Kauvery Hospital",
            "Billroth Hospitals",
            "Sri Ramachandra Medical Centre",
            "Apollo Hospitals"
        ]
    },
    "hyderabad": {
        "Heart Disease": [
            "Yashoda Hospitals",
            "Care Hospitals",
            "Continental Hospitals",
            "KIMS Hospitals",
            "Apollo Hospitals"
        ],
        "Kidney Disease": [
            "Nizam's Institute of Medical Sciences (NIMS)",
            "Asian Institute of Nephrology and Urology",
            "Yashoda Hospitals",
            "KIMS Hospitals",
            "AIG Hospitals"
        ]
    },
    "pune": {
        "Heart Disease": [
            "Ruby Hall Clinic",
            "Jehangir Hospital",
            "Sahyadri Hospitals",
            "Deenanath Mangeshkar Hospital",
            "Columbia Asia Hospital"
        ],
        "Kidney Disease": [
            "Jehangir Hospital",
            "Sahyadri Hospitals",
            "Ruby Hall Clinic",
            "Inamdar Multispeciality Hospital",
            "Aditya Birla Memorial Hospital"
        ]
    }
}

# Function to get location based on IP address
def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        location_data = response.json()
        if location_data['status'] == 'fail':
            return None, None, None
        lat = location_data.get("lat")
        lon = location_data.get("lon")
        city = location_data.get("city")
        return lat, lon, city
    except Exception as e:
        st.error(f"Error fetching location: {e}")
        return None, None, None

# Function to load or initialize user history
def load_user_history():
    try:
        with open('user_history.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save user history
def save_user_history(history):
    with open('user_history.json', 'w') as file:
        json.dump(history, file)

# Get user's location
lat, lon, city = get_location()

# Page title
st.title(" Multi-Disease Predictor App ")

# Load or initialize user history
user_history = load_user_history()

# Sidebar navigation
option = st.sidebar.selectbox("Choose a Prediction Service", ["Heart Disease", "Kidney Disease", "Hospital Recommendation", "Doctor Appointment Booking"])

# User profile section
if "user_name" not in user_history:
    user_history["user_name"] = st.text_input("Enter your name", "")
    if user_history["user_name"]:
        st.success(f"Welcome, {user_history['user_name']}! Let's keep track of your health.")

# HEART DISEASE SECTION
if option == "Heart Disease":
    st.subheader("🫀 Heart Disease Prediction")
    age = st.number_input("Age", min_value=20, max_value=100, value=45)
    sex = st.radio("Sex", ["Male", "Female"])
    cigs_per_day = st.number_input("Cigarettes Per Day", min_value=0, max_value=60, value=0)
    chol = st.number_input("Total Cholesterol", min_value=100, max_value=600, value=200)
    sys_bp = st.number_input("Systolic BP", min_value=90, max_value=250, value=120)
    glucose = st.number_input("Glucose", min_value=50, max_value=400, value=85)

    if st.button("Predict Heart Risk"):
        sex_male = 1 if sex == "Male" else 0
        heart_input = np.array([[age, sex_male, cigs_per_day, chol, sys_bp, glucose]])
        heart_input_scaled = heart_scaler.transform(heart_input)
        heart_prob = heart_model.predict_proba(heart_input_scaled)[0][1]

        user_history['heart_predictions'] = user_history.get('heart_predictions', [])
        user_history['heart_predictions'].append({
            'timestamp': str(datetime.now()),
            'age': age,
            'sex': sex,
            'cigs_per_day': cigs_per_day,
            'chol': chol,
            'sys_bp': sys_bp,
            'glucose': glucose,
            'risk_score': heart_prob
        })
        save_user_history(user_history)

        if heart_prob > 0.55:
            st.error(f"⚠️ High risk of heart disease in 10 years. (Risk Score: {heart_prob:.2f})")
            if lat and lon:
                st.info(f"🏥 Finding Hospitals near your location: {lat}, {lon}")
                found = False
                for city_name, hospitals in hospital_data.items():
                    if city_name.lower() in city.lower():
                        st.write(f"Recommended hospitals in {city_name.title()}:")
                        st.write("❤️ Heart Disease Hospitals:", hospitals["Heart Disease"])
                        st.write("🧫 Kidney Disease Hospitals:", hospitals["Kidney Disease"])
                        found = True
                        break
                if not found:
                    st.write("Could not match your location. Here are some popular options:")
                    st.write("Heart: Kokilaben, AIIMS, Narayana | Kidney: Medanta, Manipal, Raheja")
        else:
            st.success(f"💚 Low risk of heart disease. (Risk Score: {heart_prob:.2f}) Keep it up!")
    
# KIDNEY DISEASE SECTION
elif option == "Kidney Disease":
    st.subheader("🧫 Kidney Disease Prediction")
    age = st.number_input("Age", 0.0, 120.0, 45.0)
    bp = st.number_input("Blood Pressure", 0.0, 200.0, 80.0)
    al = st.number_input("Albumin", 0.0, 5.0, 1.0)
    su = st.number_input("Sugar", 0.0, 5.0, 0.0)
    rbc = st.selectbox("Red Blood Cells", ['normal', 'abnormal'])
    pc = st.selectbox("Pus Cell", ['normal', 'abnormal'])
    pcc = st.selectbox("Pus Cell Clumps", ['present', 'notpresent'])
    ba = st.selectbox("Bacteria", ['present', 'notpresent'])
    bgr = st.number_input("Blood Glucose Random", 0.0, 500.0, 121.0)
    bu = st.number_input("Blood Urea", 0.0, 200.0, 36.0)
    sc = st.number_input("Serum Creatinine", 0.0, 20.0, 1.2)
    pot = st.number_input("Potassium", 2.5, 8.0, 4.5)
    wc = st.number_input("WBC Count", 3000.0, 20000.0, 8000.0)
    ane = st.selectbox("Anemia", ['yes', 'no'])

    if st.button("Predict Kidney Risk"):
        inputs = [
            age, bp, al, su,
            0 if rbc == "normal" else 1,
            0 if pc == "normal" else 1,
            1 if pcc == "present" else 0,
            1 if ba == "present" else 0,
            bgr, bu, sc, pot, wc,
            1 if ane == "yes" else 0
        ]
        prediction = kidney_model.predict([inputs])[0]

        user_history['kidney_predictions'] = user_history.get('kidney_predictions', [])
        user_history['kidney_predictions'].append({
            'timestamp': str(datetime.now()),
            'inputs': inputs,
            'prediction': int(prediction)
        })
        save_user_history(user_history)

        if prediction == 1:
            st.error("🧪 High risk of kidney disease. Go see your doc ASAP!")
            if lat and lon:
                st.info(f"🏥 Finding Hospitals near your location: {lat}, {lon}")
                found = False
                for city_name, hospitals in hospital_data.items():
                    if city_name.lower() in city.lower():
                        st.write(f"Recommended hospitals in {city_name.title()}:")
                        st.write("❤️ Heart Disease Hospitals:", hospitals["Heart Disease"])
                        st.write("🧫 Kidney Disease Hospitals:", hospitals["Kidney Disease"])
                        found = True
                        break
                if not found:
                    st.write("Could not match your location. Here are some popular options:")
                    st.write("Heart: Kokilaben, AIIMS, Narayana | Kidney: Medanta, Manipal, Raheja")
        else:
            st.success("✅ Kidneys look good! Keep being a hydrated king/queen!")
    
# HOSPITAL RECOMMENDATION SECTION
elif option == "Hospital Recommendation":
    st.subheader("🏥 Hospital Finder")
    if lat and lon:
        st.info(f"🔍 Finding Hospitals near you at: {city} ({lat}, {lon})")
        found = False
        for city_name, hospitals in hospital_data.items():
            if city_name.lower() in city.lower():
                st.write(f"Recommended hospitals in {city_name.title()}:")
                st.write("❤️ Heart Disease Hospitals:", hospitals["Heart Disease"])
                st.write("🧫 Kidney Disease Hospitals:", hospitals["Kidney Disease"])
                found = True
                break
        if not found:
            st.write("Could not match your location. Here are some popular options:")
            st.write("Heart: Kokilaben, AIIMS, Narayana | Kidney: Medanta, Manipal, Raheja")
    
# DOCTOR APPOINTMENT BOOKING SECTION
elif option == "Doctor Appointment Booking":
    st.subheader("📅 Book a Doctor's Appointment")
    selected_city = st.selectbox("Select your city", list(hospital_data.keys()))
    selected_disease = st.selectbox("Select your condition", ["Heart Disease", "Kidney Disease"])

    if selected_city and selected_disease:
        hospitals = hospital_data[selected_city][selected_disease]
        selected_hospital = st.selectbox("Select a hospital", hospitals)
        selected_date = st.date_input("Select appointment date")
        selected_time = st.time_input("Select appointment time")

        # Patient Details
        st.markdown("### 👤 Patient Details")
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        phone = st.text_input("Phone Number")
        email = st.text_input("Email ID")

        if st.button("Confirm Appointment"):
            if name and phone and email and age:
                st.success(
                    f"✅ Appointment confirmed for **{name}** at **{selected_hospital}** "
                    f"for **{selected_disease}** on **{selected_date}** at **{selected_time}**.\n\n"
                    f"📞 Contact: {phone} | 📧 {email}"
                )
            else:
                st.warning("⚠️ Please fill in all the patient details before confirming the appointment.")
