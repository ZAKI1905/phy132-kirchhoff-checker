
# PHY 132 Kirchhoff Current Checker

This is a simple web-based current checker designed for PHY 132 students at Eastern Kentucky University (EKU). 
The tool helps students verify their calculated currents for a Kirchhoff’s Rules circuit by comparing their answers 
to pre-set correct values. 

The app accounts for small rounding errors and provides clear feedback:

- ✅ Exact match (correct)
- ⚠️ Close match (within rounding tolerance)
- ❌ Incorrect (values are off)

## How It Works
This app is built using **Streamlit**, making it lightweight and accessible from any device — phone, tablet, or computer. 
It uses a JSON file (`correct_answers.json`) to store the answer key, so students never see the solutions directly.

## How to Deploy to Streamlit Cloud

### Step 1: Create a GitHub Repository
Create a new GitHub repository (recommended name: `phy132-kirchhoff-checker`) and upload these two files:
- `app.py` (the main Streamlit app)
- `correct_answers.json` (the answer key)

### Step 2: Deploy to Streamlit Cloud
Go to [https://share.streamlit.io](https://share.streamlit.io) and:
- Connect to your GitHub account.
- Select your new repository.
- Set the **main file** to `app.py`.
- Deploy!

### Step 3: Share the Link with Students
Once deployed, Streamlit will give you a link like:

```
https://your-username-your-repo-name.streamlit.app
```

Share this link with your students so they can check their work.

---

## Example
Students will see a simple form asking for:
- Set Number (1-10)
- I1 (in mA)
- I2 (in mA)
- I3 (in mA)

They enter their values and click **Check Answers** to get instant feedback.

---

## Topics
`physics` `circuits` `streamlit` `kirchhoff` `phy132` `eku` `education` `teaching`

---

## License
This project is for educational use only. Feel free to modify it for your own class.
