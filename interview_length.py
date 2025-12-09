import os
import subprocess
import csv
import numpy as np

# ---------- CONFIG ----------
video_folder = r"C:\Users\madis\Downloads\Videos"  # folder with videos
transcript_file = r"C:\Users\madis\Downloads\Labels\interview_transcripts_by_turkers.csv"
output_file = r"C:\Users\madis\mit_interview_research\interview_WPS.csv"

video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}
FFPROBE_PATH = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"

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

def simple_tokenize(text):
    """Very basic tokenizer: split on whitespace."""
    return text.split()

def count_words(text):
    """Count words for interviewer, interviewee, total using simple tokenizer."""
    segments = text.split("|")
    interviewee_words = 0
    interviewer_words = 0
    for seg in segments:
        seg = seg.strip()
        if seg.startswith("Interviewee:"):
            content = seg.replace("Interviewee:", "").strip()
            interviewee_words += len(simple_tokenize(content))
        elif seg.startswith("Interviewer:"):
            content = seg.replace("Interviewer:", "").strip()
            interviewer_words += len(simple_tokenize(content))
    total_words = interviewee_words + interviewer_words
    return interviewee_words, interviewer_words, total_words

def count_unique_words(text):
    """Return number of unique words (case-insensitive)."""
    words = simple_tokenize(text)
    words = [w.lower() for w in words]   # normalize
    return len(set(words))

# ---------- LOAD VIDEO DURATIONS ----------
video_durations = {}
print("Listing folder:", video_folder)
for file in os.listdir(video_folder):
    if any(file.lower().endswith(ext) for ext in video_extensions):
        full_path = os.path.join(video_folder, file)
        seconds = get_video_duration_seconds(full_path)
        if seconds is not None:
            video_id = os.path.splitext(file)[0]
            video_durations[video_id.lower()] = seconds

print("Loaded video durations for:", list(video_durations.keys()))

# ---------- PROCESS TRANSCRIPTS AND COMPUTE WPS / UWPS ----------
wps_list = []
uwps_list = []
interview_lengths = []

with open(transcript_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", newline="", encoding="utf-8") as f_out:

    reader = csv.reader(f_in)
    writer = csv.writer(f_out)

    writer.writerow([
        "Interview ID",
        "Interviewee Words",
        "Interviewer Words",
        "Total Words",
        "Unique Words",
        "Video Duration (s)",
        "Words per Second",
        "Unique Words per Second"
    ])

    for row in reader:
        if not row or len(row) < 2:
            continue

        interview_id = row[0].strip()
        text = row[1].strip()

        interviewee_words, interviewer_words, total_words = count_words(text)
        interview_lengths.append(total_words)

        # Unique words
        unique_words = count_unique_words(text)

        duration = video_durations.get(interview_id.lower())
        if duration is None:
            print(f"Warning: No video found for {interview_id}, skipping rates")
            wps = ""
            uwps = ""
            duration_val = ""
        else:
            wps = round(total_words / duration, 3)
            uwps = round(unique_words / duration, 3)
            wps_list.append(wps)
            uwps_list.append(uwps)
            duration_val = duration

        writer.writerow([
            interview_id,
            interviewee_words,
            interviewer_words,
            total_words,
            unique_words,
            duration_val,
            wps,
            uwps
        ])

# ---------- PRINT STATS ----------
print("\n===== STATS =====")
print(f"Number of interviews: {len(interview_lengths)}")
print(f"Average interview length (words): {np.mean(interview_lengths):.2f}")
print(f"Std interview length (words): {np.std(interview_lengths):.2f}")
print(f"Max interview length (words): {np.max(interview_lengths)}")
print(f"Min interview length (words): {np.min(interview_lengths)}")

if wps_list:
    print(f"Average WPS: {np.mean(wps_list):.3f}")
    print(f"Std WPS: {np.std(wps_list):.3f}")
    print(f"Max WPS: {np.max(wps_list):.3f}")
    print(f"Min WPS: {np.min(wps_list):.3f}")

if uwps_list:
    print(f"\nAverage Unique WPS: {np.mean(uwps_list):.3f}")
    print(f"Std Unique WPS: {np.std(uwps_list):.3f}")
    print(f"Max Unique WPS: {np.max(uwps_list):.3f}")
    print(f"Min Unique WPS: {np.min(uwps_list):.3f}")

print(f"\nDone! Saved results to {output_file}")
