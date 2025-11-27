"""
Word cloud generation module using Plotly for interactivity.
"""
import plotly.graph_objects as go
from wordcloud import WordCloud
import numpy as np

from config import WORDCLOUD_CONFIG


def generate_wordcloud_figure(word_frequencies: dict, config: dict = None) -> go.Figure:
    """
    Generate an interactive word cloud using Plotly.

    Args:
        word_frequencies: Dict of {word: count}
        config: Optional config overrides

    Returns:
        Plotly Figure object
    """
    if not word_frequencies:
        return generate_empty_figure()

    # Merge default config with overrides
    cfg = {**WORDCLOUD_CONFIG, **(config or {})}

    # Use wordcloud library to compute layout
    wc = WordCloud(
        width=cfg["width"],
        height=cfg["height"],
        background_color=cfg["background_color"],
        max_words=cfg["max_words"],
        min_font_size=cfg["min_font_size"],
        max_font_size=cfg["max_font_size"],
        colormap=cfg["colormap"],
        prefer_horizontal=0.9,
        relative_scaling=0.5,
    )

    wc.generate_from_frequencies(word_frequencies)

    # Extract layout info from wordcloud
    # layout_ contains: (word, freq, font_size, position, orientation, color)
    words = []
    x_positions = []
    y_positions = []
    font_sizes = []
    colors = []
    counts = []

    for (word, freq), font_size, position, orientation, color in wc.layout_:
        words.append(word)
        # Position is (x, y) from top-left, convert to center-based
        x_positions.append(position[0] + font_size * len(word) * 0.3)
        y_positions.append(cfg["height"] - position[1] - font_size * 0.5)
        font_sizes.append(font_size)
        # Convert RGB tuple to hex color
        if isinstance(color, tuple):
            colors.append(f'rgb({color[0]},{color[1]},{color[2]})')
        else:
            colors.append(color)
        counts.append(word_frequencies.get(word, 0))

    # Create Plotly figure
    fig = go.Figure()

    # Add each word as a separate scatter trace for individual hover
    for i, word in enumerate(words):
        fig.add_trace(go.Scatter(
            x=[x_positions[i]],
            y=[y_positions[i]],
            mode='text',
            text=[word],
            textfont=dict(
                size=font_sizes[i],
                color=colors[i],
            ),
            hoverinfo='text',
            hovertext=f"<b>{word}</b><br>Count: {counts[i]:,}<br><i>Click for details</i>",
            customdata=[word],
            name=word,
            showlegend=False,
        ))

    # Configure layout
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, cfg["width"]],
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, cfg["height"]],
            scaleanchor="x",
            scaleratio=1,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        height=cfg["height"],
        width=cfg["width"],
        hovermode='closest',
    )

    return fig


def generate_empty_figure() -> go.Figure:
    """Generate an empty placeholder figure."""
    fig = go.Figure()

    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="No data available",
        showarrow=False,
        font=dict(size=20, color="gray"),
        xref="paper",
        yref="paper",
    )

    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=WORDCLOUD_CONFIG["height"],
        width=WORDCLOUD_CONFIG["width"],
    )

    return fig


def get_wordcloud_dimensions() -> tuple:
    """Return configured width and height for layout purposes."""
    return WORDCLOUD_CONFIG["width"], WORDCLOUD_CONFIG["height"]
