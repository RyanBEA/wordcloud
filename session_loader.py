"""
Session loader module for discovering and managing multiple transcript sessions.
"""
import os
from pathlib import Path
from collections import defaultdict

from config import DATA_DIR
from data_processor import SessionData, compute_word_stats, get_word_frequencies, filter_word_stats


def discover_sessions(data_dir: str = None) -> list:
    """
    Auto-discover sessions in the data directory.

    Sessions are identified by folders containing both:
    - *_labeled.json (transcript)
    - speakerlist.csv (speaker metadata)

    Returns list of dicts with session info.
    """
    if data_dir is None:
        data_dir = DATA_DIR

    sessions = []
    data_path = Path(data_dir)

    if not data_path.exists():
        return sessions

    # Check for session folders
    for item in data_path.iterdir():
        if item.is_dir():
            # Look for required files
            json_files = list(item.glob("*_labeled.json"))
            csv_file = item / "speakerlist.csv"

            if json_files and csv_file.exists():
                sessions.append({
                    "name": item.name,
                    "path": str(item),
                    "json_path": str(json_files[0]),
                    "csv_path": str(csv_file),
                })

    return sorted(sessions, key=lambda x: x["name"])


class SessionManager:
    """Manages loading and caching of multiple session data."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or DATA_DIR
        self._sessions = {}  # Cache of loaded SessionData
        self._session_info = []  # List of discovered sessions
        self.refresh()

    def refresh(self):
        """Refresh the list of available sessions."""
        self._session_info = discover_sessions(self.data_dir)
        # Clear cache for sessions that no longer exist
        valid_names = {s["name"] for s in self._session_info}
        self._sessions = {k: v for k, v in self._sessions.items() if k in valid_names}

    def get_session_list(self) -> list:
        """Get list of available session names."""
        return [s["name"] for s in self._session_info]

    def get_session(self, session_name: str) -> SessionData:
        """Get SessionData for a specific session, loading if necessary."""
        if session_name not in self._sessions:
            # Find session info
            info = next((s for s in self._session_info if s["name"] == session_name), None)
            if info is None:
                raise ValueError(f"Session not found: {session_name}")

            # Load session data
            self._sessions[session_name] = SessionData(
                session_name=session_name,
                json_path=info["json_path"],
                csv_path=info["csv_path"]
            )

        return self._sessions[session_name]

    def get_all_sessions(self) -> list:
        """Get all SessionData objects."""
        return [self.get_session(name) for name in self.get_session_list()]

    def get_merged_filter_options(self) -> dict:
        """Get combined filter options from all sessions."""
        merged = defaultdict(set)

        for session in self.get_all_sessions():
            for col, values in session.get_filter_options().items():
                merged[col].update(values)

        return {k: sorted(v) for k, v in merged.items()}

    def get_merged_word_stats(self) -> dict:
        """
        Get word stats merged across all sessions.

        Returns combined statistics for the "All Sessions" view.
        """
        merged_stats = defaultdict(lambda: {
            "total_count": 0,
            "speakers": defaultdict(int),
            "metadata": defaultdict(lambda: defaultdict(int))
        })

        for session in self.get_all_sessions():
            for word, stats in session.word_stats.items():
                merged = merged_stats[word]
                merged["total_count"] += stats["total_count"]

                for speaker, count in stats["speakers"].items():
                    # Prefix speaker with session name to distinguish
                    merged["speakers"][f"{session.session_name}:{speaker}"] += count

                for meta_key, meta_values in stats["metadata"].items():
                    for value, count in meta_values.items():
                        merged["metadata"][meta_key][value] += count

        # Convert to regular dict and add speaker count
        result = {}
        for word, stats in merged_stats.items():
            result[word] = {
                "total_count": stats["total_count"],
                "speaker_count": len(stats["speakers"]),
                "speakers": dict(stats["speakers"]),
                "metadata": {k: dict(v) for k, v in stats["metadata"].items()}
            }

        return result

    def get_merged_speakers(self) -> dict:
        """Get all speakers from all sessions with prefixed names."""
        merged = {}
        for session in self.get_all_sessions():
            for name, meta in session.speakers.items():
                prefixed_name = f"{session.session_name}:{name}"
                merged[prefixed_name] = {**meta, "session": session.session_name}
        return merged

    def get_merged_frequencies(self, filters: dict = None, top_n: int = 100) -> dict:
        """Get word frequencies merged across all sessions with optional filtering."""
        merged_stats = self.get_merged_word_stats()

        if filters:
            merged_speakers = self.get_merged_speakers()
            merged_stats = filter_word_stats(merged_stats, merged_speakers, filters)

        return get_word_frequencies(merged_stats, top_n)

    def get_merged_word_details(self, word: str, filters: dict = None) -> dict:
        """Get detailed stats for a word across all sessions."""
        merged_stats = self.get_merged_word_stats()

        if filters:
            merged_speakers = self.get_merged_speakers()
            merged_stats = filter_word_stats(merged_stats, merged_speakers, filters)

        return merged_stats.get(word.lower(), {
            "total_count": 0,
            "speaker_count": 0,
            "speakers": {},
            "metadata": {}
        })
