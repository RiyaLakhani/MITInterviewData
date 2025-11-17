from dataclasses import dataclass, field
import unicodedata
import re
import docx
import torch
from torch.utils.data import Dataset
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pickle
import logging
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
    

