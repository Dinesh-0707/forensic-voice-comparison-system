# Longitudinal Forensic Voice Comparison System

## Overview
A research-oriented system to collect, organize, and analyze multiple audio samples of the same speaker over time, enabling forensic voice comparison and longitudinal studies of voice change.

## Features
- Scrape and trim audio from YouTube, C-SPAN, PBS, and VoxCeleb
- Generate and store rich metadata (speaker, date, event, emotion, etc.)
- Store metadata and file paths in a database (PostgreSQL or MongoDB)
- Backend API for querying/filtering/exporting audio clips
- Frontend UI for searching, filtering, and previewing audio
- Embedding engine for speaker similarity (ECAPA-TDNN)
- (Optional) Automatic emotion tagging

## Directory Structure
```
forensic_pr/
│
├── scripts/
│   ├── audio_scraper.py
│   ├── audio_trimmer.py
│   ├── metadata_generator.py
│   └── embedding_engine.py
│
├── backend/
│   ├── app.py
│   ├── models.py
│   └── db.py
│
├── frontend/
│   ├── src/
│   └── ...
│
├── data/
│   └── {speaker_id}/
│         └── {video_id}_{start}_{end}.wav
│
├── metadata/
│   └── master_metadata.csv
│
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Python Environment
- Install Python 3.8+
- `pip install -r requirements.txt`

### 2. Database
- Install PostgreSQL or MongoDB
- Configure connection in `backend/db.py`

### 3. Frontend
- Install Node.js
- `cd frontend && npm install && npm start`

### 4. Audio Tools
- Install `ffmpeg` (required for audio processing)

## Usage
- Use `scripts/audio_scraper.py` to download and trim audio
- Use `scripts/metadata_generator.py` to build metadata CSV/DB
- Start backend API: `python backend/app.py`
- Start frontend: `cd frontend && npm start`

## Research Use Cases
- Longitudinal speaker verification
- Voice aging analysis
- Forensic voice comparison

## Citation
If you use this system in research, please cite appropriately. 