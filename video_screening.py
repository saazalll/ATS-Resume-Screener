import os
import tempfile
from typing import Dict

import speech_recognition as sr

from text_cleaner import clean_text
from skill_gap import get_skill_match_details
from svm_model import ATSMatcher

try:
    from moviepy.editor import VideoFileClip
except ModuleNotFoundError:
    from moviepy import VideoFileClip


def transcribe_video_to_text(video_bytes: bytes, suffix: str = ".mp4") -> str:
    """
    Extract audio from video and transcribe speech using Google Web Speech API
    through SpeechRecognition.

    Note: internet is required at runtime for online transcription.
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

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)

        try:
            transcript = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            transcript = ""
        except sr.RequestError:
            transcript = ""

        return transcript
    finally:
        for path in (video_path, temp_audio_path):
            if os.path.exists(path):
                os.remove(path)


def screen_video_resume(video_bytes: bytes, job_description: str, video_name: str = "resume.mp4") -> Dict:
    transcript = transcribe_video_to_text(video_bytes, suffix=os.path.splitext(video_name)[1] or ".mp4")
    clean_transcript = clean_text(transcript)
    clean_jd = clean_text(job_description)

    matcher = ATSMatcher()
    matcher.fit(clean_jd)

    prediction = matcher.predict_match(clean_transcript)
    skills = get_skill_match_details(clean_jd, clean_transcript)

    return {
        "transcript": transcript,
        "ats_score": prediction.score_percent,
        "label": prediction.label,
        "matched_skills": skills["matched_skills"],
        "missing_skills": skills["missing_skills"],
    }
