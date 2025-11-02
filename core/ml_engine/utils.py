import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'Model V1')

def load_model(filename):
    path = os.path.join(MODEL_DIR, filename)
    with open(path, 'rb') as f:
        return pickle.load(f)

# Load once and cache
break_length_model = load_model('break_length_model.pkl')
seasonal_pref_model = load_model('seasonal_pref_model.pkl')
scaler = load_model('scaler.pkl')
