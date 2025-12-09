# VSCode + Spring + Gradle + WebLogic 開発環境構築ガイド

> SpringプロジェクトをVSCodeで開発し、Gradleでビルド、WebLogicでデバッグする環境

このドキュメントでは、Springプロジェクトの依存関係管理にGradleを活用しながら、VSCodeで快適に開発してWebLogicでデバッグする環境を構築する方法を解説します。

---

## 目次

1. [環境構成の概要](#環境構成の概要)
2. [プロジェクト構成](#プロジェクト構成)
3. [Gradle設定（依存関係管理）](#gradle設定依存関係管理)
4. [VSCode設定](#vscode設定)
5. [WebLogicデバッグ設定](#weblogicデバッグ設定)
6. [開発ワークフロー](#開発ワークフロー)
7. [トラブルシューティング](#トラブルシューティング)

---

## 環境構成の概要

### Gradleの役割

```
┌────────────────────────────────────────────────────────────┐
│                   Gradleの利用目的                          │
└────────────────────────────────────────────────────────────┘

1. 依存関係の自動管理（Spring、Struts2、Hibernateなど）
2. ユーザーライブラリの手動設定を不要に
3. クラスパスの自動生成
4. WARファイルのビルド
5. WebLogicへのデプロイ自動化

※ Gradleはビルドツールとして利用するが、
  開発自体はVSCodeでSpringプロジェクトとして行う
```

### アーキテクチャ

```
┌──────────────────┐
│   VSCode IDE     │
│                  │
│  - Springプロジェ │  Gradle Eclipse Plugin
│    クトとして開発  │◄─────────────────┐
│  - Java拡張機能  │                   │
│  - コード補完    │                   │
│  - リファクタ    │                   ▼
└──────────────────┘         ┌────────────────────┐
         │                   │  Gradle            │
         │ JDWP              │  - build.gradle    │
         ▼                   │  - 依存関係定義     │
┌──────────────────┐         │  - クラスパス生成   │
│ WebLogic Server  │         └────────────────────┘
│ - Debug Mode ON  │                   │
│ - Port 8453      │◄──────────────────┘
│ - myapp.war      │        ./gradlew war
└──────────────────┘
```

---

## プロジェクト構成

### ディレクトリ構造

```
my-spring-project/
├── build.gradle                 # Gradle依存関係定義
├── settings.gradle              # プロジェクト設定
├── gradle.properties            # Gradle設定
├── gradlew                      # Gradleラッパー
├── gradlew.bat
├── .vscode/                     # VSCode設定
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── controller/
│   │   │           │   └── UserController.java
│   │   │           ├── service/
│   │   │           │   └── UserService.java
│   │   │           ├── repository/
│   │   │           │   └── UserRepository.java
│   │   │           └── config/
│   │   │               ├── ApplicationConfig.java
│   │   │               └── WebConfig.java
│   │   ├── resources/
│   │   │   ├── application.properties
│   │   │   ├── applicationContext.xml (XML設定の場合)
│   │   │   └── logback.xml
│   │   └── webapp/
│   │       ├── WEB-INF/
│   │       │   ├── web.xml
│   │       │   └── spring/
│   │       │       └── servlet-context.xml
│   │       └── index.jsp
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── service/
│                       └── UserServiceTest.java
└── build/                       # ビルド成果物（.gitignoreに追加）
    └── libs/
        └── myapp.war
```

### マルチモジュール構成の場合

```
my-spring-project/
├── settings.gradle              # include 'common', 'business', 'web'
├── build.gradle                 # ルート設定
├── common/                      # 共通モジュール
│   ├── build.gradle
│   └── src/main/java/
├── business/                    # ビジネスロジック
│   ├── build.gradle
│   └── src/main/java/
└── web/                         # Webモジュール
    ├── build.gradle
    └── src/
        ├── main/java/
        └── main/webapp/
```

---

## Gradle設定（依存関係管理）

### build.gradle（シングルモジュール）

```groovy
plugins {
    id 'java'
    id 'war'
    id 'eclipse'  // Eclipse/VSCode用のクラスパス生成
}

group = 'com.example'
version = '1.0.0-SNAPSHOT'

sourceCompatibility = JavaVersion.VERSION_11
targetCompatibility = JavaVersion.VERSION_11

repositories {
    mavenCentral()
}

// 依存関係の定義
dependencies {
    // Spring Framework
    implementation 'org.springframework:spring-context:5.3.27'
    implementation 'org.springframework:spring-webmvc:5.3.27'
    implementation 'org.springframework:spring-jdbc:5.3.27'
    implementation 'org.springframework:spring-tx:5.3.27'

    // Struts2（必要に応じて）
    implementation 'org.apache.struts:struts2-core:2.5.30'
    implementation 'org.apache.struts:struts2-spring-plugin:2.5.30'

    // Hibernate/JPA（必要に応じて）
    implementation 'org.hibernate:hibernate-core:5.6.15.Final'
    implementation 'org.hibernate:hibernate-entitymanager:5.6.15.Final'

    // Database
    implementation 'com.oracle.database.jdbc:ojdbc8:21.9.0.0'
    implementation 'com.zaxxer:HikariCP:5.0.1'

    // Logging
    implementation 'org.slf4j:slf4j-api:1.7.36'
    implementation 'ch.qos.logback:logback-classic:1.2.11'

    // JSON
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.14.2'

    // Validation
    implementation 'javax.validation:validation-api:2.0.1.Final'
    implementation 'org.hibernate.validator:hibernate-validator:6.2.5.Final'

    // WebLogicで提供されるライブラリ（provided）
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
    providedCompile 'javax.servlet.jsp:javax.servlet.jsp-api:2.3.3'
    providedCompile 'javax.el:javax.el-api:3.0.0'

    // テスト
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.springframework:spring-test:5.3.27'
    testImplementation 'org.mockito:mockito-core:4.11.0'
}

// コンパイル設定
tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
    options.debug = true
    options.debugOptions.debugLevel = 'source,lines,vars'
}

// WAR設定
war {
    archiveBaseName = 'myapp'
    archiveVersion = ''
}

// WebLogicデプロイタスク
task deployToWebLogic(type: Copy, dependsOn: war) {
    from war.archiveFile
    into '/opt/oracle/domains/my_domain/applications'

    doLast {
        println "Deployed to WebLogic: ${war.archiveFileName.get()}"
    }
}

// Eclipse/VSCode用のクラスパス生成
eclipse {
    classpath {
        downloadSources = true
        downloadJavadoc = true
    }
}
```

### build.gradle（マルチモジュール - ルート）

```groovy
// ルート build.gradle
plugins {
    id 'java'
}

subprojects {
    apply plugin: 'java'
    apply plugin: 'eclipse'

    group = 'com.example'
    version = '1.0.0-SNAPSHOT'

    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11

    repositories {
        mavenCentral()
    }

    tasks.withType(JavaCompile) {
        options.encoding = 'UTF-8'
        options.debug = true
        options.debugOptions.debugLevel = 'source,lines,vars'
    }

    eclipse {
        classpath {
            downloadSources = true
            downloadJavadoc = true
        }
    }
}
```

### build.gradle（マルチモジュール - webモジュール）

```groovy
// web/build.gradle
plugins {
    id 'war'
}

dependencies {
    // 他のモジュール
    implementation project(':common')
    implementation project(':business')

    // Spring
    implementation 'org.springframework:spring-webmvc:5.3.27'

    // WebLogic provided
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
    providedCompile 'javax.servlet.jsp:javax.servlet.jsp-api:2.3.3'
}

war {
    archiveBaseName = 'myapp'
    archiveVersion = ''
}
```

### settings.gradle（マルチモジュール）

```groovy
rootProject.name = 'my-spring-project'

include 'common'
include 'business'
include 'web'
```

### gradle.properties

```properties
# JVM設定
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m

# 並列ビルド
org.gradle.parallel=true
org.gradle.daemon=true
org.gradle.caching=true

# WebLogic設定
weblogic.domain.home=/opt/oracle/domains/my_domain
```

---

## VSCode設定

### 1. 初回セットアップ

#### ステップ1: Gradleでクラスパスを生成

```bash
cd /path/to/my-spring-project

# Eclipse/VSCode用のクラスパスファイルを生成
./gradlew eclipse

# 生成されるファイル:
# - .classpath
# - .project
# - .settings/
```

これにより、VSCodeのJava拡張機能が依存関係を認識できるようになります。

#### ステップ2: VSCodeで開く

```bash
code /path/to/my-spring-project
```

VSCodeのJava拡張機能が自動的に `.classpath` を読み込み、Gradleの依存関係を認識します。

### 2. .vscode/settings.json

```json
{
    // Java設定
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.import.gradle.enabled": true,
    "java.import.gradle.wrapper.enabled": true,

    // ソースパス（シングルモジュール）
    "java.project.sourcePaths": [
        "src/main/java"
    ],

    // マルチモジュールの場合
    // "java.project.sourcePaths": [
    //     "web/src/main/java",
    //     "business/src/main/java",
    //     "common/src/main/java"
    // ],

    // 出力パス
    "java.project.outputPath": "bin",

    // 参照ライブラリ（Gradleが管理）
    "java.project.referencedLibraries": [
        "build/libs/**/*.jar",
        "lib/**/*.jar"
    ],

    // デバッグ設定
    "java.debug.settings.hotCodeReplace": "auto",
    "java.debug.settings.enableHotCodeReplace": true,

    // Gradle設定
    "gradle.nestedProjects": true,

    // ファイル除外
    "files.exclude": {
        "**/.gradle": true,
        "**/.classpath": true,
        "**/.project": true,
        "**/.settings": true
    },

    // エディタ設定
    "editor.formatOnSave": true,
    "editor.tabSize": 4,
    "files.encoding": "utf8",

    // Spring Boot拡張機能（Spring Boot使用時）
    "spring-boot.ls.java.home": "/usr/lib/jvm/java-11-openjdk"
}
```

### 3. .vscode/launch.json

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (Local)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (Multi-Module)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/web/src/main/java",
                "${workspaceFolder}/business/src/main/java",
                "${workspaceFolder}/common/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (Remote)",
            "request": "attach",
            "hostName": "${env:WEBLOGIC_HOST}",
            "port": "${env:WEBLOGIC_DEBUG_PORT}",
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/src/main/java"
            ]
        }
    ]
}
```

### 4. .vscode/tasks.json

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Gradle: Eclipse Classpath",
            "type": "shell",
            "command": "./gradlew",
            "args": ["eclipse"],
            "group": "build",
            "problemMatcher": [],
            "detail": "Gradleの依存関係からEclipse/VSCode用のクラスパスを生成"
        },
        {
            "label": "Gradle: Build",
            "type": "shell",
            "command": "./gradlew",
            "args": ["build", "-x", "test"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": []
        },
        {
            "label": "Gradle: Clean Build",
            "type": "shell",
            "command": "./gradlew",
            "args": ["clean", "build"],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "Gradle: War",
            "type": "shell",
            "command": "./gradlew",
            "args": ["war"],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "Deploy to WebLogic",
            "type": "shell",
            "command": "./gradlew",
            "args": ["deployToWebLogic"],
            "group": "none",
            "dependsOn": ["Gradle: War"],
            "problemMatcher": []
        },
        {
            "label": "Full Build and Deploy",
            "dependsOn": [
                "Gradle: Clean Build",
                "Deploy to WebLogic"
            ],
            "dependsOrder": "sequence",
            "group": "build",
            "problemMatcher": []
        }
    ]
}
```

### 5. 必須VSCode拡張機能

```json
// .vscode/extensions.json
{
    "recommendations": [
        "vscjava.vscode-java-pack",
        "vscjava.vscode-gradle",
        "vscjava.vscode-spring-initializr",
        "vscjava.vscode-spring-boot-dashboard",
        "Pivotal.vscode-spring-boot"
    ]
}
```

インストール:
```bash
code --install-extension vscjava.vscode-java-pack
code --install-extension vscjava.vscode-gradle
code --install-extension Pivotal.vscode-spring-boot
```

---

## WebLogicデバッグ設定

### setDomainEnv.sh の設定

```bash
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

追加:

```bash
# デバッグ設定（開発環境のみ）
if [ "${SERVER_NAME}" = "ManagedServer1" ] ; then
    DEBUG_PORT="8453"
    JAVA_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
    JAVA_OPTIONS="${JAVA_OPTIONS} ${JAVA_DEBUG}"

    echo "Debug mode enabled on port ${DEBUG_PORT}"
fi

export JAVA_OPTIONS
```

### WebLogicの起動

```bash
cd /opt/oracle/domains/my_domain/bin
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

ログで確認:
```
Listening for transport dt_socket at address: 8453
```

---

## 開発ワークフロー

### 初回セットアップ

```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/my-spring-project

# 2. Gradleでクラスパス生成
./gradlew eclipse

# 3. VSCodeで開く
code .

# 4. ビルド
./gradlew build

# 5. WebLogicにデプロイ
./gradlew deployToWebLogic

# 6. WebLogic起動（デバッグモード）
/opt/oracle/domains/my_domain/bin/startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

### 日常の開発フロー

#### パターン1: コード変更 → ビルド → デプロイ → デバッグ

```bash
# 1. VSCodeでコード編集
#    - UserController.java を編集

# 2. ビルド（VSCodeターミナル）
./gradlew build -x test

# または、VSCodeタスク（Ctrl+Shift+B）
# → "Gradle: Build" を実行

# 3. デプロイ
./gradlew deployToWebLogic

# または、VSCodeタスク
# Ctrl+Shift+P → Tasks: Run Task → "Deploy to WebLogic"

# 4. デバッグ開始
# F5 → "Debug WebLogic (Local)" を選択

# 5. ブレークポイント設定
#    - UserController.java の該当行をクリック

# 6. アプリケーションテスト
curl http://localhost:7003/myapp/users
```

#### パターン2: 依存関係追加時

```bash
# 1. build.gradle を編集
#    dependencies {
#        implementation 'org.apache.commons:commons-lang3:3.12.0'
#    }

# 2. クラスパス再生成
./gradlew eclipse

# または、VSCodeタスク
# Tasks: Run Task → "Gradle: Eclipse Classpath"

# 3. VSCodeをリロード
# Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
# VSCodeを再起動

# 4. コードで新しいライブラリを使用可能
# import org.apache.commons.lang3.StringUtils;
```

#### パターン3: 高速デバッグサイクル（ホットリロード）

```bash
# 前提: デバッグセッション起動中

# 1. コード編集（メソッド内部のみ）
#    - ビジネスロジックの修正など

# 2. 保存（Ctrl+S）

# 3. VSCodeが自動的にクラスを再コンパイル・再定義
#    → サーバー再起動不要

# 4. すぐにテスト可能
```

**制限**: メソッド追加、フィールド追加、クラス構造変更は不可

---

## トラブルシューティング

### 問題1: VSCodeが依存関係を認識しない

#### 症状
```
import org.springframework.stereotype.Service;
```
が赤線（エラー）になる。

#### 解決方法

**方法1: Gradleクラスパス再生成**
```bash
./gradlew cleanEclipse eclipse
```

VSCodeタスク:
```
Tasks: Run Task → "Gradle: Eclipse Classpath"
```

**方法2: Java Language Server再起動**
```
Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
→ VSCode再起動
```

**方法3: build.gradleを確認**
```groovy
plugins {
    id 'eclipse'  // ← これが必須
}
```

### 問題2: コード補完が効かない

#### 症状
Springのアノテーションやメソッドの補完が表示されない。

#### 解決方法

**方法1: ソースとJavadocをダウンロード**

build.gradle:
```groovy
eclipse {
    classpath {
        downloadSources = true
        downloadJavadoc = true
    }
}
```

実行:
```bash
./gradlew cleanEclipse eclipse
```

**方法2: Java拡張機能の設定確認**

.vscode/settings.json:
```json
{
    "java.configuration.updateBuildConfiguration": "automatic"
}
```

### 問題3: ビルドは成功するがVSCodeでエラー表示

#### 症状
- Gradleビルドは成功: `./gradlew build` → BUILD SUCCESSFUL
- VSCodeではエラー表示される

#### 解決方法

**原因**: VSCodeとGradleのクラスパスが同期していない

```bash
# 1. Gradleのビルドディレクトリをクリーン
./gradlew clean

# 2. Eclipseクラスパス再生成
./gradlew cleanEclipse eclipse

# 3. VSCodeのJavaキャッシュクリア
# Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"

# 4. VSCode再起動
```

### 問題4: 依存関係が変更されない

#### 症状
build.gradleに新しい依存関係を追加したが、VSCodeで認識されない。

#### 解決方法

```bash
# 1. Gradle依存関係を更新
./gradlew dependencies --refresh-dependencies

# 2. Eclipseクラスパス再生成
./gradlew cleanEclipse eclipse

# 3. VSCodeリロード
# Ctrl+Shift+P → "Reload Window"
```

### 問題5: WebLogicデプロイ後にソースが見つからない

#### 症状
```
Source not found for UserService
```

#### 解決方法

**方法1: sourcePaths確認**

.vscode/launch.json:
```json
{
    "sourcePaths": [
        "${workspaceFolder}/src/main/java",  // ← パスが正しいか確認
        "${workspaceFolder}/web/src/main/java"  // マルチモジュールの場合
    ]
}
```

**方法2: デバッグ情報がコンパイル時に含まれているか確認**

build.gradle:
```groovy
tasks.withType(JavaCompile) {
    options.debug = true
    options.debugOptions.debugLevel = 'source,lines,vars'
}
```

再ビルド:
```bash
./gradlew clean build
```

---

## ベストプラクティス

### 1. 依存関係管理

#### バージョンを変数で管理

build.gradle:
```groovy
ext {
    springVersion = '5.3.27'
    struts2Version = '2.5.30'
    hibernateVersion = '5.6.15.Final'
}

dependencies {
    implementation "org.springframework:spring-context:${springVersion}"
    implementation "org.springframework:spring-webmvc:${springVersion}"
    implementation "org.apache.struts:struts2-core:${struts2Version}"
}
```

#### 依存関係のスコープを正しく設定

```groovy
dependencies {
    // アプリケーションコード
    implementation 'org.springframework:spring-context:5.3.27'

    // WebLogicで提供される（WARに含めない）
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'

    // コンパイル時のみ必要
    compileOnly 'org.projectlombok:lombok:1.18.26'

    // ランタイムのみ必要
    runtimeOnly 'com.oracle.database.jdbc:ojdbc8:21.9.0.0'

    // テストのみ
    testImplementation 'junit:junit:4.13.2'
}
```

### 2. 開発効率化

#### Gradleタスクのエイリアス

build.gradle:
```groovy
// 高速ビルド（テストスキップ）
task quickBuild(type: GradleBuild) {
    tasks = ['build']
    startParameter.excludedTaskNames = ['test']
}

// ビルド + デプロイ
task bd(dependsOn: ['build', 'deployToWebLogic']) {
    description = 'Build and Deploy'
}
```

実行:
```bash
./gradlew quickBuild
./gradlew bd
```

#### VSCodeキーボードショートカット設定

.vscode/keybindings.json:
```json
[
    {
        "key": "ctrl+shift+b",
        "command": "workbench.action.tasks.runTask",
        "args": "Gradle: Build"
    },
    {
        "key": "ctrl+shift+d",
        "command": "workbench.action.tasks.runTask",
        "args": "Deploy to WebLogic"
    }
]
```

### 3. チーム開発

#### .gitignore

```gitignore
# Gradle
.gradle/
build/
!gradle-wrapper.jar

# Eclipse/VSCode
.classpath
.project
.settings/
bin/

# VSCode個人設定
.vscode/*
!.vscode/settings.json
!.vscode/launch.json
!.vscode/tasks.json
!.vscode/extensions.json

# 環境変数
.env
```

#### 環境変数テンプレート

.env.example:
```bash
# WebLogic設定
WEBLOGIC_HOST=localhost
WEBLOGIC_DEBUG_PORT=8453
WEBLOGIC_ADMIN_URL=t3://localhost:7001
WEBLOGIC_USERNAME=weblogic
WEBLOGIC_PASSWORD=Welcome1

# データベース設定
DB_HOST=localhost
DB_PORT=1521
DB_NAME=ORCL
```

---

## まとめ

この構成により、以下が実現できます:

1. **Gradleで依存関係を自動管理** → ユーザーライブラリの手動設定不要
2. **VSCodeでSpringプロジェクトとして快適に開発** → コード補完、リファクタリング
3. **`./gradlew eclipse`でクラスパス生成** → VSCodeが依存関係を自動認識
4. **`./gradlew build`でWARファイル作成** → WebLogicにデプロイ
5. **F5でデバッグ開始** → ブレークポイント、変数確認

この環境で、効率的な開発とデバッグが可能になります。
