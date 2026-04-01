from flask import Blueprint, jsonify, request
from db.models import AudioClip
from utils.filters import filter_clips
from utils.forensic_scraper import ForensicScraper
import logging

metadata_bp = Blueprint("metadata", __name__)
logger = logging.getLogger(__name__)

@metadata_bp.route("/clips", methods=["GET"])
def get_all_clips():
    clips = AudioClip.query.all()
    results = [
        {
            "id": clip.id,
            "filename": clip.filename,
            "speaker_id": clip.speaker_id,
            "date": clip.date,
            "emotion": clip.emotion
        }
        for clip in clips
    ]
    return jsonify(results)


@metadata_bp.route("/filters", methods=["GET"])
def get_filtered_clips():
    speaker_id = request.args.get("speaker_id")
    emotion = request.args.get("emotion")
    date = request.args.get("date")

    clips = AudioClip.query.all()
    filtered = filter_clips(clips, speaker_id, emotion, date)

    results = [
        {
            "id": clip.id,
            "filename": clip.filename,
            "speaker_id": clip.speaker_id,
            "date": clip.date,
            "emotion": clip.emotion
        }
        for clip in filtered
    ]
    return jsonify(results)

@metadata_bp.route("/scrape/pbs", methods=["POST"])
def scrape_pbs():
    """Scrape PBS for forensic voice recordings"""
    try:
        data = request.get_json() or {}
        search_terms = data.get('search_terms', [
            "interview", "speech", "testimony", "press conference", 
            "debate", "news anchor", "reporter"
        ])
        max_videos = data.get('max_videos', 5)
        
        scraper = ForensicScraper()
        results = scraper.scrape_pbs(search_terms, max_videos)
        
        return jsonify({
            "message": f"Successfully scraped {len(results)} PBS videos",
            "videos": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping PBS: {str(e)}")
        return jsonify({"error": f"Error scraping PBS: {str(e)}"}), 500

@metadata_bp.route("/scrape/voxceleb", methods=["POST"])
def scrape_voxceleb():
    """Scrape VoxCeleb dataset"""
    try:
        data = request.get_json() or {}
        max_videos = data.get('max_videos', 5)
        
        scraper = ForensicScraper()
        results = scraper.scrape_voxceleb(max_videos)
        
        return jsonify({
            "message": f"Successfully scraped {len(results)} VoxCeleb samples",
            "videos": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping VoxCeleb: {str(e)}")
        return jsonify({"error": f"Error scraping VoxCeleb: {str(e)}"}), 500

@metadata_bp.route("/scrape/youtube", methods=["POST"])
def scrape_youtube():
    """Scrape YouTube channel for forensic voice recordings"""
    try:
        data = request.get_json()
        channel_url = data.get('channel_url')
        search_terms = data.get('search_terms', [])
        max_videos = data.get('max_videos', 5)
        
        if not channel_url:
            return jsonify({"error": "channel_url is required"}), 400
        
        scraper = ForensicScraper()
        results = scraper.scrape_youtube_channel(channel_url, search_terms, max_videos)
        
        return jsonify({
            "message": f"Successfully scraped {len(results)} YouTube videos",
            "videos": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping YouTube: {str(e)}")
        return jsonify({"error": f"Error scraping YouTube: {str(e)}"}), 500

@metadata_bp.route("/scrape/full", methods=["POST"])
def run_full_scraping():
    """Run comprehensive scraping from all sources"""
    try:
        data = request.get_json() or {}
        pbs_terms = data.get('pbs_terms', [
            "interview", "speech", "testimony", "press conference", 
            "debate", "news anchor", "reporter"
        ])
        max_videos_per_source = data.get('max_videos_per_source', 3)
        
        scraper = ForensicScraper()
        results = scraper.run_full_scraping(pbs_terms, max_videos_per_source)
        
        return jsonify({
            "message": f"Successfully scraped {len(results)} total videos",
            "videos": results,
            "summary": {
                "total_videos": len(results),
                "pbs_terms_used": pbs_terms,
                "max_videos_per_source": max_videos_per_source
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in full scraping: {str(e)}")
        return jsonify({"error": f"Error in full scraping: {str(e)}"}), 500

@metadata_bp.route("/export", methods=["GET"])
def export_metadata():
    """Export all audio clip metadata as CSV and JSON"""
    import pandas as pd
    import os
    clips = AudioClip.query.all()
    data = [
        {
            "id": clip.id,
            "filename": clip.filename,
            "speaker_id": clip.speaker_id,
            "date": str(clip.date),
            "emotion": clip.emotion,
            "event": getattr(clip, "event", ""),
            "file_path": getattr(clip, "file_path", ""),
        }
        for clip in clips
    ]
    df = pd.DataFrame(data)
    os.makedirs("../metadata", exist_ok=True)
    csv_path = "../metadata/exported_clips.csv"
    json_path = "../metadata/exported_clips.json"
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", lines=True)
    return jsonify({"csv": csv_path, "json": json_path, "count": len(df)})
