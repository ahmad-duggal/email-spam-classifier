from flask import Flask, request, jsonify
import os
import sys

# Ensure 'src' folder is in system path safely so we can import our prediction logic
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'src'))

try:
    from predict import predict_message, load_models
except ImportError:
    raise ImportError("predict module could not be found. Make sure src/predict.py exists.")

# -----------------------------------------
# FLASK CONFIGURATION
# -----------------------------------------
app = Flask(__name__)

# Load models at application startup
try:
    load_models()
    print("Models successfully loaded into memory!")
except FileNotFoundError:
    print("CRITICAL: ML Models missing from 'models/' directory.")

# -----------------------------------------
# ENDPOINTS
# -----------------------------------------
@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to verify the server is running."""
    return jsonify({"status": "online", "message": "Email Spam Flask API is running."})

@app.route("/predict", methods=["POST"])
def predict_spam():
    """
    Main Prediction Endpoint.
    Accepts JSON containing 'text' and returns the algorithm's verdict.
    """
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in JSON request."}), 400
        
    text = data["text"]
    
    # 1. Edge Case: Empty string check
    if not str(text).strip():
        return jsonify({"error": "The 'text' field cannot be completely empty."}), 400
        
    try:
        # 2. Delegate to the decoupled Predict module
        result = predict_message(text)
        
        # 3. Return a clean, standardized JSON response
        return jsonify({
            "success": True,
            "prediction": {
                "is_spam": result["is_spam"],
                "label": result["label"],
                "confidence_score": result["score"]
            }
        })
    except Exception as e:
        return jsonify({"error": f"Internal AI Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
