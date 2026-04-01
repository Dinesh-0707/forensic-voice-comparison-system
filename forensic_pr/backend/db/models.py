from db.database import db
from datetime import datetime

class AudioClip(db.Model):
    __tablename__ = "audio_clips"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    speaker_id = db.Column(db.String(100), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    emotion = db.Column(db.String(50), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AudioClip id={self.id} speaker={self.speaker_id} emotion={self.emotion}>"

class Recording(db.Model):
    __tablename__ = "recordings"

    id = db.Column(db.Integer, primary_key=True)
    speaker_id = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    emotion = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    embedding_path = db.Column(db.String(500), nullable=True)
    source_platform = db.Column(db.String(50), nullable=True)  # PBS, VoxCeleb, etc.
    duration = db.Column(db.Float, nullable=True)
    sample_rate = db.Column(db.Integer, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Recording id={self.id} speaker={self.speaker_id} date={self.date} emotion={self.emotion}>"

class ComparisonResult(db.Model):
    __tablename__ = "comparison_results"

    id = db.Column(db.Integer, primary_key=True)
    recording1_id = db.Column(db.Integer, db.ForeignKey('recordings.id'), nullable=False)
    recording2_id = db.Column(db.Integer, db.ForeignKey('recordings.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    time_gap_days = db.Column(db.Integer, nullable=False)
    comparison_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ComparisonResult id={self.id} score={self.similarity_score} gap={self.time_gap_days}>"
