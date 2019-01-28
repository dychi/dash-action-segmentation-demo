# Document for Dash Plotly
このドキュメントではDashの[demoアプリ](https://dash-action-segmentation.appspot.com/)の作り方を説明していきます。

## 参考にしたサイト
* [Dash Object Detection Explorer](https://github.com/plotly/dash-object-detection)
* [Dash recipes](https://github.com/plotly/dash-recipes)

## 必要なもの
```
certifi==2018.11.29
chardet==3.0.4
Click==7.0
dash==0.32.2
dash-core-components==0.40.3
dash-html-components==0.13.2
dash-renderer==0.16.0
dash-table==3.1.11
decorator==4.3.0
Flask==1.0.2
Flask-Compress==1.4.0
gunicorn==19.9.0
idna==2.8
ipython-genutils==0.2.0
itsdangerous==1.1.0
Jinja2==2.10
jsonschema==2.6.0
jupyter-core==4.4.0
MarkupSafe==1.1.0
nbformat==4.4.0
numpy==1.15.4
pandas==0.23.4
plotly==3.4.2
python-dateutil==2.7.5
pytz==2018.7
requests==2.21.0
retrying==1.3.3
six==1.12.0
traitlets==4.3.2
urllib3==1.24.1
Werkzeug==0.14.1
```

## ディレクトリ構造
```
.
├── README.md
├── app.py
├── flex.app.yaml
├── annotations
│   ├── match_7.csv
│   ├── match_8.csv
│   ├── match_9.csv
│   ├── match_10.csv
├── imgaes
│   ├── match_7/
│   ├── match_8/
│   ├── match_9/
│   ├── match_10/
├── requirements.txt
└── standard.app.yaml
```

## コードの解説
ここからはapp.pyの詳細について解説していきます。
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

### 



