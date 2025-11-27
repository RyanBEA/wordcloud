"""
Interactive Word Cloud Dashboard - Main Dash Application

A web application for visualizing word frequencies from consultation session
transcripts, with filtering by speaker metadata and detailed statistics.
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from config import DEBUG, HOST, PORT
from session_loader import SessionManager
from wordcloud_generator import generate_wordcloud_svg, get_wordcloud_dimensions

# Initialize the session manager
session_manager = SessionManager()

# Brand colors
BRAND_PURPLE = "#4F3D63"

# Google Fonts - Open Sans with ExtraBold (800) weight
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;800&display=swap"

# Initialize Dash app with Bootstrap styling and custom fonts
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, GOOGLE_FONTS],
    title="Consultation Word Cloud",
    update_title=None,  # Disable "Updating..." title flash
    suppress_callback_exceptions=True,
)

# Custom CSS for Open Sans typography
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* === BASE STYLES === */
            body {
                font-family: 'Open Sans', sans-serif;
                font-weight: 400;
                background-color: #F5F3F7; /* Soft lavender-gray */
            }

            .container-fluid {
                background-color: #F5F3F7;
                min-height: 100vh;
            }

            /* === TYPOGRAPHY === */
            h1, h2, h3, h4, h5, h6,
            .h1, .h2, .h3, .h4, .h5, .h6 {
                font-family: 'Open Sans', sans-serif;
                font-weight: 800;
                color: ''' + BRAND_PURPLE + ''';
                text-shadow: 0 1px 2px rgba(79, 61, 99, 0.08);
            }

            h1 {
                text-shadow: 0 2px 4px rgba(79, 61, 99, 0.1);
            }

            strong, b {
                font-weight: 600;
                color: #2C2433;
            }

            .text-muted {
                color: #766985 !important;
            }

            /* === CARDS === */
            .card {
                background-color: #FFFFFF;
                border: none;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(79, 61, 99, 0.08),
                            0 1px 3px rgba(79, 61, 99, 0.06);
                transition: box-shadow 0.3s ease;
            }

            .card:hover {
                box-shadow: 0 4px 12px rgba(79, 61, 99, 0.12),
                            0 2px 6px rgba(79, 61, 99, 0.08);
            }

            .card-header {
                font-family: 'Open Sans', sans-serif;
                font-weight: 800;
                color: #FFFFFF;
                background: linear-gradient(135deg, #4F3D63 0%, #5D4A74 100%);
                border: none;
                border-radius: 8px 8px 0 0 !important;
                padding: 12px 16px;
            }

            .card-body {
                padding: 20px;
                background-color: #FFFFFF;
                border-radius: 0 0 8px 8px;
            }

            /* === BUTTONS === */
            .btn-primary {
                background: linear-gradient(135deg, #4F3D63 0%, #5D4A74 100%);
                border: none;
                border-radius: 6px;
                box-shadow: 0 2px 6px rgba(79, 61, 99, 0.2);
                transition: all 0.3s ease;
            }

            .btn-primary:hover {
                background: linear-gradient(135deg, #3d2f4d 0%, #4a3859 100%);
                box-shadow: 0 4px 10px rgba(79, 61, 99, 0.3);
                transform: translateY(-1px);
            }

            .btn-primary:active {
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(79, 61, 99, 0.2);
            }

            .btn-secondary {
                background-color: #E8E4ED;
                border: 1px solid #D1C9DB;
                color: #4F3D63;
                border-radius: 6px;
                transition: all 0.3s ease;
            }

            .btn-secondary:hover {
                background-color: #DDD6E6;
                border-color: #C4B9D1;
                color: #3d2f4d;
            }

            /* === INPUTS === */
            .input-group {
                box-shadow: 0 2px 6px rgba(79, 61, 99, 0.08);
                border-radius: 6px;
                overflow: hidden;
            }

            .input-group .form-control {
                border: 1px solid #E0DBE6;
                background-color: #FFFFFF;
            }

            .input-group .form-control:focus {
                border-color: #4F3D63;
                box-shadow: 0 0 0 3px rgba(79, 61, 99, 0.1);
            }

            /* === FILTER COLUMN === */
            #filter-column {
                background: linear-gradient(to bottom, #FDFCFE 0%, #F8F6FA 100%);
                padding: 20px 15px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(79, 61, 99, 0.06);
                transition: flex 0.3s ease, max-width 0.3s ease, min-width 0.3s ease;
                overflow: hidden;
            }

            #filter-column.collapsed {
                flex: 0 0 50px !important;
                max-width: 50px !important;
                min-width: 50px !important;
                padding: 10px 5px;
            }

            #filter-column.collapsed .filter-content {
                display: none;
            }

            #filter-column.collapsed .filter-header h5 {
                display: none;
            }

            /* === TOGGLE BUTTON === */
            .filter-toggle-btn {
                background: rgba(79, 61, 99, 0.08);
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                color: ''' + BRAND_PURPLE + ''';
                font-size: 1.2rem;
                border-radius: 6px;
                transition: all 0.3s ease;
                box-shadow: 0 1px 3px rgba(79, 61, 99, 0.1);
            }

            .filter-toggle-btn:hover {
                background: rgba(79, 61, 99, 0.15);
                transform: scale(1.05);
            }

            /* === WORDCLOUD COLUMN === */
            #wordcloud-column {
                transition: flex 0.3s ease, max-width 0.3s ease;
                padding: 0 15px;
            }

            #wordcloud-column.expanded {
                flex: 1 1 auto !important;
                max-width: calc(100% - 50px - 25%) !important;
            }

            #wordcloud-column .card {
                box-shadow: 0 4px 16px rgba(79, 61, 99, 0.1),
                            0 2px 8px rgba(79, 61, 99, 0.06);
            }

            /* === BLOCKQUOTES === */
            .blockquote {
                background: linear-gradient(to right, #F9F8FB 0%, #FDFCFE 100%);
                border-left: 3px solid #4F3D63 !important;
                padding: 12px 16px !important;
                border-radius: 0 6px 6px 0;
                box-shadow: 0 1px 4px rgba(79, 61, 99, 0.06);
                margin-bottom: 16px !important;
            }

            .blockquote p {
                color: #2C2433;
            }

            .blockquote-footer {
                color: #766985 !important;
            }

            /* === LISTS === */
            ul {
                padding-left: 20px;
            }

            li {
                padding: 4px 0;
                color: #3d3447;
            }

            /* === DIVIDERS === */
            hr {
                border-top: 1px solid #E8E4ED;
                opacity: 1;
            }

            /* === DROPDOWNS === */
            .Select-control {
                border: 1px solid #E0DBE6 !important;
                border-radius: 6px !important;
                box-shadow: 0 1px 3px rgba(79, 61, 99, 0.06) !important;
            }

            .Select-control:hover {
                border-color: #C4B9D1 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Expose server for gunicorn (Railway deployment)
server = app.server


def create_filter_controls():
    """Create filter controls dynamically based on available sessions and metadata."""
    sessions = session_manager.get_session_list()
    filter_options = session_manager.get_merged_filter_options()

    controls = []

    # Session selector
    if sessions:
        controls.append(
            dbc.Card([
                dbc.CardHeader("Session"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id="session-dropdown",
                        options=[{"label": "All Sessions", "value": "all"}] +
                                [{"label": s.title(), "value": s} for s in sessions],
                        value="all" if len(sessions) > 1 else (sessions[0] if sessions else None),
                        clearable=False,
                    )
                ])
            ], className="mb-3")
        )

    # Dynamic filters based on metadata columns
    for col, values in filter_options.items():
        if col in ["description"]:  # Skip non-filterable columns
            continue

        controls.append(
            dbc.Card([
                dbc.CardHeader(col.replace("_", " ").title()),
                dbc.CardBody([
                    dcc.Checklist(
                        id=f"filter-{col}",
                        options=[{"label": v, "value": v} for v in values],
                        value=[],  # Nothing selected by default (show all)
                        labelStyle={"display": "block", "marginBottom": "5px"},
                    )
                ])
            ], className="mb-3")
        )

    return controls


def create_stats_panel():
    """Create the statistics panel for word details."""
    return dbc.Card([
        dbc.CardHeader("Word Details"),
        dbc.CardBody([
            html.Div(id="word-stats-content", children=[
                html.P("Click a word or type below to see details.",
                       className="text-muted")
            ])
        ])
    ])


# Get dimensions for sizing
wc_width, wc_height = get_wordcloud_dimensions()

# App layout
app.layout = dbc.Container([
    # Store for clicked word
    dcc.Store(id="clicked-word-store", data=""),

    # Store for filter collapse state
    dcc.Store(id="filters-collapsed-store", data=False),

    # Interval to poll for clicked words from iframe (500ms is responsive enough)
    dcc.Interval(id="click-poll-interval", interval=500, n_intervals=0),

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Consultation Session Word Cloud", className="text-center my-4"),
            html.P(
                "Interactive visualization of word frequencies from consultation transcripts. "
                "Use filters to explore by role, region, and more. Click words to see details.",
                className="text-center text-muted mb-4"
            )
        ])
    ]),

    # Main content
    dbc.Row([
        # Left sidebar - Filters (collapsible horizontally)
        dbc.Col([
            # Filter header with toggle button
            html.Div([
                html.Button(
                    "◀",
                    id="filter-toggle-btn",
                    className="filter-toggle-btn",
                    title="Toggle filters"
                ),
                html.H5("Filters", className="mb-0 ms-2"),
            ], className="filter-header d-flex align-items-center mb-3"),

            # Filter content (hidden via CSS when collapsed)
            html.Div([
                html.Div(id="filter-container", children=create_filter_controls()),
                dbc.Button(
                    "Reset Filters",
                    id="reset-filters-btn",
                    color="secondary",
                    size="sm",
                    className="w-100 mt-2"
                ),
            ], className="filter-content"),
        ], id="filter-column", md=3),

        # Center - Word Cloud
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-wordcloud",
                        type="circle",
                        children=[
                            # Container for SVG word cloud - properly sized
                            html.Div(
                                id="wordcloud-container",
                                style={
                                    "width": "100%",
                                    "aspectRatio": f"{wc_width}/{wc_height}",
                                    
                                    
                                }
                            )
                        ]
                    )
                ], style={"padding": "10px"})
            ]),
            # Word input for manual lookup
            dbc.InputGroup([
                dbc.Input(
                    id="word-lookup-input",
                    placeholder="Type a word to see details...",
                    type="text",
                ),
                dbc.Button("Look Up", id="word-lookup-btn", color="primary"),
            ], className="mt-3"),
        ], id="wordcloud-column", md=6),

        # Right sidebar - Stats
        dbc.Col([
            html.H5("Statistics", className="mb-3"),
            create_stats_panel(),

            # Summary stats
            dbc.Card([
                dbc.CardHeader("Summary"),
                dbc.CardBody(id="summary-stats")
            ], className="mt-3"),
        ], md=3),
    ]),

], fluid=True)


# Clientside callback to listen for postMessage from iframe
app.clientside_callback(
    """
    function(n_intervals) {
        // Set up message listener once
        if (!window._wordcloudMessageListener) {
            window._wordcloudMessageListener = function(event) {
                if (event.data && event.data.type === 'wordcloud-click') {
                    // Store the word for polling
                    window._clickedWord = event.data.word;
                }
            };
            window.addEventListener('message', window._wordcloudMessageListener);
        }

        // Check if there's a clicked word to process
        if (window._clickedWord) {
            var word = window._clickedWord;
            window._clickedWord = null;
            return word;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("clicked-word-store", "data"),
    Input("click-poll-interval", "n_intervals"),
    prevent_initial_call=True
)


@app.callback(
    Output("wordcloud-container", "children"),
    Output("summary-stats", "children"),
    Input("session-dropdown", "value"),
    Input("filter-role", "value"),
    Input("filter-zone", "value"),
    Input("filter-region", "value"),
    prevent_initial_call=False,
)
def update_wordcloud(session_value, role_filter, zone_filter, region_filter):
    """Update the word cloud based on selected filters."""
    # Build filters dict
    filters = {}
    if role_filter:
        filters["role"] = role_filter
    if zone_filter:
        filters["zone"] = zone_filter
    if region_filter:
        filters["region"] = region_filter

    # Get word frequencies
    if session_value == "all" or session_value is None:
        frequencies = session_manager.get_merged_frequencies(filters=filters)
        total_words = sum(frequencies.values()) if frequencies else 0
        unique_words = len(frequencies)
    else:
        session = session_manager.get_session(session_value)
        frequencies = session.get_filtered_frequencies(filters=filters)
        total_words = sum(frequencies.values()) if frequencies else 0
        unique_words = len(frequencies)

    # Generate SVG word cloud
    svg_content = generate_wordcloud_svg(frequencies)

    # Embed SVG in an iframe with no scrollbars
    wordcloud_element = html.Iframe(
        srcDoc=svg_content,
        style={
            "width": "100%",
            "height": "100%",
            "border": "none",
            "display": "block",
            "overflow": "hidden",
        },
        id="wordcloud-iframe"
    )

    # Generate summary stats
    summary = [
        html.P([html.Strong("Total words: "), f"{total_words:,}"]),
        html.P([html.Strong("Unique words: "), f"{unique_words:,}"]),
    ]

    if filters:
        active_filters = ", ".join([
            f"{k}: {', '.join(v)}" for k, v in filters.items() if v
        ])
        summary.append(html.P([html.Strong("Active filters: "), active_filters]))

    return wordcloud_element, summary


@app.callback(
    Output("word-stats-content", "children"),
    Input("clicked-word-store", "data"),
    Input("word-lookup-btn", "n_clicks"),
    State("word-lookup-input", "value"),
    State("session-dropdown", "value"),
    State("filter-role", "value"),
    State("filter-zone", "value"),
    State("filter-region", "value"),
    prevent_initial_call=True,
)
def update_word_details(clicked_word, lookup_clicks, lookup_input, session_value, role_filter, zone_filter, region_filter):
    """Update word details from click or manual lookup."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Get the word to look up
    if trigger_id == "clicked-word-store" and clicked_word:
        word = clicked_word
    elif trigger_id == "word-lookup-btn" and lookup_input:
        word = lookup_input
    else:
        return html.P("Click a word or type below to see details.", className="text-muted")

    # Build filters dict
    filters = {}
    if role_filter:
        filters["role"] = role_filter
    if zone_filter:
        filters["zone"] = zone_filter
    if region_filter:
        filters["region"] = region_filter

    # Get word details
    if session_value == "all" or session_value is None:
        details = session_manager.get_merged_word_details(word, filters=filters)
    else:
        session = session_manager.get_session(session_value)
        details = session.get_word_details(word, filters=filters)

    if not details or details["total_count"] == 0:
        return html.P(f"Word '{word}' not found in the current selection.", className="text-warning")

    # Build stats display - start with word title
    content = [
        html.H4(word.title()),  # Uses brand purple from CSS
        html.Hr(),
    ]

    # Add curated example quotes at the TOP (before stats)
    # Filter out facilitator, SME, Client roles - focus on participant voices
    excluded_roles = {"facilitator", "sme", "client", "na"}
    examples = session_manager.get_word_examples(word, session_value)
    filtered_examples = [
        ex for ex in examples
        if ex.get("role", "").lower() not in excluded_roles
    ][:3]  # Limit to 3 quotes

    if filtered_examples:
        for ex in filtered_examples:
            role = ex.get("role", "participant")
            session = ex.get("session", "").title()
            attribution = f"{role}, {session}" if session else role

            quote_block = html.Blockquote([
                html.P(f'"{ex.get("quote", "")}"', className="mb-1", style={"fontStyle": "italic"}),
                html.Footer([
                    html.Small(attribution, className="text-muted"),
                ], className="blockquote-footer")
            ], className="blockquote mb-3", style={"borderLeft": "3px solid #4F3D63", "paddingLeft": "10px"})
            content.append(quote_block)
        content.append(html.Hr())

    # Stats section
    content.append(html.P([html.Strong("Total mentions: "), f"{details['total_count']:,}"]))
    content.append(html.P([html.Strong("Unique speakers: "), f"{details['speaker_count']}"]))

    # Metadata breakdowns (skip description)
    for meta_key, meta_values in details.get("metadata", {}).items():
        if meta_values and meta_key != "description":
            content.append(html.H6(f"By {meta_key.title()}:", className="mt-3"))
            sorted_meta = sorted(meta_values.items(), key=lambda x: x[1], reverse=True)
            content.append(html.Ul([
                html.Li(f"{val}: {count}") for val, count in sorted_meta
            ]))

    return content


@app.callback(
    Output("filter-role", "value"),
    Output("filter-zone", "value"),
    Output("filter-region", "value"),
    Input("reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n_clicks):
    """Reset all filters to empty (show all)."""
    return [], [], []


# Clientside callback to toggle filter collapse horizontally
app.clientside_callback(
    """
    function(n_clicks, is_collapsed) {
        if (n_clicks === undefined) {
            return window.dash_clientside.no_update;
        }
        var new_collapsed = !is_collapsed;
        var filterCol = document.getElementById('filter-column');
        var wordcloudCol = document.getElementById('wordcloud-column');
        var btn = document.getElementById('filter-toggle-btn');

        if (filterCol && wordcloudCol && btn) {
            if (new_collapsed) {
                filterCol.classList.add('collapsed');
                wordcloudCol.classList.add('expanded');
                btn.innerHTML = '▶';
            } else {
                filterCol.classList.remove('collapsed');
                wordcloudCol.classList.remove('expanded');
                btn.innerHTML = '◀';
            }
        }
        return new_collapsed;
    }
    """,
    Output("filters-collapsed-store", "data"),
    Input("filter-toggle-btn", "n_clicks"),
    State("filters-collapsed-store", "data"),
    prevent_initial_call=True
)


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
