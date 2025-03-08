
import streamlit as st
import json
import requests
import numpy as np
from datetime import datetime


# Load javab from the JSON file
with open('data/javab.json', 'r') as file:
    javab = json.load(file)

# Tolerance for rounding (in mA)
tolerance = 1

# Expected Kirchhoff equation coefficients for each set (precomputed)
expected_equations = {
    "1": [(120, 180, -220, 15), (150, 220, -270, 18), (1, -1, -1, 0)],
    "2": [(140, 200, -260, 17), (170, 240, -310, 22), (1, -1, -1, 0)],
    "3": [(100, 200, -150, 12), (110, 180, -130, 14), (1, -1, -1, 0)],
    "4": [(130, 170, -190, 16), (140, 190, -220, 19), (1, -1, -1, 0)],
    "5": [(200, 250, -300, 20), (220, 270, -320, 23), (1, -1, -1, 0)],
    "6": [(140, 160, -180, 14), (160, 190, -210, 16), (1, -1, -1, 0)],
    "7": [(180, 220, -240, 17), (200, 260, -280, 21), (1, -1, -1, 0)],
    "8": [(160, 210, -230, 19), (170, 220, -250, 20), (1, -1, -1, 0)],
    "9": [(110, 140, -160, 13), (120, 150, -170, 15), (1, -1, -1, 0)],
    "10": [(120, 150, -170, 15), (130, 180, -190, 18), (1, -1, -1, 0)]
}

# Google Apps Script Web App URL (replace with your actual deployment URL)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyeN6BHsSkyc9yORGaxhD8kNgpZPL1TiYNX0hry-nzAzgJJOXHquNRsxOPb1hY9coJk/exec"

# Title
st.title("PHY 132 - Kirchhoff Current Checker")

# Intro Text
st.write("Welcome to the Kirchhoff Current Checker for PHY 132 at Eastern Kentucky University. 🤓")

# Optional Name Field
name = st.text_input("Optional: Enter your name (leave blank if you prefer to remain anonymous 🫣)")

# Select Problem Set
set_number = st.number_input("Select your problem set number (1 to 10):", min_value=1, max_value=10, step=1)

# Display corresponding circuit diagram
diagram_path = f"https://raw.githubusercontent.com/ZAKI1905/phy132-kirchhoff-checker/main/Diagrams/circuit_set_{set_number}.png"
st.image(diagram_path, caption=f"Problem Set {set_number} Circuit Diagram")

# Input Fields for Kirchhoff Coefficients
st.write("### Enter your Kirchhoff equation coefficients")

coeff_labels = ["I1", "I2", "I3", "Constant"]
student_eqs = []

for i in range(3):
    st.write(f"#### Equation {i+1}")
    eq = [st.number_input(f"Eq {i+1}: Coefficient of {label}", value=0.0, format="%.2f") for label in coeff_labels]
    student_eqs.append(eq)

# Input Fields for Currents
st.write("### Enter your calculated currents (in mA)")
I1 = st.number_input("Current I1 (mA)", value=0.0, format="%.2f")
I2 = st.number_input("Current I2 (mA)", value=0.0, format="%.2f")
I3 = st.number_input("Current I3 (mA)", value=0.0, format="%.2f")

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

# Check Kirchhoff Equations
if st.button("Check Kirchhoff Equations"):
    expected_eqs = expected_equations[str(set_number)]
    matches = compare_equations(student_eqs, expected_eqs)

    feedback_messages = []
    for i, match in enumerate(matches):
        if match:
            feedback_messages.append(f"✅ Equation {i+1} is correctly set up.")
        else:
            feedback_messages.append(f"❌ Equation {i+1} does not match any expected Kirchhoff equation. Check signs and coefficients.")

    st.write("\n".join(feedback_messages))

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

# Kirchhoff Recap
with st.expander("📚 Kirchhoff’s Rules Recap"):
    st.write("""
    **Kirchhoff's Voltage Law (KVL)**: The sum of all voltages around a closed loop is zero.

    **Kirchhoff's Current Law (KCL)**: The sum of currents entering a junction equals the sum of currents leaving the junction.

    Use these rules to solve for the currents in each resistor.
    """)

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
