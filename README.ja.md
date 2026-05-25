# ekiben

bento.me のような個人プロフィールページを生成する静的サイトジェネレーターです。

YAMLでレイアウトを定義して、コマンド一発でデプロイ可能なHTMLページを生成します。

[English README](README.md)

## インストール

```bash
pip install ekiben
```

## クイックスタート

```bash
mkdir my-site && cd my-site
ekiben init
# site.yaml を編集して、assets/ に画像を配置する
ekiben serve       # http://localhost:8080 でライブリロード付きプレビュー
ekiben build       # dist/ に出力
```

## site.yaml

```yaml
profile:
  name: "山田 太郎"
  avatar: "./assets/avatar.png"  # 任意
  bio: "エンジニア / 東京"        # 任意

theme:
  background: "#f5f5f0"
  card_background: "#ffffff"
  accent: "#3b82f6"
  font_family: "system-ui, sans-serif"
  border_radius: 16
  card_shadow: true

blocks:
  - type: text
    size: 2x1
    content: "👋 こんにちは！"

  - type: link
    size: 1x1
    title: "ブログ"
    url: "https://example.com"
    # image: "./assets/blog.png"  # 任意。省略するとURLのOGP画像を自動取得

  - type: social
    size: 1x1
    platform: github
    username: "your-username"

  - type: social
    size: 1x1
    platform: x
    username: "your-handle"

  - type: social
    size: 1x1
    platform: misskey
    username: "your-username"
    instance: "misskey.io"

  - type: spacer
    size: 1x1
```

### ブロックの種類

| タイプ | 説明 |
|--------|------|
| `text` | 見出し・自己紹介などのテキストカード |
| `link` | タイトルと画像付きのリンクカード（画像未指定時はURLのOGP画像を自動取得）。GIF対応。 |
| `social` | ビルド時にX・GitHub・Misskeyのプロフィール情報を取得して表示するカード |
| `spacer` | レイアウトの隙間を作る空のセル |

### サイズ

`1x1` · `2x1` · `1x2` · `2x2` — 横×縦のグリッド単位で指定します。

グリッドはデスクトップで4列、モバイルで2列に自動折りたたみされます。ブロックは左上から順に配置されます。

### カードごとの背景色

`spacer` 以外のブロックには `color` フィールドでカード背景色を個別に指定できます：

```yaml
- type: text
  size: 1x1
  color: "#fef3c7"
  content: "目立たせたいカード"
```

## ソーシャルプラットフォーム

| プラットフォーム | 認証 |
|----------------|------|
| GitHub | 不要（公開API） |
| X | `TWITTER_BEARER_TOKEN` 環境変数が必要 |
| Misskey | 不要（YAMLの `instance:` フィールドでインスタンスURLを指定） |

## GitHub Pages へのデプロイ

### ステップ1 — サイト用リポジトリを作成する

GitHubで新しいリポジトリを作成（例: `my-profile`）し、以下を実行します：

```bash
mkdir my-profile && cd my-profile
ekiben init --with-actions
# site.yaml を編集して、assets/ に画像を配置する
git init -b main
git add .
git commit -m "Initial site"
git remote add origin git@github.com:<ユーザー名>/my-profile.git
git push -u origin main
```

### ステップ2 — GitHub Pages を有効にする

1. GitHubでリポジトリを開く
2. **Settings → Pages** を開く
3. **Source** で **GitHub Actions** を選択する

`main` ブランチへのプッシュのたびにワークフローが自動実行されます。公開URLは以下になります：

```
https://<ユーザー名>.github.io/<リポジトリ名>/
```

### ステップ3 — シークレットを登録する（Xブロックを使う場合のみ）

`platform: x` のブロックを使う場合、Bearer Tokenをリポジトリのシークレットに登録します：

1. **Settings → Secrets and variables → Actions** を開く
2. **New repository secret** をクリック
3. 名前: `TWITTER_BEARER_TOKEN` / 値: [X Developer Portal](https://developer.twitter.com/) のBearer Token

GitHubブロックとMisskeyブロックはシークレット不要です。

### サイトを更新する

`site.yaml` や `assets/` を編集してコミット・プッシュするだけで、自動的に再ビルド＆再デプロイされます：

```bash
# 例: 自己紹介を更新する
# site.yaml を編集 ...
git add site.yaml
git commit -m "自己紹介を更新"
git push
```

## CLIリファレンス

```
ekiben init [--with-actions]                   site.yamlテンプレートを生成（GitHub Actionsワークフローも生成）
ekiben build [--input .] [--output dist]       サイトをビルドして出力ディレクトリに書き出す
ekiben serve [--input .] [--port 8080]         ライブリロード付きでローカルプレビューサーバーを起動する
```
