import torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
from datasets import load_dataset
import torchaudio
import os

# Global model and processor instances
emotion_model = None
emotion_processor = None

def get_emotion_model():
    """Get or create the emotion model instance"""
    global emotion_model, emotion_processor
    if emotion_model is None:
        try:
            # Try to load local model first
            emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained("backend/pretrained/emotion_model")
            emotion_processor = Wav2Vec2Processor.from_pretrained("backend/pretrained/emotion_model")
        except:
            # Fallback to pretrained model
            emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained("facebook/wav2vec2-base", num_labels=4)
            emotion_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
    return emotion_model, emotion_processor

def predict_emotion(file_path: str) -> str:
    """
    Predict emotion of the speaker in an audio file
    Args:
        file_path (str): Path to audio file
    Returns:
        str: Predicted emotion label
    """
    try:
        model, processor = get_emotion_model()
        
        # Load and resample audio
        waveform, sr = torchaudio.load(file_path)
        if sr != 16000:
            waveform = torchaudio.functional.resample(waveform, sr, 16000)
        
        # Process audio
        inputs = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt")
        
        # Predict
        with torch.no_grad():
            logits = model(**inputs).logits
            prediction = torch.argmax(logits, dim=-1).item()
        
        # Map to emotion labels (assuming 4 classes: happy, sad, angry, neutral)
        emotion_labels = ["happy", "sad", "angry", "neutral"]
        return emotion_labels[prediction] if prediction < len(emotion_labels) else "neutral"
        
    except Exception as e:
        print(f"[ERROR] Emotion prediction failed: {e}")
        return "unknown"

# You'll replace this with your own data loader if you don't have metadata
def load_emotion_dataset():
    return load_dataset("superb", "ks")  # Just for placeholder/testing

def train_emotion_model():
    model = Wav2Vec2ForSequenceClassification.from_pretrained("facebook/wav2vec2-base", num_labels=4)
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")

    # You'd implement dataset, dataloader, training loop here
    print("Load your dataset and train here...")

    # Save model
    model.save_pretrained("backend/pretrained/emotion_model")
    processor.save_pretrained("backend/pretrained/emotion_model")

def load_emotion_model():
    model = Wav2Vec2ForSequenceClassification.from_pretrained("backend/pretrained/emotion_model")
    processor = Wav2Vec2Processor.from_pretrained("backend/pretrained/emotion_model")
    return model, processor
