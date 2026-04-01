import os
import requests
import yt_dlp
from datetime import datetime
from utils.audio_processor import AudioProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForensicScraper:
    def __init__(self, download_dir="static/dataset"):
        self.download_dir = download_dir
        self.audio_processor = AudioProcessor(download_dir)
        os.makedirs(download_dir, exist_ok=True)

    def scrape_pbs(self, search_terms, max_videos=10):
        """
        Scrape PBS videos for voice recordings
        """
        logger.info(f"Starting PBS scraping for terms: {search_terms}")
        
        # PBS YouTube channel IDs
        pbs_channels = [
            "UC3IZvse_dpRiG2E1SPZRW7g",  # PBS NewsHour
            "UC6ZFN9Tx6xh-skXCuRHCDpQ",  # PBS Digital Studios
            "UCYJdpnjuSWVOLgGT9fIzL0g",  # PBS
        ]
        
        downloaded_videos = []
        
        for channel_id in pbs_channels:
            for term in search_terms:
                try:
                    # Search for videos in PBS channels
                    search_url = f"https://www.youtube.com/results?search_query={term}&sp=EgIQAQ%253D%253D"
                    
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.download_dir, f'pbs_{term}_%(id)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'wav',
                        }],
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': True,
                        'playlist_items': f'1-{max_videos}',
                        'channel_url': f'https://www.youtube.com/channel/{channel_id}'
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Get video info
                        info = ydl.extract_info(search_url, download=False)
                        
                        if 'entries' in info:
                            for entry in info['entries']:
                                if entry:
                                    video_id = entry.get('id')
                                    title = entry.get('title', 'Unknown')
                                    upload_date = entry.get('upload_date', '')
                                    url = f"https://www.youtube.com/watch?v={video_id}"
                                    
                                    # Download the video
                                    try:
                                        ydl.download([url])
                                        
                                        # Find the downloaded file
                                        downloaded_file = None
                                        for file in os.listdir(self.download_dir):
                                            if video_id in file and file.endswith('.wav'):
                                                downloaded_file = os.path.join(self.download_dir, file)
                                                break
                                        
                                        if downloaded_file:
                                            # Process the audio
                                            recording_date = datetime.strptime(upload_date, "%Y%m%d").date()
                                            speaker_id = f"pbs_{term}_{video_id}"
                                            
                                            recording = self.audio_processor.process_new_audio(
                                                file_path=downloaded_file,
                                                speaker_id=speaker_id,
                                                recording_date=recording_date,
                                                url=url,
                                                source_platform="PBS"
                                            )
                                            
                                            downloaded_videos.append({
                                                'id': recording.id,
                                                'title': title,
                                                'url': url,
                                                'speaker_id': speaker_id,
                                                'date': recording_date.isoformat()
                                            })
                                            
                                            logger.info(f"Successfully processed PBS video: {title}")
                                            
                                    except Exception as e:
                                        logger.error(f"Error downloading PBS video {video_id}: {str(e)}")
                                        continue
                                        
                except Exception as e:
                    logger.error(f"Error scraping PBS for term '{term}': {str(e)}")
                    continue
        
        return downloaded_videos

    def scrape_voxceleb(self, max_videos=10):
        """
        Scrape VoxCeleb dataset (simulated - in real implementation, you'd download from official sources)
        """
        logger.info("Starting VoxCeleb scraping")
        # VoxCeleb URLs (example - you'd need to implement actual scraping)
        voxceleb_urls = [
            "https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html",
            "https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox2.html"
        ]
        downloaded_videos = []
        # For demonstration, we'll create some sample entries
        # In a real implementation, you'd download from the actual VoxCeleb dataset
        sample_voxceleb_data = [
            {
                'id': 'vox1_00001',
                'title': 'VoxCeleb Sample 1',
                'url': 'https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html',
                'speaker_id': 'voxceleb_speaker_001',
                'date': '2020-01-15'
            },
            {
                'id': 'vox1_00002', 
                'title': 'VoxCeleb Sample 2',
                'url': 'https://www.robots.ox.ac.uk/~vgg/data/voxceleb/vox1.html',
                'speaker_id': 'voxceleb_speaker_002',
                'date': '2020-01-20'
            }
        ]
        for sample in sample_voxceleb_data[:max_videos]:
            try:
                # In real implementation, you'd download the actual audio file
                # For now, just append the sample metadata (no DB entry)
                downloaded_videos.append({
                    'id': sample['id'],
                    'title': sample['title'],
                    'url': sample['url'],
                    'speaker_id': sample['speaker_id'],
                    'date': sample['date']
                })
                logger.info(f"Simulated VoxCeleb sample: {sample['title']}")
            except Exception as e:
                logger.error(f"Error processing VoxCeleb sample {sample['id']}: {str(e)}")
                continue
        return downloaded_videos

    def scrape_youtube_channel(self, channel_url, search_terms=None, max_videos=10):
        """
        Generic YouTube channel scraper
        """
        logger.info(f"Starting YouTube channel scraping: {channel_url}")
        
        downloaded_videos = []
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, 'youtube_%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'quiet': True,
                'no_warnings': True,
                'playlist_items': f'1-{max_videos}'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get channel info
                info = ydl.extract_info(channel_url, download=False)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            video_id = entry.get('id')
                            title = entry.get('title', 'Unknown')
                            upload_date = entry.get('upload_date', '')
                            url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            # Check if video matches search terms
                            if search_terms:
                                title_lower = title.lower()
                                if not any(term.lower() in title_lower for term in search_terms):
                                    continue
                            
                            try:
                                # Download the video
                                ydl.download([url])
                                
                                # Find the downloaded file
                                downloaded_file = None
                                for file in os.listdir(self.download_dir):
                                    if video_id in file and file.endswith('.wav'):
                                        downloaded_file = os.path.join(self.download_dir, file)
                                        break
                                
                                if downloaded_file:
                                    # Process the audio
                                    recording_date = datetime.strptime(upload_date, "%Y%m%d").date()
                                    speaker_id = f"youtube_{video_id}"
                                    
                                    recording = self.audio_processor.process_new_audio(
                                        file_path=downloaded_file,
                                        speaker_id=speaker_id,
                                        recording_date=recording_date,
                                        url=url,
                                        source_platform="YouTube"
                                    )
                                    
                                    downloaded_videos.append({
                                        'id': recording.id,
                                        'title': title,
                                        'url': url,
                                        'speaker_id': speaker_id,
                                        'date': recording_date.isoformat()
                                    })
                                    
                                    logger.info(f"Successfully processed YouTube video: {title}")
                                    
                            except Exception as e:
                                logger.error(f"Error downloading YouTube video {video_id}: {str(e)}")
                                continue
                                
        except Exception as e:
            logger.error(f"Error scraping YouTube channel {channel_url}: {str(e)}")
        
        return downloaded_videos

    def run_full_scraping(self, pbs_terms=None, max_videos_per_source=5):
        """
        Run comprehensive scraping from all sources with robust error handling
        """
        if pbs_terms is None:
            pbs_terms = [
                "interview",
                "speech", 
                "testimony",
                "press conference",
                "debate",
                "news anchor",
                "reporter"
            ]
        logger.info("Starting comprehensive forensic voice scraping")
        all_downloaded = []
        errors = {}
        # Scrape PBS
        try:
            pbs_videos = self.scrape_pbs(pbs_terms, max_videos_per_source)
            all_downloaded.extend(pbs_videos)
        except Exception as e:
            logger.error(f"PBS scraping failed: {str(e)}")
            errors['pbs'] = str(e)
        # Scrape VoxCeleb
        try:
            voxceleb_videos = self.scrape_voxceleb(max_videos_per_source)
            all_downloaded.extend(voxceleb_videos)
        except Exception as e:
            logger.error(f"VoxCeleb scraping failed: {str(e)}")
            errors['voxceleb'] = str(e)
        logger.info(f"Scraping completed. Total videos processed: {len(all_downloaded)}")
        return {
            'videos': all_downloaded,
            'errors': errors,
            'summary': {
                'total_videos': len(all_downloaded),
                'pbs_terms_used': pbs_terms,
                'max_videos_per_source': max_videos_per_source
            }
        } 