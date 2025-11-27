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
    "max_words": 50,
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
    # Facilitation colors (polling paddles - not substantive content)
    "green", "yellow", "red", "greens", "yellows", "reds",
    # Additional filler/conversational words
    "oh", "us", "anything", "feel", "done", "sure", "start",
    "point", "couple", "sense", "last", "end", "else", "folks",
    "session", "four", "half", "looking", "coming", "terms",
    "another", "anyone", "everyone", "talking", "talk", "day",
    "across", "trying", "better", "whether", "saying",
    # Geographic (fragments of "Nova Scotia")
    "nova", "scotia",
    # Contractions (very common in speech, rarely meaningful)
    "there's", "that's", "it's", "don't", "can't", "won't",
    "wouldn't", "couldn't", "shouldn't", "we're", "they're",
    "you're", "i'm", "he's", "she's", "we've", "they've",
    "you've", "i've", "let's", "what's", "who's", "how's",
    "here's", "wasn't", "weren't", "hasn't", "haven't",
    "didn't", "isn't", "aren't", "doesn't",
    # Modal verbs (very common in speech, rarely meaningful)
    "would", "could", "should", "might", "may", "must",
    # Common verbs that don't carry meaning in this context
    "get", "go", "went", "come", "came", "say", "said",
    "see", "saw", "make", "made", "take", "took", "give",
    "gave", "put", "let", "try", "look", "want", "need",
    "tell", "told", "ask", "asked", "use", "used",
    # Common speech fillers and transitions
    "well", "right", "mean", "bit", "way", "even", "still",
    "also", "probably", "maybe", "anyway", "basically",
    "certainly", "definitely", "obviously", "actually",
    "essentially", "guess", "suppose",
    # Time/sequence words
    "now", "then", "today", "time", "already", "yet",
    # Quantifiers and pronouns often not meaningful alone
    "one", "two", "three", "first", "much", "many",
    "little", "big", "good", "great", "back", "around",
    "different", "able", "new", "part", "people",
}

# Columns from speakerlist.csv to use as filter options
# These are read dynamically, but we can specify which to prioritize
FILTER_COLUMNS = ["role", "zone", "region"]
