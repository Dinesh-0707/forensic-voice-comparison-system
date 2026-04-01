import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from utils.audio_processor import AudioProcessor

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_clips.py <recording1_id> <recording2_id>")
        sys.exit(1)
    rec1_id = int(sys.argv[1])
    rec2_id = int(sys.argv[2])
    processor = AudioProcessor(static_dir="../backend/static/dataset")
    result = processor.compare_recordings(rec1_id, rec2_id)
    print(f"Similarity score: {result['similarity_score']:.4f}")
    print(f"Time gap (days): {result['time_gap_days']}")
    print(f"Recording 1: {result['recording1']}")
    print(f"Recording 2: {result['recording2']}")











