---
title: "Content"
date: 2019-01-28T23:08:00+09:00
draft: false
pre: "<b>2. </b>"
---

このドキュメントではDashの[demoアプリ](https://dash-action-segmentation.appspot.com/)の作り方を説明していきます。

### 処理の概要
まずは全体の処理の流れを見ていきます。

1. Dash から Flask のインスタンスにアクセス
2. html likeなスタイルでページ内の配置を指定
3. データの読み込み
4. static なデータを読み込むために path の指定
5. @app.callback でインタラクティブなグラフの配置を指定
6. State, Input によるグラフの変化を関数内で定義し返す
7. グラフの描画スタイルは plotly のスタイル
8. css の path を指定
9. server をローカルで起動


