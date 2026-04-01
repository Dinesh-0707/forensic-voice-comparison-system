from pyannote.audio import Pipeline
import os

# Load pretrained diarization model (once)
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

def diarize_audio(file_path):
    """
    Returns speaker segments with time (can be extended to split audio)
    """
    try:
        diarization = diarization_pipeline(file_path)
        results = []

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            results.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })

        return results
    except Exception as e:
        print(f"[ERROR] Diarization failed: {e}")
        return []
