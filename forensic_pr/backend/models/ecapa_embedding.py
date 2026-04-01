


# import os
# import torch
# from speechbrain.inference import EncoderClassifier
# from speechbrain.dataio.dataio import read_audio
# from torch.nn.functional import cosine_similarity

# DATA_DIR = "backend/static/audio"

# # Global classifier instance
# classifier = None

# def get_classifier():
#     """Get or create the classifier instance"""
#     global classifier
#     if classifier is None:
#         classifier = EncoderClassifier.from_hparams(
#             source="speechbrain/spkrec-ecapa-voxceleb", 
#             savedir="backend/pretrained/ecapa"
#         )
#     return classifier

# def get_speaker_embedding(file_path: str) -> torch.Tensor | None:
#     """
#     Extracts speaker embedding from an audio file.
#     Args:
#         file_path (str): Path to audio file
#     Returns:
#         torch.Tensor | None: Speaker embedding tensor or None if error
#     """
#     try:
#         clf = get_classifier()
#         signal = read_audio(file_path)
#         emb = clf.encode_batch(signal.unsqueeze(0))
#         return emb.squeeze().detach()
#     except Exception as e:
#         print(f"[ERROR] Failed to process audio {file_path}: {e}")
#         return None

# def compare_embeddings(emb1: torch.Tensor, emb2: torch.Tensor, threshold: float = 0.5) -> tuple[float, bool]:
#     """
#     Compares two speaker embeddings using cosine similarity.
#     Args:
#         emb1 (torch.Tensor): First embedding
#         emb2 (torch.Tensor): Second embedding
#         threshold (float): Similarity threshold to classify same speaker
#     Returns:
#         tuple: (similarity_score, is_same_speaker)
#     """
#     try:
#         if emb1 is None or emb2 is None:
#             return 0.0, False

#         sim_score = cosine_similarity(emb1, emb2, dim=0).item()
#         return sim_score, sim_score > threshold

#     except Exception as e:
#         print(f"[ERROR] Embedding comparison failed: {e}")
#         return 0.0, False

# def get_speaker_embeddings():
#     """Get embeddings for all speakers in the dataset"""
#     clf = get_classifier()
#     embeddings = {}

#     for speaker in os.listdir(DATA_DIR):
#         speaker_path = os.path.join(DATA_DIR, speaker)
#         if os.path.isdir(speaker_path):
#             for file in os.listdir(speaker_path):
#                 if file.endswith(".wav"):
#                     audio_path = os.path.join(speaker_path, file)
#                     signal = read_audio(audio_path)
#                     emb = clf.encode_batch(signal.unsqueeze(0))
#                     embeddings[audio_path] = (speaker, emb.squeeze().detach())
#     return embeddings

# def compare_embeddings_batch(embeddings):
#     """Compare all embeddings in batch mode"""
#     files = list(embeddings.keys())
#     for i in range(len(files)):
#         for j in range(i + 1, len(files)):
#             spk1, emb1 = embeddings[files[i]]
#             spk2, emb2 = embeddings[files[j]]
#             sim = cosine_similarity(emb1, emb2, dim=0).item()
#             print(f"{os.path.basename(files[i])} vs {os.path.basename(files[j])} → Similarity: {sim:.2f} | Match: {spk1 == spk2}")


import os
import torch
from speechbrain.inference import EncoderClassifier
from speechbrain.dataio.dataio import read_audio
from torch.nn.functional import cosine_similarity

DATA_DIR = "backend/static/audio"

# Global classifier instance
classifier = None

def get_classifier():
    """Get or create the classifier instance."""
    global classifier
    if classifier is None:
        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="backend/pretrained/ecapa"
        )
    return classifier

def get_speaker_embedding(file_path: str) -> torch.Tensor | None:
    """
    Extracts speaker embedding from an audio file.
    Args:
        file_path (str): Path to audio file
    Returns:
        torch.Tensor | None: Speaker embedding tensor or None if error
    """
    try:
        clf = get_classifier()
        signal = read_audio(file_path)
        emb = clf.encode_batch(signal.unsqueeze(0))
        return emb.squeeze().detach()
    except Exception as e:
        print(f"[ERROR] Failed to process audio {file_path}: {e}")
        return None

def compare_embeddings(emb1: torch.Tensor, emb2: torch.Tensor, threshold: float = 0.5) -> tuple[float, bool]:
    """
    Compares two speaker embeddings using cosine similarity.
    Args:
        emb1 (torch.Tensor): First embedding
        emb2 (torch.Tensor): Second embedding
        threshold (float): Similarity threshold to classify same speaker
    Returns:
        tuple: (similarity_score, is_same_speaker)
    """
    try:
        if emb1 is None or emb2 is None:
            return 0.0, False

        sim_score = cosine_similarity(emb1, emb2, dim=0).item()
        return sim_score, sim_score > threshold

    except Exception as e:
        print(f"[ERROR] Embedding comparison failed: {e}")
        return 0.0, False

def get_speaker_embeddings():
    """
    Get embeddings for all speakers in the dataset.
    Returns:
        dict: {audio_path: (speaker, embedding)}
    """
    clf = get_classifier()
    embeddings = {}

    for speaker in os.listdir(DATA_DIR):
        speaker_path = os.path.join(DATA_DIR, speaker)
        if os.path.isdir(speaker_path):
            for file in os.listdir(speaker_path):
                if file.endswith(".wav"):
                    audio_path = os.path.join(speaker_path, file)
                    try:
                        signal = read_audio(audio_path)
                        emb = clf.encode_batch(signal.unsqueeze(0))
                        embeddings[audio_path] = (speaker, emb.squeeze().detach())
                    except Exception as e:
                        print(f"[ERROR] Failed to process {audio_path}: {e}")
    return embeddings

def compare_embeddings_batch(embeddings):
    """
    Compare all embeddings in batch mode.
    Args:
        embeddings (dict): {audio_path: (speaker, embedding)}
    """
    files = list(embeddings.keys())
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            spk1, emb1 = embeddings[files[i]]
            spk2, emb2 = embeddings[files[j]]
            try:
                sim = cosine_similarity(emb1, emb2, dim=0).item()
                print(f"{os.path.basename(files[i])} vs {os.path.basename(files[j])} → Similarity: {sim:.2f} | Match: {spk1 == spk2}")
            except Exception as e:
                print(f"[ERROR] Failed to compare {files[i]} and {files[j]}: {e}")