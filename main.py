import pickle
import os
import sys

# Add src folder to system path so we can import our preprocessing file
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from preprocessing import clean_text

def load_ai():
    """Loads the saved AI model and vectorizer from the models folder."""
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'spam_classifier.pkl')
    vec_path = os.path.join(os.path.dirname(__file__), 'models', 'tfidf_vectorizer.pkl')

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(vec_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except FileNotFoundError:
        print("ERROR: Could not find the AI models. Did you run the Jupyter Notebook first?")
        exit(1)

def main():
    print("="*60)
    print(" 📧 WELCOME TO THE AI SPAM CLASSIFIER CLI 📧")
    print("="*60)
    print("Loading AI core...")
    
    model, vectorizer = load_ai()
    
    while True:
        print("\n" + "-"*60)
        user_input = input("Enter an SMS or Email message (or type 'exit' to quit):\n> ")
        
        if user_input.strip().lower() == 'exit':
            print("Shutting down the AI. Goodbye!")
            break
            
        if not user_input.strip():
            print("Please type a valid message.")
            continue
            
        # 1. Clean Text
        cleaned = clean_text(user_input)
        
        # 2. Vectorize using the SAVED vocabulary
        vectorized_text = vectorizer.transform([cleaned]).toarray()
        
        # 3. Predict
        prediction = model.predict(vectorized_text)[0]
        
        # 4. Output
        if prediction == 1:
            print("\n🚨 AI VERDICT: SPAM (Malicious/Junk)")
        else:
            print("\n✅ AI VERDICT: HAM (Safe)")

if __name__ == "__main__":
    main()
