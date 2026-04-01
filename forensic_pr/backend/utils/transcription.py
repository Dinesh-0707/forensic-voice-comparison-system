import whisper

model = whisper.load_model("base")  # You can use 'medium' or 'large' too

def transcribe_audio(file_path):
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return ""
