"""
Configuration settings for the Word Cloud Dashboard.
Automatically detects Railway production vs local development environment.
"""
import os

# Detect environment
IS_PRODUCTION = os.environ.get("RAILWAY_ENVIRONMENT") is not None

# Data directory paths
if IS_PRODUCTION:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
else:
    # Local development - point to transcribe output folder
    DATA_DIR = r"C:\Users\RyanKelly\OneDrive - Baseline Energy Analytics\opt\transcribe\output"

# Server configuration
DEBUG = not IS_PRODUCTION
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8050))

# Word cloud styling
WORDCLOUD_CONFIG = {
    "width": 800,
    "height": 400,
    "background_color": "white",
    "max_words": 100,
    "min_font_size": 10,
    "max_font_size": 100,
    "colormap": "viridis",
}

# Custom stop words to add beyond NLTK defaults
CUSTOM_STOP_WORDS = {
    # Filler words common in speech
    "yeah", "okay", "ok", "um", "uh", "like", "know", "think",
    "going", "gonna", "got", "just", "really", "actually",
    "thing", "things", "something", "lot", "kind", "sort",
    # Meeting-specific
    "question", "questions", "slide", "slides", "next",
}

# Columns from speakerlist.csv to use as filter options
# These are read dynamically, but we can specify which to prioritize
FILTER_COLUMNS = ["role", "zone", "region"]
