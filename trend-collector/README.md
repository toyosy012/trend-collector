
## パッケージ管理

[リファレンス](https://packaging.python.org/ja/latest/guides/installing-using-pip-and-virtual-environments/)
[参考](https://qiita.com/ryu22e/items/ad3f8f3df30886d23661)

- プロジェクトディレクトリ毎の依存関係を満たすための作業
- requirements.inに記載
- pip-compileを使うことでrequirements.txtを生成

```
# プロジェクトディレクトリ以下のpython, pipを使用するためPATHに設定
$ source venv/bin/activate

# ツールインストール
$ pip install pip-tools
Successfully installed build-0.9.0 pep517-0.13.0 pip-tools-6.11.0

# 依存ファイル作成
$ pip-compile requirements.in
requirements.txt

# パッケージインストール
$ pip-sync
```

## APIの実行

- PYTHONPATHへのプロジェクトディレクトリパス追加

```
$ export PYTHONPATH=/Users/yasui/Practice/trend_collector/trend-collector/trendcollector/libs:$PYTHONPATH
$ cd trendcollector
$ uvicorn server:app --reload
```
