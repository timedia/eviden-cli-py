[![CircleCI](https://circleci.com/gh/timedia/eviden-cli-py/tree/master.svg?style=svg)](https://circleci.com/gh/timedia/eviden-cli-py/tree/master)

# eviden-cli-py
Pythonによるtim社内ツールEvidenのCLIラッパーツールです
## dependency
* pipenv
* python3
## setup
```
# 最初にこのリポジトリのcloneをしておく
$ pip install git+https://github.com/timedia/eviden-cli-py
$ eviden <command>
```
## commands
### setup
依存性のあるディレクトリ/ファイルの生成を行います
### login <user_id>
user_idによるloginを試みます。
パスワードの入力が要求されます。
### list *1
現在ログインしているユーザーが参加しているプロジェクトの一覧が表示されます
### select <project_name> *1
project_nameで指定したプロジェクトを選択した状態になります
### issues *2
selectで選択したプロジェクトに投稿されているイシューの一覧が表示されます 
### post <title> <text> *2
指定したタイトルと本文で選択されているプロジェクトにイシューを投稿します

> *1 : 要ログイン
> *2 : 要プロジェクト選択

## author
濱田（2019/02インターン）
