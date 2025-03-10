
import streamlit as st
import json
import requests
import numpy as np
from datetime import datetime

# Normalize equations for comparison
def normalize_equation(eq):
    """ Normalize an equation by dividing all terms by the first nonzero coefficient. """
    coeffs = np.array(eq, dtype=np.float64)
    nonzero_indices = np.nonzero(coeffs[:-1])[0]  # Find nonzero coefficients (ignore constant term)
    
    if len(nonzero_indices) == 0:  # If all coefficients are zero, return as-is to avoid errors
        return coeffs
            
    first_nonzero = nonzero_indices[0]  # Get index of first nonzero coefficient
    return coeffs / coeffs[first_nonzero]  # Normalize

def compare_equations(student_eqs, expected_eqs):
    """ Check if student equations match expected equations (within tolerance). """
    normalized_student_eqs = [normalize_equation(eq) for eq in student_eqs]
    normalized_expected_eqs = [normalize_equation(eq) for eq in expected_eqs]

    matches = []
    for stud_eq in normalized_student_eqs:
        match_found = any(np.allclose(stud_eq, exp_eq, atol=0.1) for exp_eq in normalized_expected_eqs)
        matches.append(match_found)
    
    return matches

def check_linear_independence(equations):
    """ Check if the given equations are linearly independent. """
    coeff_matrix = np.array([eq[:-1] for eq in equations])  # Exclude the constant term
    rank = np.linalg.matrix_rank(coeff_matrix)
    return rank == len(equations)

# Google Apps Script Web App URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwYkzqimnnqLgoWS6BSmmpRbwPPMsPV-K2OZcBMcSRVlmFl-akUPRNf7nXBhKF1hg5J/exec"

# Log Submission to Google Sheets via Apps Script
def log_submission_to_apps_script(set_number, I1, I2, I3, result, name=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gs_result = ""
    if result.startswith("✅"):
        gs_result = "Correct"
    elif result.startswith("⚠️"):
        gs_result = "Almost correct"
    else:
        gs_result = "Incorrect"

    payload = {
        "timestamp": timestamp,
        "set_number": set_number,
        "I1": I1,
        "I2": I2,
        "I3": I3,
        "result": gs_result,
        "name": name
    }
    requests.post(APPS_SCRIPT_URL, json=payload)


# Log Kirchhoff Submission to Google Sheets via Apps Script
def log_Kirchhoff_submission_to_apps_script(set_number, student_eqs, name=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert student equations to a JSON string
    student_eqs_str = json.dumps(student_eqs)  # Store equations as a JSON-encoded string

    # Prepare the payload to send
    payload = {
        "timestamp": timestamp,
        "set_number": set_number,
        "name": name,
        "student_equations": student_eqs_str,  # Send equations as a string
        "sheet": "Kirchhoff_Submissions"  # Specify the target sheet name (must be handled in Apps Script)
    }

    # Send the data to Google Apps Script
    response = requests.post(APPS_SCRIPT_URL, json=payload)

    # Optional: Print response for debugging
    if response.status_code == 200:
        print("Submission logged successfully.")
    else:
        print(f"Error logging submission: {response.text}")
        
# Load javab from the JSON file
with open('data/javab.json', 'r') as file:
    javab = json.load(file)

# Tolerance for rounding (in mA)
tolerance = 1

# Load problem sets from JSON file
with open("data/problems.json", "r") as file:
    problems = json.load(file)
    
# Function to compute Kirchhoff equation coefficients
def compute_kirchhoff_coefficients(V1, V2, R1, R2, R3):
    eq1 = (1, -1, -1, 0)  # I1 - I2 - I3 = 0 (Junction rule)
    eq2 = (-R1, 0, -R3, V1)  # V1 - R3 I3 - R1 I1 = 0 (Left loop)
    eq3 = (0, R2, -R3, -V2)  # V2 + R2 I2 - R3 I3 = 0 (Right loop)
    eq4 = (-R1, -R2, 0, V1 - V2)  # V1 - R2 I2 - V2 - R1 I1 = 0 (Big loop)
    return [eq1, eq2, eq3, eq4]

# Title
st.title("PHY 132 - Kirchhoff Current Checker")

# Intro Text
st.write("Welcome to the Kirchhoff Current Checker for PHY 132 at Eastern Kentucky University. 🤓")


# Kirchhoff Recap
with st.expander("📚 Kirchhoff’s Rules Recap"):
    st.write("""
    **Kirchhoff's Voltage Law (KVL)**: The sum of all voltages around a closed loop is zero.

    **Kirchhoff's Current Law (KCL)**: The sum of currents entering a junction equals the sum of currents leaving the junction.

    Use these rules to solve for the currents in each resistor.
    """)
    
# Optional Name Field
name = st.text_input("Optional: Enter your name (leave blank if you prefer to remain anonymous 🫣)")

# Select Problem Set
set_number = st.number_input("Select your problem set number (1 to 10):", min_value=1, max_value=10, step=1)

# Get corresponding circuit parameters
V1, V2, R1, R2, R3 = problems[str(set_number)]

# Display corresponding circuit diagram
diagram_path = f"https://raw.githubusercontent.com/ZAKI1905/phy132-kirchhoff-checker/main/Diagrams/circuit_set_{set_number}.png"
st.image(diagram_path, caption=f"Problem Set {set_number} Circuit Diagram")

# Compute expected Kirchhoff equations dynamically
expected_eqs = compute_kirchhoff_coefficients(V1, V2, R1, R2, R3)

# Input Fields for Kirchhoff Coefficients
st.write("### Enter your Kirchhoff equation coefficients in the following format:")

st.latex(r"A \cdot I_1 \,+ \, B \cdot I_2 \, +\,  C \cdot I_3\,  +\,  D \, =\,  0")

st.write("Where:")
st.markdown(r"""
- $A, B, C$ are the coefficients of $I_1, I_2, I_3$, respectively.  
- $D$ is the constant term (voltage sum).
""", unsafe_allow_html=True)

coeff_labels = ["I1", "I2", "I3", "Constant"]
student_eqs = []

for i in range(3):
    st.write(f"#### Equation {i+1}")
    eq = [st.number_input(f"Eq {i+1}: Coefficient of {label}", value=0.0, format="%.2f") for label in coeff_labels]
    student_eqs.append(eq)

# Check Kirchhoff Equations
if st.button("Check Kirchhoff Equations"):
    matches = compare_equations(student_eqs, expected_eqs)

    if not check_linear_independence(student_eqs):
        st.error("⚠️ Your equations are not linearly independent! You may have repeated the same equation multiple times.")

    feedback_messages = []
    for i, match in enumerate(matches):
        if match:
            feedback_messages.append(f"✅ Equation {i+1} is correctly set up.")
        else:
            feedback_messages.append(f"❌ Equation {i+1} does not match any expected Kirchhoff equation. Check signs and coefficients.")

    st.write("\n".join(feedback_messages))
    log_Kirchhoff_submission_to_apps_script(set_number, student_eqs, name)
    
# Input Fields for Currents
st.write("### Enter your calculated currents (in mA)")
I1 = st.number_input("Current I1 (mA)", value=0.0, format="%.2f")
I2 = st.number_input("Current I2 (mA)", value=0.0, format="%.2f")
I3 = st.number_input("Current I3 (mA)", value=0.0, format="%.2f")

# Check Answer Logic
def is_close(actual, expected, tol=tolerance):
    return abs(actual - expected) <= tol

def check_answer(set_number, I1, I2, I3):
    if str(set_number) not in javab:
        return "⚠️ Invalid set number. Please check with your instructor."
    
    correct = javab[str(set_number)]
    close_match = all(is_close(student, correct_value) for student, correct_value in zip([I1, I2, I3], correct))

    if [I1, I2, I3] == correct:
        return "✅ Correct! All currents exactly match the answer key."
    elif close_match:
        differences = [abs(student - correct_value) for student, correct_value in zip([I1, I2, I3], correct)]
        diff_message = "\n".join([f"I{index+1}: off by {diff:.2f} mA" for index, diff in enumerate(differences)])
        return f"⚠️ Almost correct (within rounding tolerance).\n{diff_message}"
    else:
        return "❌ Incorrect. Try again!"

# Submit Button
if st.button("Check Answers"):
    result = check_answer(set_number, I1, I2, I3)
    log_submission_to_apps_script(set_number, I1, I2, I3, result, name)
    if result.startswith("✅"):
        st.success(result)
    elif result.startswith("⚠️"):
        st.warning(result)
    else:
        st.error(result)


# Footer with contact info and right-aligned EKU logo
footer = '''
---
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        This tool was developed for <b>PHY 132 - College Physics II</b> at Eastern Kentucky University.<br>
        For questions, contact: <b>Professor Zakeri</b> (m.zakeri@eku.edu)
    </div>
    <div>
        <img src="https://raw.githubusercontent.com/ZAKI1905/phy132-kirchhoff-checker/main/img/PrimaryLogo_Maroon.png" width="150">
    </div>
</div>
'''
st.markdown(footer, unsafe_allow_html=True)
