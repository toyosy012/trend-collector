
## パッケージ管理

[リファレンス](https://packaging.python.org/ja/latest/guides/installing-using-pip-and-virtual-environments/)

[参考](https://qiita.com/ryu22e/items/ad3f8f3df30886d23661)

- プロジェクトディレクトリ毎の依存関係を満たすための作業
- requirements.inに記載
- pip-compileを使うことでrequirements.txtを生成

```
# Enable activation when using venv
$ source venv/bin/activate

# Install a package management tools
$ pip install pip-tools
Successfully installed build-0.9.0 pep517-0.13.0 pip-tools-6.11.0

# Creation of requirements.txt for prod environment
$ vi requirements.in
$ pip-compile requirements.in
requirements.txt

# Creation of requirements.txt for development environment
$ vi requirements.in
`-c requirements.txt` is a configuration for getting package information for the production environment into a file for 
the development environment.

$ pip-compile dev-requirements.in
dev-requirements.txt

# Install packages
$ pip-sync requirements.txt dev-requirements.txt
```

## Linter

```
$ pylint `dir`

# When used in conjunction with plugins for third-party libraries
$ pylint --load-plugins pylint_pydantic `dir`
```

## Sort

```
# module import path sorting
$ isort main.py

# per-directory import path sorting
$ isort -rc terndcollector
```

## APIの実行

```
$ cd trendcollector
$ uvicorn server:app --reload
```

## APIリファレンス

- https://127.0.0.1:8000/docs

## トレンド

### クエリ文字数制限

- varchar(1)は1バイト
- 日本語の常用文字である3バイト(基本多言語面: BMP)文字で30文字
- 90バイトを限度とする
- https://tech.sanwasystem.com/entry/2017/11/13/102531
- https://qiita.com/aki3061/items/65a381145d83b4ee32c6
