# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from textwrap import dedent

import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import plotly.graph_objs as go
import plotly.figure_factory as ff

DEBUG = True

app = dash.Dash(__name__)
server = app.server # the Flask app

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

# Load Data
def load_data(path):
    # Load the dataframe
    video_info_df = pd.read_csv(path)
    
    # The list of classes, and the number of classes.
    classes_list = ['spt', 'fhpt', 'bhpt', 'lbpt', 'smpt', 'rtpt', 'n', 'spb', 'fhpb', 'bhpb', 'lbpb', 'smpb', 'rtpb']
    n_classes = len(classes_list)
    
    # Round the number of classes
    total_size = np.round(n_classes + 0.5)
    padding_value = int(total_size - n_classes)
    classes_padded = np.pad(classes_list, (0, padding_value), mode='constant')
    
    # Class Matrix
    class_list = [rename_dict[name] for name in classes_list]
    class_pad = np.pad(class_list, (0, padding_value), mode='constant')
    classes_matrix = np.reshape(class_pad, (2, int(total_size/2)))
    classes_matrix = np.flip(classes_matrix, axis=0)

    data_dict = {
            "video_info_df": video_info_df,
            "n_classes": n_classes,
            "classes_matrix": classes_matrix,
            "classes_padded": classes_padded,
            "total_size": total_size
    }
    if DEBUG:
        print('{} loaded.'.format(path))
    return data_dict

def get_score_bar(data_dict, frame_num):
    video_info_df = data_dict["video_info_df"]
    classes_padded = data_dict["classes_padded"]
    # The list of scores
    score_list = []
    for name in classes_padded:
        if name == '0':
            break
        score_list.append(video_info_df[name][frame_num]) 
    # Score and labels
    x_score = ["{}".format(rename_dict[shot]) for shot in classes_padded[:-1]]
    y_score = score_list
    # Add Text information
    y_text = ["{}% confidence".format(round(value*100)) for value in score_list]
    colors = "rgb(100,100,100)"
    return np.array(x_score), np.array(y_score), y_text, colors


def get_heatmap(data_dict, frame_num, row_name:str, color_code:str):
    video_df = data_dict["video_info_df"]
    classes_padded = data_dict["classes_padded"]
    total_size = data_dict["total_size"]
    classes_matrix = data_dict["classes_matrix"]
    # The list of scores
    score_list = []
    for el in classes_padded:
        if el in video_df[row_name][frame_num]:
            value = 1 if row_name == "class_str_label" else video_df["Top1_score"][frame_num] 
            score_list.append(value)
        else:
            score_list.append(0)

    # Generate the score matrix, and flip it for visual
    score_matrix = np.reshape(score_list, (-1, int(total_size/2)))
    score_matrix = np.flip(score_matrix, axis=0)
    # color scale
    colorscale = [[0, '#ffffff'], [1,color_code]]
    font_colors = ['#3c3636', '#efecee']
    # Hover Text
    hover_text = ['{:.2f}% confidence'.format(score * 100) for score in score_list]
    hover_text = np.reshape(hover_text, (-1, int(total_size/2)))
    hover_text = np.flip(hover_text, axis=0)
    return score_matrix, classes_matrix, colorscale, font_colors, hover_text


# Static Path to images
STATIC_PATH = os.path.join(os.getcwd(), 'images/')
# Rename Dictionary
rename_dict = {'spt':  'Serve <br> Top',
               'fhpt': 'Forehand <br> Top', 
               'bhpt': 'Backhand <br> Top',
               'lbpt': 'Lob <br> Top',
               'smpt': 'Smash <br> Top',
               'rtpt': 'React <br> Top',
               'n':    'None', 
               'spb':  'Serve <br> Bottom',
               'fhpb': 'Forehabd <br> Bottom',
               'bhpb': 'Backhand <br> Bottom',
               'lbpb': 'Lob <br> Bottom',
               'smpb': 'Smash <br> Bottom',
               'rtpb': 'React <br> Bottom'}

# Main App
app.layout = html.Div([
    # Banner display
    html.Div([
        html.H2(
            'Action Segmentation Explorer',
            id='title',
        ),
        html.Img(
            src="https://wwwdc05.adst.keio.ac.jp/kj/vi/common/img/thumbF2.png",
            style={
                'height': '65px',
                'margin-top': '8px',
                'margin-bottom': '0px'
                }
        )
    ],
        className="banner",
        style={
                'background-color': '#1A8695',
                'height': '75px',
                'padding-top': '0px',
                'padding-left': '0px',
                'padding-right': '0px',
                'width': '100%',
                'margin-bottom': '10px',
            }
    ),

    # Body
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Img(
                        style={
                            'width': '90%',#600,
                            'height': 'auto',#400,
                            'margin': '30px 20px 15px 20px'
                            },
                        id="images",
                    )
                    ],
                    id='div-video-player',
                    style={
                        'color': 'rgb(255,255,255)',
                        'margin-bottom': '-30px'
                    }
                ),
                html.Div([
                    "Frame Position",
                    dcc.Slider(
                        min=0,
                        max=120,
                        marks={i: '{}th'.format(i) for i in range(0,120,30)},
                        value=0,
                        updatemode='drag',
                        id='slider-frame-position'
                        ),
                    ],
                    style={'margin': '30px 30px 30px 30px'} # top right bottom left
                ),
                dcc.Interval(
                    id='interval-component',
                    n_intervals=0, # default: Off
                    max_intervals=120
                ),
                html.Div([
                    "Video Selection",
                    dcc.Dropdown(
                        options=[
                            {'label': 'Match 7: Weilee vs Long @ Semi Finals', 'value': 'match_7'},
                            {'label': 'Match 8: Chen vs Zwiebler @ R32', 'value': 'match_8'},
                            {'label': 'Match 9: Li vs Wang @ Semi Finals', 'value': 'match_9'},
                            {'label': 'Match 10: Na vs Fasungova @ Group D', 'value': 'match_10'}
                     ],
                        value='match_8',
                        id='dropdown-video-selection',
                        clearable=False
                    )
                    ],
                    style={'margin': '30px 20px 15px 20px'}
                ),
                html.Div([
                    "Play Mode",
                    dcc.RadioItems(
                        options=[
                            {'label': ' Manual mode', 'value': 60*60*1000},
                            {'label': ' Auto mode', 'value': 1000},
                        ],
                        value=60*60*1000,
                        id='radioitem-play-selection',
                    )
                ],
                    style={'margin': '15px 20px 15px 20px'}
                ),
            ],
                className="six columns",
                style={'margin-bottom': '20px'}
            ),

            #  Heatmap Area and Classification Score
            html.Div(id="div-visual-mode", className="six columns")
        ],
            
            className="row"
        ),
        html.Div(
            className='row',
            style={
                'padding': '15px 30px 27px',
                'margin': '10px auto 45px',
                'width': '80%',
                'max-width': '1024px',
                'borderRadius': 5,
                'border': 'thin lightgrey solid',
                'font-family': 'Roboto, sans-serif',
            },
            children=dcc.Markdown(dedent(
                '''
                ## Badminton Action Segmentation Demo View
                To get started, select a footage you want to view, and choose the match video.
                
                If you want to know how to create this demonstration page, you can refer this
                [explanation page](https://dychi.github.io/dash-action-segmentation-demo/).
                '''
                ))
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
        'match_7': load_data("annotations/match_7.csv"),
        'match_8': load_data("annotations/match_8.csv"),
        'match_9': load_data("annotations/match_9.csv"),
        'match_10': load_data("annotations/match_10.csv")
    }
    url_dict = {
            'match_7':  os.path.join(STATIC_PATH + 'match_7/'),
            'match_8': os.path.join(STATIC_PATH +'match_8/'),
            'match_9': os.path.join(STATIC_PATH +'match_9/'),
            'match_10': os.path.join(STATIC_PATH +'match_10/'),
    }

# Interval
@app.callback(Output('interval-component', 'interval'),
             [Input('radioitem-play-selection', 'value')])
def choose_update_interval(value):
    return value

# Update Slider Position
@app.callback(Output('slider-frame-position', 'value'),
             [Input('interval-component', 'n_intervals')])
def slider_position(n):
    return n

# Images Display mode: analysis
@app.callback(Output("images", "src"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_image_src(frame, video):
    video_df = data_dict[video]["video_info_df"]
    frame_name = video_df["Frames"][frame]
    return url_dict[video] + frame_name

@app.server.route('{}<path:image_path>'.format(STATIC_PATH))
def serve_image(image_path):
    return flask.send_file(STATIC_PATH + image_path)

# Graph View 
@app.callback(Output("div-visual-mode", "children"),
             [Input("dropdown-video-selection", "value")])
def update_visual(value):
    return [
            dcc.Graph(
                style={'height': '25vh'},
                id="heatmap-confidence"
            ),
            dcc.Graph(
                style={'height': '20vh'},
                id="correct-label"
            ),
            dcc.Graph(
                style={'height': '40vh'},
                id="bar-score-graph"
            )
    ]

# Update Correct Label
@app.callback(Output("correct-label", "figure"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_label(frame, video):
    layout = go.Layout(
        title="Ground Truth",
        margin=go.layout.Margin(l=20, r=20, t=50, b=10)
    )
    scoreMatrix, classMatrix, colorScale, fontColors, hoverText = get_heatmap(data_dict[video], frame, 'class_str_label', '#288FF7')

    pt = ff.create_annotated_heatmap(
            z=scoreMatrix,
            annotation_text=classMatrix,
            colorscale=colorScale,
            font_colors=fontColors,
            hoverinfo='text',
            text=hoverText,
            zmin=0,
            zmax=1
    )
    pt.layout.title = layout.title
    pt.layout.margin = layout.margin
    return pt

# Updating Heatmap
@app.callback(Output("heatmap-confidence", "figure"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_heatmap(frame, video):
    layout = go.Layout(
        title="Predicted Confidence Level of Action Classification",
        margin=go.layout.Margin(l=20, r=20, t=50, b=10)
    )
    scoreMatrix, classMatrix, colorScale, fontColors, hoverText = get_heatmap(data_dict[video], frame, 'class_str_top1', '#f71111')

    pt = ff.create_annotated_heatmap(
            z=scoreMatrix,
            annotation_text=classMatrix,
            colorscale=colorScale,
            font_colors=fontColors,
            hoverinfo='text',
            text=hoverText,
            zmin=0,
            zmax=1
    )
    pt.layout.title = layout.title
    pt.layout.margin = layout.margin
    return pt

# Updating Bar Score
@app.callback(Output("bar-score-graph", "figure"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_score_bar(frame, video):
    layout = go.Layout(
        title="Classification Score of Player's Shot",
        showlegend=False,
        margin=go.layout.Margin(l=70, r=40, t=50, b=30),
        xaxis={'tickfont': {'size': 8}},
        yaxis={'title': 'Score', 'range': [0,1]}
        )
    x_score, y_score, y_text, colors = get_score_bar(data_dict[video], frame)

    bar = go.Bar(
            x=x_score,
            y=y_score,
            text=y_text,
            name="Classification Score",
            hoverinfo="x+text",
        )
    return go.Figure(data=[bar], layout=layout)


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
