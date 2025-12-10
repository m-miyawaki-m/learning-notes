# WebLogic × VSCode 連携チートシート

> クイックリファレンス: WebLogic開発でよく使うVSCode設定・コマンド・トラブル対処

---

## 目次

1. [連携のシンプルさ](#連携のシンプルさ)
2. [初回セットアップ（5分）](#初回セットアップ5分)
3. [日常の開発フロー](#日常の開発フロー)
4. [よく使うVSCode設定](#よく使うvscode設定)
5. [デバッグ設定（launch.json）](#デバッグ設定launchjson)
6. [Gradle操作コマンド](#gradle操作コマンド)
7. [WebLogic操作コマンド](#weblogic操作コマンド)
8. [トラブルシューティング](#トラブルシューティング)
9. [キーボードショートカット](#キーボードショートカット)

---

## 連携のシンプルさ

### 重要な前提: 連携は「ポート接続だけ」

VSCodeとWebLogicの連携は驚くほどシンプルです。**お互いを特別に意識する必要はありません**。

```
┌─────────────────┐                    ┌──────────────────┐
│   VSCode        │                    │  WebLogic        │
│                 │                    │                  │
│  ✓ Java設定済み │                    │  ✓ デバッグポート│
│  ✓ Gradle認識済│ ─── ポート8453 ───→ │    開放済み      │
│  ✓ launch.json │    で接続するだけ   │  ✓ アプリ起動済 │
└─────────────────┘                    └──────────────────┘
```

### なぜシンプルなのか

標準的な**JDWPプロトコル**を使うため：

- WebLogic側は「Javaプロセスとしてデバッグポートを開く」だけ
- VSCode側は「そのポートに接続する」だけ
- 両者は相手が何か（WebLogic/VSCode）を知らなくてもよい

### 最小設定の実態

#### WebLogic側（1行だけ）

`setDomainEnv.sh` に追加：
```bash
export JAVA_OPTIONS="$JAVA_OPTIONS -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8453"
```

#### VSCode側（数行だけ）

`.vscode/launch.json`:
```json
{
  "type": "java",
  "name": "WebLogic",
  "request": "attach",
  "hostName": "localhost",
  "port": 8453
}
```

### 日常の使い方

```bash
# 1. WebLogic起動（普通に起動するだけ）
./startWebLogic.sh

# 2. VSCodeでF5押すだけ
# → 自動的に接続される

# それだけ！
```

### よくある誤解

| 誤解 | 実際 |
|------|------|
| WebLogic専用の設定が必要 | 不要（標準JDWP） |
| 特別なプラグインが必要 | 不要（Java拡張だけ） |
| 複雑な連携設定が必要 | 不要（ポート番号合わせるだけ） |
| ビルドツールと連携が必須 | 不要（Gradleビルドは別作業） |

### チェックリスト

連携に必要なのはこれだけ：

**WebLogic側**:
- [ ] デバッグポート設定（-Xdebug）
- [ ] ポートが開いている（8453等）

**VSCode側**:
- [ ] Java拡張機能インストール済み
- [ ] launch.jsonでポート指定

**両方が揃えば**:
- [ ] F5押すだけで接続完了

---

## 初回セットアップ（5分）

### 1. 必須VSCode拡張機能

```bash
# 拡張機能のインストール
code --install-extension vscjava.vscode-java-pack
code --install-extension vscjava.vscode-gradle
code --install-extension redhat.java
```

または、`.vscode/extensions.json` に記述：

```json
{
  "recommendations": [
    "vscjava.vscode-java-pack",
    "vscjava.vscode-gradle",
    "redhat.java",
    "vscjava.vscode-java-debug"
  ]
}
```

### 2. 最小限のsettings.json

`.vscode/settings.json`:

```json
{
  "java.home": "/usr/lib/jvm/java-11-openjdk",
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-11",
      "path": "/usr/lib/jvm/java-11-openjdk",
      "default": true
    }
  ],
  "java.import.gradle.enabled": true,
  "java.import.gradle.wrapper.enabled": true,
  "files.exclude": {
    "**/.gradle": true,
    "**/build": true
  }
}
```

### 3. 最小限のlaunch.json（リモートデバッグ）

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "WebLogic Debug",
      "request": "attach",
      "hostName": "localhost",
      "port": 8453
    }
  ]
}
```

---

## 日常の開発フロー

### パターン1: コード編集 → ビルド → デプロイ → デバッグ

```bash
# 1. VSCodeでコード編集
# 2. ビルド
./gradlew clean build

# 3. WARファイルの確認
ls -lh build/libs/*.war

# 4. WebLogicにデプロイ（管理コンソールまたはWLST）
# http://localhost:7001/console

# 5. VSCodeでデバッグ開始（F5）
```

### パターン2: ホットデプロイ（開発時）

```bash
# WebLogic起動時に開発モードで起動
# startWebLogic.sh または setDomainEnv.sh で設定

# Gradleの継続ビルド
./gradlew build --continuous

# ファイル変更を検知して自動ビルド → WebLogicが自動再デプロイ
```

---

## よく使うVSCode設定

### 基本設定（settings.json）

```json
{
  // Java設定
  "java.home": "/usr/lib/jvm/java-11-openjdk",
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-11",
      "path": "/usr/lib/jvm/java-11-openjdk",
      "default": true
    }
  ],

  // Gradle設定
  "java.import.gradle.enabled": true,
  "java.import.gradle.wrapper.enabled": true,
  "java.import.gradle.home": "/opt/gradle",
  "java.import.gradle.java.home": "/usr/lib/jvm/java-11-openjdk",

  // 除外設定（パフォーマンス改善）
  "files.exclude": {
    "**/.gradle": true,
    "**/.settings": true,
    "**/.classpath": true,
    "**/.project": true,
    "**/build": true,
    "**/bin": true
  },
  "search.exclude": {
    "**/build": true,
    "**/.gradle": true
  },

  // 保存時フォーマット
  "editor.formatOnSave": true,
  "[java]": {
    "editor.defaultFormatter": "redhat.java",
    "editor.tabSize": 4
  }
}
```

### マルチモジュールプロジェクト設定

```json
{
  "java.project.sourcePaths": [
    "web-module/src/main/java",
    "business-module/src/main/java",
    "common-module/src/main/java"
  ],
  "java.project.outputPath": "bin",
  "java.project.referencedLibraries": [
    "lib/**/*.jar",
    "${env:WEBLOGIC_HOME}/wlserver/server/lib/weblogic.jar"
  ]
}
```

---

## デバッグ設定（launch.json）

### 基本: リモートデバッグ（Attach）

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "Attach to WebLogic",
      "request": "attach",
      "hostName": "localhost",
      "port": 8453,
      "projectName": "myapp"
    }
  ]
}
```

### 応用: 複数サーバー対応

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "WebLogic - Server1 (8453)",
      "request": "attach",
      "hostName": "localhost",
      "port": 8453
    },
    {
      "type": "java",
      "name": "WebLogic - Server2 (8454)",
      "request": "attach",
      "hostName": "localhost",
      "port": 8454
    },
    {
      "type": "java",
      "name": "WebLogic - Production",
      "request": "attach",
      "hostName": "192.168.1.100",
      "port": 8453,
      "timeout": 30000
    }
  ]
}
```

### ソースパス指定（外部プロジェクト参照時）

```json
{
  "type": "java",
  "name": "WebLogic Debug with Source",
  "request": "attach",
  "hostName": "localhost",
  "port": 8453,
  "sourcePaths": [
    "${workspaceFolder}/src/main/java",
    "/path/to/external/project/src/main/java"
  ]
}
```

---

## Gradle操作コマンド

### 基本コマンド

```bash
# クリーン
./gradlew clean

# ビルド
./gradlew build

# クリーン＋ビルド
./gradlew clean build

# テストスキップビルド
./gradlew build -x test

# WARファイル生成
./gradlew war

# 依存関係の確認
./gradlew dependencies

# タスク一覧
./gradlew tasks

# プロジェクト情報
./gradlew projects

# 継続ビルド（ファイル監視）
./gradlew build --continuous
```

### トラブル対処コマンド

```bash
# Gradleキャッシュクリア
./gradlew clean --refresh-dependencies

# Gradleデーモン停止
./gradlew --stop

# デバッグモードでビルド
./gradlew build --debug

# スタックトレース表示
./gradlew build --stacktrace

# オフラインモード（ネットワーク不要）
./gradlew build --offline
```

### VSCode統合Gradle操作

1. `Ctrl+Shift+P` → "Gradle: Run a Gradle Task"
2. Gradle Elephantアイコン（サイドバー）からタスク実行
3. `build.gradle` 右クリック → "Run Gradle Task"

---

## WebLogic操作コマンド

### サーバー起動・停止

```bash
# 管理サーバー起動（Linux）
cd $DOMAIN_HOME
./startWebLogic.sh

# 管理サーバー起動（Windows）
cd %DOMAIN_HOME%
startWebLogic.cmd

# 管理対象サーバー起動
./startManagedWebLogic.sh server1 http://localhost:7001

# サーバー停止
./stopWebLogic.sh
./stopManagedWebLogic.sh server1
```

### デバッグモード起動

#### 方法1: 起動スクリプト編集

`$DOMAIN_HOME/bin/setDomainEnv.sh` に追記：

```bash
export JAVA_OPTIONS="$JAVA_OPTIONS -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8453"
```

#### 方法2: 起動時に環境変数設定

```bash
export DEBUG_PORT=8453
./startWebLogic.sh
```

#### 方法3: 管理コンソールで設定

1. http://localhost:7001/console
2. Environment → Servers → [サーバー名]
3. Configuration → Server Start タブ
4. Arguments欄に追加：
   ```
   -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8453
   ```

### デプロイコマンド（WLST）

```python
# WLSTスクリプト例: deploy.py
connect('weblogic','password','t3://localhost:7001')
deploy('myapp', '/path/to/myapp.war', targets='AdminServer')
disconnect()
exit()
```

実行：
```bash
java weblogic.WLST deploy.py
```

### ログ確認

```bash
# 管理サーバーログ
tail -f $DOMAIN_HOME/servers/AdminServer/logs/AdminServer.log

# アプリケーションログ
tail -f $DOMAIN_HOME/servers/AdminServer/logs/myapp.log

# アクセスログ
tail -f $DOMAIN_HOME/servers/AdminServer/logs/access.log
```

---

## トラブルシューティング

### 問題1: VSCodeでJavaプロジェクトが認識されない

**症状**: インポートエラー、補完が効かない

**解決**:
```bash
# 1. Java Language Serverのクリーンアップ
Ctrl+Shift+P → "Java: Clean Language Server Workspace"

# 2. VSCode再起動

# 3. Gradleプロジェクトの再インポート
Ctrl+Shift+P → "Java: Reload Projects"

# 4. settings.jsonの確認
{
  "java.home": "/usr/lib/jvm/java-11-openjdk",
  "java.import.gradle.enabled": true
}
```

### 問題2: デバッガーが接続できない

**症状**: "Failed to connect to remote VM"

**原因と解決**:
```bash
# 1. WebLogicがデバッグモードで起動しているか確認
netstat -an | grep 8453
# または
ss -tulpn | grep 8453

# 2. JDWPパラメータの確認
ps aux | grep java | grep Xdebug

# 正しい設定:
-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8453

# 3. ファイアウォール確認（リモートの場合）
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=8453/tcp --permanent
sudo firewall-cmd --reload

# 4. launch.jsonのポート番号確認
{
  "port": 8453  // WebLogicの設定と一致すること
}
```

### 問題3: ブレークポイントで止まらない

**原因と解決**:

1. **ソースコードとWARが一致していない**
   ```bash
   # 最新のWARを再ビルド・再デプロイ
   ./gradlew clean build
   # WebLogic管理コンソールで再デプロイ
   ```

2. **クラスパスの問題**
   ```json
   // launch.jsonにソースパス追加
   {
     "sourcePaths": [
       "${workspaceFolder}/src/main/java"
     ]
   }
   ```

3. **コンパイル時にデバッグ情報が削除されている**
   ```gradle
   // build.gradle
   tasks.withType(JavaCompile) {
       options.compilerArgs << '-g'  // デバッグ情報を含める
       options.debug = true
   }
   ```

### 問題4: Gradleビルドが遅い

**解決**:
```bash
# 1. Gradleデーモン有効化
echo "org.gradle.daemon=true" >> ~/.gradle/gradle.properties

# 2. 並列ビルド有効化
echo "org.gradle.parallel=true" >> ~/.gradle/gradle.properties

# 3. メモリ設定
echo "org.gradle.jvmargs=-Xmx2048m -XX:MaxMetaspaceSize=512m" >> ~/.gradle/gradle.properties

# 4. ビルドキャッシュ有効化
echo "org.gradle.caching=true" >> ~/.gradle/gradle.properties
```

### 問題5: WebLogicのクラスが見つからない

**症状**: `NoClassDefFoundError: weblogic/servlet/...`

**解決**:
```json
// settings.json
{
  "java.project.referencedLibraries": [
    "${env:WEBLOGIC_HOME}/wlserver/server/lib/weblogic.jar",
    "${env:WEBLOGIC_HOME}/wlserver/server/lib/api.jar"
  ]
}
```

または `build.gradle`:
```gradle
dependencies {
    compileOnly files("${System.env.WEBLOGIC_HOME}/wlserver/server/lib/weblogic.jar")
}
```

### 問題6: メモリ不足エラー

**症状**: `OutOfMemoryError: Java heap space`

**解決**:
```bash
# setDomainEnv.sh または setDomainEnv.cmd
export USER_MEM_ARGS="-Xms1024m -Xmx2048m -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m"

# VSCode Java Language Server
// settings.json
{
  "java.jdt.ls.vmargs": "-Xmx2G -Xms256m"
}
```

---

## キーボードショートカット

### VSCode標準（Windows/Linux）

| 操作 | ショートカット |
|------|--------------|
| デバッグ開始/続行 | `F5` |
| デバッグ停止 | `Shift+F5` |
| ステップオーバー | `F10` |
| ステップイン | `F11` |
| ステップアウト | `Shift+F11` |
| ブレークポイントトグル | `F9` |
| コマンドパレット | `Ctrl+Shift+P` |
| ファイル検索 | `Ctrl+P` |
| シンボル検索 | `Ctrl+T` |
| 定義へジャンプ | `F12` |
| 参照の検索 | `Shift+F12` |
| 名前の変更 | `F2` |
| フォーマット | `Shift+Alt+F` |

### Java拡張機能

| 操作 | ショートカット |
|------|--------------|
| インポートの整理 | `Shift+Alt+O` |
| クイックフィックス | `Ctrl+.` |
| 実装へジャンプ | `Ctrl+F12` |

### カスタムショートカット（推奨設定）

`.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+b",
    "command": "workbench.action.tasks.build",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+d",
    "command": "workbench.action.debug.start",
    "when": "!inDebugMode"
  },
  {
    "key": "ctrl+shift+r",
    "command": "java.projectConfiguration.update"
  }
]
```

---

## よく使うタスク設定（tasks.json）

`.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Gradle: Clean Build",
      "type": "shell",
      "command": "./gradlew clean build",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": []
    },
    {
      "label": "Gradle: Build WAR",
      "type": "shell",
      "command": "./gradlew war",
      "group": "build"
    },
    {
      "label": "WebLogic: Tail Log",
      "type": "shell",
      "command": "tail -f ${env:DOMAIN_HOME}/servers/AdminServer/logs/AdminServer.log",
      "isBackground": true
    },
    {
      "label": "Deploy to WebLogic",
      "type": "shell",
      "command": "java weblogic.WLST scripts/deploy.py",
      "dependsOn": ["Gradle: Build WAR"]
    }
  ]
}
```

実行: `Ctrl+Shift+P` → "Tasks: Run Task"

---

## クイックリファレンス表

### ポート番号

| サービス | デフォルトポート | 用途 |
|---------|----------------|------|
| 管理サーバー | 7001 | 管理コンソール |
| 管理サーバー（SSL） | 7002 | HTTPS管理 |
| 管理対象サーバー | 8001+ | アプリケーション |
| デバッグポート | 8453 | JDWP |

### 重要ディレクトリ

| パス | 説明 |
|------|------|
| `$DOMAIN_HOME` | WebLogicドメインルート |
| `$DOMAIN_HOME/bin` | 起動スクリプト |
| `$DOMAIN_HOME/config` | 設定ファイル |
| `$DOMAIN_HOME/servers/[サーバー名]/logs` | ログ |
| `$DOMAIN_HOME/autodeploy` | オートデプロイ |
| `$WEBLOGIC_HOME` | WebLogicインストール先 |

### 環境変数

| 変数名 | 説明 |
|--------|------|
| `JAVA_HOME` | JDKインストールパス |
| `WEBLOGIC_HOME` | WebLogicインストールパス |
| `DOMAIN_HOME` | ドメインディレクトリ |
| `USER_MEM_ARGS` | JVMメモリ設定 |
| `JAVA_OPTIONS` | JVMオプション |

---

## 参考ドキュメント

- [vscode-weblogic-debug.md](vscode-weblogic-debug.md) - 詳細なデバッグ設定
- [vscode-gradle-weblogic-setup.md](vscode-gradle-weblogic-setup.md) - 環境構築ガイド
- [vscode-multi-project-workspace.md](vscode-multi-project-workspace.md) - マルチプロジェクト設定
- [weblogic-configuration.md](weblogic-configuration.md) - WebLogic基本設定
- [wlst-cli-windows.md](wlst-cli-windows.md) - WLST操作ガイド
