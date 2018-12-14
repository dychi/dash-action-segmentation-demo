# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pandas as pd
from PIL import ImageColor

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.figure_factory as ff

import utils.desc_card as drc
from utils.video import PlayVideo

DEBUG = True
FRAME_RATE = 24.0

app = dash.Dash(__name__)
server = app.server

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

# Load Data
def load_data(path):
    # Load the dataframe
    video_info_df = pd.read_csv(path)
    
    # The list of classes, and the number of classes.
    classes_list = video_info_df["class_str_pred"].value_counts().index.tolist()
    n_classes = len(classes_list)
    
    # Get the smallest value needed to the end of the classes list to get a squere matrix
    root_round = np.ceil(np.sqrt(len(classes_list)))
    total_size = root_round ** 2
    padding_value = int(total_size - n_classes)
    classes_padded = np.pad(classes_list, (0, padding_value), mode='constant')

    # The padded matrix containing all the classes inside a matrix
    classes_matrix = np.reshape(classes_padded, (int(root_round), int(root_round)))

    # Flip
    classes_matrix = np.flip(classes_matrix, axis=0)

    data_dict = {
            "video_info_df": video_info_df,
            "n_classes": n_classes,
            "classes_matrix": classes_matrix,
            "classes_padded": classes_padded,
            "root_round": root_round
    }
    if DEBUG:
        print(f'{path} loaded.')
    return data_dict

# Main App
app.layout = html.Div([
    # Banner display
    html.Div([
        html.H2(
            'Action Segmentation Explorer',
            id='title'
        ),
        html.Img(
            src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
        )
    ],
        className="banner",
    ),

    # Body
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    # Write player() insted of rdp.my_Player()

                    ],
                    id='div-video-player',
                    style={
                        'color': 'rgb(255,255,255)',
                        'margin-bottom': '-30px'
                    }
                ),
                html.Div([
                    "Frame Position:",
                    dcc.Slider(
                        min=0,
                        max=120,
                        marks={i: f'{i}s' for i in range(0,120,10)},
                        value=50,
                        updatemode='drag',
                        id='slider-frame-position'
                        )
                    ],
                    style={'margin': '15px 30px 30px 30px'} # top right bottom left
                ),
                html.Div([
                    "Video Selection",
                    dcc.Dropdown(
                        options=[
                            {'label': 'Match 7: Weilee vs Long @ Semi Finals', 'value': 'match_7'},
                            {'label': 'Match 8: Chen vs Zwiebler @ R32', 'value': 'match_8'}
                        ],
                        value='match_7',
                        id='dropdown-video-selection',
                        clearable=False
                        )
                    ],
                    style={'margin': '30px 20px 15px 20px'}
                    )
                ],
                className="four columns", # why four?
                style={'margin-bottom': '20px'}
            ),

            html.Div(id="div-visual-mode", className="four columns"),

            html.Div(id="div-detection-mode", className="four columns")
            ],
            className="row"
        ),

        drc.DemoDescriptionCard(
            '''
            ## Badminton Action Segmentation Demo View
            To get started, select a footage you want to view, and choose the match video.
            '''
            )
        ],
        className="container scalable"
    )
])

# Data Loading
@app.server.before_first_request
def load_all_match():
    global data_dict, url_dict

    # Load the dictionary containing all the variables needed for analysis
    data_dict = {
        'match_7': load_data("data/match_7.csv"),
        #'match_8': load_data("data/match_8.csv")
    }

    url_dict = {
        'match_7': "video/bad_youtube.mp4",
        #'match_8': 'path to mp4'
    }

# Video Selectioin
@app.callback(Output("div-video-player", "children"),
             [Input('dropdown-video-selection', 'value')])
def select_video(video):
    url = url_dict[video]
    layout = go.Layout(
            title="Confidence Level of Action Segmentation",
            margin=go.layout.Margin(l=20,  r=20, t=57, b=30)
    )

    return go.Figure(data=[go.Bar()], layout=layout)
        #rpd.my_Player(id='video-display',url=url, width='100%',
            # height='50vh', controls=True, seekTo=0, volume=1)

# Graph View Selection
@app.callback(Output("div-visual-mode", "children"),
              [Input("dropdown-graph-view-mode", "value")])
def update_visual_mode(value):
    if value == "visual":
        return [
            dcc.Interval(
                id="interval-visual-mode",
                interval=700,
                n_intervals=0
            ),

            dcc.Graph(
                style={'height': '55vh'},
                id="heatmap-confidence"
            ),

            dcc.Graph(
                style={'height': '40vh'},
                id="pie-object-count"
            )
        ]

    else:
        return []


# Updating Figures
@app.callback(Output("heatmap-confidence", "figure"),
             [Input('dropdown-video-selection', 'value')],# Input("interval-detection-mode", "n_interval")],
             [#State('dropdown-video-selection', 'value'),
              State('slider-frame-position', 'value')])
def update_heatmap_confidence(video, position):
    layout = go.Layout(
            title="Confidence Level of Action Segmentation",
            margin=go.Margin(l=20,  r=20, t=57, b=30)
    )
    # Load variables from the data dictionary
    video_info_df = data_dict[video]["video_info_df"]
    classes_padded = data_dict[video]["classes_padded"]
    root_round = data_dict[video]["root_round"]
    classes_matrix = data_dict[video]["classes_matrix"]

    # Select the subset of the dataset that correspond to the currenct frame
    #frame_df = video_info_df[video_info_df["Frames"] == current_frame]
    frame_df = video_info_df.iloc[0,:]
    # Remove duplicate, keep the top result
    frame_no_dup = frame_df[["class_str_pred", "Scores"]].drop_duplicates("class_str_pred")
    frame_no_dup.set_index("class_str_pred", inplace=True)
    
    # The list of scores
    score_list = []
    for el in classes_padded:
        if el in frame_no_dup.index.values:
            score_list.append(frame_no_dup.loc[el][0])
        else:
            score_list.append(0)
    
    # Generate the score matrix, and flip it for visual
    score_matrix = np.reshape(score_list, (-1, int(root_round)))
    score_matrix = np.flip(score_matrix, axis=0)

    # We set the color scale to white if there's nothing in the frame_no_dup
    if frame_no_dup.shape != (0, 1):
        colorscale = [[0, '#ffffff'], [1,'#f71111']]
        font_colors = ['#3c3636', '#efecee']
    else:
        colorscale = [[0, '#ffffff'], [1,'#ffffff']]
        font_colors = ['#3c3636']

    hover_text = [f"{score * 100:.2f}% confidence" for score in score_list]
    hover_text = np.reshape(hover_text, (-1, int(root_round)))
    hover_text = np.flip(hover_text, axis=0)

    pt = ff.create_annotated_heatmap(
        score_matrix,
        annotation_text=classes_matrix,
        colorscale=colorscale,
        font_colors=font_colors,
        hoverinfo='text',
        text=hover_text,
        zmin=0,
        zmax=1
    )

    pt.layout.title = layout.title
    pt.layout.margin = layout.margin

    return pt

    # Returns empty figure
    #return go.Figure(data[go.Pie()], layout=layout)

external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/base-styles.css",
    "https://cdn.rawgit.com/plotly/dash-object-detection/875fdd6b/custom-styles.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=DEBUG)
