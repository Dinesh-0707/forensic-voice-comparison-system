def filter_clips(clips, speaker_id=None, emotion=None, date=None):
    """
    Filters a list of clip dicts based on speaker ID, emotion, or date
    """
    results = clips

    if speaker_id:
        results = [clip for clip in results if clip.get("speaker_id") == speaker_id]

    if emotion:
        results = [clip for clip in results if clip.get("emotion") == emotion]

    if date:
        results = [clip for clip in results if clip.get("date") == date]

    return results
