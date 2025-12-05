import os
import subprocess
import csv

# ---------- CONFIG ----------
video_folder = r"C:\Users\madis\Downloads\Videos"  # your video folder
transcript_file = r"C:\Users\madis\Downloads\Labels\interview_transcripts_by_turkers.csv"
output_file = r"C:\Users\madis\mit_interview_research\interview_WPS.csv"

video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}
FFPROBE_PATH = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"  # full path to ffprobe

# ---------- FUNCTIONS ----------

def get_video_duration_seconds(path):
    """Return video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [FFPROBE_PATH, "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def count_words(text):
    """Count words for interviewer, interviewee, total."""
    segments = text.split("|")
    interviewee_words = 0
    interviewer_words = 0
    for seg in segments:
        seg = seg.strip()
        if seg.startswith("Interviewee:"):
            content = seg.replace("Interviewee:", "").strip()
            interviewee_words += len(content.split())
        elif seg.startswith("Interviewer:"):
            content = seg.replace("Interviewer:", "").strip()
            interviewer_words += len(content.split())
    total_words = interviewee_words + interviewer_words
    return interviewee_words, interviewer_words, total_words

# ---------- LOAD VIDEO DURATIONS ----------
video_durations = {}
print("Listing folder:", video_folder)
for file in os.listdir(video_folder):
    if any(file.lower().endswith(ext) for ext in video_extensions):
        full_path = os.path.join(video_folder, file)
        seconds = get_video_duration_seconds(full_path)
        if seconds is not None:
            video_id = os.path.splitext(file)[0]  # keep original case
            video_durations[video_id.lower()] = seconds



print("Loaded video durations for:", list(video_durations.keys()))

# ---------- PROCESS TRANSCRIPTS AND COMPUTE WPS ----------
with open(transcript_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", newline="", encoding="utf-8") as f_out:

    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    
    # Write header
    writer.writerow([
        "Interview ID",
        "Interviewee Words",
        "Interviewer Words",
        "Total Words",
        "Video Duration (s)",
        "Words per Second"
    ])
    
    for row in reader:
        if not row or len(row) < 2:
            continue  # skip empty or malformed rows

        interview_id = row[0].strip()
        text = row[1].strip()
        
        interviewee_words, interviewer_words, total_words = count_words(text)
        
        duration = video_durations.get(interview_id.lower())
        if duration is None:
            print(f"Warning: No video found for {interview_id}, skipping WPS")
            wps = ""
            duration = ""
        else:
            wps = round(total_words / duration, 3)
        
        writer.writerow([
            interview_id,
            interviewee_words,
            interviewer_words,
            total_words,
            duration,
            wps
        ])


print(f"Done! Saved results to {output_file}")
