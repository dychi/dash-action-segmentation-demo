---
title: "Usage"
date: 2019-01-31T20:29:28+09:00
draft: false
weight: 4
---

### 使い方

仮想環境の作成
```=shell
$ pyenv virtualenv 3.7.0 {ENV_NAME}
$ cd dash-action-segmentation-demo
$ pyenv local {ENV_NAME}
```

パッケージのインストール
```=shell
$ pip install -r requirements.txt
```

デモの起動
```=shell
$ python app.py
```

{{% notice note %}}
ただし自分で画像とCSVファイルを別途用意する必要があります。<br>
DirectoriesとAnnotationsを参考にしながらそれぞれデータを用意してください。
{{% /notice %}}
