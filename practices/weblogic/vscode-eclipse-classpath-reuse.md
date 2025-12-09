# VSCode × Eclipse クラスパス活用ガイド

> EclipseのクラスパスをVSCodeで再利用してWebLogicデバッグ環境を構築

既にEclipseで作成された `.classpath` ファイルをそのままVSCodeで活用し、WebLogicのデバッグ環境を構築する方法を解説します。

---

## 目次

1. [概要](#概要)
2. [Eclipseクラスパスの確認](#eclipseクラスパスの確認)
3. [VSCodeでの活用方法](#vscodeでの活用方法)
4. [デバッグ設定](#デバッグ設定)
5. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### Eclipseクラスパスとは

Eclipseプロジェクトには以下のファイルが存在します：

```
my-project/
├── .classpath              # クラスパス定義（依存関係、ソースパス）
├── .project                # プロジェクト設定
├── .settings/              # Eclipse固有の設定
│   ├── org.eclipse.jdt.core.prefs
│   └── org.eclipse.wst.common.component
└── src/
    └── main/
        └── java/
```

### VSCodeでの活用

```
┌─────────────────────────────────────────────────────┐
│         Eclipse .classpath ファイル                   │
│                                                     │
│  - 依存ライブラリ（Spring, Struts2, etc）              │
│  - ソースパス（src/main/java）                        │
│  - 出力パス（build/classes）                          │
└─────────────────────────────────────────────────────┘
                      │
                      │ VSCode Java拡張機能が自動認識
                      ▼
┌─────────────────────────────────────────────────────┐
│          VSCode Java Language Server                │
│                                                     │
│  - コード補完                                         │
│  - 参照ジャンプ                                       │
│  - リファクタリング                                    │
│  - デバッグ対応                                       │
└─────────────────────────────────────────────────────┘
```

**メリット**:
- Eclipseで既に設定済みの依存関係をそのまま使用
- Gradleやプロジェクト固有の設定は不要
- `.classpath` を変更すれば自動的にVSCodeにも反映

---

## Eclipseクラスパスの確認

### .classpath ファイルの構造

```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <!-- ソースパス -->
    <classpathentry kind="src" path="src/main/java"/>
    <classpathentry kind="src" path="src/main/resources"/>
    <classpathentry kind="src" output="build/test-classes" path="src/test/java"/>

    <!-- JDK -->
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/
        org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-11"/>

    <!-- 依存ライブラリ（例: Spring） -->
    <classpathentry kind="lib" path="lib/spring-context-5.3.27.jar" sourcepath="lib/spring-context-5.3.27-sources.jar"/>
    <classpathentry kind="lib" path="lib/spring-webmvc-5.3.27.jar"/>
    <classpathentry kind="lib" path="lib/spring-jdbc-5.3.27.jar"/>

    <!-- Struts2 -->
    <classpathentry kind="lib" path="lib/struts2-core-2.5.30.jar"/>

    <!-- WebLogic provided（コンテナ提供） -->
    <classpathentry kind="lib" path="lib/javax.servlet-api-4.0.1.jar"/>

    <!-- 出力パス -->
    <classpathentry kind="output" path="build/classes"/>
</classpath>
```

### 確認方法

```bash
# プロジェクトディレクトリに .classpath が存在するか確認
cd /path/to/my-project
ls -la .classpath

# 内容を確認
cat .classpath
```

出力例:
```
-rw-r--r-- 1 user user 2456 Dec 10 10:00 .classpath
```

---

## VSCodeでの活用方法

### ステップ1: VSCodeでプロジェクトを開く

```bash
# Eclipseプロジェクトを直接VSCodeで開く
code /path/to/my-project
```

**重要**: プロジェクトルート（`.classpath` が存在するディレクトリ）を開いてください。

### ステップ2: Java拡張機能のインストール

VSCodeを開いたら、以下の拡張機能をインストール：

```
Extension Pack for Java (vscjava.vscode-java-pack)
```

インストール方法:
```bash
code --install-extension vscjava.vscode-java-pack
```

または、VSCode UI:
1. 拡張機能パネルを開く (`Ctrl+Shift+X`)
2. "Extension Pack for Java" を検索
3. **Install** をクリック

### ステップ3: VSCodeが自動的にプロジェクトをインポート

VSCodeのJava拡張機能が `.classpath` を自動的に検出してインポートします。

#### インポートプロセス

1. VSCodeを開く
2. 右下に通知が表示される:
   ```
   Importing Java projects...
   ```
3. 数秒〜数分待つ（プロジェクトサイズによる）
4. 完了通知:
   ```
   Java projects imported successfully
   ```

#### ステータス確認

VSCodeのステータスバー（左下）で確認:
```
Java: Ready
```

または、出力パネルで確認:
```
Ctrl+Shift+U → "Language Support for Java" を選択
```

### ステップ4: .vscode/settings.json の作成（オプション）

基本的には `.classpath` があれば不要ですが、追加設定が必要な場合:

```json
{
    // Eclipseプロジェクトを優先
    "java.import.eclipse.enabled": true,

    // 自動ビルド
    "java.autobuild.enabled": true,

    // デバッグ設定
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true,

    // ファイル除外（Eclipse固有ファイルを非表示）
    "files.exclude": {
        "**/.settings": true,
        "**/.project": false,  // .projectは表示（編集する場合があるため）
        "**/.classpath": false  // .classpathも表示
    }
}
```

### ステップ5: デバッグ設定（.vscode/launch.json）

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/src/main/java"
            ]
        }
    ]
}
```

マルチモジュールの場合:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (Multi-Module)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/web-module/src/main/java",
                "${workspaceFolder}/business-module/src/main/java",
                "${workspaceFolder}/common-module/src/main/java"
            ]
        }
    ]
}
```

---

## デバッグ設定

### WebLogic側の設定

#### setDomainEnv.sh の編集

```bash
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

追加:
```bash
# デバッグ設定
if [ "${SERVER_NAME}" = "ManagedServer1" ] ; then
    DEBUG_PORT="8453"
    JAVA_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
    JAVA_OPTIONS="${JAVA_OPTIONS} ${JAVA_DEBUG}"

    echo "Debug mode enabled on port ${DEBUG_PORT}"
fi

export JAVA_OPTIONS
```

#### WebLogicの起動

```bash
cd /opt/oracle/domains/my_domain/bin
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

ログで確認:
```
Listening for transport dt_socket at address: 8453
```

### デバッグの実行

1. **ブレークポイントを設定**
   - VSCodeでJavaファイルを開く
   - 行番号の左をクリックして赤い点を表示

2. **デバッグセッション開始**
   - `F5` を押す
   - または、デバッグパネル（`Ctrl+Shift+D`）→ 再生ボタン

3. **接続成功**
   ```
   Debugger attached successfully
   ```

4. **アプリケーションをテスト**
   ```bash
   curl http://localhost:7003/myapp/users
   ```

5. **ブレークポイントで停止**
   - VSCodeがアクティブになり、実行が停止
   - 変数、スタックトレースを確認可能

---

## Eclipseクラスパスの更新

### 依存関係を追加した場合

Eclipseで依存関係を追加すると、`.classpath` が自動的に更新されます。

#### Eclipse側の操作

1. Eclipseでプロジェクトを右クリック
2. **Build Path > Configure Build Path...**
3. **Libraries** タブ → **Add External JARs...**
4. ライブラリを追加
5. **Apply and Close**

`.classpath` が更新される:
```xml
<!-- 新しいライブラリが追加される -->
<classpathentry kind="lib" path="lib/commons-lang3-3.12.0.jar"/>
```

#### VSCode側の操作

VSCodeは自動的に変更を検出しますが、認識されない場合:

```
Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
```

または、VSCodeを再起動:
```
Ctrl+Shift+P → "Reload Window"
```

### 手動で .classpath を編集する場合

```bash
vi /path/to/my-project/.classpath
```

追加:
```xml
<classpathentry kind="lib" path="lib/new-library.jar"/>
```

VSCodeリロード:
```
Ctrl+Shift+P → "Reload Window"
```

---

## 実践例: 完全な開発フロー

### シナリオ: Eclipseプロジェクトを初めてVSCodeで開く

#### 1. プロジェクト構成の確認

```bash
cd /path/to/my-project
ls -la

# 出力例:
# -rw-r--r-- 1 user user  2456 Dec 10 10:00 .classpath
# -rw-r--r-- 1 user user   835 Dec 10 10:00 .project
# drwxr-xr-x 2 user user  4096 Dec 10 10:00 .settings
# drwxr-xr-x 3 user user  4096 Dec 10 10:00 src
# drwxr-xr-x 2 user user  4096 Dec 10 10:00 lib
```

#### 2. VSCodeで開く

```bash
code /path/to/my-project
```

#### 3. Java拡張機能のインストール（初回のみ）

VSCodeが推奨拡張機能のインストールを提案する:
```
This workspace has recommended extensions.
Show Recommendations
```

**Show Recommendations** → **Install All** をクリック

または、手動でインストール:
```bash
code --install-extension vscjava.vscode-java-pack
```

#### 4. プロジェクトのインポート待機

右下の通知を確認:
```
Importing Java projects...
```

完了まで待つ（1〜5分）。

#### 5. コード確認

Javaファイルを開く:
```
src/main/java/com/example/controller/UserController.java
```

- コード補完が効くか確認（`Ctrl+Space`）
- クラス参照がジャンプできるか確認（`F12`）

#### 6. .vscode/launch.json の作成

```bash
mkdir -p .vscode
vi .vscode/launch.json
```

内容:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "sourcePaths": [
                "${workspaceFolder}/src/main/java"
            ]
        }
    ]
}
```

#### 7. WebLogicの設定とデバッグ

```bash
# WebLogicのデバッグモード有効化
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
# （デバッグ設定を追加）

# WebLogic起動
/opt/oracle/domains/my_domain/bin/startManagedWebLogic.sh ManagedServer1 http://localhost:7001

# VSCodeでデバッグ開始
# F5 を押す
```

#### 8. ブレークポイントでテスト

- `UserController.java` の該当行にブレークポイント設定
- ブラウザまたはcurlでアクセス:
  ```bash
  curl http://localhost:7003/myapp/users
  ```
- VSCodeで実行が停止
- 変数の値を確認

---

## トラブルシューティング

### 問題1: VSCodeが .classpath を認識しない

#### 症状
```
Java projects are not recognized
```

#### 解決方法

**方法1: Java拡張機能を再インストール**
```
拡張機能パネル → "Extension Pack for Java" → Uninstall
→ Reload Window → "Extension Pack for Java" → Install
```

**方法2: Java Language Serverをクリーン**
```
Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
→ "Reload and Delete" を選択
```

**方法3: .classpath の構文確認**
```bash
# XMLの構文エラーがないか確認
xmllint --noout .classpath

# エラーがある場合:
# .classpath:15: parser error : Opening and ending tag mismatch
```

### 問題2: 依存関係が見つからない

#### 症状
```java
import org.springframework.stereotype.Service;
```
が赤線（エラー）になる。

#### 解決方法

**方法1: .classpath のパス確認**
```xml
<!-- パスが正しいか確認 -->
<classpathentry kind="lib" path="lib/spring-context-5.3.27.jar"/>
```

実際にファイルが存在するか確認:
```bash
ls -la lib/spring-context-5.3.27.jar
```

**方法2: 相対パス vs 絶対パス**

相対パス（推奨）:
```xml
<classpathentry kind="lib" path="lib/spring-context-5.3.27.jar"/>
```

絶対パス（移植性が低い）:
```xml
<classpathentry kind="lib" path="/opt/project/lib/spring-context-5.3.27.jar"/>
```

**方法3: VSCodeリロード**
```
Ctrl+Shift+P → "Reload Window"
```

### 問題3: デバッグ時にソースが見つからない

#### 症状
```
Source not found for UserService.class
```

#### 解決方法

**方法1: sourcePaths を確認**

.vscode/launch.json:
```json
{
    "sourcePaths": [
        "${workspaceFolder}/src/main/java"  // ← パスが正しいか確認
    ]
}
```

**方法2: .classpath にソースが含まれているか確認**
```xml
<classpathentry kind="src" path="src/main/java"/>  <!-- ← これが必要 -->
```

**方法3: ビルド時にデバッグ情報を含める**

コンパイルオプションで `-g` を指定:
```bash
javac -g -d build/classes src/main/java/com/example/**/*.java
```

### 問題4: Eclipse設定とVSCode設定が競合する

#### 症状
Eclipseで動作するがVSCodeでエラーになる、またはその逆。

#### 解決方法

**ワークスペースを分ける**:

```
/path/to/my-project/              # Eclipse用
/path/to/my-project-vscode/       # VSCode用（シンボリックリンク）
```

シンボリックリンク作成:
```bash
ln -s /path/to/my-project /path/to/my-project-vscode
code /path/to/my-project-vscode
```

**または、.vscode を .gitignore に追加**:
```gitignore
# VSCode設定（個人用）
.vscode/

# Eclipse設定（チーム共有）
.classpath
.project
.settings/
```

---

## ベストプラクティス

### 1. .classpath の管理

#### Eclipseで自動生成させる

手動編集ではなく、Eclipseの GUI を使用:
- **Build Path > Configure Build Path...**
- ライブラリの追加・削除を GUI で行う
- `.classpath` が自動的に正しい形式で更新される

#### バージョン管理

`.classpath` をGitにコミット（チーム共有）:
```bash
git add .classpath .project
git commit -m "Update Eclipse project configuration"
```

### 2. VSCode設定の共有

#### .vscode/settings.json（チーム共有）

```json
{
    "java.import.eclipse.enabled": true,
    "java.configuration.updateBuildConfiguration": "automatic"
}
```

#### .vscode/launch.json（個人設定）

デバッグ設定は環境依存のため、`.gitignore` に追加:
```gitignore
.vscode/launch.json
```

テンプレートを提供:
```bash
cp .vscode/launch.json .vscode/launch.json.example
```

### 3. 依存関係の整理

#### lib ディレクトリの構成

```
lib/
├── spring/
│   ├── spring-context-5.3.27.jar
│   ├── spring-context-5.3.27-sources.jar  # ソース（コード補完用）
│   └── spring-webmvc-5.3.27.jar
├── struts2/
│   └── struts2-core-2.5.30.jar
└── provided/  # WebLogicで提供されるライブラリ
    └── javax.servlet-api-4.0.1.jar
```

#### .classpath でソースを関連付け

```xml
<classpathentry kind="lib" path="lib/spring/spring-context-5.3.27.jar"
                sourcepath="lib/spring/spring-context-5.3.27-sources.jar"/>
```

これにより、VSCodeでSpringのメソッドにジャンプすると、ソースコードが表示されます。

---

## まとめ

Eclipseの `.classpath` をVSCodeで活用することで、以下が実現できます:

1. **依存関係の再利用** - Eclipseで設定済みのライブラリをそのまま使用
2. **設定不要** - Gradleやその他のビルドツール設定が不要
3. **チーム開発に最適** - `.classpath` を共有すれば全員が同じ環境
4. **WebLogicデバッグ** - `.vscode/launch.json` を追加するだけ

この方法で、既存のEclipseプロジェクトをVSCodeで効率的に開発・デバッグできます。
