# Email Spam Classifier

A robust, production-ready Machine Learning system that detects if a given text message or email is Spam or Ham (legitimate).

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Usage (Local)](#usage-local)
- [Usage (Docker)](#usage-docker)
- [API Documentation](#api-documentation)

---

## Overview
This repository contains a full-stack ML pipeline that trains a **Multinomial Naive Bayes** classifier using text feature extraction (TF-IDF), evaluates it, and deploys it via a backend API (FastAPI/Flask) and a frontend web interface (Streamlit).

## Architecture
- **src/predict.py**: The decoupled inference module that loads the trained `.pkl` models and applies the text classification algorithm.
- **app/api.py**: A high-performance REST API built with FastAPI that exposes the spam detection model.
- **app/flask_app.py**: An optional alternative Flask API endpoint.
- **app/streamlit_app.py**: A beautiful, interactive Next-Gen Web UI built with Streamlit.

## Features
- **Accurate Predictions**: Uses Scikit-learn's TF-IDF Vectorizer and MultinomialNB.
- **Separation of Concerns**: ML inference is decoupled from the web layer for cleaner microservices.
- **Containerized**: Fully deployable via Docker and Docker Compose.
- **Error Handling**: Comprehensive backend validation using Pydantic.

## Setup & Installation

### Option 1: Virtual Environment (Recommended locally)
1. Clone the repository and navigate into it.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage (Local)

### 1. Run the Backend API (FastAPI)
```bash
python -m uvicorn app.api:app --reload
```
*The API will be available at http://127.0.0.1:8000*
*Swagger Documentation available at http://127.0.0.1:8000/docs*

### 2. Run the Streamlit UI
In a separate terminal (with the same `.venv` active):
```bash
streamlit run app/streamlit_app.py
```
*The UI will be available at http://localhost:8501*

## Usage (Docker)
To run both the backend API and the frontend UI concurrently using Docker:
```bash
docker-compose up --build
```

---
*Built for educational and production environments.*
