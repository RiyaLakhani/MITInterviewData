from dataclasses import dataclass
#import unicodedata
#import re
#import docx
#import torch
#from torch.utils.data import Dataset
#from langchain_text_splitters import RecursiveCharacterTextSplitter
#import pickle
#import logging
import numpy as np
from pathlib import Path
import argparse
from typing import List, Dict, Optional
import csv
import sys




@dataclass
class Participant:
    participant_id: str
 
    # optional “extra” fields
    facial_data: Optional[int] = None

    # ONE smile token (average of first column from smile data)
    smile_data: Optional[float] = None

    interview_transcript: Optional[str] = None


COLUMNS = [
    "/participant&question",
    "duration",
    "energy",
    "power",
    "min_pitch",
    "max_pitch",
    "mean_pitch",
    "pitch_sd",
    "pitch_abs",
    "pitch_quant",
    "pitchUvsVRatio",
    "Time:8",
    "iDifference",
    "diffPitchMaxMin",
    "diffPitchMaxMean",
    "diffPitchMaxMode",
    "intensityMin",
    "intensityMax",
    "intensityMean",
    "intensitySD",
    "intensityQuant",
    "diffIntMaxMin",
    "diffIntMaxMean",
    "diffIntMaxMode",
    "avgVal1",
    "avgVal2",
    "avgVal3",
    "avgBand1",
    "avgBand2",
    "avgBand3",
    "fmean1",
    "fmean2",
    "fmean3",
    "f2meanf1",
    "f3meanf1",
    "f1STD",
    "f2STD",
    "f3STD",
    "f2STDf1",
    "f2STDf2",
    "jitter",
    "shimmer",
    "jitterRap",
    "meanPeriod",
    "percentUnvoiced",
    "numVoiceBreaks",
    "PercentBreaks",
    "speakRate",
    "numPause",
    "maxDurPause",
    "avgDurPause",
    "TotDurPause:3",
    "iInterval",
    "MaxRising:3",
    "MaxFalling:3",
    "AvgTotRis:3",
    "AvgTotFall:3",
    "numRising",
    "numFall",
    "loudness",
]

NAME_TO_IDX: Dict[str, int] = {name: i for i, name in enumerate(COLUMNS)}

SELECTED_COLUMNS = [
    "avgBand1",
    "percentUnvoiced",
    "PercentBreaks",
    "avgDurPause",
    "f3meanf1",
    "f1STD",
    "intensityMean",
    "maxDurPause",
    "f2meanf1",
    "f3STD",
]


import re

class CleanSmileData:
    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir).expanduser().resolve()

    def compute_smile_tokens(self) -> Dict[str, float]:
        tokens: Dict[str, float] = {}

        for path in sorted(self.data_dir.glob("*.txt")):
            participant_id = self._participant_from_filename(path.name)
            if participant_id is None:
                # debug helper: uncomment to see any filenames we fail to parse
                # print("Could not extract participant ID from", path.name)
                continue

            avg = self._average_first_column(path)
            tokens[participant_id] = avg

        return tokens

    @staticmethod
    def _participant_from_filename(filename: str) -> Optional[str]:
        
        base = filename.rsplit(".", 1)[0]
        match = re.search(r"P{1,2}\d+", base)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def _average_first_column(path: Path) -> float:
        total = 0.0
        count = 0

        with path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                try:
                    value = float(parts[0])   # ONLY first column
                except (ValueError, IndexError):
                    continue
                total += value
                count += 1

        if count == 0:
            raise ValueError(f"No numeric data in first column for {path}")
        return total / count



def iter_data_files(data_dir: Path):
    """Yield all data files to process from a directory."""

    yield from sorted(data_dir.glob("*.txt"))            

def merge_prosodic_and_smile(
    prosodic_participants: Dict[str, Participant],
    smile_tokens: Dict[str, float],
) -> Dict[str, Participant]:
    """
    Fill Participant.smile_data using smile_tokens, keeping prosodic data.
    """
    participants = dict(prosodic_participants)  # shallow copy

    for pid, token in smile_tokens.items():
        if pid not in participants:
            participants[pid] = Participant(participant_id=pid)
        participants[pid].smile_data = token

    return participants




# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("data_dir", help="Directory with SmileData .txt files")
#     args = parser.parse_args()

#     data_dir = Path(args.data_dir).expanduser().resolve()

#     file_tokens = []   # <-- one average token per file

#     for filepath in iter_data_files(data_dir):
#         cleaner = CleanSmileData(filepath)

#         avg = cleaner.aggregate_average()
#         print(f"{filepath.name}: average first-column token = {avg}")

#         # TOKEN = the average
#         file_tokens.append(avg)

#     print("\nFinal tokens (one per file):")
#     print(file_tokens)



@dataclass
class CleanProsodicData:
    """
    Cleans and parses the prosodic_features.csv file into Participant/Question objects.
    """
    csv_path: Path

    def __post_init__(self) -> None:
        # Allow passing a string path
        self.csv_path = Path(self.csv_path).expanduser().resolve()

    # ---------- public API --------------------------------------------------

    def load_participants(self) -> Dict[str, Participant]:
        """
        Read the CSV and return a dict:
            { participant_id -> Participant }
        Each Participant has q1–q5 filled with Question objects
        containing only the selected prosodic features.
        """
        participants: Dict[str, Participant] = {}

        with self.csv_path.open(newline="") as f:
            reader = csv.reader(f)

            # Read first row and skip if it's the header
            first_row = next(reader)
            if first_row and first_row[0] != "/participant&question":
                # That wasn't a header; treat it as data
                data_rows = [first_row] + list(reader)
            else:
                data_rows = list(reader)

            for row in data_rows:
                if not row or not row[0].strip():
                    continue

                label = row[NAME_TO_IDX["/participant&question"]]  # e.g. "P1Q1"
                participant_id, q_attr = self._parse_participant_and_question(label)

                # Get or create the Participant
                if participant_id not in participants:
                    participants[participant_id] = Participant(participant_id=participant_id)
                participant = participants[participant_id]

                # Extract only the desired prosodic features
                prosodic = self._parse_prosodic_row_from_list(row)
                q_obj = Question(prosodic_data=prosodic)

                # Attach Question object to q1–q5 on Participant
                if not hasattr(participant, q_attr):
                    raise ValueError(f"Unexpected question attr '{q_attr}' from label '{label}'")
                setattr(participant, q_attr, q_obj)

        return participants

    # ---------- internal helpers -------------------------------------------

    @staticmethod
    def _parse_participant_and_question(pq_label: str) -> tuple[str, str]:
        """
        Convert 'P1Q1' or 'PP3Q5' -> ('P1', 'q1'), ('PP3', 'q5'), etc.
        """
        pq_label = pq_label.strip()
        q_index = pq_label.index("Q")   # will raise if 'Q' is missing
        participant_id = pq_label[:q_index]        # 'P1', 'PP3'
        q_num = pq_label[q_index + 1:]            # '1'...'5'
        q_attr = f"q{q_num}"                      # 'q1'...'q5'
        return participant_id, q_attr

    def _parse_prosodic_row_from_list(self, row: list[str]) -> Dict[str, float]:
        """
        Given a row like:
            ['P1Q1', '51.95', '0.0153', ...]
        return ONLY the selected features, using column positions.
        """
        features: Dict[str, float] = {}
        for name in SELECTED_COLUMNS:
            idx = NAME_TO_IDX[name]
            val_str = row[idx] if idx < len(row) else ""
            if val_str == "":
                features[name] = 0.0  # or float("nan") if you prefer
            else:
                features[name] = float(val_str)
        return features



class CleanTranscriptData:
    def __init__(self, transcript_csv_path: str | Path) -> None:
        self.transcript_csv_path = Path(transcript_csv_path).expanduser().resolve()

    def load_participants(self) -> Dict[str, Participant]:
        """
        Transcript CSV format (your example):
          p11,<BIG STRING WITH Interviewer:/Interviewee: and '|' separators>

        Returns:
          { 'P11': Participant(...), 'PP10': Participant(...), ... }
        """
        participants: Dict[str, Participant] = {}

        with self.transcript_csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                # Expect exactly 2 columns (id, transcript)
                if len(row) < 2:
                    continue

                pid = self._normalize_participant_id(row[0])
                if pid is None:
                    # header row or malformed id
                    continue

                transcript = row[1].strip()
                if transcript == "":
                    continue

                participants[pid] = Participant(
                    participant_id=pid,
                    interview_transcript=transcript
                )

        return participants

    @staticmethod
    def _normalize_participant_id(raw: str) -> Optional[str]:
        """
        'p11' -> 'P11'
        'pp11' -> 'PP11'
        Also handles spaces like ' p03 ' -> 'P3'
        """
        s = raw.strip().lower()
        if not s:
            return None

        if s.startswith("pp"):
            num = s[2:]
            return f"PP{int(num)}" if num.isdigit() else None

        if s.startswith("p"):
            num = s[1:]
            return f"P{int(num)}" if num.isdigit() else None

        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python clean_transcripts.py <transcripts.csv>")

    cleaner = CleanTranscriptData(sys.argv[1])
    participants = cleaner.load_participants()

    print("Num participants:", len(participants))

    #example

    p57 = participants.get("P57")
    if p57:
        print("\nP57 transcript preview:")
        print(p57.interview_transcript[:250], "...")



