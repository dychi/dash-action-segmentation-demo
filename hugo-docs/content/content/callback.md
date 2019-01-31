---
title: "Callback"
date: 2019-01-31T19:32:49+09:00
draft: false
---

### Callback

callbackは作成したグラフをインタラクティブに描画するために使います。

```
# Update Correct Label
@app.callback(Output("correct-label", "children"),
             [Input("slider-frame-position", "value")],
             [State("dropdown-video-selection", "value")])
def update_label(frame, video):
    label = data_dict[video]["video_info_df"]["class_str_label"][frame]
    return 'Correct Label is "{}"'.format(rename_dict[label].replace('<br>', ''))
```

ここでは、app.pyのupdate_visual関数の中で作成したhtml.H4で指定している id="correct-label" のchildren要素を更新することを示しています。

インタラクティブに変更する際には入力と状態を定義する必要があり、Input, Stateをupdate_label関数の引数とします。

その引数に対して、H4の
Correct Label is {}
の{}を更新することになります。

このようにしてそれぞれのグラフでの値を変更していきます。