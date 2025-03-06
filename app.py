
import streamlit as st
import json
import os

# Load correct answers from the JSON file (assumed to be in the same directory)
with open('correct_answers.json', 'r') as file:
    correct_answers = json.load(file)

# Tolerance for rounding (in mA)
tolerance = 0.5

# Title
st.title("PHY 132 - Kirchhoff Current Checker")

# Intro Text
st.write("Welcome to the Kirchhoff Current Checker for PHY 132 at Eastern Kentucky University.")

# Select Problem Set
set_number = st.number_input("Select your problem set number (1 to 10):", min_value=1, max_value=10, step=1)

# Display corresponding circuit diagram
diagram_path = f"https://raw.githubusercontent.com/ZAKI1905/phy132-kirchhoff-checker/main/Diagrams/circuit_set_{set_number}.png"
st.image(diagram_path, caption=f"Problem Set {set_number} Circuit Diagram")

# Input Fields for Currents
st.write("### Enter your calculated currents (in mA)")
I1 = st.number_input("Current I1 (mA)", value=0.0, format="%.2f")
I2 = st.number_input("Current I2 (mA)", value=0.0, format="%.2f")
I3 = st.number_input("Current I3 (mA)", value=0.0, format="%.2f")

# Check Answer Logic
def is_close(actual, expected, tol):
    return abs(actual - expected) <= tol

def check_answer(set_number, I1, I2, I3):
    if str(set_number) not in correct_answers:
        return "⚠️ Invalid set number. Please check with your instructor."
    
    correct = correct_answers[str(set_number)]
    close_match = all(is_close(student, correct_value, tolerance)
                      for student, correct_value in zip([I1, I2, I3], correct))

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

footer = """
---
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="font-size: 0.9em;">
        This tool was developed for <b>PHY 132 - College Physics II</b> at Eastern Kentucky University.<br>
        For questions, contact: <b>Professor Zakeri</b> (m.zakeri@eku.edu)
    </div>
    <div>
        <img src="https://raw.githubusercontent.com/ZAKI1905/phy132-kirchhoff-checker/main/img/PrimaryLogo_Maroon.png" width="150">
    </div>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
