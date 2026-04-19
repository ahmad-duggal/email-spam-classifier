import os
import sys

# Ensure src in system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from predict import predict_message, load_models

def main():
    print("="*60)
    print(" 📧 WELCOME TO THE AI SPAM CLASSIFIER CLI 📧")
    print("="*60)
    print("Loading AI core...")
    
    try:
        # Pre-load to avoid delay on first prediction
        load_models() 
    except FileNotFoundError:
        print("ERROR: Could not find the AI models. Did you run the Jupyter Notebook first?")
        sys.exit(1)
        
    while True:
        print("\n" + "-"*60)
        user_input = input("Enter an SMS or Email message (or type 'exit' to quit):\n> ")
        
        if user_input.strip().lower() == 'exit':
            print("Shutting down the AI. Goodbye!")
            break
            
        if not user_input.strip():
            print("Please type a valid message.")
            continue
            
        try:
            # Delegate to our prediction module
            result = predict_message(user_input)
            
            # Output
            if result["is_spam"]:
                print("\n🚨 AI VERDICT: SPAM (Malicious/Junk)")
            else:
                print("\n✅ AI VERDICT: HAM (Safe)")
                
        except Exception as e:
            print(f"Error during prediction: {e}")

if __name__ == "__main__":
    main()
