"""
preview_model_input.py

LOCAL-ONLY INPUT PREVIEW
------------------------
This script does NOT:
- read config.json
- import transformers
- load a tokenizer
- load a model
- use CUDA
- call an LLM

It only reproduces the participant-data formatting used by
llm_experiments.py so you can see exactly what participant data
would later be inserted into a model prompt.

PRE and POST smile folders are treated as separate participant records.
"""

from pathlib import Path
import copy
import numpy as np

from clean_data import (
    CleanProsodicData,
    CleanTranscriptData,
    CleanSmileData,
    CleanLexicalData,
    merge_prosodic_and_smile,
)


# ============================================================
# LOCAL FILE PATHS
# ============================================================

PROSODIC_CSV = Path(
    "/Users/riyalakhani/MITInterviewData/prosodic_features.csv"
)

TRANSCRIPT_CSV = Path(
    "/Users/riyalakhani/MITInterviewData/interview_transcripts_by_turkers.csv"
)

LEXICAL_CSV = Path(
    "/Users/riyalakhani/MITInterviewData/interview_WPS.csv"
)

SMILE_PRE_DIR = Path(
    "/Users/riyalakhani/Downloads/MIT_INTERVIEW_DATASET/SmileData/pre"
)

SMILE_POST_DIR = Path(
    "/Users/riyalakhani/Downloads/MIT_INTERVIEW_DATASET/SmileData/post"
)


# Change this to inspect a different participant.
PARTICIPANT_ID = "P21"


# ============================================================
# SAME PROSODIC AGGREGATION AS llm_experiments.py
# ============================================================

def aggregate_prosodic(prosodic_dict):
    aggregated = {}

    for feature, values in prosodic_dict.items():
        aggregated[feature] = (
            float(np.mean(values))
            if values
            else 0.0
        )

    return aggregated


# ============================================================
# SAME FORMATTER AS llm_experiments.py
# ============================================================

def format_participant_for_llm(participant):

    prosodic_means = aggregate_prosodic(
        participant.prosodic_data
    )

    prosodic_text = "\n".join(
        f"{k}: {v}"
        for k, v in prosodic_means.items()
    )

    lexical_text = ""

    if participant.lexical_data:
        lexical_text = "\n".join(
            f"{k}: {v}"
            for k, v in participant.lexical_data.items()
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


# ============================================================
# HELPERS
# ============================================================

def check_paths():
    required = {
        "prosodic CSV": PROSODIC_CSV,
        "transcript CSV": TRANSCRIPT_CSV,
        "lexical CSV": LEXICAL_CSV,
        "SmileData/pre": SMILE_PRE_DIR,
        "SmileData/post": SMILE_POST_DIR,
    }

    missing = []

    for label, path in required.items():
        if not path.exists():
            missing.append((label, path))

    if missing:
        print("\nERROR: These local paths were not found:\n")

        for label, path in missing:
            print(f"{label}:")
            print(f"  {path}")

        print(
            "\nUpdate the path constants at the top of "
            "preview_model_input.py if any filename/location differs."
        )

        return False

    return True


def attach_transcript_and_lexical(
    participants,
    transcripts,
    lexical,
):
    """
    Attach transcript + lexical information exactly as in
    llm_experiments.py.
    """

    for pid, participant in participants.items():

        if pid in transcripts:
            participant.interview_transcript = (
                transcripts[pid].interview_transcript
            )

        if pid in lexical:
            participant.lexical_data = (
                lexical[pid].lexical_data
            )

    return participants


def build_condition_participants(
    prosodic,
    transcripts,
    lexical,
    smile_dir,
):
    """
    Build one independent set of participant objects for a
    single smile condition (PRE or POST).
    """

    smile_tokens = CleanSmileData(
        smile_dir
    ).compute_smile_tokens()

    # Deep-copy the prosodic participant objects so PRE and POST
    # cannot overwrite each other's smile values.
    participants = merge_prosodic_and_smile(
        copy.deepcopy(prosodic),
        smile_tokens,
    )

    return attach_transcript_and_lexical(
        participants,
        transcripts,
        lexical,
    )


def print_participant_input(
    condition_name,
    participant_id,
    participant,
):
    """
    Print the exact participant text produced by the same formatter
    used in llm_experiments.py.
    """

    participant_text = format_participant_for_llm(
        participant
    )

    record_id = f"{participant_id}_{condition_name}"

    print("\n" + "=" * 120)
    print(f"RECORD: {record_id}")
    print("=" * 120)

    print(participant_text)

    print("=" * 120)
    print(
        "END OF EXACT PARTICIPANT DATA THAT WOULD BE "
        "INSERTED INTO THE PROMPT"
    )
    print("=" * 120)

    output_path = (
        Path(__file__).resolve().parent
        / f"{record_id}_model_input.txt"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        f.write(participant_text)

    print(f"\nSaved copy to:\n{output_path}\n")


# ============================================================
# MAIN
# ============================================================

def main():

    if not check_paths():
        return

    print("\nLoading LOCAL participant data only...")
    print("No model or config file will be used.\n")

    # --------------------------------------------------------
    # Load non-smile data once
    # --------------------------------------------------------

    prosodic = CleanProsodicData(
        PROSODIC_CSV
    ).load_participants()

    transcripts = CleanTranscriptData(
        TRANSCRIPT_CSV
    ).load_participants()

    lexical = CleanLexicalData(
        LEXICAL_CSV
    ).load_participants()

    # --------------------------------------------------------
    # Build PRE and POST independently
    # --------------------------------------------------------

    pre_participants = build_condition_participants(
        prosodic=prosodic,
        transcripts=transcripts,
        lexical=lexical,
        smile_dir=SMILE_PRE_DIR,
    )

    post_participants = build_condition_participants(
        prosodic=prosodic,
        transcripts=transcripts,
        lexical=lexical,
        smile_dir=SMILE_POST_DIR,
    )

    # --------------------------------------------------------
    # Make sure requested participant exists
    # --------------------------------------------------------

    found = False

    if PARTICIPANT_ID in pre_participants:
        found = True
        print_participant_input(
            condition_name="pre",
            participant_id=PARTICIPANT_ID,
            participant=pre_participants[PARTICIPANT_ID],
        )
    else:
        print(
            f"\nWARNING: {PARTICIPANT_ID} was not found "
            "in the PRE participant data."
        )

    if PARTICIPANT_ID in post_participants:
        found = True
        print_participant_input(
            condition_name="post",
            participant_id=PARTICIPANT_ID,
            participant=post_participants[PARTICIPANT_ID],
        )
    else:
        print(
            f"\nWARNING: {PARTICIPANT_ID} was not found "
            "in the POST participant data."
        )

    if not found:
        print("\nParticipant was not found in either condition.")

        all_ids = sorted(
            set(pre_participants.keys())
            | set(post_participants.keys())
        )

        print("\nAvailable participant IDs:")
        print(", ".join(all_ids))

    print("\nDone.")
    print(
        "This script did not load or call any model."
    )


if __name__ == "__main__":
    main()
