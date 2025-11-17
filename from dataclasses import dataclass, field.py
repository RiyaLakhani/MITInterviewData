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
logger = logging.getLogger(__name__)

