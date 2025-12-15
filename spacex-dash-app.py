# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Dropdown options
launch_sites = sorted(spacex_df["Launch Site"].unique())
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in launch_sites
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=site_options,
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                marks={
                                                    int(min_payload): str(int(min_payload)),
                                                    int(max_payload): str(int(max_payload)),
                                                },
                                                value=[min_payload, max_payload],
                                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        site_success = (
            spacex_df.groupby("Launch Site", as_index=False)["class"]
            .sum()
            .rename(columns={"class": "Successes"})
        )
        fig = px.pie(
            site_success,
            values="Successes",
            names="Launch Site",
            title="Total Successful Launches by Launch Site",
        )
        return fig

    filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
    success_count = int((filtered_df["class"] == 1).sum())
    fail_count = int((filtered_df["class"] == 0).sum())

    fig = px.pie(
        names=["Success", "Failure"],
        values=[success_count, fail_count],
        title=f"Total Success vs Failure Launches for site {entered_site}",
    )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site != "ALL":
        df_filtered = df_filtered[df_filtered["Launch Site"] == entered_site]
        title = f"Correlation between Payload and Success for site {entered_site}"
    else:
        title = "Correlation between Payload and Success for all sites"

    fig = px.scatter(
        df_filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title=title,
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
