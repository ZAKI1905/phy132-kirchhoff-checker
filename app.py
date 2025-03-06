
import streamlit as st
import json

# Load correct answers
with open('correct_answers.json', 'r') as file:
    correct_answers = json.load(file)

tolerance = 0.5

def is_close(actual, expected, tol):
    return abs(actual - expected) <= tol

def check_answer(set_number, I1, I2, I3):
    correct = correct_answers.get(str(set_number))
    if correct is None:
        return "❌ Invalid set number."

    close_match = all(is_close(student, correct_value, tolerance)
                      for student, correct_value in zip([I1, I2, I3], correct))

    if [I1, I2, I3] == correct:
        return "✅ Correct! All currents exactly match."
    elif close_match:
        differences = [abs(student - correct_value) for student, correct_value in zip([I1, I2, I3], correct)]
        diff_message = "\n".join([f"I{index+1}: off by {diff:.2f} mA" for index, diff in enumerate(differences)])
        return f"⚠️ Almost correct (within rounding tolerance):\n{diff_message}"
    else:
        return "❌ Incorrect."

# Streamlit UI
st.title("PHY 132 - Kirchhoff Current Checker")

set_number = st.number_input("Set Number", min_value=1, max_value=10, step=1)
I1 = st.number_input("Current I1 (mA)")
I2 = st.number_input("Current I2 (mA)")
I3 = st.number_input("Current I3 (mA)")

if st.button("Check Answers"):
    result = check_answer(set_number, I1, I2, I3)
    st.write(result)
