import os
import torch
import torchaudio
import numpy as np
from tqdm import tqdm
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
from speechbrain.inference import EncoderClassifier

# Set paths
DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'svm_speaker_classifier.pkl')

# Load pretrained ECAPA model (copy strategy to avoid symlink issue)
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/ecapa",
    run_opts={"local_file_strategy": "copy"}
)

# Function to extract embeddings
def extract_embedding(file_path):
    try:
        signal, fs = torchaudio.load(file_path)
        if signal.shape[0] > 1:
            signal = torch.mean(signal, dim=0, keepdim=True)  # Convert to mono
        embedding = classifier.encode_batch(signal).squeeze().detach().cpu().numpy()
        return embedding
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Prepare data
embeddings = []
labels = []

print(f"\n🔍 Scanning dataset in: {DATASET_PATH}\n")

for speaker_dir in sorted(os.listdir(DATASET_PATH)):
    speaker_path = os.path.join(DATASET_PATH, speaker_dir)
    if not os.path.isdir(speaker_path):
        continue

    for file in os.listdir(speaker_path):
        if file.endswith(".wav"):
            file_path = os.path.join(speaker_path, file)
            emb = extract_embedding(file_path)
            if emb is not None:
                embeddings.append(emb)
                labels.append(speaker_dir)

print(f"✅ Total samples processed: {len(embeddings)}")

# Encode speaker labels
le = LabelEncoder()
encoded_labels = le.fit_transform(labels)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    embeddings, encoded_labels, test_size=0.2, random_state=42
)

# Train SVM model
print("\n🧠 Training SVM classifier...\n")
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X_train, y_train)

# Evaluate
y_pred = svm_model.predict(X_test)
print("📊 Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save model and label encoder
joblib.dump({'model': svm_model, 'label_encoder': le}, MODEL_SAVE_PATH)
print(f"\n💾 Model saved to {MODEL_SAVE_PATH}")
