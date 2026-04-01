import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from db.models import Recording
from db.database import db

OUTPUT_CSV = "../metadata/master_metadata.csv"
OUTPUT_JSON = "../metadata/master_metadata.json"

def export_metadata():
    # Query all recordings
    recordings = Recording.query.all()
    data = []
    for rec in recordings:
        data.append({
            'id': rec.id,
            'speaker_id': rec.speaker_id,
            'file_path': rec.file_path,
            'recording_date': rec.date.isoformat() if rec.date else '',
            'event': getattr(rec, 'event', ''),
            'emotion': rec.emotion,
            'source_platform': rec.source_platform,
            'duration': rec.duration,
            'sample_rate': rec.sample_rate,
            'url': rec.url
        })
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    df.to_json(OUTPUT_JSON, orient='records', lines=True)
    print(f"Exported {len(df)} recordings to {OUTPUT_CSV} and {OUTPUT_JSON}")

if __name__ == "__main__":
    export_metadata()











