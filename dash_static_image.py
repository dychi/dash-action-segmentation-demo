import os
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__)
server = app.server

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

# Static path
STATIC_PATH = os.path.join(os.getcwd(), 'images/')
img_list = sorted(os.listdir(STATIC_PATH))
url_dict = {
    'match_7': os.path.join(STATIC_PATH + 'match_7/'),
    'match_8': os.path.join(STATIC_PATH + 'match_8/')
}

app.layout = html.Div([
    html.Label('Image here!'),
    html.Div([
        html.Img(
            id='images',
            style={
                'height': 500,
                
            }
        ),
        html.Div([
            dcc.Dropdown(
                options=[
                    {'label': 'match_7', 'value': 'match_7'},
                    {'label': 'match_8', 'value': 'match_8'}
                ],
                value='match_7',
                id='dropdown'
            )
            ]
        ),
        html.Div([
            dcc.Slider(
                id='frame', 
                min=0,
                max=200,
                updatemode='drag',
                value=0
                )
            ]
        )
        ]
    )
])

@app.callback(Output('images', 'src'),
             [Input('frame', 'value')],
             [State('dropdown', 'value')])
def select_imgae(frame, video):
    img_list = sorted(os.listdir(url_dict[video]))
    img_name = img_list[int(frame)]
    return url_dict[video] + img_name

@app.server.route('{}<path:image_name>'.format(STATIC_PATH))
def serve_static(image_name):
    print(image_name)
    #return flask.send_from_directory(STATIC_PATH, image_name)
    return flask.send_file(STATIC_PATH+image_name)

if __name__ == '__main__':
    app.run_server(debug=True)
