"""
Word cloud generation module - JavaScript-based with d3-cloud.

Uses d3-cloud library for browser-native layout, ensuring no overlap
since the same environment calculates and renders the word positions.
"""
import json
from config import WORDCLOUD_CONFIG


def generate_wordcloud_html(word_frequencies: dict, config: dict = None) -> str:
    """
    Generate an interactive word cloud using d3-cloud.

    Returns an HTML document with embedded JavaScript that renders
    the word cloud client-side, ensuring accurate font metrics.
    """
    if not word_frequencies:
        return generate_empty_html()

    cfg = {**WORDCLOUD_CONFIG, **(config or {})}
    width = cfg["width"]
    height = cfg["height"]
    max_words = cfg["max_words"]
    min_font_size = cfg["min_font_size"]
    max_font_size = cfg["max_font_size"]
    bg_color = cfg["background_color"]

    # Get top N words by frequency
    sorted_words = sorted(
        word_frequencies.items(),
        key=lambda x: x[1],
        reverse=True
    )[:max_words]

    if not sorted_words:
        return generate_empty_html()

    # Calculate font size scaling
    max_freq = sorted_words[0][1]
    min_freq = sorted_words[-1][1] if len(sorted_words) > 1 else max_freq
    freq_range = max_freq - min_freq if max_freq != min_freq else 1

    # Prepare word data with scaled font sizes
    words_data = []
    for word, freq in sorted_words:
        # Linear scaling between min and max font size
        normalized = (freq - min_freq) / freq_range
        font_size = min_font_size + normalized * (max_font_size - min_font_size)
        words_data.append({
            "text": word,
            "size": round(font_size, 1),
            "freq": freq
        })

    words_json = json.dumps(words_data)

    # Custom brand color palette
    colors = [
        "#4F3D63",  # Purple (brand primary)
        "#C17F47",  # Orange/brown
        "#47A68C",  # Teal
        "#8C4747",  # Red/maroon
        "#8C7A47",  # Olive/gold
        "#476B8C",  # Steel blue
        "#8C4776",  # Magenta/pink
        "#5C8C47",  # Green
        "#8C5C47",  # Brown
        "#478C67",  # Green-teal
    ]
    colors_json = json.dumps(colors)

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: {bg_color};
            overflow: hidden;
            width: 100%;
            height: 100%;
        }}
        svg {{
            display: block;
            width: 100%;
            height: 100%;
        }}
        .word {{
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        .word:hover {{
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <svg id="wordcloud"></svg>

    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3-cloud@1.2.7/build/d3.layout.cloud.min.js"></script>
    <script>
        const words = {words_json};
        const colors = {colors_json};
        const width = {width};
        const height = {height};

        // Set up SVG
        const svg = d3.select("#wordcloud")
            .attr("viewBox", [0, 0, width, height])
            .attr("preserveAspectRatio", "xMidYMid meet");

        const g = svg.append("g")
            .attr("transform", `translate(${{width/2}},${{height/2}})`);

        // Create color scale
        const colorScale = d3.scaleOrdinal(colors);

        // Create word cloud layout
        const layout = d3.layout.cloud()
            .size([width, height])
            .words(words.map(d => ({{
                text: d.text,
                size: d.size,
                freq: d.freq
            }})))
            .padding(5)
            .rotate(() => Math.random() > 0.8 ? 90 : 0)
            .font("Impact")
            .fontSize(d => d.size)
            .spiral("archimedean")
            .on("end", draw);

        layout.start();

        function draw(words) {{
            g.selectAll("text")
                .data(words)
                .enter()
                .append("text")
                .attr("class", "word")
                .style("font-size", d => d.size + "px")
                .style("font-family", "Impact, sans-serif")
                .style("fill", (d, i) => colorScale(i))
                .attr("text-anchor", "middle")
                .attr("transform", d => `translate(${{d.x}},${{d.y}})rotate(${{d.rotate}})`)
                .attr("data-word", d => d.text)
                .text(d => d.text)
                .on("click", function(event, d) {{
                    window.parent.postMessage({{type: 'wordcloud-click', word: d.text}}, '*');
                }});
        }}
    </script>
</body>
</html>'''

    return html


def generate_empty_html() -> str:
    """Generate an empty/placeholder word cloud."""
    width = WORDCLOUD_CONFIG["width"]
    height = WORDCLOUD_CONFIG["height"]
    bg = WORDCLOUD_CONFIG["background_color"]

    return f'''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            background: {bg};
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: sans-serif;
            color: #999;
        }}
    </style>
</head>
<body>
    <p>No data available</p>
</body>
</html>'''


def get_wordcloud_dimensions() -> tuple:
    """Return configured width and height for layout purposes."""
    return WORDCLOUD_CONFIG["width"], WORDCLOUD_CONFIG["height"]


# Keep old function name for compatibility
generate_wordcloud_svg = generate_wordcloud_html
