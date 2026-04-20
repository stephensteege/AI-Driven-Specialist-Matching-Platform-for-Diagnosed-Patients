# AI-Driven Specialist Matching Platform for Diagnosed Patients

This project is an AI-driven specialist matching platform that takes a free-text patient query, predicts the user's intent and relevant slots, and returns structured results through a Flask backend.

The backend uses NVIDIA NeMo for joint intent and slot classification.

---

# Project Overview

The goal of this platform is to allow a user to describe what kind of doctor or procedure they need in natural language, such as:

- "I need a female surgeon for an appendectomy"
- "Find me a cardiologist who speaks Spanish"
- "I want an orthopedic doctor near me"

The model predicts:
- **Intent** — what the user is asking for
- **Slots** — structured pieces of information such as gender, operation, specialty, language, etc.

Those outputs can then be used to query a database and return specialist matches.

---

# Tech Stack

- Python 3.10
- Flask
- Flask-CORS
- PyTorch
- NVIDIA NeMo
- HTML / CSS / JavaScript frontend
- SQLite database

---

# Recommended Python Version

This project should be run with:

**Python 3.10**

Using a newer version of Python may cause package compatibility issues with NeMo and related dependencies.

To check your Python versions on Windows:

```powershell
py -0