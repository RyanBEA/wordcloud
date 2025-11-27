"""
Data processing module for loading transcripts and computing word statistics.
"""
import json
import csv
import re
from collections import defaultdict
from pathlib import Path
import nltk
from nltk.corpus import stopwords

from config import CUSTOM_STOP_WORDS

# Download NLTK stopwords if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def load_speakerlist(csv_path: str) -> dict:
    """
    Load speaker metadata from CSV file.

    Returns dict keyed by speaker name with all metadata fields.
    Also returns list of column headers for dynamic filter generation.
    """
    speakers = {}
    columns = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Handle the arrow separator in the CSV
        content = f.read()
        # Remove the arrow characters if present
        content = re.sub(r'\d+→', '', content)

        lines = content.strip().split('\n')
        if not lines:
            return {}, []

        # Parse header
        header = [col.strip() for col in lines[0].split(',')]
        columns = header[1:]  # Skip 'Speaker' column

        # Parse rows
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue

            speaker_id = parts[0]
            name = parts[1] if len(parts) > 1 else speaker_id

            # Build metadata dict
            metadata = {"speaker_id": speaker_id, "name": name}
            for i, col in enumerate(columns):
                if i + 2 < len(parts):
                    metadata[col.lower()] = parts[i + 2]
                else:
                    metadata[col.lower()] = ""

            # Key by name for easy lookup
            speakers[name] = metadata

    return speakers, columns


def load_transcript(json_path: str) -> list:
    """
    Load transcript from JSON file.

    Returns list of word objects with speaker attribution.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    words = []
    for segment in data.get("segments", []):
        for word_data in segment.get("words", []):
            words.append({
                "word": word_data.get("word", "").lower().strip(),
                "speaker": word_data.get("speaker", "Unknown"),
                "start": word_data.get("start", 0),
                "end": word_data.get("end", 0),
                "score": word_data.get("score", 0),
            })

    return words


def get_stop_words() -> set:
    """Get combined set of NLTK and custom stop words."""
    stop_words = set(stopwords.words('english'))
    stop_words.update(CUSTOM_STOP_WORDS)
    # Add single characters and numbers
    stop_words.update(set('abcdefghijklmnopqrstuvwxyz'))
    stop_words.update(set(str(i) for i in range(100)))
    return stop_words


def clean_word(word: str) -> str:
    """Clean a word by removing punctuation and normalizing."""
    # Remove punctuation from start and end
    word = re.sub(r'^[^\w]+|[^\w]+$', '', word)
    # Convert to lowercase
    word = word.lower().strip()
    return word


def compute_word_stats(words: list, speakers: dict) -> dict:
    """
    Compute statistics for each word.

    Returns dict with word as key and stats including:
    - total_count: Total occurrences
    - speaker_count: Number of unique speakers
    - speakers: Dict of speaker -> count
    - Plus counts for each metadata field (role, region, etc.)
    """
    stop_words = get_stop_words()
    word_stats = defaultdict(lambda: {
        "total_count": 0,
        "speakers": defaultdict(int),
        "metadata": defaultdict(lambda: defaultdict(int))
    })

    for word_data in words:
        word = clean_word(word_data["word"])

        # Skip stop words and empty/short words
        if not word or word in stop_words or len(word) < 2:
            continue

        speaker = word_data["speaker"]
        stats = word_stats[word]

        stats["total_count"] += 1
        stats["speakers"][speaker] += 1

        # Add metadata counts if speaker is in our list
        if speaker in speakers:
            speaker_meta = speakers[speaker]
            for key, value in speaker_meta.items():
                if key not in ["speaker_id", "name"] and value:
                    stats["metadata"][key][value] += 1

    # Convert to regular dict and add derived stats
    result = {}
    for word, stats in word_stats.items():
        result[word] = {
            "total_count": stats["total_count"],
            "speaker_count": len(stats["speakers"]),
            "speakers": dict(stats["speakers"]),
            "metadata": {k: dict(v) for k, v in stats["metadata"].items()}
        }

    return result


def filter_word_stats(word_stats: dict, speakers: dict, filters: dict) -> dict:
    """
    Filter word stats based on selected filters.

    filters: dict of {metadata_field: [selected_values]}
    """
    if not filters or all(not v for v in filters.values()):
        return word_stats

    # Build set of speakers that match filters
    matching_speakers = set()
    for speaker, meta in speakers.items():
        matches = True
        for field, selected in filters.items():
            if selected:  # If filter has selections
                speaker_value = meta.get(field.lower(), "")
                if speaker_value not in selected:
                    matches = False
                    break
        if matches:
            matching_speakers.add(speaker)

    # Filter word stats to only include matching speakers
    filtered = {}
    for word, stats in word_stats.items():
        # Recompute counts for matching speakers only
        new_speakers = {s: c for s, c in stats["speakers"].items() if s in matching_speakers}
        if not new_speakers:
            continue

        new_total = sum(new_speakers.values())

        # Recompute metadata counts
        new_metadata = defaultdict(lambda: defaultdict(int))
        for speaker, count in new_speakers.items():
            if speaker in speakers:
                for key, value in speakers[speaker].items():
                    if key not in ["speaker_id", "name"] and value:
                        new_metadata[key][value] += count

        filtered[word] = {
            "total_count": new_total,
            "speaker_count": len(new_speakers),
            "speakers": new_speakers,
            "metadata": {k: dict(v) for k, v in new_metadata.items()}
        }

    return filtered


def get_word_frequencies(word_stats: dict, top_n: int = 100) -> dict:
    """Get word frequencies suitable for word cloud generation."""
    sorted_words = sorted(
        word_stats.items(),
        key=lambda x: x[1]["total_count"],
        reverse=True
    )[:top_n]

    return {word: stats["total_count"] for word, stats in sorted_words}


class SessionData:
    """Container for a single session's processed data."""

    def __init__(self, session_name: str, json_path: str, csv_path: str):
        self.session_name = session_name
        self.json_path = json_path
        self.csv_path = csv_path

        # Load data
        self.speakers, self.columns = load_speakerlist(csv_path)
        self.words = load_transcript(json_path)
        self.word_stats = compute_word_stats(self.words, self.speakers)

    def get_filter_options(self) -> dict:
        """Get unique values for each filterable column."""
        options = {}
        for col in self.columns:
            col_lower = col.lower()
            if col_lower in ["name", "speaker", "description"]:
                continue
            values = set()
            for speaker_meta in self.speakers.values():
                val = speaker_meta.get(col_lower, "")
                if val:
                    values.add(val)
            if values:
                options[col_lower] = sorted(values)
        return options

    def get_filtered_frequencies(self, filters: dict = None, top_n: int = 100) -> dict:
        """Get word frequencies with optional filtering."""
        if filters:
            filtered_stats = filter_word_stats(self.word_stats, self.speakers, filters)
        else:
            filtered_stats = self.word_stats
        return get_word_frequencies(filtered_stats, top_n)

    def get_word_details(self, word: str, filters: dict = None) -> dict:
        """Get detailed stats for a specific word."""
        if filters:
            stats = filter_word_stats(self.word_stats, self.speakers, filters)
        else:
            stats = self.word_stats

        return stats.get(word.lower(), {
            "total_count": 0,
            "speaker_count": 0,
            "speakers": {},
            "metadata": {}
        })
