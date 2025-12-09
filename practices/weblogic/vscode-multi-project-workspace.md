# VSCode マルチプロジェクト・ワークスペース構築ガイド

> 複数のマルチモジュールJavaプロジェクトを1つのワークスペースで管理し、相互依存関係を解決する方法

このドキュメントでは、VSCodeで複数のJavaプロジェクト（各プロジェクトが複数のモジュールを持つ）を1つのワークスペースに配置し、プロジェクト間の依存関係を解決する方法を解説します。

---

## 目次

1. [概要](#概要)
2. [シナリオと要件](#シナリオと要件)
3. [VSCode Workspaceの構成](#vscode-workspaceの構成)
4. [プロジェクト間の依存関係解決](#プロジェクト間の依存関係解決)
5. [Eclipseクラスパスでの依存関係管理](#eclipseクラスパスでの依存関係管理)
6. [Gradleでの依存関係管理](#gradleでの依存関係管理)
7. [デバッグ設定](#デバッグ設定)
8. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### VSCodeのプロジェクト管理能力

VSCode Java拡張機能は以下をサポートします:

✅ **マルチプロジェクト・ワークスペース**
- 1つのワークスペースに複数のJavaプロジェクトを配置可能

✅ **マルチモジュール・プロジェクト**
- 各プロジェクトが複数のモジュール（サブプロジェクト）を持つ構成

✅ **プロジェクト間の依存関係**
- ワークスペース内の別プロジェクトのモジュールを参照可能

✅ **ビルドツールサポート**
- Eclipse `.classpath`
- Gradle `build.gradle`
- Maven `pom.xml`
- それらの混在も可能

### アーキテクチャ例

```
VSCode Workspace
├── project-A/                    # プロジェクトA（Eclipseプロジェクト）
│   ├── .classpath
│   ├── module-A1/
│   │   └── src/main/java/
│   └── module-A2/
│       └── src/main/java/
│
├── project-B/                    # プロジェクトB（Gradleプロジェクト）
│   ├── build.gradle
│   ├── settings.gradle
│   ├── module-B1/
│   │   └── src/main/java/
│   └── module-B2/
│       └── src/main/java/
│
└── project-C/                    # プロジェクトC（Mavenプロジェクト）
    ├── pom.xml
    ├── module-C1/
    │   └── src/main/java/
    └── module-C2/
        └── src/main/java/

依存関係の例:
- project-B/module-B1 → project-A/module-A1 を参照
- project-C/module-C2 → project-B/module-B2 を参照
```

---

## シナリオと要件

### 典型的なシナリオ

#### シナリオ1: 複数のWebアプリケーション + 共通ライブラリ

```
Workspace
├── common-lib/                   # 共通ライブラリプロジェクト
│   ├── .classpath
│   ├── util/                     # ユーティリティモジュール
│   ├── domain/                   # ドメインモデル
│   └── infra/                    # インフラ層
│
├── webapp-A/                     # WebアプリケーションA
│   ├── build.gradle
│   ├── web/                      # Webモジュール
│   └── business/                 # ビジネスロジック
│       └── 依存 → common-lib/util, common-lib/domain
│
└── webapp-B/                     # WebアプリケーションB
    ├── build.gradle
    ├── web/
    └── business/
        └── 依存 → common-lib/util, common-lib/domain
```

#### シナリオ2: マイクロサービス構成

```
Workspace
├── shared-lib/                   # 共有ライブラリ
│   ├── api-contracts/            # API定義
│   └── common-utils/             # 共通ユーティリティ
│
├── service-user/                 # ユーザーサービス
│   ├── api/
│   ├── impl/
│   └── 依存 → shared-lib/api-contracts
│
└── service-order/                # 注文サービス
    ├── api/
    ├── impl/
    └── 依存 → shared-lib/api-contracts, service-user/api
```

### 要件

1. **すべてJavaプロジェクト** ✅ サポート
2. **マルチモジュール構成** ✅ サポート
3. **プロジェクト間の相互依存** ✅ サポート（設定必要）
4. **異なるビルドツールの混在** ✅ サポート（Eclipse + Gradle + Maven）
5. **コード補完・参照ジャンプ** ✅ サポート
6. **デバッグ** ✅ サポート

---

## VSCode Workspaceの構成

### 方法1: Workspace ファイルを使用（推奨）

#### my-workspace.code-workspace の作成

```json
{
    "folders": [
        {
            "name": "Common Library",
            "path": "/path/to/common-lib"
        },
        {
            "name": "WebApp A",
            "path": "/path/to/webapp-A"
        },
        {
            "name": "WebApp B",
            "path": "/path/to/webapp-B"
        }
    ],
    "settings": {
        // Java設定
        "java.configuration.updateBuildConfiguration": "automatic",
        "java.import.eclipse.enabled": true,
        "java.import.gradle.enabled": true,
        "java.import.maven.enabled": true,

        // 複数プロジェクトのソースパス
        "java.project.sourcePaths": [
            "common-lib/util/src/main/java",
            "common-lib/domain/src/main/java",
            "webapp-A/web/src/main/java",
            "webapp-A/business/src/main/java",
            "webapp-B/web/src/main/java",
            "webapp-B/business/src/main/java"
        ],

        // プロジェクト間の参照を有効化
        "java.project.referencedLibraries": [
            "common-lib/util/build/libs/**/*.jar",
            "common-lib/domain/build/libs/**/*.jar",
            "webapp-A/business/build/libs/**/*.jar"
        ],

        // デバッグ設定
        "java.debug.settings.hotCodeReplace": "auto",

        // ファイル除外
        "files.exclude": {
            "**/.gradle": true,
            "**/build": false
        }
    }
}
```

#### ワークスペースを開く

```bash
code /path/to/my-workspace.code-workspace
```

### 方法2: フォルダを直接開く（シンプル）

複数のプロジェクトを親ディレクトリにまとめる:

```bash
# ディレクトリ構成
mkdir -p /home/m-miyawaki/dev/my-workspace
cd /home/m-miyawaki/dev/my-workspace

# プロジェクトをシンボリックリンクで配置
ln -s /path/to/common-lib common-lib
ln -s /path/to/webapp-A webapp-A
ln -s /path/to/webapp-B webapp-B

# VSCodeで親ディレクトリを開く
code /home/m-miyawaki/dev/my-workspace
```

VSCodeが自動的に複数のJavaプロジェクトを検出します。

---

## プロジェクト間の依存関係解決

### VSCode Java拡張機能の依存関係解決メカニズム

VSCodeは以下の順序で依存関係を解決します:

1. **同一ワークスペース内のプロジェクト**
   - ワークスペース内の他のプロジェクトのクラスを自動認識

2. **ビルドツールの依存関係定義**
   - `.classpath` (Eclipse)
   - `build.gradle` (Gradle)
   - `pom.xml` (Maven)

3. **Referenced Libraries**
   - `settings.json` の `java.project.referencedLibraries`

### パターン1: ワークスペース内での自動解決

VSCodeは同一ワークスペース内のJavaプロジェクトを自動的に認識します。

#### 例: webapp-A が common-lib を参照

```
Workspace
├── common-lib/
│   └── util/
│       └── src/main/java/
│           └── com/example/common/
│               └── StringUtils.java
│
└── webapp-A/
    └── business/
        └── src/main/java/
            └── com/example/webapp/
                └── UserService.java
```

**UserService.java (webapp-A)**:
```java
package com.example.webapp;

import com.example.common.StringUtils;  // ← common-libを参照

public class UserService {
    public String formatName(String name) {
        return StringUtils.capitalize(name);  // ✅ 自動補完・参照ジャンプ可能
    }
}
```

**条件**:
- 両方のプロジェクトが同一ワークスペースに存在
- VSCode Java拡張機能が両プロジェクトをインポート済み

### パターン2: ビルドツールでの依存関係定義

より明確に依存関係を定義する場合。

#### Gradleの場合

**webapp-A/build.gradle**:
```groovy
dependencies {
    // ワークスペース内の別プロジェクトを参照
    implementation project(':common-lib:util')
    implementation project(':common-lib:domain')
}
```

**settings.gradle（ルート）**:
```groovy
// ワークスペース内の全プロジェクトを含める
include ':common-lib:util'
include ':common-lib:domain'
include ':webapp-A:business'
include ':webapp-A:web'

// プロジェクトの場所を指定
project(':common-lib:util').projectDir = new File('../common-lib/util')
project(':common-lib:domain').projectDir = new File('../common-lib/domain')
```

#### Eclipseの場合

**webapp-A/.classpath**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <!-- 自プロジェクトのソース -->
    <classpathentry kind="src" path="business/src/main/java"/>
    <classpathentry kind="src" path="web/src/main/java"/>

    <!-- 別プロジェクトへの依存 -->
    <classpathentry combineaccessrules="false" kind="src" path="/common-lib-util"/>
    <classpathentry combineaccessrules="false" kind="src" path="/common-lib-domain"/>

    <!-- またはJARファイルとして参照 -->
    <classpathentry kind="lib" path="../common-lib/util/build/libs/util.jar"/>

    <classpathentry kind="output" path="bin"/>
</classpath>
```

**common-lib/.project**（プロジェクト名を定義）:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>common-lib-util</name>  <!-- ← この名前で参照される -->
    <comment></comment>
    <projects></projects>
    <buildSpec>...</buildSpec>
    <natures>...</natures>
</projectDescription>
```

---

## Eclipseクラスパスでの依存関係管理

### 実践例: 複数のEclipseプロジェクト

#### プロジェクト構成

```
Workspace
├── common-lib/                   # Eclipseプロジェクト
│   ├── .classpath
│   ├── .project
│   └── src/main/java/
│       └── com/example/common/
│           └── StringUtils.java
│
└── webapp-A/                     # Eclipseプロジェクト
    ├── .classpath
    ├── .project
    └── src/main/java/
        └── com/example/webapp/
            └── UserService.java
```

#### common-lib/.project

```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>common-lib</name>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
    </natures>
</projectDescription>
```

#### webapp-A/.project

```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>webapp-A</name>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
    </natures>
</projectDescription>
```

#### webapp-A/.classpath（プロジェクト参照）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" path="src/main/java"/>

    <!-- JDK -->
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>

    <!-- 別プロジェクトへの参照 -->
    <classpathentry combineaccessrules="false" kind="src" path="/common-lib"/>

    <classpathentry kind="output" path="bin"/>
</classpath>
```

**重要ポイント**:
- `kind="src"` と `path="/common-lib"` でプロジェクト参照
- `combineaccessrules="false"` で別プロジェクトのクラスにアクセス可能

#### VSCodeでの確認

```bash
# ワークスペースを開く
code /path/to/workspace

# または .code-workspace ファイル
code my-workspace.code-workspace
```

VSCodeが両プロジェクトをインポート:
```
Java Projects
├── common-lib
│   └── src/main/java
│       └── com.example.common
└── webapp-A
    └── src/main/java
        └── com.example.webapp
```

**webapp-A/UserService.java**:
```java
import com.example.common.StringUtils;  // ✅ 補完・ジャンプ可能
```

---

## Gradleでの依存関係管理

### 実践例: Gradleマルチプロジェクト + 外部プロジェクト参照

#### プロジェクト構成

```
Workspace
├── common-lib/                   # Gradleプロジェクト
│   ├── settings.gradle
│   ├── build.gradle
│   ├── util/
│   │   ├── build.gradle
│   │   └── src/main/java/
│   └── domain/
│       ├── build.gradle
│       └── src/main/java/
│
└── webapp-A/                     # Gradleプロジェクト
    ├── settings.gradle
    ├── build.gradle
    ├── business/
    │   ├── build.gradle
    │   └── src/main/java/
    └── web/
        ├── build.gradle
        └── src/main/java/
```

#### common-lib/settings.gradle

```groovy
rootProject.name = 'common-lib'

include 'util'
include 'domain'
```

#### common-lib/build.gradle

```groovy
subprojects {
    apply plugin: 'java'
    apply plugin: 'eclipse'

    group = 'com.example.common'
    version = '1.0.0'

    repositories {
        mavenCentral()
    }
}
```

#### webapp-A/settings.gradle（他プロジェクトを含める）

```groovy
rootProject.name = 'webapp-A'

include 'business'
include 'web'

// 外部プロジェクトを含める
includeBuild('../common-lib') {
    dependencySubstitution {
        substitute module('com.example.common:util') with project(':util')
        substitute module('com.example.common:domain') with project(':domain')
    }
}
```

または、従来の方法:

```groovy
rootProject.name = 'webapp-A'

include 'business'
include 'web'

// 外部モジュールを含める
include ':common-lib:util'
include ':common-lib:domain'

project(':common-lib:util').projectDir = new File('../common-lib/util')
project(':common-lib:domain').projectDir = new File('../common-lib/domain')
```

#### webapp-A/business/build.gradle

```groovy
dependencies {
    // 外部プロジェクトのモジュールを参照
    implementation project(':common-lib:util')
    implementation project(':common-lib:domain')

    // または、includeBuildを使った場合
    // implementation 'com.example.common:util:1.0.0'
    // implementation 'com.example.common:domain:1.0.0'
}
```

#### VSCodeでの設定

**.vscode/settings.json**:
```json
{
    "java.import.gradle.enabled": true,
    "gradle.nestedProjects": true
}
```

Gradleプロジェクトをインポート:
```bash
# VSCodeでワークスペースを開く
code /path/to/workspace

# GradleタスクでEclipseクラスパス生成（VSCodeが自動認識）
cd common-lib
./gradlew eclipse

cd ../webapp-A
./gradlew eclipse
```

---

## デバッグ設定

### 複数プロジェクトを含むデバッグ設定

#### .vscode/launch.json

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "java",
            "name": "Debug WebLogic (WebApp A)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                // webapp-A のソース
                "${workspaceFolder}/webapp-A/web/src/main/java",
                "${workspaceFolder}/webapp-A/business/src/main/java",

                // 依存する common-lib のソース
                "${workspaceFolder}/common-lib/util/src/main/java",
                "${workspaceFolder}/common-lib/domain/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (WebApp B)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8454,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/webapp-B/web/src/main/java",
                "${workspaceFolder}/webapp-B/business/src/main/java",
                "${workspaceFolder}/common-lib/util/src/main/java",
                "${workspaceFolder}/common-lib/domain/src/main/java"
            ]
        }
    ]
}
```

### デバッグの動作

1. **webapp-Aのコードでブレークポイント**
   - `UserService.java` にブレークポイント設定
   - デバッグ開始（F5）
   - ブレークポイントで停止

2. **common-libのコードにステップイン**
   - `StringUtils.capitalize()` で `F11` (Step Into)
   - common-libのソースコードが開く ✅
   - ブレークポイント設定も可能

3. **変数の確認**
   - common-libのオブジェクトも確認可能

---

## トラブルシューティング

### 問題1: プロジェクト間の参照が認識されない

#### 症状
```java
import com.example.common.StringUtils;  // ← 赤線（エラー）
```

#### 解決方法

**方法1: VSCodeでプロジェクトを再インポート**
```
Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
→ "Reload and Delete" を選択
```

**方法2: .classpath の依存関係を確認**

webapp-A/.classpath:
```xml
<!-- プロジェクト参照が定義されているか確認 -->
<classpathentry combineaccessrules="false" kind="src" path="/common-lib"/>
```

**方法3: 両プロジェクトがワークスペースに含まれているか確認**

my-workspace.code-workspace:
```json
{
    "folders": [
        {"path": "/path/to/common-lib"},   // ✅ 両方含める
        {"path": "/path/to/webapp-A"}
    ]
}
```

### 問題2: Gradleの外部プロジェクト参照が動作しない

#### 症状
```
Could not find project :common-lib:util
```

#### 解決方法

**方法1: settings.gradle で正しくプロジェクトを参照**

```groovy
// 相対パスが正しいか確認
project(':common-lib:util').projectDir = new File('../common-lib/util')

// または絶対パス
project(':common-lib:util').projectDir = new File('/absolute/path/to/common-lib/util')
```

**方法2: includeBuild を使用（Gradle 6.0+）**

```groovy
includeBuild('../common-lib')
```

**方法3: Gradleリフレッシュ**

```bash
# VSCodeターミナルで
./gradlew clean build --refresh-dependencies

# Gradleキャッシュクリア
./gradlew cleanEclipse eclipse
```

VSCodeリロード:
```
Ctrl+Shift+P → "Reload Window"
```

### 問題3: デバッグ時に依存プロジェクトのソースが見つからない

#### 症状
```
Source not found for StringUtils.class
```

#### 解決方法

**方法1: sourcePaths に依存プロジェクトを追加**

.vscode/launch.json:
```json
{
    "sourcePaths": [
        "${workspaceFolder}/webapp-A/business/src/main/java",
        "${workspaceFolder}/common-lib/util/src/main/java"  // ← 追加
    ]
}
```

**方法2: ワークスペースフォルダ名を確認**

```
${workspaceFolder}  ← ルートフォルダを指す
```

マルチフォルダワークスペースの場合:
```json
{
    "sourcePaths": [
        "${workspaceFolder:webapp-A}/business/src/main/java",
        "${workspaceFolder:common-lib}/util/src/main/java"
    ]
}
```

### 問題4: ビルド順序の問題

#### 症状
webapp-Aをビルドする前に common-lib がビルドされていない。

#### 解決方法

**Gradleの場合: 依存関係を定義**

webapp-A/build.gradle:
```groovy
dependencies {
    implementation project(':common-lib:util')  // ← Gradleが自動的にビルド順序を解決
}
```

**Eclipseの場合: プロジェクト参照を定義**

webapp-A/.classpath:
```xml
<classpathentry combineaccessrules="false" kind="src" path="/common-lib"/>
```

VSCodeが自動的にビルド順序を解決。

**手動ビルド順序の指定**:
```bash
# 1. common-lib をビルド
cd common-lib
./gradlew build

# 2. webapp-A をビルド
cd ../webapp-A
./gradlew build
```

---

## ベストプラクティス

### 1. ワークスペース構成

#### 推奨: 論理的なグループ化

```
my-workspace.code-workspace
├── "共通ライブラリ" フォルダグループ
│   ├── common-lib
│   └── shared-utils
├── "Webアプリケーション" フォルダグループ
│   ├── webapp-A
│   └── webapp-B
└── "マイクロサービス" フォルダグループ
    ├── service-user
    └── service-order
```

**.code-workspace**:
```json
{
    "folders": [
        {"name": "📚 Common Lib", "path": "/path/to/common-lib"},
        {"name": "📚 Shared Utils", "path": "/path/to/shared-utils"},
        {"name": "🌐 WebApp A", "path": "/path/to/webapp-A"},
        {"name": "🌐 WebApp B", "path": "/path/to/webapp-B"}
    ]
}
```

### 2. 依存関係の管理方針

#### パターンA: すべてGradleで管理

```groovy
// settings.gradle（ルート）
include ':common-lib:util'
include ':common-lib:domain'
include ':webapp-A:business'
include ':webapp-A:web'

// すべてのプロジェクトを1つのGradleビルドで管理
```

**メリット**: 一貫性、ビルド効率
**デメリット**: 大規模化すると遅い

#### パターンB: プロジェクトごとに独立

各プロジェクトが独自のビルドツールを持つ:
```
common-lib/  → Gradle
webapp-A/    → Eclipse
webapp-B/    → Maven
```

依存関係はJARファイルで管理:
```xml
<!-- webapp-A/.classpath -->
<classpathentry kind="lib" path="../common-lib/build/libs/util.jar"/>
```

**メリット**: プロジェクト独立性
**デメリット**: 手動でJARビルド・配置が必要

### 3. バージョン管理

#### .gitignore

```gitignore
# VSCodeワークスペース個人設定
.vscode/
*.code-workspace

# ビルド成果物
build/
bin/
target/

# Eclipse/Gradle生成ファイル
.classpath
.project
.settings/
.gradle/
```

#### チーム共有

```bash
# ワークスペーステンプレート
cp my-workspace.code-workspace my-workspace.code-workspace.example

# .gitignore に追加
echo "*.code-workspace" >> .gitignore
echo "!*.code-workspace.example" >> .gitignore
```

---

## まとめ

VSCodeで複数のマルチモジュールJavaプロジェクトを管理する際:

### ✅ 可能なこと

1. **1つのワークスペースに複数プロジェクト配置**
2. **各プロジェクトがマルチモジュール構成**
3. **プロジェクト間の相互依存関係解決**
4. **異なるビルドツールの混在** (Eclipse + Gradle + Maven)
5. **コード補完・参照ジャンプ**
6. **デバッグ時の依存プロジェクトへのステップイン**

### 🔧 必要な設定

1. **VSCode Workspaceファイル** (`.code-workspace`)
2. **ビルドツールでの依存関係定義** (`.classpath`, `build.gradle`, `pom.xml`)
3. **sourcePaths 設定** (デバッグ用)
4. **Java拡張機能のインストール**

### 📋 推奨構成

```json
// my-workspace.code-workspace
{
    "folders": [
        {"path": "/path/to/project-A"},
        {"path": "/path/to/project-B"},
        {"path": "/path/to/project-C"}
    ],
    "settings": {
        "java.import.gradle.enabled": true,
        "java.import.eclipse.enabled": true
    }
}
```

この構成で、複雑なマルチプロジェクト環境でも効率的に開発・デバッグが可能です。
