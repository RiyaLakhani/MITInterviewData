import re
import pandas as pd
from pdfplumber import open as pdf_open

rows = []

with pdf_open("/Users/mharris/Downloads/prompt 5 scale.pdf") as pdf:
    text = ""

    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

# split into participant blocks
blocks = re.split(r'(?=P\d+,)', text)

for block in blocks:

    # participant
    participant_match = re.search(r'(P\d+)', block)

    # condition
    condition_match = re.search(
        r'(non_gendered|gendered),(none|male|female)',
        block
    )

    # score extraction
    score_match = re.search(
        r'(?:score(?: of)?\:?\s*)(\d+(?:\.\d+)?)',
        block,
        re.IGNORECASE
    )

    # fallback for patterns like "4:"
    if not score_match:
        score_match = re.search(r'^\s*(\d+(?:\.\d+)?)\s*:', block)

    if participant_match and condition_match and score_match:

        participant = participant_match.group(1)
        prompt_type = condition_match.group(1)
        gender = condition_match.group(2)
        score = float(score_match.group(1))

        rows.append({
            "participant": participant,
            "prompt_type": prompt_type,
            "gender": gender,
            "score": score
        })

df = pd.DataFrame(rows)

# create combined condition
df["condition"] = (
    df["prompt_type"] + "_" + df["gender"]
)

# averages
avg_scores = (
    df.groupby("condition")["score"]
      .mean()
      .reset_index()
)

print(avg_scores)