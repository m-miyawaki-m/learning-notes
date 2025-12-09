# VSCode + Gradle + WebLogic 実践セットアップガイド

> 本番環境のGradleプロジェクトをVSCodeで開発しながらWebLogicでデバッグする環境構築の実践ガイド

---

## 目次

1. [環境構築の全体像](#環境構築の全体像)
2. [ステップ1: Gradleプロジェクトの準備](#ステップ1-gradleプロジェクトの準備)
3. [ステップ2: VSCode環境の構築](#ステップ2-vscode環境の構築)
4. [ステップ3: WebLogicデバッグ設定](#ステップ3-weblogicデバッグ設定)
5. [ステップ4: 開発フローの確立](#ステップ4-開発フローの確立)
6. [実践例: 完全な開発サイクル](#実践例-完全な開発サイクル)
7. [チーム開発での共有設定](#チーム開発での共有設定)

---

## 環境構築の全体像

### アーキテクチャ図

```
┌──────────────────────────────────────────────────────────────┐
│                    開発ワークフロー                              │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌──────────────────────┐
│  本番Gradleプロジェクト │         │   VSCode IDE         │
│  /path/to/project   │◄────────│   - Java拡張機能      │
│                     │  直接開く  │   - Gradle拡張機能    │
│  ├── settings.gradle│         │   - デバッガー        │
│  ├── build.gradle   │         └──────────────────────┘
│  ├── web-module/    │                    │
│  ├── business-module/│                   │ JDWP
│  └── common-module/ │                    ▼
└─────────────────────┘         ┌──────────────────────┐
         │                      │  WebLogic Server     │
         │ ./gradlew build      │  - Debug Mode ON     │
         ▼                      │  - Port 8453 Listen  │
┌─────────────────────┐         │  - myapp.war         │
│  WARファイル          │────────►└──────────────────────┘
│  build/libs/myapp.war│  Deploy
└─────────────────────┘
```

### 開発フロー

1. **VSCodeでGradleプロジェクトを開く**
2. **コードを編集**
3. **Gradleでビルド** (`./gradlew build`)
4. **WARをWebLogicにデプロイ**
5. **VSCodeデバッガーをWebLogicにアタッチ**
6. **ブレークポイントでデバッグ**
7. **修正 → 再ビルド → 再デプロイ** （繰り返し）

---

## ステップ1: Gradleプロジェクトの準備

### 1.1 プロジェクト構成の確認

本番環境のGradleプロジェクトの構成を確認します。

```bash
# プロジェクトディレクトリに移動
cd /path/to/production/gradle-project

# ディレクトリ構造を確認
tree -L 2 -I 'build|.gradle'
```

想定される構成:

```
gradle-project/
├── settings.gradle              # モジュール定義
├── build.gradle                 # ルートビルド設定
├── gradle.properties            # Gradle設定
├── gradlew                      # Gradleラッパー（Linux/Mac）
├── gradlew.bat                  # Gradleラッパー（Windows）
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── common-module/               # 共通ライブラリモジュール
│   ├── build.gradle
│   └── src/
│       └── main/
│           └── java/
├── business-module/             # ビジネスロジックモジュール
│   ├── build.gradle
│   └── src/
│       └── main/
│           └── java/
└── web-module/                  # Webアプリケーションモジュール
    ├── build.gradle
    └── src/
        ├── main/
        │   ├── java/
        │   └── webapp/
        │       ├── WEB-INF/
        │       │   └── web.xml
        │       └── index.jsp
        └── test/
            └── java/
```

### 1.2 build.gradleのデバッグ設定確認

デバッグ情報がクラスファイルに含まれるように設定します。

#### ルート build.gradle

```groovy
// gradle-project/build.gradle

plugins {
    id 'java'
}

// 全サブプロジェクトに適用
subprojects {
    apply plugin: 'java'

    group = 'com.example.myapp'
    version = '1.0.0-SNAPSHOT'

    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11

    repositories {
        mavenCentral()
        // WebLogic固有のリポジトリ（必要に応じて）
        maven {
            url 'https://maven.oracle.com'
        }
    }

    // デバッグ情報を含める設定
    tasks.withType(JavaCompile) {
        options.encoding = 'UTF-8'
        options.debug = true
        options.debugOptions.debugLevel = 'source,lines,vars'

        // 非推奨警告を表示
        options.compilerArgs << '-Xlint:deprecation'
    }

    // テスト設定
    test {
        useJUnitPlatform()
        testLogging {
            events "passed", "skipped", "failed"
        }
    }
}
```

#### web-module/build.gradle

```groovy
// gradle-project/web-module/build.gradle

plugins {
    id 'war'
}

dependencies {
    // 他のモジュールへの依存
    implementation project(':common-module')
    implementation project(':business-module')

    // WebLogicで提供されるライブラリ（provided）
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
    providedCompile 'javax.servlet.jsp:javax.servlet.jsp-api:2.3.3'

    // Struts2（例）
    implementation 'org.apache.struts:struts2-core:2.5.30'
    implementation 'org.apache.struts:struts2-spring-plugin:2.5.30'

    // Spring（例）
    implementation 'org.springframework:spring-context:5.3.27'
    implementation 'org.springframework:spring-web:5.3.27'

    // ロギング
    implementation 'org.slf4j:slf4j-api:1.7.36'
    runtimeOnly 'ch.qos.logback:logback-classic:1.2.11'

    // テスト
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.mockito:mockito-core:4.6.1'
}

war {
    archiveBaseName = 'myapp'
    archiveVersion = ''  // バージョンなし: myapp.war

    // WEB-INFにlibを含める
    from('src/main/webapp') {
        into('')
    }
}

// デプロイタスクの追加（オプション）
task deployToWebLogic(type: Copy, dependsOn: war) {
    from war.archiveFile
    into '/opt/oracle/domains/my_domain/applications'

    doLast {
        println "Deployed ${war.archiveFileName.get()} to WebLogic"
    }
}
```

#### gradle.properties

```properties
# gradle-project/gradle.properties

# JVM設定
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError

# 並列ビルド
org.gradle.parallel=true

# Gradleデーモン
org.gradle.daemon=true

# ビルドキャッシュ
org.gradle.caching=true

# コンソール出力
org.gradle.console=rich

# プロジェクト固有の設定
weblogic.domain.home=/opt/oracle/domains/my_domain
weblogic.admin.url=t3://localhost:7001
weblogic.username=weblogic
# パスワードは環境変数で管理: WEBLOGIC_PASSWORD
```

### 1.3 ビルドの確認

```bash
# クリーンビルド
./gradlew clean build

# ビルド結果の確認
ls -lh web-module/build/libs/myapp.war

# 依存関係の確認
./gradlew dependencies --configuration runtimeClasspath
```

---

## ステップ2: VSCode環境の構築

### 2.1 VSCodeでプロジェクトを開く

```bash
# 本番Gradleプロジェクトを直接開く
code /path/to/production/gradle-project
```

### 2.2 必要な拡張機能のインストール

VSCodeを開いたら、拡張機能をインストールします。

#### 必須拡張機能

1. **Extension Pack for Java** (Microsoft)
   - ID: `vscjava.vscode-java-pack`
   - 含まれる拡張機能:
     - Language Support for Java (Red Hat)
     - Debugger for Java
     - Test Runner for Java
     - Maven for Java
     - Project Manager for Java
     - Visual Studio IntelliCode

2. **Gradle for Java** (Microsoft)
   - ID: `vscjava.vscode-gradle`

#### オプション拡張機能

3. **Spring Boot Extension Pack** (Pivotal) - Spring使用時
   - ID: `Pivotal.vscode-boot-dev-pack`

4. **GitLens** (GitKraken) - Git履歴確認
   - ID: `eamodio.gitlens`

#### インストール方法

**方法1: VSCode UI**
1. サイドバーの拡張機能アイコンをクリック (Ctrl+Shift+X)
2. 検索ボックスに拡張機能名を入力
3. **Install** をクリック

**方法2: コマンドライン**
```bash
code --install-extension vscjava.vscode-java-pack
code --install-extension vscjava.vscode-gradle
code --install-extension Pivotal.vscode-boot-dev-pack
code --install-extension eamodio.gitlens
```

### 2.3 .vscode/settings.json の作成

プロジェクトルートに `.vscode` ディレクトリを作成し、`settings.json` を設定します。

```bash
cd /path/to/production/gradle-project
mkdir -p .vscode
```

#### .vscode/settings.json

```json
{
    // Java設定
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.import.gradle.enabled": true,
    "java.import.gradle.wrapper.enabled": true,

    // ソースパス設定（マルチモジュール）
    "java.project.sourcePaths": [
        "web-module/src/main/java",
        "business-module/src/main/java",
        "common-module/src/main/java"
    ],

    // 出力ディレクトリ
    "java.project.outputPath": "bin",

    // 参照ライブラリ
    "java.project.referencedLibraries": [
        "web-module/build/libs/**/*.jar",
        "business-module/build/libs/**/*.jar",
        "common-module/build/libs/**/*.jar",
        "lib/**/*.jar"
    ],

    // デバッグ設定
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true,
    "java.debug.settings.enableRunDebugCodeLens": true,

    // Gradle設定
    "gradle.nestedProjects": true,
    "gradle.autoDetect": "on",

    // ファイル除外設定
    "files.exclude": {
        "**/.gradle": true,
        "**/build": false,  // ビルド出力を表示
        "**/.classpath": true,
        "**/.project": true,
        "**/.settings": true,
        "**/.factorypath": true
    },

    // エディタ設定
    "editor.formatOnSave": true,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,

    // Java フォーマット
    "java.format.settings.url": "${workspaceFolder}/.vscode/java-formatter.xml",
    "java.format.settings.profile": "GoogleStyle",

    // ターミナル設定
    "terminal.integrated.env.linux": {
        "JAVA_HOME": "/usr/lib/jvm/java-11-openjdk",
        "WEBLOGIC_HOME": "/opt/oracle/wlserver"
    },

    // 文字エンコーディング
    "files.encoding": "utf8",

    // 検索除外
    "search.exclude": {
        "**/build": true,
        "**/.gradle": true
    }
}
```

### 2.4 .vscode/launch.json の作成（デバッグ設定）

#### .vscode/launch.json

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (ManagedServer1)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "projectName": "web-module",
            "sourcePaths": [
                "${workspaceFolder}/web-module/src/main/java",
                "${workspaceFolder}/business-module/src/main/java",
                "${workspaceFolder}/common-module/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (ManagedServer2)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8454,
            "timeout": 30000,
            "projectName": "web-module",
            "sourcePaths": [
                "${workspaceFolder}/web-module/src/main/java",
                "${workspaceFolder}/business-module/src/main/java",
                "${workspaceFolder}/common-module/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (Remote DEV)",
            "request": "attach",
            "hostName": "${env:DEV_WEBLOGIC_HOST}",
            "port": "${env:DEV_WEBLOGIC_PORT}",
            "timeout": 30000,
            "projectName": "web-module",
            "sourcePaths": [
                "${workspaceFolder}/web-module/src/main/java",
                "${workspaceFolder}/business-module/src/main/java",
                "${workspaceFolder}/common-module/src/main/java"
            ]
        }
    ]
}
```

### 2.5 .vscode/tasks.json の作成（ビルド・デプロイタスク）

#### .vscode/tasks.json

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Gradle: Clean Build",
            "type": "shell",
            "command": "./gradlew",
            "args": ["clean", "build"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Gradle: Build (Skip Tests)",
            "type": "shell",
            "command": "./gradlew",
            "args": ["build", "-x", "test"],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "Gradle: Build and Deploy to WebLogic",
            "type": "shell",
            "command": "./gradlew",
            "args": ["clean", "build", "deployToWebLogic"],
            "group": "build",
            "problemMatcher": [],
            "dependsOrder": "sequence"
        },
        {
            "label": "WebLogic: Deploy WAR",
            "type": "shell",
            "command": "wlst.sh",
            "args": [
                "${workspaceFolder}/.vscode/scripts/deploy.py"
            ],
            "group": "none",
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Restart ManagedServer1",
            "type": "shell",
            "command": "${workspaceFolder}/.vscode/scripts/restart-server.sh",
            "args": ["ManagedServer1"],
            "group": "none",
            "problemMatcher": []
        },
        {
            "label": "Full Rebuild and Deploy",
            "dependsOn": [
                "Gradle: Clean Build",
                "WebLogic: Deploy WAR",
                "WebLogic: Restart ManagedServer1"
            ],
            "dependsOrder": "sequence",
            "group": "build",
            "problemMatcher": []
        }
    ]
}
```

### 2.6 デプロイ自動化スクリプトの作成

#### .vscode/scripts/deploy.py（WLSTスクリプト）

```bash
mkdir -p .vscode/scripts
```

```python
# .vscode/scripts/deploy.py

import sys
import os

# 設定
ADMIN_URL = os.getenv('WEBLOGIC_ADMIN_URL', 't3://localhost:7001')
USERNAME = os.getenv('WEBLOGIC_USERNAME', 'weblogic')
PASSWORD = os.getenv('WEBLOGIC_PASSWORD', 'Welcome1')
APP_NAME = 'myapp'
WAR_FILE = os.path.join(os.path.dirname(__file__), '../../web-module/build/libs/myapp.war')
TARGET = 'ManagedServer1'

print('=== WebLogic Deployment Script ===')
print('Admin URL: ' + ADMIN_URL)
print('Application: ' + APP_NAME)
print('WAR File: ' + WAR_FILE)
print('Target: ' + TARGET)
print('')

try:
    # 接続
    print('Connecting to WebLogic...')
    connect(USERNAME, PASSWORD, ADMIN_URL)
    print('Connected successfully.')

    # 既存アプリケーションの確認
    print('Checking existing application...')
    cd('AppDeployments')
    apps = ls(returnMap='true')

    if APP_NAME in apps:
        print('Application exists. Redeploying...')
        redeploy(APP_NAME, WAR_FILE, targets=TARGET, upload='true')
        print('Redeployment completed.')
    else:
        print('Application does not exist. Deploying new application...')
        deploy(APP_NAME, WAR_FILE, targets=TARGET, upload='true')
        print('Deployment completed.')

    # 切断
    disconnect()
    print('')
    print('=== Deployment Successful ===')
    exit(0)

except Exception, e:
    print('')
    print('=== Deployment Failed ===')
    print('Error: ' + str(e))
    dumpStack()
    exit(1)
```

#### .vscode/scripts/restart-server.sh

```bash
#!/bin/bash
# .vscode/scripts/restart-server.sh

SERVER_NAME=$1

if [ -z "$SERVER_NAME" ]; then
    echo "Usage: $0 <SERVER_NAME>"
    exit 1
fi

DOMAIN_HOME="${DOMAIN_HOME:-/opt/oracle/domains/my_domain}"
ADMIN_URL="${WEBLOGIC_ADMIN_URL:-t3://localhost:7001}"
USERNAME="${WEBLOGIC_USERNAME:-weblogic}"
PASSWORD="${WEBLOGIC_PASSWORD:-Welcome1}"

echo "=== Restarting $SERVER_NAME ==="

wlst.sh <<EOF
connect('$USERNAME', '$PASSWORD', '$ADMIN_URL')

print('Stopping server...')
shutdown('$SERVER_NAME', 'Server', force='true')

print('Starting server...')
start('$SERVER_NAME', 'Server')

disconnect()
print('Server restarted successfully.')
EOF
```

```bash
chmod +x .vscode/scripts/restart-server.sh
```

---

## ステップ3: WebLogicデバッグ設定

### 3.1 setDomainEnv.sh の編集

```bash
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

以下を追加:

```bash
# デバッグ設定（開発環境のみ）
if [ "${SERVER_NAME}" = "ManagedServer1" ] ; then
    DEBUG_PORT="8453"
    JAVA_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
    JAVA_OPTIONS="${JAVA_OPTIONS} ${JAVA_DEBUG}"

    echo "Debug mode enabled on port ${DEBUG_PORT}"
fi

if [ "${SERVER_NAME}" = "ManagedServer2" ] ; then
    DEBUG_PORT="8454"
    JAVA_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
    JAVA_OPTIONS="${JAVA_OPTIONS} ${JAVA_DEBUG}"

    echo "Debug mode enabled on port ${DEBUG_PORT}"
fi

export JAVA_OPTIONS
```

### 3.2 WebLogicサーバーの再起動

```bash
# 管理対象サーバーを停止
cd /opt/oracle/domains/my_domain/bin
./stopManagedWebLogic.sh ManagedServer1

# デバッグモードで起動
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

起動ログで確認:
```
Listening for transport dt_socket at address: 8453
```

### 3.3 デバッグポートの確認

```bash
netstat -tuln | grep 8453
```

出力例:
```
tcp6       0      0 :::8453                 :::*                    LISTEN
```

---

## ステップ4: 開発フローの確立

### 4.1 初回セットアップ

```bash
# 1. プロジェクトをVSCodeで開く
code /path/to/production/gradle-project

# 2. VSCodeでJava拡張機能が自動的にプロジェクトをインポート
# （数分かかる場合があります）

# 3. Gradleビルドを実行
# VSCodeターミナル（Ctrl+`）で:
./gradlew clean build

# 4. WARファイルをWebLogicにデプロイ
./gradlew deployToWebLogic

# または、VSCodeタスクから:
# Ctrl+Shift+P → Tasks: Run Task → Gradle: Build and Deploy to WebLogic
```

### 4.2 日常的な開発フロー

#### パターンA: コード修正 → ビルド → デプロイ → デバッグ

1. **コード編集**
   - VSCodeでJavaファイルを編集

2. **ビルド**
   ```bash
   ./gradlew build -x test  # テストスキップで高速化
   ```
   または、VSCodeタスク: `Ctrl+Shift+B`（デフォルトビルドタスク）

3. **デプロイ**
   - VSCodeタスク: `Tasks: Run Task` → `WebLogic: Deploy WAR`
   - または、WLSTスクリプトを直接実行:
     ```bash
     wlst.sh .vscode/scripts/deploy.py
     ```

4. **デバッグ開始**
   - `F5` キーを押す、または
   - デバッグパネル（`Ctrl+Shift+D`）→ `Debug WebLogic (ManagedServer1)` → 再生ボタン

5. **ブレークポイント設定**
   - デバッグしたい行の左側をクリック

6. **アプリケーションをテスト**
   ```bash
   curl http://localhost:7003/myapp/users
   ```
   または、ブラウザでアクセス

#### パターンB: ホットリロード（軽微な変更）

1. **デバッグセッション起動中**
2. **コード編集**（メソッド内部のみ）
3. **保存** (`Ctrl+S`)
4. **VSCodeが自動的にクラスを再定義**
5. **サーバー再起動不要**

**制限**: メソッド追加、フィールド追加、クラス構造変更は不可

---

## 実践例: 完全な開発サイクル

### シナリオ: ユーザー一覧機能のバグ修正

#### 1. バグの発見

ブラウザで `http://localhost:7003/myapp/users` にアクセスすると、
500エラーが発生。

#### 2. ログの確認

```bash
tail -f /opt/oracle/domains/my_domain/servers/ManagedServer1/logs/ManagedServer1.log
```

ログ:
```
java.lang.NullPointerException
    at com.example.service.UserService.findAll(UserService.java:45)
    at com.example.action.UserAction.listUsers(UserAction.java:23)
```

#### 3. VSCodeでデバッグ準備

1. **デバッグセッション開始**
   - `F5` → `Debug WebLogic (ManagedServer1)`

2. **ブレークポイント設定**
   - `UserService.java` の 45行目にブレークポイント
   - `UserAction.java` の 23行目にブレークポイント

#### 4. リクエスト再実行

```bash
curl http://localhost:7003/myapp/users
```

VSCodeがブレークポイントで停止。

#### 5. 変数の確認

**Variables パネル**で確認:
```
userRepository = null  ← これが原因！
```

`UserService` に `@Autowired` アノテーションが欠けていることが判明。

#### 6. コード修正

```java
// web-module/src/main/java/com/example/service/UserService.java

@Service
public class UserService {

    @Autowired  // ← 追加
    private UserRepository userRepository;

    public List<User> findAll() {
        return userRepository.findAll();  // line 45
    }
}
```

保存 (`Ctrl+S`)。

#### 7. 再ビルド・再デプロイ

```bash
# VSCodeターミナルで
./gradlew build -x test
wlst.sh .vscode/scripts/deploy.py
```

または、VSCodeタスク:
- `Ctrl+Shift+P` → `Tasks: Run Task` → `Full Rebuild and Deploy`

#### 8. サーバー再起動（Spring DIの変更のため）

```bash
.vscode/scripts/restart-server.sh ManagedServer1
```

#### 9. デバッグセッション再接続

`F5` で再度デバッガーをアタッチ。

#### 10. 動作確認

```bash
curl http://localhost:7003/myapp/users
```

正常にユーザー一覧が返される。

#### 11. ブレークポイント削除

デバッグ完了後、不要なブレークポイントを削除。

---

## チーム開発での共有設定

### .gitignore の設定

`.vscode` ディレクトリの一部のみをGit管理下に置きます。

#### .gitignore

```gitignore
# VSCode設定の一部を除外
.vscode/*
!.vscode/settings.json
!.vscode/launch.json
!.vscode/tasks.json
!.vscode/extensions.json
!.vscode/scripts/

# ビルド成果物
build/
.gradle/
bin/

# IDE固有
.idea/
*.iml
.classpath
.project
.settings/
```

これにより、以下のファイルがGitにコミットされます:
- `.vscode/settings.json`
- `.vscode/launch.json`
- `.vscode/tasks.json`
- `.vscode/scripts/*.py`
- `.vscode/scripts/*.sh`

### 環境変数の管理

チームメンバーごとに異なる環境変数は `.env` ファイルで管理（`.gitignore` に追加）。

#### .env.example（テンプレート）

```bash
# .env.example
# コピーして .env として使用: cp .env.example .env

# WebLogic設定
WEBLOGIC_ADMIN_URL=t3://localhost:7001
WEBLOGIC_USERNAME=weblogic
WEBLOGIC_PASSWORD=Welcome1

# デバッグ設定
DEV_WEBLOGIC_HOST=localhost
DEV_WEBLOGIC_PORT=8453

# Java設定
JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

#### .env（個人設定、Gitには含めない）

各開発者が `.env.example` をコピーして `.env` を作成:

```bash
cp .env.example .env
vi .env
```

### 推奨拡張機能の共有

#### .vscode/extensions.json

```json
{
    "recommendations": [
        "vscjava.vscode-java-pack",
        "vscjava.vscode-gradle",
        "Pivotal.vscode-boot-dev-pack",
        "eamodio.gitlens"
    ]
}
```

チームメンバーがVSCodeでプロジェクトを開くと、推奨拡張機能のインストールを促すメッセージが表示されます。

---

## まとめ

この構成により、以下が実現できます:

1. **本番環境のGradleプロジェクトを直接VSCodeで開発**
2. **ビルド → デプロイ → デバッグのシームレスな連携**
3. **ブレークポイント、変数確認、ステップ実行**
4. **VSCodeタスクによる自動化（ビルド・デプロイ・再起動）**
5. **チーム開発での設定共有**

この環境で、効率的な開発とデバッグが可能になります。
