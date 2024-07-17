# 『つくりながら学ぶ！生成AIアプリ＆エージェント開発入門』 サンプルコードリポジトリ

このリポジトリは、書籍『つくりながら学ぶ！生成AIアプリ＆エージェント開発入門』のサンプルコードを提供しています。

## ディレクトリ構成

- `.devcontainer`: VS CodeのDevContainerの設定ファイルが含まれています。
  - `Dockerfile`: DevContainerで使用するDockerfileです。
  - `devcontainer.json`: DevContainerの設定ファイルです。
- `.streamlit`: Streamlitの設定ファイルが含まれています。
- `chapter_001`～`chapter_011`: 各章のサンプルコードが格納されています。
- `.env.template`: 環境変数のテンプレートファイルです。
- `.gitignore`: Gitレポジトリの管理対象から外すファイルの設定が記述されています。
- `requirements.txt`: 必要なPythonパッケージが記載されています。


## 使い方

### 環境変数の設定

1. `.env.template`をコピーして`.env`ファイルを作成します。
2. `.env`ファイルに必要な環境変数の値を設定します。以下の環境変数が利用可能です：
   - `OPENAI_API_KEY`: OpenAI APIのAPIキー
   - `ANTHROPIC_API_KEY`: Anthropic APIのAPIキー
   - `GOOGLE_API_KEY`: Google APIのAPIキー
   - `LANGCHAIN_TRACING_V2`: LangChainのトレース機能の有効化設定
   - `LANGCHAIN_ENDPOINT`: LangChainのエンドポイントURL
   - `LANGCHAIN_API_KEY`: LangChainのAPIキー

### 環境変数の読み込み

- このレポジトリでは各章のアプリケーションは`load_dotenv`を利用して`.env`ファイルから環境変数を読み込みます。
  - そのため、事前に環境変数を設定しておく必要があります。
  - `load_dotenv`を利用しない場合は、`from dotenv import load_dotenv; load_dotenv()`の周辺の行を削除してください。

### (オプション) DevContainerの利用

- このリポジトリはVS CodeのDevContainerに対応しています。
  - DevContainerを利用する際はDockerが事前にインストールされている必要があります。
- DevContainerを利用する場合は以下の手順で開発環境を構築できます：
  - ルートディレクトリをVS Codeで開きます。
  - 「コンテナで開く」オプションを選択して開きます。
  - しばらくするとDocker Containerのビルドが実行されます。
  - コンテナ内でStreamlitアプリケーションを起動すると、`local:8501`でアクセスできます
    - 8501ポートをコンテナに開放するようにDockerfileに設定されています

## 注意事項

- 各章のアプリケーションを実行する際は、必要なパッケージがインストールされていることを確認してください。
  - `requirements.txt`に記載されているパッケージは、DevContainerを利用する場合は自動的にインストールされます。

## 各社のモデルの最新状況
- 各社のモデルは随時更新されています。そのため出版時から状況が変化していることがあります。
- ChatGPT, Claude, Gemini の主要なモデルの最新状況は以下の記事か各社のホームページで確認してください
  - [【随時更新】主要な大規模言語モデル比較表](https://zenn.dev/ml_bear/articles/3c5e7975f1620a)

## 各章のアプリケーション・エージェントの動作例

TODO: 動画を足す
