
# 0.Git環境準備
1. Gitのインストール確認
```
git --version
```

2. Gitのインストール確認

```
#ユーザー名の確認
git config --global user.name

#メールアドレスの確認
git config --global user.email
```

3. SSHキーの設定
```
cat ~/.ssh/id_rsa.pub
```

3-1. SSHキーの作成
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
このコマンドは、新しいキーペアを生成するプロンプトが表示されると、デフォルトの場所（~/.ssh/id_rsa）にキーペアを保存します。必要に応じて異なる場所に保存するか、パスフレーズを設定することができます。

3-2. SSHキーの公開部分をクリップボードにコピー
```
cat ~/.ssh/id_rsa.pub | xclip -selection clipboard

#wsl環境の場合、下記コマンドでwindowsのクリップボードを利用できる
cat ~/.ssh/id_rsa.pub | clip.exe
```
上記のコマンドは、xclipを使用してキーをクリップボードにコピーします。
`xclip`がインストールされていない場合は、`sudo apt install xclip` または適切なパッケージマネージャを使用してインストールできます。

3-3. GitHubにSSHキーを作成
- GitHubにログインします。
- プロフィールのアイコンをクリックして、Settings を選択します。
- 左のサイドバーで SSH and GPG keys を選択します。
- New SSH key ボタンをクリックします。
- キーのタイトルを入力し（例えば "My Linux Machine"）、先程コピーした公開キーを Key フィールドにペーストします。
- Add SSH key ボタンをクリックしてキーを保存します。

4. GitHubへの接続テスト
```
ssh -T git@github.com
```

# 1. gitのコマンド

すべての変更をステージングエリアに追加するには：
```
# ステージングに追加
git add .
git add [filename]

# ステージングされた変更の確認
git status

#　変更のコミット
git commit -m "コミットメッセージ"
# コミットのログ
git log

# 変更のアップロード
git push origin [branch-name]
```



# GitHubに新しいリポジトリを作成し、ローカルのプロジェクトをそこにプッシュするための手順は以下のとおりです。

1. **GitHubで新しいリポジトリを作成**
    - GitHubにログインします。
    - 右上の「+」アイコンをクリックし、`New repository`を選択します。
    - リポジトリ名を入力し、その他の設定を選択します。
    - `Create repository`ボタンをクリックしてリポジトリを作成します。

2. **ローカルでプロジェクトをgitで管理する**
    - ターミナルやコマンドプロンプトを開き、プロジェクトのディレクトリに移動します。
    - 以下のコマンドを実行して、gitリポジトリを初期化します:
      ```bash
      git init
      ```

3. **ローカルの変更をステージング・コミットする**
    - 以下のコマンドでファイルをステージングします:
      ```bash
      git add .
      ```
    - 以下のコマンドでコミットします:
      ```bash
      git commit -m "初めてのコミット"
      ```

4. **リモートリポジトリを追加する**
    - GitHubで新しく作成したリポジトリのURLをコピーします。
    - 以下のコマンドでリモートリポジトリを追加します（`[URL]`の部分を先ほどコピーしたURLに置き換えてください）:
      ```bash
      git remote add origin [URL]
      ```

5. **ローカルの変更をGitHubにプッシュする**
    - 以下のコマンドで変更をプッシュします:
      ```bash
      git push -u origin master
      ```

これで、ローカルのプロジェクトがGitHubのリポジトリにプッシュされました。今後の変更は、コミットした後に`git push`コマンドを使用してGitHubにプッシュすることができます。


