from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
from models.ecapa_embedding import get_speaker_embedding, compare_embeddings
from models.emotion_model import predict_emotion
from db.models import AudioClip, Recording, ComparisonResult
from db.database import db
from utils.audio_processor import AudioProcessor
from datetime import datetime, date

audio_bp = Blueprint("audio", __name__)
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
audio_processor = AudioProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Upload and process audio file (legacy support)
@audio_bp.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Safe file saving
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        # Feature extraction
        embedding = get_speaker_embedding(filepath)
        emotion = predict_emotion(filepath)

        if embedding is None:
            return jsonify({"error": "Speaker embedding failed"}), 500

        # Save metadata to DB
        clip = AudioClip(
            filename=unique_filename,
            speaker_id=request.form.get("speaker_id", "unknown"),
            date=request.form.get("date", ""),
            emotion=emotion
        )
        db.session.add(clip)
        db.session.commit()

        return jsonify({
            "message": "File uploaded successfully",
            "clip_id": clip.id,
            "emotion": emotion
        }), 200

    return jsonify({"error": "Invalid file type"}), 400

# ✅ Compare two audio clips by IDs (legacy support)
@audio_bp.route("/compare", methods=["POST"])
def compare_audio():
    try:
        data = request.get_json()
        clip1_id = data.get("clip1_id")
        clip2_id = data.get("clip2_id")

        if not clip1_id or not clip2_id:
            return jsonify({"error": "Both clip1_id and clip2_id are required"}), 400

        clip1 = AudioClip.query.get(clip1_id)
        clip2 = AudioClip.query.get(clip2_id)

        if not clip1 or not clip2:
            return jsonify({"error": "One or both clips not found"}), 404

        path1 = os.path.join(Config.UPLOAD_FOLDER, clip1.filename)
        path2 = os.path.join(Config.UPLOAD_FOLDER, clip2.filename)

        emb1 = get_speaker_embedding(path1)
        emb2 = get_speaker_embedding(path2)

        if emb1 is None or emb2 is None:
            return jsonify({"error": "Failed to extract embeddings"}), 500

        similarity, is_same = compare_embeddings(emb1, emb2)

        return jsonify({
            "clip1_id": clip1.id,
            "clip2_id": clip2.id,
            "similarity_score": round(similarity, 4),
            "result": "Same Speaker" if is_same else "Different Speaker"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

# 🆕 Forensic Voice Comparison Routes

@audio_bp.route("/recordings", methods=["GET"])
def get_recordings():
    """Get all recordings with optional filters"""
    try:
        speaker_id = request.args.get('speaker_id')
        emotion = request.args.get('emotion')
        source_platform = request.args.get('source_platform')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Convert date strings to date objects
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        recordings = audio_processor.get_recordings_by_filter(
            speaker_id=speaker_id,
            emotion=emotion,
            source_platform=source_platform,
            date_from=date_from,
            date_to=date_to
        )
        
        return jsonify([{
            'id': r.id,
            'speaker_id': r.speaker_id,
            'date': r.date.isoformat(),
            'url': r.url,
            'emotion': r.emotion,
            'source_platform': r.source_platform,
            'duration': r.duration,
            'sample_rate': r.sample_rate,
            'uploaded_at': r.uploaded_at.isoformat()
        } for r in recordings]), 200
        
    except Exception as e:
        return jsonify({"error": f"Error fetching recordings: {str(e)}"}), 500

@audio_bp.route("/recordings", methods=["POST"])
def add_recording():
    """Add a new recording with full processing"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Get form data
        speaker_id = request.form.get("speaker_id")
        recording_date = request.form.get("date")
        url = request.form.get("url", "")
        source_platform = request.form.get("source_platform", "uploaded")

        if not speaker_id or not recording_date:
            return jsonify({"error": "speaker_id and date are required"}), 400

        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        # Process the recording
        recording = audio_processor.process_new_audio(
            file_path=filepath,
            speaker_id=speaker_id,
            recording_date=recording_date,
            url=url,
            source_platform=source_platform
        )

        return jsonify({
            "message": "Recording processed successfully",
            "recording_id": recording.id,
            "emotion": recording.emotion
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error processing recording: {str(e)}"}), 500

# ...existing code...

@audio_bp.route("/recordings/compare", methods=["POST"])
def compare_recordings():
    """Compare two recordings with time gap analysis"""
    try:
        data = request.get_json()
        recording1_id = data.get("recording1_id")
        recording2_id = data.get("recording2_id")

        if not recording1_id or not recording2_id:
            return jsonify({"error": "Both recording1_id and recording2_id are required"}), 400

        result = audio_processor.compare_recordings(recording1_id, recording2_id)
        
        return jsonify(result), 200

    except Exception as e:
        # Improved error reporting for debugging
        import traceback
        tb = traceback.format_exc()
        print("Error in /recordings/compare:", tb)
        # Add a hint for the allow_pickle error
        if "allow_pickle" in str(e):
            return jsonify({
                "error": f"Error comparing recordings: {str(e)}",
                "hint": "Check np.load(..., allow_pickle=True) in your embedding/model loading code."
            }), 500
        return jsonify({"error": f"Error comparing recordings: {str(e)}"}), 500

# ...existing code...
@audio_bp.route("/recordings/analysis", methods=["GET"])
def get_time_gap_analysis():
    """Get time gap analysis for forensic research"""
    try:
        speaker_id = request.args.get('speaker_id')
        analysis = audio_processor.get_time_gap_analysis(speaker_id=speaker_id)
        
        return jsonify({
            "time_gap_analysis": analysis,
            "speaker_id": speaker_id
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error getting analysis: {str(e)}"}), 500

@audio_bp.route("/recordings/<int:recording_id>", methods=["GET"])
def get_recording(recording_id):
    """Get a specific recording by ID"""
    try:
        recording = Recording.query.get(recording_id)
        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        return jsonify({
            'id': recording.id,
            'speaker_id': recording.speaker_id,
            'date': recording.date.isoformat(),
            'url': recording.url,
            'emotion': recording.emotion,
            'source_platform': recording.source_platform,
            'duration': recording.duration,
            'sample_rate': recording.sample_rate,
            'uploaded_at': recording.uploaded_at.isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching recording: {str(e)}"}), 500

@audio_bp.route("/recordings/stats", methods=["GET"])
def get_recording_stats():
    """Get statistics about recordings"""
    try:
        total_recordings = Recording.query.count()
        unique_speakers = db.session.query(Recording.speaker_id.distinct()).count()
        platforms = db.session.query(Recording.source_platform.distinct()).all()
        emotions = db.session.query(Recording.emotion.distinct()).all()
        
        return jsonify({
            "total_recordings": total_recordings,
            "unique_speakers": unique_speakers,
            "platforms": [p[0] for p in platforms if p[0]],
            "emotions": [e[0] for e in emotions if e[0]]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error getting stats: {str(e)}"}), 500

@audio_bp.route("/speakers", methods=["GET"])
def get_speakers():
    speakers = db.session.query(Recording.speaker_id.distinct()).all()
    return jsonify([s[0] for s in speakers if s[0]])

@audio_bp.route("/emotions", methods=["GET"])
def get_emotions():
    emotions = db.session.query(Recording.emotion.distinct()).all()
    return jsonify([e[0] for e in emotions if e[0]])

@audio_bp.route("/events", methods=["GET"])
def get_events():
    events = db.session.query(Recording.event.distinct()).all() if hasattr(Recording, 'event') else []
    return jsonify([ev[0] for ev in events if ev and ev[0]])
