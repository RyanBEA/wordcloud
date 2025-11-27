# Consultation Session Word Cloud

Interactive word cloud visualization for consultation session transcripts. Built with Dash (Plotly) for professional, client-facing dashboards.

## Features

- **Interactive Word Cloud**: Visualize word frequencies from transcripts
- **Dynamic Filtering**: Filter by speaker role, region, zone, and other metadata
- **Word Statistics**: Click any word to see detailed stats (frequency, speakers, role breakdown)
- **Multi-Session Support**: View individual sessions or merge all sessions together
- **Professional UI**: Bootstrap-styled interface suitable for client presentations

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repo
git clone https://github.com/RyanBEA/wordcloud.git
cd wordcloud

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will be available at http://localhost:8050

### Data Format

Place session data in the `data/` folder with this structure:

```
data/
├── session_name/
│   ├── SessionName_labeled.json  # Transcript with word-level speaker attribution
│   └── speakerlist.csv           # Speaker metadata (name, role, region, etc.)
```

**speakerlist.csv format:**
```csv
Speaker, name, role, description, zone, region
SPEAKER_01, John Doe, energy advisor, Description here, All, Halifax
```

**JSON format:** WhisperX output with speaker-assigned words.

## Production Deployment (Railway)

This app is configured for automatic deployment to Railway:

1. Push to `main` branch
2. Railway auto-detects Python and deploys
3. Gunicorn serves the app via the Procfile

## Configuration

Edit `config.py` to customize:
- Word cloud dimensions and styling
- Custom stop words
- Data directory paths

## License

MIT
