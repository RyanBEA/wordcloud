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
from wordcloud_generator import generate_wordcloud_image, get_wordcloud_dimensions

# Initialize the session manager
session_manager = SessionManager()

# Initialize Dash app with Bootstrap styling
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Consultation Word Cloud",
    suppress_callback_exceptions=True,
)

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
                html.P("Hover over a word in the cloud or click to see details.",
                       className="text-muted")
            ])
        ])
    ])


# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Consultation Session Word Cloud", className="text-center my-4"),
            html.P(
                "Interactive visualization of word frequencies from consultation transcripts. "
                "Use filters to explore by role, region, and more.",
                className="text-center text-muted mb-4"
            )
        ])
    ]),

    # Main content
    dbc.Row([
        # Left sidebar - Filters
        dbc.Col([
            html.H5("Filters", className="mb-3"),
            html.Div(id="filter-container", children=create_filter_controls()),
            dbc.Button(
                "Reset Filters",
                id="reset-filters-btn",
                color="secondary",
                size="sm",
                className="w-100 mt-2"
            ),
        ], md=3),

        # Center - Word Cloud
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-wordcloud",
                        type="circle",
                        children=[
                            html.Img(
                                id="wordcloud-image",
                                style={
                                    "width": "100%",
                                    "maxWidth": f"{get_wordcloud_dimensions()[0]}px",
                                    "cursor": "pointer"
                                }
                            )
                        ]
                    )
                ])
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
        ], md=6),

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

    # Hidden div to store current filters state
    dcc.Store(id="current-filters-store"),

], fluid=True)


def get_active_filters(session, *filter_values):
    """
    Extract active filters from callback inputs.

    Returns dict of {column: [selected_values]}
    """
    filter_options = session_manager.get_merged_filter_options()
    columns = list(filter_options.keys())

    filters = {}
    for i, col in enumerate(columns):
        if col in ["description"]:
            continue
        if i < len(filter_values) and filter_values[i]:
            filters[col] = filter_values[i]

    return filters


@app.callback(
    Output("wordcloud-image", "src"),
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

    # Generate word cloud image
    img_src = generate_wordcloud_image(frequencies)

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

    return img_src, summary


@app.callback(
    Output("word-stats-content", "children"),
    Input("word-lookup-btn", "n_clicks"),
    State("word-lookup-input", "value"),
    State("session-dropdown", "value"),
    State("filter-role", "value"),
    State("filter-zone", "value"),
    State("filter-region", "value"),
    prevent_initial_call=True,
)
def lookup_word(n_clicks, word, session_value, role_filter, zone_filter, region_filter):
    """Look up details for a specific word."""
    if not word:
        return html.P("Please enter a word to look up.", className="text-muted")

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

    # Build stats display
    content = [
        html.H4(word.title(), className="text-primary"),
        html.Hr(),
        html.P([html.Strong("Total mentions: "), f"{details['total_count']:,}"]),
        html.P([html.Strong("Unique speakers: "), f"{details['speaker_count']}"]),
    ]

    # Speaker breakdown
    if details["speakers"]:
        speaker_items = sorted(
            details["speakers"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 speakers

        content.append(html.H6("Top Speakers:", className="mt-3"))
        content.append(html.Ul([
            html.Li(f"{speaker}: {count}") for speaker, count in speaker_items
        ]))

    # Metadata breakdowns
    for meta_key, meta_values in details.get("metadata", {}).items():
        if meta_values:
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


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
