import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import pickle

# Step 1: Load and Explore the Dataset
data = pd.read_csv('train_data.csv')  # Load dataset from CSV

# Clean the text data
def preprocess_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    text = text.lower()
    return text

data['cleaned_text'] = data['sentence'].apply(preprocess_text)

# Feature Engineering
X = data['cleaned_text']
y = data['sentiment']
label_mapping = {1: 'positive', 0: 'negative'}
y = y.map(label_mapping)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(max_features=500)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Step 2: Train the Model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Step 3: Save the Model and Vectorizer
with open('sentiment_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('tfidf_vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

# Function to predict sentiment based on text input
def predict_sentiment(text):
    cleaned_text = preprocess_text(text)
    text_tfidf = vectorizer.transform([cleaned_text])
    prediction = model.predict(text_tfidf)
    return prediction[0]
