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
from dataclasses import dataclass, field




@dataclass
class Participant:
    participant_id: str
 
    # optional “extra” fields
    facial_data: Optional[int] = None

    prosodic_data: Dict[str, List[float]] = field(default_factory=dict)

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



import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class CleanProsodicData:
    csv_path: Path

    def __post_init__(self) -> None:
        self.csv_path = Path(self.csv_path).expanduser().resolve()

    def load_participants(self) -> Dict[str, Participant]:
        participants: Dict[str, Participant] = {}

        with self.csv_path.open(newline="") as f:
            reader = csv.reader(f)
            first_row = next(reader)
            if first_row and first_row[0] != "/participant&question":
                data_rows = [first_row] + list(reader)
            else:
                data_rows = list(reader)

        for row in data_rows:
            if not row or not row[0].strip():
                continue

            label = row[NAME_TO_IDX["/participant&question"]]  # e.g. "P1Q1"
            participant_id = self._participant_from_label(label)

            if participant_id not in participants:
                participants[participant_id] = Participant(participant_id=participant_id)
            participant = participants[participant_id]

            feats = self._parse_prosodic_row_from_list(row)

            # Initialize per-feature lists once
            if not participant.prosodic_data:
                participant.prosodic_data = {feat: [] for feat in SELECTED_COLUMNS}

            # Append this question’s values
            for feat, value in feats.items():
                participant.prosodic_data[feat].append(value)

        return participants
    # -------- helpers --------

    @staticmethod
    def _participant_from_label(pq_label: str) -> str:
        """
        'P1Q1' -> 'P1'
        'PP3Q5' -> 'PP3'
        """
        pq_label = pq_label.strip()
        q_index = pq_label.index("Q")
        return pq_label[:q_index]

    def _parse_prosodic_row_from_list(self, row: list[str]) -> Dict[str, float]:
        features: Dict[str, float] = {}
        for name in SELECTED_COLUMNS:
            idx = NAME_TO_IDX[name]
            val_str = row[idx] if idx < len(row) else ""
            features[name] = float(val_str) if val_str != "" else 0.0
        return features

    @staticmethod
    def _mean(xs: List[float]) -> float:
        if not xs:
            return 0.0
        return sum(xs) / len(xs)

    @staticmethod
    def _std(xs: List[float]) -> float:
        """
        Population std dev (divide by N). If you want sample std dev, divide by (N-1).
        """
        n = len(xs)
        if n == 0:
            return 0.0
        if n == 1:
            return 0.0
        mu = sum(xs) / n
        var = sum((x - mu) ** 2 for x in xs) / n
        return math.sqrt(var)

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

    participants = CleanProsodicData("/Users/riyalakhani/Downloads/MIT_INTERVIEW_DATASET/Prosody/prosodic_features.csv").load_participants()
    pid = "P1"
    p = participants.get(pid)

    if p:
        print(f"\nParticipant {pid}")
        for feature, values in p.prosodic_data.items():
            print(f"{feature}: {values}")


