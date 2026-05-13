"""
MIT Interview Bias Experiment
Participant-Level Aggregated Prosodic Version
NO LangChain – Pure HuggingFace
"""

# ----------------------------------------------------------
# Imports
# ----------------------------------------------------------

import json
import time
import re
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
# import logging
from simplify_data import simplify_participant, participant_to_llm_text
import argparse

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from clean_data import (
    CleanProsodicData,
    CleanTranscriptData,
    CleanSmileData,
    CleanLexicalData,
    merge_prosodic_and_smile,
)
# from memory_profile import Monitor

from prompts import build_prompt_gendered, build_prompt_non_gendered


# ----------------------------------------------------------
# Aggregate prosodic lists → mean per feature
# ----------------------------------------------------------

def aggregate_prosodic(prosodic_dict):
    aggregated = {}
    for feature, values in prosodic_dict.items():
        aggregated[feature] = float(np.mean(values)) if values else 0.0
    return aggregated


# ----------------------------------------------------------
# Format participant for LLM
# ----------------------------------------------------------

def format_participant_for_llm(participant):

    prosodic_means = aggregate_prosodic(participant.prosodic_data)

    prosodic_text = "\n".join(
        f"{k}: {v}" for k, v in prosodic_means.items()
    )
    lexical_text = ""

    if participant.lexical_data:
        lexical_text = "\n".join(
            f"{k}: {v}" for k, v in participant.lexical_data.items()
        )

    return f"""
Full Interview Transcript:
{participant.interview_transcript}

Smile Score:
{participant.smile_data}

Lexical Features:
{lexical_text}

Aggregated Prosodic Features:
{prosodic_text}
"""


# ----------------------------------------------------------
# Extract Likert Score
# ----------------------------------------------------------

def extract_score(text):
    match = re.search(r"Score\s*[:\-]?\s*([1-7])", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


# ----------------------------------------------------------
# Main Experiment
# ----------------------------------------------------------

def main():

    # -----------------------
    # Parse Command Line Args
    # -----------------------

    parser = argparse.ArgumentParser(description="Run MIT Interview Bias Experiment")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the config JSON file"
    )

    args = parser.parse_args()

    config_path = Path(args.config)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")

    print(f"\nUsing config file: {config_path}\n")

    # -----------------------
    # Load Config
    # -----------------------

    with config_path.open("r") as f:
        settings = json.load(f)

    model_id = settings["model_id"]
    model_path = settings["model_path"]

    print(f"\nLoading model: {model_id}")
    print(f"From local path: {model_path}/{model_id}\n")

    # -----------------------
    # Load Local Model
    # -----------------------

    local_model_dir = Path(model_path) / model_id

    print(f"\nLoading model: {model_id}")
    print(f"From local path: {local_model_dir}\n")

    if not local_model_dir.exists():
        raise FileNotFoundError(f"Model path does not exist: {local_model_dir}")

    tokenizer = AutoTokenizer.from_pretrained(
        str(local_model_dir),
        local_files_only=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        str(local_model_dir),
        local_files_only=True,
        device_map="auto",
        dtype="auto"
    )

    print("Model device:", model.device)

    text_pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
        pad_token_id=tokenizer.eos_token_id,
        max_new_tokens=settings["max_new_tokens"],
        do_sample=True,
        temperature=settings["temperature"]
    )

    # -----------------------
    # Load Data
    # -----------------------

    prosodic = CleanProsodicData(settings["prosodic_csv"]).load_participants()
    transcripts = CleanTranscriptData(settings["transcript_csv"]).load_participants()
    smile_tokens = CleanSmileData(settings["smile_dir"]).compute_smile_tokens()
    lexical = CleanLexicalData(settings["lexical_csv"]).load_participants()

    merged = merge_prosodic_and_smile(prosodic, smile_tokens)

    for pid, p in merged.items():
        if pid in transcripts:
            p.interview_transcript = transcripts[pid].interview_transcript
    
    # merge lexical
    for pid, p in merged.items():
        if pid in lexical:
            p.lexical_data = lexical[pid].lexical_data

    #participants = merged
    # ------------------------
    # TESTING: only one participant
    # ------------------------
    participants = merged

    print(f"Participants loaded: {len(participants)}")

    # -----------------------
    # Prepare Output CSV
    # -----------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temperature = settings["temperature"]

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / (
        f"{timestamp}_mit_bias_results_"
        f"{model_id.replace('/', '_')}_"
        f"temp_{temperature}.csv"
    )
    # data_used = "no_transcript"

    columns = [
        "participant_id",
        "condition",
        "assumed_gender",
        "model_id",
        "temperature",
        # "data_used"
        "score",
        "llm_output",
        "runtime_seconds"
    ]

    with output_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)

    # -----------------------
    # Run Experiment
    # -----------------------

    for pid, participant in participants.items():

        if not participant.interview_transcript:
            continue

        participant_text = format_participant_for_llm(participant)
            
        # -------- Gendered --------
        for gender in ["male","female"]:

            prompt = build_prompt_gendered(participant_text, gender)

            start = time.perf_counter()
            result = text_pipe(prompt)[0]["generated_text"]
            end = time.perf_counter()

            output = result.strip()
            score = extract_score(output)

            with output_file.open("a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    pid,
                    "gendered",
                    gender,
                    model_id,
                    settings["temperature"],
                    # data_used,
                    score,
                    output,
                    end - start
                ])

        # -------- Non-Gendered --------
        prompt = build_prompt_non_gendered(participant_text)

        start = time.perf_counter()
        result = text_pipe(prompt)[0]["generated_text"]
        end = time.perf_counter()

        output = result.strip()
        score = extract_score(output)

        with output_file.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                pid,
                "non_gendered",
                "none",
                model_id,
                settings["temperature"],
                # data_used,
                score,
                output,
                end - start
        ])

    print("\nExperiment complete.")
    print(f"Results saved to: {output_file}")

    print("Loading model:", model_id)
# ----------------------------------------------------------
# Run Script
# ----------------------------------------------------------

if __name__ == "__main__":
    # monitor = Monitor(60)
    # start_time = time.perf_counter()

    main()
    # end_time = time.perf_counter()
    # logger.info('Script complete after {:.4f} seconds'.format(end_time-start_time))
    # monitor.stop()