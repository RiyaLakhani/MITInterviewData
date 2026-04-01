from typing import Dict, Any
from clean_data import Participant


def average_list(values):
    """
    Returns the average of a list of numbers.
    If list is empty or None, returns None.
    """
    if not values:
        return None
    return sum(values) / len(values)


def simplify_facial(facial_data: Dict[str, list]) -> Dict[str, float]:
    """
    Turns:
        {"smile": [0.1,0.2], "browRaise": [0.3,0.4]}
    into:
        {"smile": 0.15, "browRaise": 0.35}
    """
    simplified = {}

    if not facial_data:
        return simplified

    for feature, values in facial_data.items():
        avg = average_list(values)
        if avg is not None:
            simplified[feature] = round(avg, 3)

    return simplified


def get_first_sentences(text: str, num_sentences: int = 3) -> str:
    """
    Gets the first few sentences of a transcript.
    Splits simply on periods. You can improve later if needed.
    """
    if not text:
        return ""

    parts = text.split(".")
    parts = [p.strip() for p in parts if p.strip()]

    first_parts = parts[:num_sentences]

    if not first_parts:
        return ""

    return ". ".join(first_parts) + "."


def simplify_participant(participant: Participant, num_sentences: int = 3) -> Dict[str, Any]:
    """
    Convert one Participant object into a smaller dictionary
    that is easier to pass to an LLM.
    """
    simplified = {
        "participant_id": participant.participant_id,
        "facial_data": simplify_facial(participant.facial_data) if participant.facial_data else {},
        "smile_data": round(participant.smile_data, 3) if participant.smile_data is not None else None,
        "interview_transcript": get_first_sentences(participant.interview_transcript, num_sentences),
    }

    return simplified


def participant_to_llm_text(participant: Participant, num_sentences: int = 3) -> str:
    """
    Convert a Participant into a clean text block for prompting.
    """
    simplified = simplify_participant(participant, num_sentences)

    lines = []
    lines.append(f"Participant ID: {simplified['participant_id']}")
    lines.append("")

    if simplified["facial_data"]:
        lines.append("Facial Features:")
        for feature, value in simplified["facial_data"].items():
            lines.append(f"{feature}: {value}")
        lines.append("")

    if simplified["smile_data"] is not None:
        lines.append(f"Smile Score: {simplified['smile_data']}")
        lines.append("")

    if simplified["interview_transcript"]:
        lines.append("Transcript Excerpt:")
        lines.append(simplified["interview_transcript"])

    return "\n".join(lines)