import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Download necessary NLTK data behind the scenes
nltk.download('stopwords', quiet=True)

stemmer = PorterStemmer()

def clean_text(text):
    """
    Cleans the input text by:
    1. Lowercasing
    2. Removing punctuation
    3. Tokenizing
    4. Removing stopwords
    5. Stemming
    """
    # 1. Lowercase text
    text = text.lower()
    
    # 2. Tokenize and remove punctuation
    # string.punctuation is a list of characters like !"#$%&'()*+
    words = [word for word in text.split() if word not in string.punctuation]
    
    # 3. Remove stopwords and stem the remaining words
    stop_words = set(stopwords.words('english'))
    cleaned_words = []
    
    for word in words:
        # Strip trailing/leading punctuations from the word
        word = word.strip(string.punctuation)
        if word and word not in stop_words:
            # 4. Stemming
            root_word = stemmer.stem(word)
            cleaned_words.append(root_word)
            
    # Join back into a single string
    return " ".join(cleaned_words)
