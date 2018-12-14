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

def get_score_bar(data_dict):
    frame_num = 0
    video_info_df = data_dict["video_info_df"]
    shot = video_info_df["class_str_pred"][frame_num]
    x_score = f"{shot}"
    y_score = video_info_df["Scores"][frame_num]
    # Add Text information
    y_text = [f"{round(value*100)}% confidence" for value in video_info_df["Scores"].tolist()][frame_num]
    colors = "rgb(100,100,100)"
    return np.array(x_score), np.array(y_score), y_text, colors

def get_heatmap(data_dict):
    frame_num = 0
    video_df = data_dict["video_info_df"]
    classes_padded = data_dict["classes_padded"]
    root_round = data_dict["root_round"]
    classes_matrix = data_dict["classes_matrix"]
    
    # The list of scores
    score_list = []#np.array(video_df["Scores"][frame_num])
    for el in classes_padded:
        if el in video_df["class_str_pred"][frame_num]:
            score_list.append(video_df["Scores"][frame_num])
        else:
            score_list.append(0)

    # Generate the score matrix, and flip it for visual
    score_matrix = np.reshape(score_list, (-1, int(root_round)))
    score_matrix = np.flip(score_matrix, axis=0)
    # color scale
    colorscale = [[0, '#ffffff'], [1,'#f71111']]
    font_colors = ['#3c3636', '#efecee']
    # Hover Text
    hover_text = [f'{score * 100:.2f}% confidence' for score in score_list]
    hover_text = np.reshape(hover_text, (-1, int(root_round)))
    hover_text = np.flip(hover_text, axis=0)
    return score_matrix, classes_matrix, colorscale, font_colors, hover_text

# local load
local_data_dict = load_data("data/match_7.csv") 
x_score, y_score, y_text, colors = get_score_bar(local_data_dict)
scoreMatrix, classMatrix, colorScale, fontColors, hoverText = get_heatmap(local_data_dict)
print(scoreMatrix, classMatrix, colorScale, fontColors, hoverText)

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
                className="six columns", # why four?
                style={'margin-bottom': '20px'}
            ),

            # Heatmap Area
            html.Div([
                dcc.Graph(
                    style={'height': '55vh'},
                    figure={
                        'data': [
                            ff.create_annotated_heatmap(
                                scoreMatrix,
                                annotation_text=classMatrix,
                                colorscale=colorScale,
                                font_colors=fontColors,
                                hoverinfo='text',
                                text=hoverText,
                                zmin=0,
                                zmax=1
                            )
                        ],
                        'layout': {
                            'title': "Confidence Level of Action Classification",
                            'margin': go.layout.Margin(l=20, r=20, t=57, b=30)
                        }
                    }
                ),
            ],
                className="six columns",
            ),
            # Classification Score
            html.Div([
                dcc.Graph(
                    style={'height': '50vh'},
                    figure={
                        'data':[
                            go.Bar(
                                x=x_score,
                                y=y_score,
                                text=y_text,
                                name="Classification Score",
                                hoverinfo='x+text',
                                #marker=go.Marker(color=colors,line=dict(color='rgb(79, 85, 91)', width=1))
                            )
                        ],
                        'layout':{
                            'title': "Classification Score of Player's Shot",
                            'showlegend': False,
                            'margin': go.layout.Margin(l=70, r=40, t=50, b=30),
                            'yaxis': {'title': 'Score', 'range': [0,1]},
                            }
                        }
                    ),
                ],
                className="six columns"
            )
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
#@app.callback(Output("div-video-player", "children"),
#             [Input('dropdown-video-selection', 'value')])
# def select_video(video):
#     url = url_dict[video]
#    return go.Figure(data=[go.Bar()], layout=layout)


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
