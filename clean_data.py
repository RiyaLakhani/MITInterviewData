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
from typing import List



@dataclass
class question():
    prosodic_data: str
    question_asked: str
    response_data: str

@dataclass
class participant():

    facial_data: int 
    smile_data: str 
    q1 = question
    q2 = question
    q3 = question
    q4 = question
    q5 = question

@dataclass
class CleanSmileData:
    filename: Path

    def aggregate_average(self) -> float:
        total = 0.0
        count = 0

        with self.filename.open("r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()

                try:
                    value = float(parts[0])
                except (ValueError, IndexError):
                    continue

                total += value
                count += 1

        if count == 0:
            raise ValueError(f"No numeric data found in first column of {self.filename}")

        return total / count



def iter_data_files(data_dir: Path):
    """Yield all data files to process from a directory."""

    yield from sorted(data_dir.glob("*.txt"))            


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help="Directory with SmileData .txt files")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()

    file_tokens = []   # <-- one average token per file

    for filepath in iter_data_files(data_dir):
        cleaner = CleanSmileData(filepath)

        avg = cleaner.aggregate_average()
        print(f"{filepath.name}: average first-column token = {avg}")

        # TOKEN = the average
        file_tokens.append(avg)

    print("\nFinal tokens (one per file):")
    print(file_tokens)




if __name__ == "__main__":
    main()