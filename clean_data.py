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
class clean_smile_data():
    filename:str = "/Users/riyalakhani/Downloads/MIT_INTERVIEW_DATASET/SmileData/pre/Smoothed-features-P1.txt"

    def aggregate_average(self):
        total = 0.0
        count = 0

    
        with open (self.filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()   # split by ANY whitespace

                try:
                    value = float(parts[0])   # first column

                except (ValueError, IndexError):
                    continue

                total += value
                count += 1

        if count == 0:
            raise ValueError("No numeric data found in first column")

        return total / count

            

def main():
    cleaner = clean_smile_data("/Users/riyalakhani/Downloads/MIT_INTERVIEW_DATASET/SmileData/pre/Smoothed-features-P1.txt")
    avg = cleaner.aggregate_average()
    print("Average of first column:", avg)

if __name__ == "__main__":
    main()


