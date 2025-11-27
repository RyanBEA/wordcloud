"""
Word cloud image generation module.
"""
import io
import base64
from wordcloud import WordCloud

from config import WORDCLOUD_CONFIG


def generate_wordcloud_image(word_frequencies: dict, config: dict = None) -> str:
    """
    Generate a word cloud image from word frequencies.

    Args:
        word_frequencies: Dict of {word: count}
        config: Optional config overrides

    Returns:
        Base64 encoded PNG image string for use in HTML img src
    """
    if not word_frequencies:
        # Return empty/placeholder image
        return generate_empty_cloud()

    # Merge default config with overrides
    cfg = {**WORDCLOUD_CONFIG, **(config or {})}

    # Create word cloud
    wc = WordCloud(
        width=cfg["width"],
        height=cfg["height"],
        background_color=cfg["background_color"],
        max_words=cfg["max_words"],
        min_font_size=cfg["min_font_size"],
        max_font_size=cfg["max_font_size"],
        colormap=cfg["colormap"],
        prefer_horizontal=0.7,
        relative_scaling=0.5,
    )

    wc.generate_from_frequencies(word_frequencies)

    # Convert to base64 PNG
    img_buffer = io.BytesIO()
    wc.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"


def generate_empty_cloud() -> str:
    """Generate an empty/placeholder word cloud."""
    wc = WordCloud(
        width=WORDCLOUD_CONFIG["width"],
        height=WORDCLOUD_CONFIG["height"],
        background_color=WORDCLOUD_CONFIG["background_color"],
    )

    # Create with placeholder text
    wc.generate("No data available")

    img_buffer = io.BytesIO()
    wc.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"


def get_wordcloud_dimensions() -> tuple:
    """Return configured width and height for layout purposes."""
    return WORDCLOUD_CONFIG["width"], WORDCLOUD_CONFIG["height"]
