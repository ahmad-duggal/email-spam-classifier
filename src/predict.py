import os
import sys
import pickle

# Ensure the src directory is in the Python path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from preprocessing import clean_text
from logger import logger
import time

# Define absolute paths for models based on the project root
project_root = os.path.dirname(current_dir)
MODEL_PATH = os.path.join(project_root, 'models', 'spam_classifier.pkl')
VECTORIZER_PATH = os.path.join(project_root, 'models', 'tfidf_vectorizer.pkl')

# Cache the loaded models so they are only loaded once
_model = None
_vectorizer = None

def load_models():
    """
    Loads and caches the trained model and vectorizer.
    Returns a tuple: (model, vectorizer)
    """
    global _model, _vectorizer
    
    if _model is None or _vectorizer is None:
        logger.info("Machine Learning models missing from hot cache. Initializing disk I/O load...")
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            logger.critical(f"FATAL: Model files explicitly missing from directory bindings at {MODEL_PATH}")
            raise FileNotFoundError(f"Model files not found. Expected them at {MODEL_PATH}")
            
        with open(MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
        with open(VECTORIZER_PATH, 'rb') as f:
            _vectorizer = pickle.load(f)
            
        logger.info("Successfully loaded ML models to RAM. Global scope cached.")
        
    return _model, _vectorizer

def predict_message(message: str) -> dict:
    """
    Core prediction logic.
    Takes a string message and returns a dictionary with the prediction and performance metrics.
    """
    start_time = time.time()
    
    if not message or not message.strip():
        logger.warning("Edge Case Hit: Empty payload provided for inference. Rejected.")
        raise ValueError("Message cannot be empty.")
    
    # 0. Anti-DOS Edge Case: Cap string length to prevent memory exhaustion
    if len(message) > 15000:
        logger.warning(f"Edge Case Hit: Rejection! Exceeded max token payload ({len(message)} chars). Possible NLP-DOS attempt.")
        raise ValueError("Payload size exceeds maximum allowed limit (15,000 characters).")
        
    model, vectorizer = load_models()
    
    # 1. Clean the raw text
    cleaned_text = clean_text(message)
    
    # 2. Convert text to numerical features using the saved vocabulary
    vectorized_text = vectorizer.transform([cleaned_text]).toarray()
    
    # 3. Predict & Probability!
    prediction_value = int(model.predict(vectorized_text)[0])
    probabilities = model.predict_proba(vectorized_text)[0]
    
    # 4. Format output
    is_spam = bool(prediction_value == 1)
    label = "SPAM" if is_spam else "HAM"
    confidence_score = round(float(probabilities[1] if is_spam else probabilities[0]) * 100, 2)
    
    end_time = time.time()
    inference_time_ms = round((end_time - start_time) * 1000, 2)
    
    logger.info(f"Inference complete: Label={label}, Confidence={confidence_score}%, Execution_Time={inference_time_ms}ms")
    
    return {
        "is_spam": is_spam,
        "label": label,
        "score": confidence_score,
        "inference_time_ms": inference_time_ms
    }
