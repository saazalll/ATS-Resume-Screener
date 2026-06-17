import os
import tempfile
from typing import Dict

from faster_whisper import WhisperModel

from text_cleaner import clean_text
from skill_gap import get_skill_match_details
from svm_model import ATSMatcher

try:
    from moviepy.editor import VideoFileClip
except ModuleNotFoundError:
    from moviepy import VideoFileClip


def transcribe_video_to_text(video_bytes: bytes, suffix: str = ".mp4") -> str:
    """
    Extract audio from video and transcribe speech using faster-whisper offline.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
        temp_video.write(video_bytes)
        video_path = temp_video.name

    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

    try:
        clip = VideoFileClip(video_path)
        if clip.audio is None:
            return ""
        clip.audio.write_audiofile(temp_audio_path, logger=None)
        clip.close()

        # Offline Whisper transcription (CPU optimized)
        model = WhisperModel('base', device='cpu', compute_type='int8')
        segments, info = model.transcribe(temp_audio_path, beam_size=5)
        
        transcript = " ".join([segment.text for segment in segments])
        return transcript.strip()
    except Exception as e:
        print(f"Faster-whisper error: {e}")
        return ""
    finally:
        for path in (video_path, temp_audio_path):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


def screen_video_resume(video_bytes: bytes, job_description: str, video_name: str = "resume.mp4") -> Dict:
    transcript = transcribe_video_to_text(video_bytes, suffix=os.path.splitext(video_name)[1] or ".mp4")
    
    if not transcript:
        return {
            "transcript": "No speech detected or transcription failed.",
            "ats_score": 0.0,
            "label": "Not Matched",
            "matched_skills": [],
            "missing_skills": [],
        }
        
    clean_transcript = clean_text(transcript)
    clean_jd = clean_text(job_description)

    matcher = ATSMatcher()
    matcher.fit(clean_jd)

    prediction = matcher.predict_match(clean_transcript)
    skills = get_skill_match_details(job_description, transcript)

    # Phase 2 aligned scoring
    hard = skills.get("hard_score", 0.0)
    soft = skills.get("soft_score", 0.0)
    semantic = prediction.semantic_score
    overall_score = round((0.50 * semantic) + (0.35 * hard) + (0.15 * soft), 2)
    label = "Matched" if overall_score >= 50 else "Not Matched"

    return {
        "transcript": transcript,
        "ats_score": overall_score,
        "label": label,
        "matched_skills": skills["matched_skills"],
        "missing_skills": skills["missing_skills"],
    }
