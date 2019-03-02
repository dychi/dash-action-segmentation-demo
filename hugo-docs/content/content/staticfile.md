---
title: "Static File"
date: 2019-01-31T19:53:09+09:00
draft: false
---

### Static File

HTMLファイルや画像ファイルなど，クライアントからの要求に対する応答に使用するファイルのうち、リクエスト内容に影響されないで常に同じ内容になるコンテンツを、静的コンテンツといいます。

Dashは動的にサイトを生成しますが、画像などの静的ファイルを表示するには画像ファイルへのパスを明示してやる必要があります。

```
# Static Path to images
STATIC_PATH = os.path.join(os.getcwd(), 'images/')
```

指定した静的ファイルのディレクトリから相対パスで画像を読み込むためには、Flaskのsend_file()を使用してrootディレクトリからのパスを返します。

```
# Images Display
@app.callback(Output("images", "src"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_image_src(frame, video):
    video_df = data_dict[video]["video_info_df"]
    frame_name = video_df["Frames"][frame]
    return url_dict[video] + frame_name

@app.server.route('{}<path:image_path>'.format(STATIC_PATH))
def serve_image(image_path):
    return flask.send_file(STATIC_PATH + img_name)
```

こうすることで、id="images"のsrcを更新して画像を表示することが出来ます。

その他にも[send_from_directory()](https://qiita.com/5zm/items/760000cf63b176be544c)などを使用することも出来ます。
