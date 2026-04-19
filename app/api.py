from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
import os
import sys

# Ensure 'src' folder is in system path safely so we can import our prediction logic
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'src'))

try:
    from predict import predict_message, load_models
    from heuristics import analyze_heuristics
    from logger import logger
except ImportError as e:
    raise ImportError(f"Could not import source modules. Error: {e}")

# -----------------------------------------
# FASTAPI CONFIGURATION
# -----------------------------------------
tags_metadata = [
    {
        "name": "Health",
        "description": "Operations to check the health and configuration of the server.",
    },
    {
        "name": "Prediction Engine",
        "description": "Machine Learning inference endpoints. Extract threat confidence and heuristic metadata.",
    },
]

app = FastAPI(
    title="Digital Sentinel ML API",
    description="### Production-Ready Cyber-Security Email Analysis API.\n\nProvides endpoints to run Deep NLP inference on text bodies to detect Phishing, Spam, and Malicious content.",
    version="2.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -----------------------------------------
# DATA MODELS (Input Validation)
# -----------------------------------------
class MessageRequest(BaseModel):
    text: str = Field(..., title="Message Payload", description="The raw content of the email or SMS.", example="URGENT: Click here to claim your $1000 prize!")

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Email payload cannot be empty or just whitespace.')
        return v

class BulkMessageRequest(BaseModel):
    messages: List[str] = Field(..., title="List of Messages", description="Array of raw email contents.", example=["First email text", "Second email text"])

    @validator('messages')
    def check_messages_list(cls, v):
        if not v:
            raise ValueError('Messages array cannot be empty.')
        if len(v) > 50:
             raise ValueError('Exceeded maximum bulk prediction limit of 50 messages.')
        return v

class PredictionResponse(BaseModel):
    success: bool
    is_spam: bool
    label: str
    confidence_score: float = Field(..., description="Percentage confidence (0-100)")
    inference_time_ms: float = Field(..., description="Time taken for ML inference in milliseconds")
    heuristics: Dict[str, Any] = Field(..., description="Triggered NLP rules and mocked technical security headers")

class BulkPredictionResponse(BaseModel):
    success: bool
    total_processed: int
    predictions: List[PredictionResponse]

# -----------------------------------------
# API LIFECYCLE
# -----------------------------------------
@app.on_event("startup")
async def startup_event():
    """Load the ML models exactly once when the server boots."""
    try:
        load_models()
        logger.info("FastAPI Event: Models successfully loaded into memory!")
    except FileNotFoundError:
        logger.critical("CRITICAL: ML Models missing from 'models/' directory.")

# -----------------------------------------
# ENDPOINTS
# -----------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    """Verify runtime status of the ML API."""
    return {"status": "online", "message": "Digital Sentinel API is actively scanning. Navigate to /docs for Swagger."}

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction Engine"])
def predict_spam(request: MessageRequest):
    """
    Analyzes a single email payload.
    Returns:
    - Overall Threat Verdict (Spam/Ham)
    - % Confidence Score
    - Technical Heuristics
    """
    try:
        result = predict_message(request.text)
        heuristics = analyze_heuristics(request.text)
        
        return PredictionResponse(
            success=True,
            is_spam=result["is_spam"],
            label=result["label"],
            confidence_score=result["score"],
            inference_time_ms=result["inference_time_ms"],
            heuristics=heuristics
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal AI Error: {str(e)}")

@app.post("/bulk-predict", response_model=BulkPredictionResponse, tags=["Prediction Engine"])
def bulk_predict_spam(request: BulkMessageRequest):
    """
    Analyzes an array of email payloads.
    Optimized for processing up to 50 messages per request natively.
    """
    predictions = []
    for text in request.messages:
        try:
            if not text.strip():
                 continue
                 
            result = predict_message(text)
            heuristics = analyze_heuristics(text)
            predictions.append(PredictionResponse(
                success=True,
                is_spam=result["is_spam"],
                label=result["label"],
                confidence_score=result["score"],
                inference_time_ms=result["inference_time_ms"],
                heuristics=heuristics
            ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed during bulk process: {str(e)}")
            
    return BulkPredictionResponse(
        success=True,
        total_processed=len(predictions),
        predictions=predictions
    )
