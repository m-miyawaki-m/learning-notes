---
title: "VSCode マルチWARプロジェクト統合デプロイ環境"
category: practices
tags:
  - weblogic
  - gradle
  - wlst
  - deployment
  - multi-module
  - vscode
  - tasks
  - java
difficulty: advanced
related:
  - practices/vscode-tasks-complete-guide.md
  - practices/weblogic/vscode-gradle-weblogic-setup.md
  - practices/weblogic/vscode-complex-multimodule-setup.md
  - practices/weblogic/wlst-cli-windows.md
language:
  - java
  - python
  - gradle
last_updated: 2025-12-12
---

# VSCode マルチWARプロジェクト統合デプロイ環境

> 複数のマルチモジュールWARプロジェクト × Gradle exploded WAR × WLSTスクリプト × VS Code Tasks

このドキュメントでは、ワークスペース内に複数のマルチモジュールプロジェクト（それぞれがWARを生成）が存在する場合に、各プロジェクトを独立してexploded形式でデプロイできる統合Gradle構成とWLSTスクリプトの構築方法を解説します。VS Code Tasksで個別デプロイ・一括デプロイの両方に対応させます。

---

## 目次

1. [概要](#概要)
2. [ワークスペース構成の選択](#ワークスペース構成の選択)
3. [プロジェクト構造例](#プロジェクト構造例)
4. [ルートGradle設定](#ルートgradle設定)
5. [個別プロジェクトのGradle設定](#個別プロジェクトのgradle設定)
6. [WLSTスクリプト](#wlstスクリプト)
7. [VS Code Tasks設定](#vs-code-tasks設定)
8. [環境変数設定](#環境変数設定)
9. [使い方](#使い方)
10. [さらなる最適化](#さらなる最適化)
11. [トラブルシューティング](#トラブルシューティング)
12. [関連ドキュメント](#関連ドキュメント)

---

## 概要

### アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────────────────┐
│                    VSCode Workspace                             │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  project-a/      │  │  project-b/      │  │  project-c/  │ │
│  │  ├─ common-lib/  │  │  ├─ core/        │  │  └─ webapp/  │ │
│  │  ├─ business/    │  │  ├─ api/         │  └──────────────┘ │
│  │  └─ webapp/      │  │  └─ webapp/      │                    │
│  └──────────────────┘  └──────────────────┘                    │
│           │                     │                    │          │
│           │ Gradle build        │                    │          │
│           ▼                     ▼                    ▼          │
│     project-a.war         project-b.war        project-c.war   │
│     (exploded)            (exploded)           (exploded)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WLST デプロイ
                              ▼
                 ┌────────────────────────────┐
                 │   WebLogic Server          │
                 │   - project-a (起動中)     │
                 │   - project-b (起動中)     │
                 │   - project-c (起動中)     │
                 └────────────────────────────┘
                              │
                              │ VS Code Tasks
                              ▼
                 ┌────────────────────────────┐
                 │ 個別デプロイ / 一括デプロイ │
                 │ 増分再デプロイ (高速)       │
                 └────────────────────────────┘
```

### 実現する機能

✅ **複数のWARプロジェクトを統合管理**
- ワークスペースに複数のマルチモジュールプロジェクトを配置
- 各プロジェクトがそれぞれWARファイルを生成

✅ **Exploded形式でのデプロイ**
- 開発効率を最大化するexploded WAR形式
- クラスファイルの即座反映（開発モード時）

✅ **柔軟なデプロイ戦略**
- 全WARの一括デプロイ（初回セットアップ）
- 個別WARのデプロイ（個別開発時）
- 増分再デプロイ（変更差分のみ高速反映）

✅ **VS Code統合**
- タスクランナーから簡単操作
- ビルド → デプロイを一括実行
- Ctrl+Shift+B でデフォルトタスク起動

---

## ワークスペース構成の選択

Git でプロジェクトが管理されているが、実際のソースコードは各サブモジュールに存在する場合、VS Code ワークスペースの構成方法を適切に選択する必要があります。

### パターン1: サブモジュールを個別登録（推奨）

**構造例:**
```
workspace-root/
├── project-a/              ← Git repository（サブモジュール管理のみ）
│   ├── common-lib/         ← 実際のコードがあるサブモジュール
│   ├── business-logic/     ← 実際のコードがあるサブモジュール
│   └── webapp/             ← 実際のコードがあるサブモジュール
└── project-b/
    ├── core/
    ├── api/
    └── webapp/
```

**ワークスペース設定（.code-workspace）:**
```json
{
  "folders": [
    {
      "name": "project-a-common",
      "path": "project-a/common-lib"
    },
    {
      "name": "project-a-business",
      "path": "project-a/business-logic"
    },
    {
      "name": "project-a-webapp",
      "path": "project-a/webapp"
    },
    {
      "name": "project-b-core",
      "path": "project-b/core"
    },
    {
      "name": "project-b-api",
      "path": "project-b/api"
    },
    {
      "name": "project-b-webapp",
      "path": "project-b/webapp"
    }
  ],
  "settings": {
    "java.project.referencedLibraries": [
      "project-*/*/lib/**/*.jar"
    ],
    "java.configuration.updateBuildConfiguration": "automatic"
  }
}
```

**利点:**
- ✅ 言語サーバーのパフォーマンス向上（各サブモジュールが独立スコープ）
- ✅ 依存関係の正確な解決（各モジュールの `.classpath` や `build.gradle` が適切に認識）
- ✅ ナビゲーションの精度向上（シンボル検索が関連モジュールにスコープされる）
- ✅ 独立したビルドタスク（各モジュールごとに個別タスク定義可能）

**使用すべき場合:**
- 各サブモジュールが独立した `.classpath` を持つ（Eclipse形式プロジェクト）
- サブモジュール間の依存が明確に分離されている
- 言語サーバーの起動を高速化したい

---

### パターン2: 親プロジェクトレベルで登録

**ワークスペース設定:**
```json
{
  "folders": [
    {
      "name": "project-a",
      "path": "project-a"
    },
    {
      "name": "project-b",
      "path": "project-b"
    },
    {
      "name": "project-c",
      "path": "project-c"
    }
  ],
  "settings": {
    "java.project.referencedLibraries": [
      "**/lib/**/*.jar"
    ]
  }
}
```

**利点:**
- ✅ シンプルなワークスペース構成
- ✅ プロジェクト全体を統一的に管理
- ✅ Gradle のマルチプロジェクトビルドと整合性が取れる

**使用すべき場合:**
- 親プロジェクトに `settings.gradle` があり、すべてのサブモジュールを定義している
- 統一されたビルドビューが必要
- 親プロジェクトに意味のある設定ファイル（build.gradle等）が存在する

---

### パターン3: ハイブリッド方式

親プロジェクトと主要サブモジュールの両方を登録する方法です。

**ワークスペース設定:**
```json
{
  "folders": [
    {
      "name": "workspace-root",
      "path": "."
    },
    {
      "name": "project-a-webapp",
      "path": "project-a/webapp"
    },
    {
      "name": "project-b-webapp",
      "path": "project-b/webapp"
    }
  ],
  "settings": {
    "files.exclude": {
      "**/project-*/": true
    }
  }
}
```

**利点:**
- ✅ ルートレベルでのビルドスクリプト管理
- ✅ 頻繁に編集するモジュールへの高速アクセス
- ✅ 柔軟性が高い

**使用すべき場合:**
- ルートに共通のビルドスクリプトやWLSTスクリプトがある
- 特定のサブモジュール（webapp等）を頻繁に編集する
- プロジェクト全体の構造把握と個別編集の両方が必要

---

## プロジェクト構造例

### 実際のディレクトリ構成

```
workspace/
├── project-a/                    # WARプロジェクト1
│   ├── common-lib/              # サブモジュール
│   │   ├── src/main/java/
│   │   └── build.gradle
│   ├── business-logic/          # サブモジュール
│   │   ├── src/main/java/
│   │   └── build.gradle
│   ├── webapp/                  # WARモジュール
│   │   ├── src/main/java/
│   │   ├── src/main/webapp/
│   │   └── build.gradle
│   ├── settings.gradle
│   └── build.gradle
├── project-b/                    # WARプロジェクト2
│   ├── core/                    # サブモジュール
│   │   ├── src/main/java/
│   │   └── build.gradle
│   ├── api/                     # サブモジュール
│   │   ├── src/main/java/
│   │   └── build.gradle
│   ├── webapp/                  # WARモジュール
│   │   ├── src/main/java/
│   │   ├── src/main/webapp/
│   │   └── build.gradle
│   ├── settings.gradle
│   └── build.gradle
├── project-c/                    # WARプロジェクト3
│   ├── webapp/                  # 単一モジュール構成
│   │   ├── src/main/java/
│   │   ├── src/main/webapp/
│   │   └── build.gradle
│   ├── settings.gradle
│   └── build.gradle
├── scripts/
│   ├── deploy-all.py            # 全WARデプロイ
│   ├── deploy-single.py         # 単一WARデプロイ
│   └── redeploy.py              # 増分デプロイ
├── settings.gradle              # ルート設定
├── build.gradle                 # ルートビルド
├── .env                         # 環境変数
└── .vscode/
    └── tasks.json               # VS Code タスク定義
```

---

## ルートGradle設定

### settings.gradle（ルート）

```gradle
rootProject.name = 'weblogic-workspace'

// 各プロジェクトをインクルード
include 'project-a:common-lib'
include 'project-a:business-logic'
include 'project-a:webapp'

include 'project-b:core'
include 'project-b:api'
include 'project-b:webapp'

include 'project-c:webapp'
```

### build.gradle（ルート）

```gradle
// 全サブプロジェクト共通設定
subprojects {
    apply plugin: 'java'

    group = 'com.example'
    version = '1.0.0'

    sourceCompatibility = '11'
    targetCompatibility = '11'

    repositories {
        mavenCentral()
    }

    dependencies {
        // 共通の依存関係
        testImplementation 'junit:junit:4.13.2'
    }
}

// WAR プロジェクトの共通設定
configure(subprojects.findAll { it.name == 'webapp' }) {
    apply plugin: 'war'

    // exploded WAR タスク
    task explodedWar(type: Sync) {
        description = 'Create exploded WAR directory'
        group = 'build'

        into "$buildDir/exploded/${rootProject.name}-${project.parent.name}"

        with war

        // 依存プロジェクトのクラスを含める
        into('WEB-INF/classes') {
            project.parent.subprojects.findAll { it != project }.each { subProj ->
                from subProj.sourceSets.main.output
            }
        }

        // ライブラリを含める
        into('WEB-INF/lib') {
            from configurations.runtimeClasspath
        }
    }

    build.dependsOn explodedWar
}

// 全WARをビルドするタスク
task buildAllWars {
    description = 'Build all WAR projects in exploded format'
    group = 'build'
    dependsOn subprojects.findAll { it.name == 'webapp' }.collect { it.tasks.explodedWar }
}

// 全WARをデプロイするタスク
task deployAllWars(type: Exec, dependsOn: buildAllWars) {
    description = 'Deploy all WARs to WebLogic using WLST'
    group = 'deployment'

    environment 'WL_HOME', System.env.WL_HOME ?: '/path/to/wlserver'

    commandLine 'java',
        '-cp', "${System.env.WL_HOME}/server/lib/weblogic.jar",
        'weblogic.WLST',
        'scripts/deploy-all.py'
}
```

---

## 個別プロジェクトのGradle設定

### project-a/build.gradle

```gradle
// プロジェクトA全体の設定

allprojects {
    repositories {
        mavenCentral()
    }
}

// サブモジュール共通設定
subprojects {
    apply plugin: 'java'

    dependencies {
        // 共通の依存関係
        implementation 'org.slf4j:slf4j-api:1.7.36'
    }
}
```

### project-a/settings.gradle

```gradle
rootProject.name = 'project-a'

include 'common-lib'
include 'business-logic'
include 'webapp'
```

### project-a/webapp/build.gradle

```gradle
plugins {
    id 'war'
}

dependencies {
    // 同一プロジェクト内のサブモジュール依存
    implementation project(':common-lib')
    implementation project(':business-logic')

    // 外部ライブラリ
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
    implementation 'org.springframework:spring-webmvc:5.3.20'
}

// このプロジェクト専用のデプロイタスク
task deployThisWar(type: Exec, dependsOn: explodedWar) {
    description = 'Deploy project-a WAR to WebLogic'
    group = 'deployment'

    environment 'DEPLOY_PROJECT', 'project-a'
    environment 'DEPLOY_PATH', "$buildDir/exploded/weblogic-workspace-project-a"
    environment 'WL_HOME', System.env.WL_HOME ?: '/path/to/wlserver'

    commandLine 'java',
        '-cp', "${System.env.WL_HOME}/server/lib/weblogic.jar",
        'weblogic.WLST',
        "${rootProject.rootDir.parentFile}/scripts/deploy-single.py"
}

task redeployThisWar(type: Exec, dependsOn: explodedWar) {
    description = 'Redeploy project-a WAR to WebLogic (fast incremental)'
    group = 'deployment'

    environment 'DEPLOY_PROJECT', 'project-a'
    environment 'DEPLOY_PATH', "$buildDir/exploded/weblogic-workspace-project-a"
    environment 'WL_HOME', System.env.WL_HOME ?: '/path/to/wlserver'

    commandLine 'java',
        '-cp', "${System.env.WL_HOME}/server/lib/weblogic.jar",
        'weblogic.WLST',
        "${rootProject.rootDir.parentFile}/scripts/redeploy.py"
}
```

---

## WLSTスクリプト

### scripts/deploy-all.py（全WARデプロイ）

```python
import os
import sys

# 接続情報
adminUrl = os.getenv('WL_ADMIN_URL', 't3://localhost:7001')
username = os.getenv('WL_USERNAME', 'weblogic')
password = os.getenv('WL_PASSWORD')
targetServers = 'AdminServer'

# デプロイするWARの定義
wars = [
    {
        'name': 'project-a',
        'path': '/workspace/project-a/webapp/build/exploded/weblogic-workspace-project-a',
        'contextRoot': '/project-a'
    },
    {
        'name': 'project-b',
        'path': '/workspace/project-b/webapp/build/exploded/weblogic-workspace-project-b',
        'contextRoot': '/project-b'
    },
    {
        'name': 'project-c',
        'path': '/workspace/project-c/webapp/build/exploded/weblogic-workspace-project-c',
        'contextRoot': '/project-c'
    }
]

# 接続
print('Connecting to WebLogic Server...')
try:
    connect(username, password, adminUrl)
except Exception, e:
    print('ERROR: Failed to connect to WebLogic Server')
    print('URL: ' + adminUrl)
    print('Error: ' + str(e))
    exit(1)

domainRuntime()
cd('AppRuntimeStateRuntime/AppRuntimeStateRuntime')
deployedApps = ls(returnMap='true')

# 各WARをデプロイ
for war in wars:
    appName = war['name']
    appPath = war['path']
    contextRoot = war['contextRoot']

    print('\n' + '='*50)
    print('Processing: ' + appName)
    print('='*50)

    # 既存アプリの確認
    if appName in deployedApps:
        print('Stopping and undeploying existing application...')
        try:
            stopApplication(appName)
            undeploy(appName)
        except Exception, e:
            print('Warning: Failed to undeploy existing app: ' + str(e))

    # デプロイ
    print('Deploying ' + appName + '...')
    try:
        deploy(
            appName,
            appPath,
            targets=targetServers,
            upload='false',
            stageMode='nostage',
            contextRoot=contextRoot
        )

        print('Starting ' + appName + '...')
        startApplication(appName)
        print('Successfully deployed: ' + appName)
    except Exception, e:
        print('ERROR: Failed to deploy ' + appName)
        print('Error: ' + str(e))

print('\n' + '='*50)
print('All applications deployed successfully!')
print('='*50)

disconnect()
exit()
```

### scripts/deploy-single.py（単一WARデプロイ）

```python
import os

# 環境変数から取得
projectName = os.getenv('DEPLOY_PROJECT')
appPath = os.getenv('DEPLOY_PATH')
adminUrl = os.getenv('WL_ADMIN_URL', 't3://localhost:7001')
username = os.getenv('WL_USERNAME', 'weblogic')
password = os.getenv('WL_PASSWORD')
targetServers = 'AdminServer'

if not projectName or not appPath:
    print('ERROR: DEPLOY_PROJECT and DEPLOY_PATH must be set')
    exit(1)

contextRoot = '/' + projectName

print('='*50)
print('Deploying: ' + projectName)
print('Path: ' + appPath)
print('Context Root: ' + contextRoot)
print('='*50)

# 接続
try:
    connect(username, password, adminUrl)
except Exception, e:
    print('ERROR: Failed to connect to WebLogic Server')
    print('Error: ' + str(e))
    exit(1)

domainRuntime()
cd('AppRuntimeStateRuntime/AppRuntimeStateRuntime')
appExists = projectName in ls(returnMap='true')

if appExists:
    print('Stopping existing application...')
    try:
        stopApplication(projectName)
    except Exception, e:
        print('Warning: Failed to stop app: ' + str(e))

    print('Undeploying existing application...')
    try:
        undeploy(projectName)
    except Exception, e:
        print('Warning: Failed to undeploy: ' + str(e))

# デプロイ
print('Deploying application...')
try:
    deploy(
        projectName,
        appPath,
        targets=targetServers,
        upload='false',
        stageMode='nostage',
        contextRoot=contextRoot
    )

    print('Starting application...')
    startApplication(projectName)
    print('Successfully deployed: ' + projectName)
except Exception, e:
    print('ERROR: Failed to deploy')
    print('Error: ' + str(e))
    disconnect()
    exit(1)

disconnect()
exit()
```

### scripts/redeploy.py（増分デプロイ）

```python
import os

projectName = os.getenv('DEPLOY_PROJECT')
appPath = os.getenv('DEPLOY_PATH')
adminUrl = os.getenv('WL_ADMIN_URL', 't3://localhost:7001')
username = os.getenv('WL_USERNAME', 'weblogic')
password = os.getenv('WL_PASSWORD')

if not projectName or not appPath:
    print('ERROR: DEPLOY_PROJECT and DEPLOY_PATH must be set')
    exit(1)

print('='*50)
print('Redeploying: ' + projectName)
print('Path: ' + appPath)
print('='*50)

try:
    connect(username, password, adminUrl)
except Exception, e:
    print('ERROR: Failed to connect to WebLogic Server')
    print('Error: ' + str(e))
    exit(1)

try:
    print('Performing redeploy (hot swap)...')
    redeploy(projectName, appPath, upload='false', stageMode='nostage')
    print('Successfully redeployed: ' + projectName)
except Exception, e:
    print('Redeploy failed: ' + str(e))
    print('Performing full deploy instead...')

    try:
        domainRuntime()
        cd('AppRuntimeStateRuntime/AppRuntimeStateRuntime')

        print('Stopping application...')
        stopApplication(projectName)

        print('Undeploying application...')
        undeploy(projectName)

        contextRoot = '/' + projectName
        print('Deploying application...')
        deploy(projectName, appPath, targets='AdminServer', upload='false', stageMode='nostage', contextRoot=contextRoot)

        print('Starting application...')
        startApplication(projectName)
        print('Successfully deployed: ' + projectName)
    except Exception, e2:
        print('ERROR: Full deploy also failed')
        print('Error: ' + str(e2))
        disconnect()
        exit(1)

disconnect()
exit()
```

---

## VS Code Tasks設定

### .vscode/tasks.json

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "WebLogic: Deploy All WARs",
            "type": "shell",
            "command": "./gradlew",
            "args": ["deployAllWars"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "clear": true
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Build All WARs",
            "type": "shell",
            "command": "./gradlew",
            "args": ["buildAllWars"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Deploy project-a",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-a:webapp:deployThisWar"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Redeploy project-a",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-a:webapp:redeployThisWar"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Deploy project-b",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-b:webapp:deployThisWar"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Redeploy project-b",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-b:webapp:redeployThisWar"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Deploy project-c",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-c:webapp:deployThisWar"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "WebLogic: Redeploy project-c",
            "type": "shell",
            "command": "./gradlew",
            "args": [":project-c:webapp:redeployThisWar"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Gradle: Clean All",
            "type": "shell",
            "command": "./gradlew",
            "args": ["clean"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```

---

## 環境変数設定

### workspace/.env（Linux/macOS）

```bash
# WebLogic環境変数
export WL_HOME=/path/to/Oracle/Middleware/wlserver
export DOMAIN_HOME=/path/to/domains/mydomain
export JAVA_HOME=/path/to/jdk

# WebLogic接続情報
export WL_ADMIN_URL=t3://localhost:7001
export WL_USERNAME=weblogic
export WL_PASSWORD=password123

# デプロイ設定
export DEPLOY_TARGET=AdminServer
```

### 環境変数の読み込み（Linux/macOS）

**~/.bashrc または ~/.zshrc に追加:**
```bash
# WebLogic Workspace環境変数
if [ -f ~/workspace/.env ]; then
    source ~/workspace/.env
fi
```

### Windows環境での設定

**workspace/setenv.bat:**
```batch
@echo off
REM WebLogic環境変数
set WL_HOME=C:\Oracle\Middleware\wlserver
set DOMAIN_HOME=C:\Oracle\Middleware\user_projects\domains\mydomain
set JAVA_HOME=C:\Program Files\Java\jdk11

REM WebLogic接続情報
set WL_ADMIN_URL=t3://localhost:7001
set WL_USERNAME=weblogic
set WL_PASSWORD=password123

REM デプロイ設定
set DEPLOY_TARGET=AdminServer

echo Environment variables set for WebLogic workspace
```

**使い方:**
```batch
cd C:\workspace
call setenv.bat
gradlew deployAllWars
```

### Docker環境での設定

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  weblogic:
    image: oracle/weblogic:12.2.1.4-dev
    ports:
      - "7001:7001"
      - "9002:9002"
    environment:
      - ADMIN_NAME=weblogic
      - ADMIN_PASSWORD=password123
      - DOMAIN_NAME=mydomain
    volumes:
      - ./project-a/webapp/build/exploded:/u01/oracle/deploy/project-a
      - ./project-b/webapp/build/exploded:/u01/oracle/deploy/project-b
      - ./project-c/webapp/build/exploded:/u01/oracle/deploy/project-c
```

---

## 使い方

### 初回セットアップ

1. **環境変数の設定:**
   ```bash
   # Linux/macOS
   source workspace/.env

   # Windows
   call workspace\setenv.bat
   ```

2. **すべてのWARをビルド:**
   ```bash
   ./gradlew buildAllWars
   ```

3. **すべてのWARをデプロイ:**
   ```bash
   ./gradlew deployAllWars
   ```

### 日常的な開発フロー

**パターン1: 特定のプロジェクトのみ開発している場合**

```bash
# project-a を開発中
./gradlew :project-a:webapp:redeployThisWar
```

**VS Code から:**
- `Ctrl+Shift+P` → "Tasks: Run Task" → "WebLogic: Redeploy project-a"
- または `Ctrl+Shift+B`（デフォルトビルドタスク）

**パターン2: 複数プロジェクトを並行開発している場合**

```bash
# project-a と project-b を更新
./gradlew :project-a:webapp:redeployThisWar
./gradlew :project-b:webapp:redeployThisWar
```

**パターン3: 新規WARを追加した場合**

```bash
# 新規WARは初回デプロイが必要
./gradlew :project-new:webapp:deployThisWar
```

### WebLogic サーバーの確認

**デプロイ状態の確認:**
```bash
# WebLogic コンソール
http://localhost:7001/console

# 各アプリケーションのアクセス
http://localhost:7001/project-a/
http://localhost:7001/project-b/
http://localhost:7001/project-c/
```

---

## さらなる最適化

### クラスファイルのみの更新（超高速）

開発モードでは、WebLogic が exploded WAR のクラスファイル変更を自動検出してリロードします。これを活用した超高速デプロイ方法を紹介します。

**各 webapp/build.gradle に追加:**

```gradle
task quickUpdate(type: Copy) {
    description = 'Copy only changed class files (fastest)'
    group = 'deployment'

    from sourceSets.main.output.classesDirs
    into "$buildDir/exploded/weblogic-workspace-${project.parent.name}/WEB-INF/classes"

    // 依存プロジェクトのクラスもコピー
    project.parent.subprojects.findAll { it != project }.each { subProj ->
        from subProj.sourceSets.main.output.classesDirs
    }
}

// コンパイル後に自動実行
quickUpdate.dependsOn classes
```

**使い方:**
```bash
# Javaファイルを編集後
./gradlew :project-a:webapp:quickUpdate

# WebLogic が自動的にクラスをリロード（数秒で反映）
```

**VS Code Tasks に追加:**

```json
{
    "label": "WebLogic: Quick Update project-a",
    "type": "shell",
    "command": "./gradlew",
    "args": [":project-a:webapp:quickUpdate"],
    "group": {
        "kind": "build",
        "isDefault": true
    },
    "presentation": {
        "reveal": "silent",
        "panel": "shared"
    },
    "problemMatcher": []
}
```

### WebLogic 開発モードの有効化

**setDomainEnv.sh (Linux) または setDomainEnv.cmd (Windows) に追加:**

```bash
# Linux/macOS
export PRODUCTION_MODE=false
export JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.ProductionModeEnabled=false"

# Windows
set PRODUCTION_MODE=false
set JAVA_OPTIONS=%JAVA_OPTIONS% -Dweblogic.ProductionModeEnabled=false
```

**開発モードの利点:**
- クラスファイルの自動リロード
- JSP の即座コンパイル
- デバッグ情報の詳細化

### CI/CDパイプライン統合

**GitHub Actions の例（.github/workflows/deploy.yml）:**

```yaml
name: Deploy to WebLogic

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 11
        uses: actions/setup-java@v3
        with:
          java-version: '11'
          distribution: 'temurin'

      - name: Build with Gradle
        run: ./gradlew buildAllWars

      - name: Deploy to WebLogic
        env:
          WL_HOME: ${{ secrets.WL_HOME }}
          WL_ADMIN_URL: ${{ secrets.WL_ADMIN_URL }}
          WL_USERNAME: ${{ secrets.WL_USERNAME }}
          WL_PASSWORD: ${{ secrets.WL_PASSWORD }}
        run: ./gradlew deployAllWars
```

**GitLab CI の例（.gitlab-ci.yml）:**

```yaml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - ./gradlew buildAllWars
  artifacts:
    paths:
      - project-*/webapp/build/exploded/

deploy:
  stage: deploy
  script:
    - export WL_HOME=$WL_HOME_PATH
    - export WL_ADMIN_URL=$WL_ADMIN_URL
    - export WL_USERNAME=$WL_USERNAME
    - export WL_PASSWORD=$WL_PASSWORD
    - ./gradlew deployAllWars
  only:
    - main
```

---

## トラブルシューティング

### ワークスペース関連

#### 問題: 依存関係が解決されない

**症状:**
- サブモジュール間の import が認識されない
- 赤い波線エラーが表示される

**解決策:**

1. **Java Language Server のリロード:**
   ```
   Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
   ```

2. **ワークスペース設定の確認:**
   ```json
   {
     "java.project.referencedLibraries": [
       "project-*/*/lib/**/*.jar"
     ],
     "java.configuration.updateBuildConfiguration": "automatic"
   }
   ```

3. **Gradle 同期の実行:**
   ```bash
   ./gradlew --refresh-dependencies
   ```

#### 問題: 言語サーバーが起動しない

**症状:**
- コード補完が効かない
- シンボルの解決ができない

**解決策:**

1. **Java Extension Pack の再インストール:**
   - VS Code 拡張機能から "Java Extension Pack" をアンインストール
   - 再度インストール

2. **ワークスペースのキャッシュクリア:**
   ```bash
   rm -rf .vscode
   rm -rf .metadata
   ```

3. **設定のリセット:**
   ```
   Ctrl+Shift+P → "Java: Clean the Java Language Server Workspace"
   ```

#### 問題: モジュール間の参照が認識されない

**症状:**
- `project-a/business-logic` から `project-a/common-lib` の参照ができない

**解決策:**

1. **settings.gradle の確認:**
   ```gradle
   // project-a/settings.gradle
   include 'common-lib'
   include 'business-logic'
   include 'webapp'
   ```

2. **build.gradle の依存関係確認:**
   ```gradle
   // project-a/business-logic/build.gradle
   dependencies {
       implementation project(':common-lib')
   }
   ```

3. **ワークスペース構成の見直し:**
   - パターン1（サブモジュール個別登録）に変更してみる

---

### Gradle関連

#### 問題: exploded WAR 生成エラー

**症状:**
```
Task :project-a:webapp:explodedWar FAILED
Could not copy file '...' to '...'
```

**解決策:**

1. **既存のビルドディレクトリをクリーン:**
   ```bash
   ./gradlew clean
   ```

2. **WebLogic がファイルをロックしている場合:**
   - WebLogic サーバーを停止
   - ビルドを再実行
   - WebLogic を再起動

3. **パーミッションエラーの場合:**
   ```bash
   chmod -R 755 project-*/webapp/build
   ```

#### 問題: サブモジュールのクラスが含まれない

**症状:**
- WARファイル内に依存モジュールのクラスが含まれていない
- ClassNotFoundException が発生

**解決策:**

1. **explodedWar タスクの確認:**
   ```gradle
   task explodedWar(type: Sync) {
       into "$buildDir/exploded/${rootProject.name}-${project.parent.name}"

       with war

       // この部分が必要
       into('WEB-INF/classes') {
           project.parent.subprojects.findAll { it != project }.each { subProj ->
               from subProj.sourceSets.main.output
           }
       }
   }
   ```

2. **依存関係の明示的な宣言:**
   ```gradle
   dependencies {
       implementation project(':common-lib')
       implementation project(':business-logic')
   }
   ```

3. **ビルド順序の確認:**
   ```gradle
   explodedWar.dependsOn(':common-lib:classes', ':business-logic:classes')
   ```

#### 問題: タスク依存関係エラー

**症状:**
```
Circular dependency between the following tasks:
:project-a:webapp:explodedWar
```

**解決策:**

1. **循環依存の確認:**
   ```bash
   ./gradlew :project-a:webapp:explodedWar --dry-run
   ```

2. **依存関係の整理:**
   - サブモジュール間の相互依存を避ける
   - 共通モジュールを作成して依存を一方向にする

---

### WLST/WebLogic関連

#### 問題: 接続エラー

**症状:**
```
ERROR: Failed to connect to WebLogic Server
URL: t3://localhost:7001
Error: [Errno 111] Connection refused
```

**解決策:**

1. **WebLogic サーバーの起動確認:**
   ```bash
   # 起動スクリプトの実行
   $DOMAIN_HOME/bin/startWebLogic.sh

   # ログの確認
   tail -f $DOMAIN_HOME/servers/AdminServer/logs/AdminServer.log
   ```

2. **ポート番号の確認:**
   ```bash
   netstat -an | grep 7001
   ```

3. **ファイアウォールの確認:**
   ```bash
   # Linux
   sudo ufw allow 7001

   # Windows
   # ファイアウォール設定でポート7001を許可
   ```

4. **接続URLの確認:**
   ```python
   # t3プロトコルが正しいか確認
   adminUrl = 't3://localhost:7001'

   # SSL使用時は t3s
   adminUrl = 't3s://localhost:7002'
   ```

#### 問題: デプロイ失敗

**症状:**
```
ERROR: Failed to deploy project-a
Error: [Deployer:149164]The deployment failed
```

**解決策:**

1. **アプリケーションパスの確認:**
   ```python
   # 絶対パスを使用
   appPath = '/full/path/to/workspace/project-a/webapp/build/exploded/...'

   # 相対パスは避ける
   ```

2. **exploded WAR の存在確認:**
   ```bash
   ls -la project-a/webapp/build/exploded/
   ```

3. **WebLogic ログの確認:**
   ```bash
   tail -f $DOMAIN_HOME/servers/AdminServer/logs/AdminServer.log
   ```

4. **デプロイモードの確認:**
   ```python
   # nostage モードを使用（exploded WAR用）
   deploy(
       appName,
       appPath,
       targets=targetServers,
       upload='false',
       stageMode='nostage',  # ← 重要
       contextRoot=contextRoot
   )
   ```

#### 問題: redeploy 失敗時のフォールバック

**症状:**
```
Redeploy failed: weblogic.management.DeploymentException
```

**解決策:**

redeploy.py スクリプトは自動的にフォールバックを実行しますが、それでも失敗する場合：

1. **手動でのアンデプロイ → デプロイ:**
   ```bash
   ./gradlew :project-a:webapp:deployThisWar
   ```

2. **WebLogic の再起動:**
   ```bash
   $DOMAIN_HOME/bin/stopWebLogic.sh
   $DOMAIN_HOME/bin/startWebLogic.sh
   ```

3. **アプリケーションの完全削除:**
   ```bash
   # WebLogic Console にアクセス
   # Deployments → アプリケーション選択 → Delete
   # その後、再度デプロイ
   ```

#### 問題: パスワード認証エラー

**症状:**
```
ERROR: Authentication denied: Boot identity not valid
```

**解決策:**

1. **環境変数の確認:**
   ```bash
   echo $WL_USERNAME
   echo $WL_PASSWORD
   ```

2. **boot.properties の作成（パスワード保存）:**
   ```bash
   mkdir -p $DOMAIN_HOME/servers/AdminServer/security
   cat > $DOMAIN_HOME/servers/AdminServer/security/boot.properties <<EOF
   username=weblogic
   password=password123
   EOF
   ```

3. **WLST スクリプトでの認証情報確認:**
   ```python
   # スクリプト内でデバッグ出力
   print('Username: ' + username)
   # パスワードは出力しない（セキュリティ）
   ```

---

## 関連ドキュメント

このドキュメントと合わせて参照すると効果的なドキュメント一覧です：

### 開発環境セットアップ
- **[VSCode 複雑なマルチモジュール環境の完全構築ガイド](vscode-complex-multimodule-setup.md)** - 開発環境の詳細なセットアップ（Eclipse classpath、デバッグ設定等）
- **[VSCode マルチプロジェクトワークスペース](vscode-multi-project-workspace.md)** - ワークスペース構成の基本

### Gradle連携
- **[VSCode WebLogic Gradle連携](vscode-gradle-weblogic-setup.md)** - Gradle と WebLogic の基本的な統合方法
- **[VSCode Spring + Gradle + WebLogic](vscode-spring-gradle-weblogic.md)** - Spring Framework を使用する場合の設定

### デバッグ
- **[VSCode WebLogicリモートデバッグ](vscode-weblogic-debug.md)** - リモートデバッグの詳細設定とトラブルシューティング

### WebLogic設定
- **[WebLogic Configuration](weblogic-configuration.md)** - WebLogic サーバーの基本設定
- **[WLST CLI操作 (Windows)](wlst-cli-windows.md)** - WLST コマンドリファレンス

### クイックリファレンス
- **[VSCode WebLogic チートシート](vscode-weblogic-cheatsheet.md)** - よく使うコマンドとタスクの一覧

---

> このドキュメントは継続的に更新されます。質問や改善提案があれば、プロジェクトのIssueに投稿してください。
