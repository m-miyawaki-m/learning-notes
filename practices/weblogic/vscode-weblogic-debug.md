# VSCode × WebLogic Server デバッグ連携ガイド

> 対象: WebLogic Server 12c/14c, Java, VSCode, Gradle
> 用途: 本番環境のGradleプロジェクトを使用したリモートデバッグ

このドキュメントでは、別の場所にある本番環境用のGradleプロジェクトを使って、VSCodeで開発しながらWebLogic Serverでデバッグする環境を構築する方法を解説します。

---

## 目次

1. [デバッグ連携の概要](#デバッグ連携の概要)
2. [前提条件](#前提条件)
3. [外部Gradleプロジェクトとの連携](#外部gradleプロジェクトとの連携)
4. [WebLogic側の設定（JDWPデバッグポート有効化）](#weblogic側の設定jdwpデバッグポート有効化)
5. [VSCode側の設定（launch.json）](#vscode側の設定launchjson)
6. [マルチモジュールプロジェクトの設定](#マルチモジュールプロジェクトの設定)
7. [デバッグ実行手順](#デバッグ実行手順)
8. [高度な設定](#高度な設定)
9. [トラブルシューティング](#トラブルシューティング)

---

## デバッグ連携の概要

### アーキテクチャ

```
┌─────────────────┐         JDWP Protocol        ┌──────────────────────┐
│   VSCode IDE    │◄──────── (Port 8453) ────────┤  WebLogic Server     │
│                 │                               │  (Managed Server)    │
│  - Breakpoints  │                               │  - Application WAR   │
│  - Step Control │                               │  - Debug Mode ON     │
│  - Variable View│                               │  - JDWP Listening    │
└─────────────────┘                               └──────────────────────┘
```

### デバッグ方式

| 方式 | 説明 | 用途 |
|------|------|------|
| **Remote Debug (Attach)** | 既に起動しているWebLogicプロセスにアタッチ | 本番同等環境のデバッグ（推奨） |
| **Launch** | VSCodeからプロセスを起動 | WebLogicでは非推奨（管理が複雑） |

**推奨**: Remote Debug (Attach)方式

---

## 外部Gradleプロジェクトとの連携

このセクションでは、本番環境で使用している既存のGradleプロジェクトを、VSCodeの開発環境に統合する方法を説明します。

### シナリオ

```
本番環境のGradleプロジェクト: /path/to/production/gradle-project/
                              ├── settings.gradle
                              ├── build.gradle
                              ├── common-module/
                              ├── business-module/
                              └── web-module/

VSCode開発環境: /home/m-miyawaki/dev/my-workspace/
                └── （このプロジェクトをVSCodeで開く）
```

### 方法1: シンボリックリンクを使用（推奨）

Gradleプロジェクトを移動せず、シンボリックリンクで開発環境に統合します。

#### 手順

```bash
# 開発用ワークスペースディレクトリを作成
mkdir -p /home/m-miyawaki/dev/my-workspace

# 本番環境のGradleプロジェクトへのシンボリックリンクを作成
cd /home/m-miyawaki/dev/my-workspace
ln -s /path/to/production/gradle-project gradle-project

# 確認
ls -la
# lrwxrwxrwx 1 user user   35 Dec 10 10:00 gradle-project -> /path/to/production/gradle-project
```

#### VSCodeで開く

```bash
# VSCodeでワークスペースを開く
code /home/m-miyawaki/dev/my-workspace
```

または、Gradleプロジェクト自体を直接開く:

```bash
# 本番環境のGradleプロジェクトを直接開く
code /path/to/production/gradle-project
```

### 方法2: VSCode Workspaceを使用（複数プロジェクト管理）

複数のプロジェクトを1つのVSCodeワークスペースで管理します。

#### my-workspace.code-workspace の作成

```json
{
    "folders": [
        {
            "name": "Gradle Project (Production)",
            "path": "/path/to/production/gradle-project"
        },
        {
            "name": "Learning Notes",
            "path": "/home/m-miyawaki/dev/learning-notes"
        },
        {
            "name": "Test Scripts",
            "path": "/home/m-miyawaki/dev/test-scripts"
        }
    ],
    "settings": {
        "java.configuration.updateBuildConfiguration": "automatic",
        "java.project.sourcePaths": [
            "/path/to/production/gradle-project/web-module/src/main/java",
            "/path/to/production/gradle-project/business-module/src/main/java",
            "/path/to/production/gradle-project/common-module/src/main/java"
        ],
        "java.debug.settings.hotCodeReplace": "auto",
        "java.debug.settings.enableHotCodeReplace": true,
        "gradle.nestedProjects": true,
        "files.exclude": {
            "**/build": true,
            "**/.gradle": true
        }
    },
    "launch": {
        "version": "0.2.0",
        "configurations": [
            {
                "type": "java",
                "name": "Debug WebLogic (Production)",
                "request": "attach",
                "hostName": "localhost",
                "port": 8453,
                "projectName": "web-module",
                "sourcePaths": [
                    "/path/to/production/gradle-project/web-module/src/main/java",
                    "/path/to/production/gradle-project/business-module/src/main/java",
                    "/path/to/production/gradle-project/common-module/src/main/java"
                ]
            }
        ]
    }
}
```

#### ワークスペースを開く

```bash
code /home/m-miyawaki/dev/my-workspace.code-workspace
```

### 方法3: Gitサブモジュールを使用（チーム開発向け）

Gradleプロジェクトをサブモジュールとして管理します。

```bash
# 開発用ワークスペースをGitリポジトリとして初期化
cd /home/m-miyawaki/dev/my-workspace
git init

# 本番環境のGradleプロジェクトをサブモジュールとして追加
git submodule add file:///path/to/production/gradle-project gradle-project

# または、リモートリポジトリから
git submodule add https://github.com/company/gradle-project.git gradle-project

# サブモジュールの初期化
git submodule update --init --recursive
```

### 方法4: ビルド成果物のみを参照（読み取り専用開発）

本番環境のプロジェクトには変更を加えず、ビルド成果物のみを使用してデバッグします。

#### 手順

1. **本番環境でビルド**

```bash
cd /path/to/production/gradle-project
./gradlew clean build
```

2. **WARファイルをWebLogicにデプロイ**

```bash
cp /path/to/production/gradle-project/web-module/build/libs/myapp.war \
   /opt/oracle/domains/my_domain/applications/
```

3. **ソースコードの参照設定（VSCode）**

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (Read-Only)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "sourcePaths": [
                "/path/to/production/gradle-project/web-module/src/main/java",
                "/path/to/production/gradle-project/business-module/src/main/java",
                "/path/to/production/gradle-project/common-module/src/main/java"
            ]
        }
    ]
}
```

### 推奨構成まとめ

| 方法 | メリット | デメリット | 推奨シナリオ |
|------|---------|-----------|-------------|
| **シンボリックリンク** | シンプル、本番環境と同期 | Linux/macOSのみ | 個人開発、ローカル環境 |
| **VSCode Workspace** | 複数プロジェクト管理可能 | 設定ファイル管理が必要 | 複数プロジェクト並行開発 |
| **Gitサブモジュール** | バージョン管理、チーム共有 | Git操作が複雑 | チーム開発、CI/CD統合 |
| **読み取り専用** | 本番環境に影響なし | コード変更不可 | 調査・分析のみ |

**最も推奨**: 本番環境のGradleプロジェクトを直接VSCodeで開く

```bash
code /path/to/production/gradle-project
```

---

## 前提条件

### 1. VSCode拡張機能のインストール

必須:
```
- Extension Pack for Java (Microsoft)
  └─ Language Support for Java(TM) by Red Hat
  └─ Debugger for Java
  └─ Test Runner for Java
  └─ Maven for Java
  └─ Project Manager for Java
```

オプション（推奨）:
```
- Gradle for Java
- Spring Boot Extension Pack（Spring使用時）
```

インストール方法:
```bash
# コマンドパレット（Ctrl+Shift+P / Cmd+Shift+P）から
Ext Install: Extension Pack for Java
```

### 2. Javaプロジェクト構成

#### Mavenマルチモジュール構成例

```
my-weblogic-app/
├── pom.xml                          # 親POM
├── common-module/                   # 共通ライブラリ
│   ├── pom.xml
│   └── src/main/java/
├── business-module/                 # ビジネスロジック
│   ├── pom.xml
│   └── src/main/java/
└── web-module/                      # Webアプリケーション
    ├── pom.xml
    ├── src/main/java/
    └── src/main/webapp/
```

#### Gradleマルチモジュール構成例

```
my-weblogic-app/
├── settings.gradle                  # モジュール定義
├── build.gradle                     # ルートビルド設定
├── common-module/
│   ├── build.gradle
│   └── src/main/java/
├── business-module/
│   ├── build.gradle
│   └── src/main/java/
└── web-module/
    ├── build.gradle
    ├── src/main/java/
    └── src/main/webapp/
```

---

## WebLogic側の設定（JDWPデバッグポート有効化）

### 方法1: setDomainEnv.shを編集（永続的）

#### Linux/macOS

```bash
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

以下を追加:

```bash
# 管理対象サーバー用のデバッグ設定
if [ "${SERVER_NAME}" = "ManagedServer1" ] ; then
    debugFlag="true"
    DEBUG_PORT="8453"

    export debugFlag

    if [ "${debugFlag}" = "true" ] ; then
        JAVA_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
        JAVA_OPTIONS="${JAVA_OPTIONS} ${JAVA_DEBUG}"
        export JAVA_OPTIONS
    fi
fi
```

**パラメータ説明:**

| パラメータ | 説明 | 推奨値 |
|-----------|------|--------|
| `transport=dt_socket` | ソケット通信を使用 | 固定 |
| `server=y` | サーバーモード（待ち受け） | `y` |
| `suspend=n` | 起動時に待機しない | `n`（開発時は`y`でも可） |
| `address=*:8453` | 全てのネットワークインターフェースでポート8453を待ち受け | `*:8453`（ローカルのみなら`127.0.0.1:8453`） |

#### Windows

```cmd
notepad %ORACLE_HOME%\user_projects\domains\my_domain\bin\setDomainEnv.cmd
```

以下を追加:

```batch
@REM 管理対象サーバー用のデバッグ設定
if "%SERVER_NAME%"=="ManagedServer1" (
    set debugFlag=true
    set DEBUG_PORT=8453

    if "%debugFlag%"=="true" (
        set JAVA_DEBUG=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:%DEBUG_PORT%
        set JAVA_OPTIONS=%JAVA_OPTIONS% %JAVA_DEBUG%
    )
)
```

### 方法2: 管理コンソールから設定（動的）

1. **Environment > Servers** を選択
2. デバッグ対象のサーバーを選択（例: ManagedServer1）
3. **Configuration > Server Start** タブ
4. **Arguments** に以下を追加:

```
-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8453
```

5. **Save** をクリック
6. サーバーを再起動

### 方法3: 起動時に環境変数で指定（一時的）

```bash
export JAVA_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8453"
cd /opt/oracle/domains/my_domain/bin
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

### デバッグポートの確認

```bash
# ポートが開いているか確認
netstat -tuln | grep 8453

# WebLogicプロセスのJVMオプション確認
ps aux | grep weblogic | grep jdwp
```

出力例:
```
tcp6       0      0 :::8453                 :::*                    LISTEN
```

### セキュリティ考慮事項

**本番環境では絶対にデバッグポートを開放しないでください。**

開発環境でも以下を推奨:
```bash
# ローカルホストのみからの接続を許可
address=127.0.0.1:8453
```

ファイアウォール設定（開発環境のみ）:
```bash
# iptables（Linux）
sudo iptables -A INPUT -p tcp --dport 8453 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8453 -j DROP

# firewalld（RHEL/CentOS）
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="127.0.0.1" port protocol="tcp" port="8453" accept'
sudo firewall-cmd --reload
```

---

## VSCode側の設定（launch.json）

### 1. launch.json の作成

`.vscode/launch.json` をプロジェクトルートに作成:

```bash
mkdir -p .vscode
vi .vscode/launch.json
```

### 2. 基本設定（シングルモジュール）

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (Remote)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "projectName": "my-weblogic-app",
            "timeout": 30000
        }
    ]
}
```

### 3. マルチモジュール対応設定（推奨）

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
        }
    ]
}
```

### 4. リモートサーバー接続設定

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug Remote WebLogic (DEV Server)",
            "request": "attach",
            "hostName": "dev-weblogic-01.example.com",
            "port": 8453,
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

### 設定パラメータ詳細

| パラメータ | 説明 | 例 |
|-----------|------|-----|
| `type` | デバッガータイプ | `"java"` |
| `name` | VSCodeデバッグパネルに表示される名前 | `"Debug WebLogic"` |
| `request` | デバッグ方式 | `"attach"`（推奨） |
| `hostName` | WebLogicサーバーのホスト名/IP | `"localhost"`, `"192.168.1.10"` |
| `port` | JDWPポート番号 | `8453` |
| `timeout` | 接続タイムアウト（ミリ秒） | `30000` |
| `projectName` | メインプロジェクト名 | `"web-module"` |
| `sourcePaths` | ソースコードパス（マルチモジュール用） | 配列形式 |

---

## マルチモジュールプロジェクトの設定

### Maven マルチモジュールの設定

#### 1. settings.json の設定

`.vscode/settings.json`:

```json
{
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.project.sourcePaths": [
        "web-module/src/main/java",
        "business-module/src/main/java",
        "common-module/src/main/java"
    ],
    "java.project.outputPath": "target/classes",
    "java.project.referencedLibraries": [
        "web-module/target/*.jar",
        "business-module/target/*.jar",
        "common-module/target/*.jar",
        "lib/**/*.jar"
    ],
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true
}
```

#### 2. 親POMの設定

`pom.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-weblogic-app</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <modules>
        <module>common-module</module>
        <module>business-module</module>
        <module>web-module</module>
    </modules>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencyManagement>
        <!-- 共通依存関係の管理 -->
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                    <debug>true</debug>
                    <debuglevel>lines,vars,source</debuglevel>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

**重要**: `<debug>true</debug>` と `<debuglevel>lines,vars,source</debuglevel>` を設定することで、デバッグ情報がクラスファイルに含まれます。

#### 3. 子モジュールPOMの例（web-module）

`web-module/pom.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.example</groupId>
        <artifactId>my-weblogic-app</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>web-module</artifactId>
    <packaging>war</packaging>

    <dependencies>
        <!-- 他のモジュールへの依存 -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>business-module</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common-module</artifactId>
            <version>${project.version}</version>
        </dependency>

        <!-- WebLogic依存関係（provided） -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
            <version>4.0.1</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <finalName>myapp</finalName>
    </build>
</project>
```

### Gradle マルチモジュールの設定

#### 1. settings.gradle

```groovy
rootProject.name = 'my-weblogic-app'

include 'common-module'
include 'business-module'
include 'web-module'
```

#### 2. ルート build.gradle

```groovy
plugins {
    id 'java'
}

subprojects {
    apply plugin: 'java'

    group = 'com.example'
    version = '1.0.0-SNAPSHOT'

    sourceCompatibility = 11
    targetCompatibility = 11

    repositories {
        mavenCentral()
    }

    // デバッグ情報を含める
    tasks.withType(JavaCompile) {
        options.debug = true
        options.debugOptions.debugLevel = 'source,lines,vars'
    }
}
```

#### 3. web-module/build.gradle

```groovy
plugins {
    id 'war'
}

dependencies {
    implementation project(':common-module')
    implementation project(':business-module')

    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveFileName = 'myapp.war'
}
```

#### 4. VSCode settings.json (Gradle用)

```json
{
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.project.sourcePaths": [
        "web-module/src/main/java",
        "business-module/src/main/java",
        "common-module/src/main/java"
    ],
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true,
    "gradle.nestedProjects": true
}
```

---

## デバッグ実行手順

### 1. ビルドとデプロイ

#### Maven

```bash
# プロジェクトルートで
mvn clean package

# WARファイルの確認
ls -lh web-module/target/myapp.war
```

#### Gradle

```bash
./gradlew clean build

# WARファイルの確認
ls -lh web-module/build/libs/myapp.war
```

#### WebLogicへのデプロイ

```bash
# WLST経由
wlst.sh << EOF
connect('weblogic', 'Welcome1', 't3://localhost:7001')
deploy('myapp', '/path/to/web-module/target/myapp.war', targets='ManagedServer1', upload='true')
disconnect()
EOF

# または管理コンソールから手動デプロイ
```

### 2. WebLogicサーバーの起動（デバッグモード）

```bash
cd /opt/oracle/domains/my_domain/bin
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

ログで以下を確認:
```
Listening for transport dt_socket at address: 8453
```

### 3. VSCodeでブレークポイントを設定

1. デバッグしたいJavaファイルを開く（例: `UserController.java`）
2. 行番号の左をクリックしてブレークポイントを設定（赤い点が表示される）

### 4. デバッグセッションを開始

1. VSCodeのデバッグパネルを開く（`Ctrl+Shift+D` / `Cmd+Shift+D`）
2. "Debug WebLogic (ManagedServer1)" を選択
3. 緑の再生ボタン（▶）をクリック

接続成功時のメッセージ:
```
Debugger attached successfully
```

### 5. アプリケーションをテスト

ブラウザやcurlでアプリケーションにアクセス:
```bash
curl http://localhost:7003/myapp/user/list
```

ブレークポイントで実行が停止し、VSCodeがアクティブになります。

### 6. デバッグ操作

| 操作 | ショートカット | 説明 |
|------|---------------|------|
| **Continue** | `F5` | 次のブレークポイントまで実行 |
| **Step Over** | `F10` | 次の行へ（メソッド内に入らない） |
| **Step Into** | `F11` | メソッド内に入る |
| **Step Out** | `Shift+F11` | 現在のメソッドを抜ける |
| **Restart** | `Ctrl+Shift+F5` | デバッグセッション再起動 |
| **Stop** | `Shift+F5` | デバッグセッション停止 |

### 7. 変数の確認

- **Variables パネル**: ローカル変数、インスタンス変数を確認
- **Watch パネル**: カスタム式を評価
- **Call Stack パネル**: メソッド呼び出しスタックを確認
- **Debug Console**: 式を評価

例:
```java
// Debug Consoleで評価
user.getName()
userList.size()
```

---

## 高度な設定

### 1. ホットコードリプレイス（HCR）

コードを変更して即座にWebLogicに反映。

#### VSCode設定

`.vscode/settings.json`:
```json
{
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true,
    "java.autobuild.enabled": true
}
```

#### WebLogic側の設定

`setDomainEnv.sh`:
```bash
# ホットコードリプレイス有効化
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+AllowEnhancedClassRedefinition"
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:HotswapAgent=fatjar"
export JAVA_OPTIONS
```

#### 使用方法

1. デバッグセッション中にコードを編集
2. ファイルを保存（`Ctrl+S` / `Cmd+S`）
3. VSCodeが自動的にクラスを再定義

**制限事項**:
- メソッド内部の変更のみ対応
- クラス構造の変更（新しいメソッド、フィールド追加）は不可
- クラス構造変更時はサーバー再起動が必要

### 2. 条件付きブレークポイント

1. ブレークポイントを右クリック
2. **Edit Breakpoint...** を選択
3. 条件を入力:

```java
// 例1: 特定のユーザーIDのみ
userId == 12345

// 例2: リストサイズが大きい場合のみ
userList.size() > 100

// 例3: nullチェック
user != null && user.getName().equals("admin")
```

### 3. ログポイント（Logpoint）

コードを変更せずにログ出力。

1. ブレークポイント設定時に右クリック
2. **Add Logpoint...** を選択
3. ログメッセージを入力:

```
User ID: {userId}, Name: {user.getName()}
```

実行時にDebug Consoleに出力されますが、実行は停止しません。

### 4. マルチスレッドデバッグ

**Call Stack** パネルで全スレッドを確認:

```
▼ Thread [WebLogic Kernel] (Suspended at breakpoint)
  ▼ UserController.getUser() line: 45
    UserService.findById() line: 23
    UserRepository.selectById() line: 67

▼ Thread [WebLogic Kernel] (Running)
  ...
```

スレッドを切り替えてデバッグ可能。

### 5. 例外ブレークポイント

特定の例外発生時に停止:

1. **Breakpoints** パネルを開く
2. **+** → **Exception Breakpoints** を選択
3. 例外クラスを入力:

```
java.lang.NullPointerException
com.example.CustomException
```

### 6. リモートJARファイルのデバッグ

WebLogic内部のライブラリをデバッグする場合:

`.vscode/launch.json`:
```json
{
    "type": "java",
    "name": "Debug WebLogic with External JARs",
    "request": "attach",
    "hostName": "localhost",
    "port": 8453,
    "sourcePaths": [
        "${workspaceFolder}/web-module/src/main/java",
        "${workspaceFolder}/business-module/src/main/java",
        "${workspaceFolder}/common-module/src/main/java"
    ],
    "sourceFileMap": {
        "/opt/oracle/wlserver/modules": "${workspaceFolder}/../weblogic-sources"
    }
}
```

WebLogicソースを取得:
```bash
# Oracle Maven Repositoryから取得
mvn dependency:sources -DincludeArtifactIds=weblogic
```

---

## トラブルシューティング

### 問題1: デバッガーが接続できない

#### 症状
```
Failed to connect to remote VM. Connection refused.
```

#### 解決方法

1. **JDWPポートが開いているか確認**
```bash
netstat -tuln | grep 8453
```

2. **WebLogicプロセスがデバッグモードで起動しているか確認**
```bash
ps aux | grep weblogic | grep jdwp
```

3. **ファイアウォール設定確認**
```bash
# iptables
sudo iptables -L -n | grep 8453

# firewalld
sudo firewall-cmd --list-all
```

4. **ポート番号の確認**
- `launch.json`のポート番号とWebLogicのJDWPポート番号が一致しているか確認

5. **ホスト名/IPアドレスの確認**
- リモートサーバーの場合、正しいホスト名/IPを指定しているか確認

### 問題2: ブレークポイントが有効にならない

#### 症状
ブレークポイントが灰色（無効状態）になる。

#### 解決方法

1. **デバッグ情報がコンパイル時に含まれているか確認**

Maven:
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <debug>true</debug>
        <debuglevel>lines,vars,source</debuglevel>
    </configuration>
</plugin>
```

Gradle:
```groovy
tasks.withType(JavaCompile) {
    options.debug = true
    options.debugOptions.debugLevel = 'source,lines,vars'
}
```

2. **ソースコードとデプロイされたクラスが一致しているか確認**
```bash
# 再ビルド・再デプロイ
mvn clean package
# または
./gradlew clean build

# 再デプロイ
```

3. **sourcePaths が正しく設定されているか確認**

`.vscode/launch.json`:
```json
"sourcePaths": [
    "${workspaceFolder}/web-module/src/main/java",
    "${workspaceFolder}/business-module/src/main/java"
]
```

4. **クラスローディング順序の問題**
- WebLogic内部のクラスと競合している可能性がある
- `weblogic.xml`で`prefer-web-inf-classes`を確認

### 問題3: 変数が表示されない

#### 症状
Variables パネルに変数が表示されない、または値が `<optimized out>` と表示される。

#### 解決方法

1. **デバッグレベルを`vars`に設定**

Maven:
```xml
<debuglevel>lines,vars,source</debuglevel>
```

Gradle:
```groovy
options.debugOptions.debugLevel = 'source,lines,vars'
```

2. **JVMの最適化を無効化（開発時のみ）**

`setDomainEnv.sh`:
```bash
JAVA_OPTIONS="${JAVA_OPTIONS} -Xint"  # インタープリターモード（遅い）
# または
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:TieredStopAtLevel=1"  # JITコンパイル最適化を制限
```

### 問題4: パフォーマンスが極端に低下する

#### 症状
デバッグモード時、アプリケーションの応答が著しく遅い。

#### 解決方法

1. **ブレークポイントを削減**
- 不要なブレークポイントを削除
- 条件付きブレークポイントを活用

2. **ログポイントの見直し**
- ログポイントも実行速度に影響する

3. **`suspend=n` を使用**
```bash
-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8453
```

4. **デバッガーをデタッチ**
- デバッグが不要な処理ではデバッガーを一時的にデタッチ

### 問題5: ホットコードリプレイスが動作しない

#### 症状
コードを変更しても反映されない。

#### 解決方法

1. **HCRの制限を理解する**
- メソッド内部の変更のみ対応
- メソッド追加、フィールド追加は不可
- クラス構造変更時はサーバー再起動が必要

2. **Java 11以降でEnhanced HCRを使用**

WebLogic起動オプション:
```bash
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+AllowEnhancedClassRedefinition"
```

または、HotswapAgentを使用:
```bash
# HotswapAgentのダウンロード
wget https://github.com/HotswapProjects/HotswapAgent/releases/download/RELEASE-1.4.1/hotswap-agent-1.4.1.jar

# JVMオプションに追加
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:HotswapAgent=fatjar -javaagent:/path/to/hotswap-agent-1.4.1.jar"
```

3. **自動ビルドが有効か確認**

`.vscode/settings.json`:
```json
{
    "java.autobuild.enabled": true
}
```

### 問題6: マルチモジュールプロジェクトでソースが見つからない

#### 症状
```
Source not found for ClassName
```

#### 解決方法

1. **sourcePaths に全モジュールのソースパスを指定**

`.vscode/launch.json`:
```json
"sourcePaths": [
    "${workspaceFolder}/web-module/src/main/java",
    "${workspaceFolder}/business-module/src/main/java",
    "${workspaceFolder}/common-module/src/main/java",
    "${workspaceFolder}/integration-module/src/main/java"
]
```

2. **VSCode Java Extensionにプロジェクトを認識させる**
```bash
# コマンドパレット（Ctrl+Shift+P）
Java: Clean Java Language Server Workspace
Java: Reload Projects
```

3. **Mavenの場合、`mvn eclipse:eclipse` を実行**
```bash
mvn eclipse:eclipse
```

---

## ベストプラクティス

### 1. 開発フロー

```
1. コード変更
   ↓
2. ローカルビルド（mvn compile）
   ↓
3. ユニットテスト実行
   ↓
4. WARファイル作成（mvn package）
   ↓
5. WebLogicへデプロイ（ホットデプロイまたは再デプロイ）
   ↓
6. デバッガーアタッチ
   ↓
7. 動作確認
```

### 2. デバッグ戦略

- **ログ駆動デバッグ**: まずログで問題箇所を特定
- **最小限のブレークポイント**: パフォーマンス維持のため
- **条件付きブレークポイント活用**: 特定ケースのみ停止
- **ログポイント活用**: 実行を止めずに情報収集

### 3. チーム開発での共有設定

`.vscode/launch.json` をGit管理下に置く:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (Local)",
            "request": "attach",
            "hostName": "${env:WEBLOGIC_DEBUG_HOST:localhost}",
            "port": "${env:WEBLOGIC_DEBUG_PORT:8453}",
            "sourcePaths": [
                "${workspaceFolder}/web-module/src/main/java",
                "${workspaceFolder}/business-module/src/main/java",
                "${workspaceFolder}/common-module/src/main/java"
            ]
        }
    ]
}
```

個人設定は `.env` ファイルで管理（`.gitignore` に追加）:

```bash
# .env
WEBLOGIC_DEBUG_HOST=localhost
WEBLOGIC_DEBUG_PORT=8453
```

---

## 参考資料

- [VSCode Java Debugging](https://code.visualstudio.com/docs/java/java-debugging)
- [Java Platform Debugger Architecture (JPDA)](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/)
- [WebLogic Server Documentation](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/)

---

## まとめ

このガイドで以下を実現できます:

1. **WebLogicサーバーのJDWPデバッグポート有効化**
2. **VSCodeからのリモートデバッグ接続**
3. **マルチモジュールプロジェクトでのソースコード参照**
4. **ブレークポイント、変数確認、ステップ実行**
5. **ホットコードリプレイスによる高速開発サイクル**

開発環境でこの設定を活用することで、効率的なデバッグとトラブルシューティングが可能になります。
