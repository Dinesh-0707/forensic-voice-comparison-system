import os
import numpy as np
import librosa
from datetime import datetime, date
from db.models import Recording, ComparisonResult
from db.database import db
from models.ecapa_embedding import get_speaker_embedding, compare_embeddings
from models.emotion_model import predict_emotion
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, static_dir="static/dataset"):
        self.static_dir = static_dir
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(f"{static_dir}/embeddings", exist_ok=True)

    def process_new_audio(self, file_path, speaker_id, recording_date, url, source_platform="unknown"):
        """
        Process a new audio file: extract embeddings, detect emotion, and save metadata
        """
        try:
            # Get audio properties
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Extract speaker embedding
            logger.info(f"Extracting embedding for {file_path}")
            embedding = get_speaker_embedding(file_path)
            
            # Save embedding
            embedding_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_embedding.npy"
            embedding_path = os.path.join(self.static_dir, "embeddings", embedding_filename)
            np.save(embedding_path, embedding)
            
            # Detect emotion
            logger.info(f"Detecting emotion for {file_path}")
            emotion = predict_emotion(file_path)
            
            # Convert date string to date object if needed
            if isinstance(recording_date, str):
                recording_date = datetime.strptime(recording_date, "%Y-%m-%d").date()
            
            # Save to database
            recording = Recording(
                speaker_id=speaker_id,
                date=recording_date,
                url=url,
                emotion=emotion,
                file_path=file_path,
                embedding_path=embedding_path,
                source_platform=source_platform,
                duration=duration,
                sample_rate=sr
            )
            
            db.session.add(recording)
            db.session.commit()
            
            logger.info(f"Successfully processed {file_path} for speaker {speaker_id}")
            return recording
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            db.session.rollback()
            raise

    def compare_recordings(self, recording1_id, recording2_id):
        """
        Compare two recordings and return similarity score with time gap analysis
        """
        try:
            recording1 = Recording.query.get(recording1_id)
            recording2 = Recording.query.get(recording2_id)
            
            if not recording1 or not recording2:
                raise ValueError("One or both recordings not found")
            
            # Load embeddings
            embedding1 = np.load(recording1.embedding_path)
            embedding2 = np.load(recording2.embedding_path)
            
            # Calculate similarity
            similarity_score = compare_embeddings(embedding1, embedding2)
            
            # Calculate time gap
            time_gap_days = abs((recording1.date - recording2.date).days)
            
            # Save comparison result
            comparison = ComparisonResult(
                recording1_id=recording1_id,
                recording2_id=recording2_id,
                similarity_score=float(similarity_score),
                time_gap_days=time_gap_days
            )
            
            db.session.add(comparison)
            db.session.commit()
            
            return {
                'similarity_score': float(similarity_score),
                'time_gap_days': time_gap_days,
                'recording1': {
                    'id': recording1.id,
                    'speaker_id': recording1.speaker_id,
                    'date': recording1.date.isoformat(),
                    'emotion': recording1.emotion,
                    'source_platform': recording1.source_platform
                },
                'recording2': {
                    'id': recording2.id,
                    'speaker_id': recording2.speaker_id,
                    'date': recording2.date.isoformat(),
                    'emotion': recording2.emotion,
                    'source_platform': recording2.source_platform
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing recordings: {str(e)}")
            db.session.rollback()
            raise

    def get_recordings_by_filter(self, speaker_id=None, emotion=None, source_platform=None, date_from=None, date_to=None):
        """
        Get recordings with various filters
        """
        query = Recording.query
        
        if speaker_id:
            query = query.filter(Recording.speaker_id == speaker_id)
        if emotion:
            query = query.filter(Recording.emotion == emotion)
        if source_platform:
            query = query.filter(Recording.source_platform == source_platform)
        if date_from:
            query = query.filter(Recording.date >= date_from)
        if date_to:
            query = query.filter(Recording.date <= date_to)
            
        return query.order_by(Recording.date.desc()).all()

    def get_time_gap_analysis(self, speaker_id=None):
        """
        Analyze how time gaps affect similarity scores
        """
        query = ComparisonResult.query
        
        if speaker_id:
            # Join with recordings to filter by speaker
            query = query.join(Recording, ComparisonResult.recording1_id == Recording.id)
            query = query.filter(Recording.speaker_id == speaker_id)
        
        comparisons = query.all()
        
        # Group by time gap ranges
        gap_ranges = {
            '0-30_days': {'count': 0, 'avg_similarity': 0, 'scores': []},
            '31-90_days': {'count': 0, 'avg_similarity': 0, 'scores': []},
            '91-365_days': {'count': 0, 'avg_similarity': 0, 'scores': []},
            '365+_days': {'count': 0, 'avg_similarity': 0, 'scores': []}
        }
        
        for comp in comparisons:
            if comp.time_gap_days <= 30:
                gap_ranges['0-30_days']['scores'].append(comp.similarity_score)
            elif comp.time_gap_days <= 90:
                gap_ranges['31-90_days']['scores'].append(comp.similarity_score)
            elif comp.time_gap_days <= 365:
                gap_ranges['91-365_days']['scores'].append(comp.similarity_score)
            else:
                gap_ranges['365+_days']['scores'].append(comp.similarity_score)
        
        # Calculate averages
        for range_name, data in gap_ranges.items():
            if data['scores']:
                data['count'] = len(data['scores'])
                data['avg_similarity'] = np.mean(data['scores'])
                data['std_similarity'] = np.std(data['scores'])
            del data['scores']  # Remove raw scores for JSON serialization
        
        return gap_ranges 