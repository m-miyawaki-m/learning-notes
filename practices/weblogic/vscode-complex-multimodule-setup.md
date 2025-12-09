# VSCode 複雑なマルチモジュール環境の完全構築ガイド

> 複数プロジェクト × サブディレクトリモジュール × Eclipse classpath × Gradleビルド × WebLogicデバッグ

このドキュメントでは、以下の複雑な環境をVSCodeで実現する方法を解説します：

- ワークスペースに複数のプロジェクトを配置
- 各プロジェクトのサブディレクトリに `.classpath` を持つモジュール
- プロジェクト間・モジュール間の相互依存
- 外部Gradle設定でビルド
- WebLogicでリモートデバッグ

---

## 目次

1. [環境構成の概要](#環境構成の概要)
2. [プロジェクト構造の詳細](#プロジェクト構造の詳細)
3. [VSCode Workspace設定](#vscode-workspace設定)
4. [Eclipseクラスパスの設定](#eclipseクラスパスの設定)
5. [Gradleビルド設定](#gradleビルド設定)
6. [WebLogicデバッグ設定](#weblogicデバッグ設定)
7. [実践的な開発フロー](#実践的な開発フロー)
8. [トラブルシューティング](#トラブルシューティング)

---

## 環境構成の概要

### アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────────────┐
│                  VSCode Workspace                           │
│                                                             │
│  ┌─────────────────┐       ┌─────────────────┐             │
│  │  Project-A      │       │  Project-B      │             │
│  │  ├── module-A1/ │       │  ├── module-B1/ │             │
│  │  │   └─.classpath│◄──────┤  │   └─.classpath│            │
│  │  └── module-A2/ │  参照  │  └── module-B2/ │             │
│  │      └─.classpath│       │      └─.classpath│             │
│  └─────────────────┘       └─────────────────┘             │
│           │                         │                       │
│           │ Gradle build            │ Gradle build          │
│           ▼                         ▼                       │
│      myapp-A.war                myapp-B.war                 │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ Deploy
                     ▼
         ┌──────────────────────────┐
         │   WebLogic Server        │
         │   - Debug Mode (JDWP)    │
         │   - Port 8453, 8454      │
         └──────────────────────────┘
                     │
                     │ Remote Debug
                     ▼
         ┌──────────────────────────┐
         │   VSCode Debugger        │
         │   - Breakpoints          │
         │   - Step execution       │
         │   - Variable inspection  │
         └──────────────────────────┘
```

### 実現する機能

✅ **マルチプロジェクト・マルチモジュール**
- ワークスペースに複数のプロジェクトを配置
- 各プロジェクトのサブディレクトリに独立したモジュール（`.classpath`あり）

✅ **相互依存関係の解決**
- Project-A/module-A1 → Project-B/module-B1 を参照
- コード補完、参照ジャンプが動作

✅ **Gradleビルド**
- 外部のGradle設定を使ってWARファイルをビルド

✅ **WebLogicデバッグ**
- WebLogicにデプロイしたアプリをVSCodeでリモートデバッグ
- 依存モジュールにもステップイン可能

---

## プロジェクト構造の詳細

### 実際の構成例

```
/path/to/workspace/
│
├── common-project/                    # 共通プロジェクト
│   ├── .project                       # Eclipseプロジェクト設定（ルート）
│   ├── build.gradle                   # Gradleビルド設定
│   ├── settings.gradle                # Gradleモジュール定義
│   │
│   ├── common-util/                   # モジュール1
│   │   ├── .classpath                 # Eclipse個別モジュール設定
│   │   ├── .project
│   │   ├── build.gradle
│   │   └── src/
│   │       └── main/java/
│   │           └── com/example/common/util/
│   │               └── StringUtils.java
│   │
│   └── common-domain/                 # モジュール2
│       ├── .classpath
│       ├── .project
│       ├── build.gradle
│       └── src/
│           └── main/java/
│               └── com/example/common/domain/
│                   └── User.java
│
└── webapp-project/                    # Webアプリケーションプロジェクト
    ├── .project
    ├── build.gradle
    ├── settings.gradle
    │
    ├── webapp-business/               # ビジネスロジックモジュール
    │   ├── .classpath                 # common-utilを参照
    │   ├── .project
    │   ├── build.gradle
    │   └── src/
    │       └── main/java/
    │           └── com/example/webapp/service/
    │               └── UserService.java
    │
    └── webapp-web/                    # Webモジュール
        ├── .classpath                 # webapp-businessを参照
        ├── .project
        ├── build.gradle
        └── src/
            ├── main/java/
            │   └── com/example/webapp/controller/
            │       └── UserController.java
            └── main/webapp/
                └── WEB-INF/
                    └── web.xml
```

### 重要なポイント

1. **ルートに `.project`** - プロジェクト全体のEclipse設定
2. **サブディレクトリに `.classpath`** - 各モジュールの個別設定
3. **Gradleも併用** - ビルドにはGradleを使用
4. **相互参照** - webapp-business → common-util を参照

---

## VSCode Workspace設定

### my-workspace.code-workspace の作成

```json
{
    "folders": [
        {
            "name": "📚 Common Project",
            "path": "/path/to/workspace/common-project"
        },
        {
            "name": "🌐 WebApp Project",
            "path": "/path/to/workspace/webapp-project"
        }
    ],
    "settings": {
        // Java基本設定
        "java.configuration.updateBuildConfiguration": "automatic",

        // Eclipseプロジェクトのインポート有効化
        "java.import.eclipse.enabled": true,

        // Gradleプロジェクトのインポート有効化
        "java.import.gradle.enabled": true,
        "gradle.nestedProjects": true,

        // 複数プロジェクトのソースパス（全モジュール）
        "java.project.sourcePaths": [
            "common-project/common-util/src/main/java",
            "common-project/common-domain/src/main/java",
            "webapp-project/webapp-business/src/main/java",
            "webapp-project/webapp-web/src/main/java"
        ],

        // ビルド成果物の参照
        "java.project.referencedLibraries": [
            "common-project/common-util/build/libs/**/*.jar",
            "common-project/common-domain/build/libs/**/*.jar",
            "webapp-project/webapp-business/build/libs/**/*.jar"
        ],

        // デバッグ設定
        "java.debug.settings.hotCodeReplace": "auto",
        "java.debug.settings.enableHotCodeReplace": true,

        // ファイル除外
        "files.exclude": {
            "**/.gradle": true,
            "**/.settings": true
        },

        // 検索除外
        "search.exclude": {
            "**/build": true,
            "**/.gradle": true
        }
    },
    "launch": {
        "version": "0.2.0",
        "configurations": [
            {
                "type": "java",
                "name": "Debug WebLogic (WebApp)",
                "request": "attach",
                "hostName": "localhost",
                "port": 8453,
                "timeout": 30000,
                "sourcePaths": [
                    "${workspaceFolder:WebApp Project}/webapp-web/src/main/java",
                    "${workspaceFolder:WebApp Project}/webapp-business/src/main/java",
                    "${workspaceFolder:Common Project}/common-util/src/main/java",
                    "${workspaceFolder:Common Project}/common-domain/src/main/java"
                ]
            }
        ]
    }
}
```

### ワークスペースを開く

```bash
code /path/to/my-workspace.code-workspace
```

---

## Eclipseクラスパスの設定

### ルートプロジェクトの .project

#### common-project/.project

```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>common-project</name>
    <comment></comment>
    <projects>
        <!-- このプロジェクトが参照する他のプロジェクト（なし） -->
    </projects>
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

#### webapp-project/.project

```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>webapp-project</name>
    <comment></comment>
    <projects>
        <!-- 依存するプロジェクト -->
        <project>common-project</project>
    </projects>
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

### モジュールごとの .classpath

#### common-project/common-util/.classpath

```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <!-- ソースパス -->
    <classpathentry kind="src" path="src/main/java"/>
    <classpathentry kind="src" path="src/main/resources"/>

    <!-- JDK -->
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/
        org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-11"/>

    <!-- 外部ライブラリ -->
    <classpathentry kind="lib" path="lib/commons-lang3-3.12.0.jar"/>

    <!-- 出力パス -->
    <classpathentry kind="output" path="bin"/>
</classpath>
```

#### common-project/common-util/.project

```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>common-util</name>  <!-- モジュール名 -->
    <comment></comment>
    <projects></projects>
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

#### webapp-project/webapp-business/.classpath

```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" path="src/main/java"/>

    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/
        org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-11"/>

    <!-- 同一ワークスペース内の別プロジェクトのモジュールを参照 -->
    <classpathentry combineaccessrules="false" kind="src" path="/common-util"/>
    <classpathentry combineaccessrules="false" kind="src" path="/common-domain"/>

    <!-- Springなどの依存ライブラリ -->
    <classpathentry kind="lib" path="lib/spring-context-5.3.27.jar"/>

    <classpathentry kind="output" path="bin"/>
</classpath>
```

**重要**: `path="/common-util"` は、`common-util/.project` で定義された `<name>` と一致させる。

#### webapp-project/webapp-web/.classpath

```xml
<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" path="src/main/java"/>
    <classpathentry kind="src" path="src/main/resources"/>

    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/
        org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-11"/>

    <!-- 同一プロジェクト内の別モジュールを参照 -->
    <classpathentry combineaccessrules="false" kind="src" path="/webapp-business"/>

    <!-- 他プロジェクトのモジュールも参照可能 -->
    <classpathentry combineaccessrules="false" kind="src" path="/common-util"/>

    <!-- WebLogic provided -->
    <classpathentry kind="lib" path="lib/javax.servlet-api-4.0.1.jar"/>

    <classpathentry kind="output" path="bin"/>
</classpath>
```

---

## Gradleビルド設定

### common-project/settings.gradle

```groovy
rootProject.name = 'common-project'

include 'common-util'
include 'common-domain'
```

### common-project/build.gradle

```groovy
// ルート設定
subprojects {
    apply plugin: 'java'
    apply plugin: 'eclipse'

    group = 'com.example.common'
    version = '1.0.0-SNAPSHOT'

    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11

    repositories {
        mavenCentral()
    }

    // デバッグ情報を含める
    tasks.withType(JavaCompile) {
        options.encoding = 'UTF-8'
        options.debug = true
        options.debugOptions.debugLevel = 'source,lines,vars'
    }

    // Eclipse設定
    eclipse {
        classpath {
            downloadSources = true
            downloadJavadoc = true
        }
    }
}
```

### common-project/common-util/build.gradle

```groovy
dependencies {
    implementation 'org.apache.commons:commons-lang3:3.12.0'
    implementation 'org.slf4j:slf4j-api:1.7.36'
}
```

### webapp-project/settings.gradle

```groovy
rootProject.name = 'webapp-project'

include 'webapp-business'
include 'webapp-web'

// 外部プロジェクトのモジュールを参照
include ':common-util'
include ':common-domain'

// プロジェクトの場所を指定
project(':common-util').projectDir = new File('../common-project/common-util')
project(':common-domain').projectDir = new File('../common-project/common-domain')
```

### webapp-project/build.gradle

```groovy
subprojects {
    apply plugin: 'java'
    apply plugin: 'eclipse'

    group = 'com.example.webapp'
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

### webapp-project/webapp-business/build.gradle

```groovy
dependencies {
    // 外部プロジェクトのモジュールを参照
    implementation project(':common-util')
    implementation project(':common-domain')

    // Spring
    implementation 'org.springframework:spring-context:5.3.27'
    implementation 'org.springframework:spring-jdbc:5.3.27'
}
```

### webapp-project/webapp-web/build.gradle

```groovy
plugins {
    id 'war'
}

dependencies {
    // 同一プロジェクト内のモジュール
    implementation project(':webapp-business')

    // 外部プロジェクトのモジュール（推移的に含まれる）
    // implementation project(':common-util')  // webapp-businessが依存しているので不要

    // Spring MVC
    implementation 'org.springframework:spring-webmvc:5.3.27'

    // WebLogic provided
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveBaseName = 'myapp'
    archiveVersion = ''
}

// WebLogicデプロイタスク
task deployToWebLogic(type: Copy, dependsOn: war) {
    from war.archiveFile
    into '/opt/oracle/domains/my_domain/applications'

    doLast {
        println "Deployed ${war.archiveFileName.get()} to WebLogic"
    }
}
```

---

## WebLogicデバッグ設定

### setDomainEnv.sh の編集

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

## 実践的な開発フロー

### 初回セットアップ

#### 1. ワークスペースファイルの作成

```bash
vi /path/to/my-workspace.code-workspace
# 上記のJSON設定をコピー
```

#### 2. VSCodeで開く

```bash
code /path/to/my-workspace.code-workspace
```

#### 3. Java拡張機能のインストール

VSCodeが推奨拡張機能のインストールを提案:
```
Extension Pack for Java
```

**Install** をクリック。

#### 4. プロジェクトのインポート待機

VSCodeが自動的に複数のプロジェクトをインポート:
```
Importing Java projects...
- common-project
  - common-util
  - common-domain
- webapp-project
  - webapp-business
  - webapp-web
```

完了まで待つ（3〜10分）。

#### 5. Gradleで Eclipse設定を生成（初回のみ）

```bash
# common-projectのEclipse設定生成
cd /path/to/workspace/common-project
./gradlew eclipse

# webapp-projectのEclipse設定生成
cd /path/to/workspace/webapp-project
./gradlew eclipse
```

これにより、各モジュールに `.classpath` が自動生成/更新される。

#### 6. VSCodeリロード

```
Ctrl+Shift+P → "Reload Window"
```

#### 7. プロジェクト構造の確認

VSCodeのJava Projectsビューで確認:
```
Java Projects
├── common-project
│   ├── common-util
│   │   └── src/main/java
│   │       └── com.example.common.util
│   └── common-domain
│       └── src/main/java
│           └── com.example.common.domain
└── webapp-project
    ├── webapp-business
    │   └── src/main/java
    │       └── com.example.webapp.service
    └── webapp-web
        └── src/main/java
            └── com.example.webapp.controller
```

### 日常的な開発フロー

#### パターン1: コード変更 → ビルド → デプロイ → デバッグ

```bash
# 1. VSCodeでコード編集
#    - UserService.java を編集
#    - StringUtils.java を編集（別プロジェクト）

# 2. ビルド（VSCodeターミナル）
cd /path/to/workspace/webapp-project
./gradlew clean build

# 3. デプロイ
./gradlew deployToWebLogic

# 4. デバッグ開始
# F5 → "Debug WebLogic (WebApp)" を選択

# 5. ブレークポイント設定
#    - UserService.java にブレークポイント
#    - StringUtils.java にもブレークポイント（別プロジェクト）

# 6. アプリケーションテスト
curl http://localhost:7003/myapp/users
```

#### パターン2: 依存関係を追加

```bash
# 1. build.gradle を編集
#    webapp-business/build.gradle:
#    dependencies {
#        implementation 'com.google.guava:guava:31.1-jre'
#    }

# 2. Gradle依存関係を更新
./gradlew dependencies --refresh-dependencies

# 3. Eclipse設定を再生成
./gradlew cleanEclipse eclipse

# 4. VSCodeリロード
# Ctrl+Shift+P → "Reload Window"

# 5. 新しいライブラリを使用可能
# import com.google.common.collect.Lists;
```

#### パターン3: 複数プロジェクトにまたがるデバッグ

```java
// webapp-web/UserController.java
package com.example.webapp.controller;

import com.example.webapp.service.UserService;  // ← webapp-business

@Controller
public class UserController {
    @Autowired
    private UserService userService;

    @RequestMapping("/users")
    public String listUsers(Model model) {
        List<User> users = userService.findAll();  // ← ブレークポイント1
        model.addAttribute("users", users);
        return "users";
    }
}
```

```java
// webapp-business/UserService.java
package com.example.webapp.service;

import com.example.common.util.StringUtils;  // ← common-util（別プロジェクト）
import com.example.common.domain.User;        // ← common-domain（別プロジェクト）

@Service
public class UserService {
    public List<User> findAll() {
        List<User> users = repository.findAll();
        for (User user : users) {
            String name = StringUtils.capitalize(user.getName());  // ← ブレークポイント2
            user.setName(name);
        }
        return users;
    }
}
```

```java
// common-util/StringUtils.java（別プロジェクト）
package com.example.common.util;

public class StringUtils {
    public static String capitalize(String str) {
        if (str == null || str.isEmpty()) {
            return str;  // ← ブレークポイント3
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
}
```

**デバッグの流れ**:
1. ブレークポイント1で停止（UserController）
2. `F11` (Step Into) でUserServiceに移動
3. ブレークポイント2で停止（UserService）
4. `F11` で別プロジェクトのStringUtilsに移動 ✅
5. ブレークポイント3で停止（StringUtils）
6. 変数の値をすべて確認可能 ✅

---

## トラブルシューティング

### 問題1: VSCodeがサブディレクトリのモジュールを認識しない

#### 症状
```
Java Projects
└── common-project  ← ルートだけ認識され、モジュールが表示されない
```

#### 解決方法

**方法1: 各モジュールに .project を作成**

VSCodeは `.project` ファイルを基準にJavaプロジェクトを認識します。

```bash
# 各モジュールディレクトリに .project を作成
cd /path/to/workspace/common-project/common-util
```

`.project`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>common-util</name>
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

**方法2: Gradleで自動生成**

```bash
cd /path/to/workspace/common-project
./gradlew eclipse
```

Gradleが各モジュールに `.project` と `.classpath` を自動生成。

**方法3: VSCodeの設定を確認**

.code-workspace:
```json
{
    "settings": {
        "java.import.eclipse.enabled": true  // ← これが必須
    }
}
```

VSCodeリロード:
```
Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"
→ "Reload and Delete"
```

### 問題2: プロジェクト間の参照が認識されない

#### 症状
```java
import com.example.common.util.StringUtils;  // ← 赤線（エラー）
```

webapp-business から common-util を参照できない。

#### 解決方法

**方法1: .classpath でプロジェクト参照を確認**

webapp-business/.classpath:
```xml
<!-- プロジェクト名が正しいか確認 -->
<classpathentry combineaccessrules="false" kind="src" path="/common-util"/>
```

common-util/.project:
```xml
<!-- この名前と一致させる -->
<name>common-util</name>
```

**方法2: 両プロジェクトがワークスペースに含まれているか確認**

.code-workspace:
```json
{
    "folders": [
        {"path": "/path/to/common-project"},   // ✅ 両方含める
        {"path": "/path/to/webapp-project"}
    ]
}
```

**方法3: VSCodeリロード**

```
Ctrl+Shift+P → "Reload Window"
```

### 問題3: Gradleビルド時に依存関係が見つからない

#### 症状
```
Could not find project :common-util
```

#### 解決方法

**方法1: settings.gradle で正しくパスを指定**

webapp-project/settings.gradle:
```groovy
include ':common-util'

// プロジェクトの場所を絶対パスで指定
project(':common-util').projectDir = new File('/path/to/workspace/common-project/common-util')

// または相対パス
project(':common-util').projectDir = new File('../common-project/common-util')
```

**方法2: 相対パスの確認**

```bash
cd /path/to/workspace/webapp-project
ls -la ../common-project/common-util  # ← パスが正しいか確認
```

**方法3: Gradleキャッシュクリア**

```bash
./gradlew clean build --refresh-dependencies
```

### 問題4: デバッグ時に別プロジェクトのソースが見つからない

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
        "${workspaceFolder:WebApp Project}/webapp-web/src/main/java",
        "${workspaceFolder:WebApp Project}/webapp-business/src/main/java",

        // 依存する別プロジェクトを追加
        "${workspaceFolder:Common Project}/common-util/src/main/java",
        "${workspaceFolder:Common Project}/common-domain/src/main/java"
    ]
}
```

**方法2: workspaceFolder名を確認**

.code-workspace:
```json
{
    "folders": [
        {
            "name": "Common Project",  // ← この名前を使用
            "path": "/path/to/common-project"
        },
        {
            "name": "WebApp Project",  // ← この名前を使用
            "path": "/path/to/webapp-project"
        }
    ]
}
```

launch.json:
```json
{
    "sourcePaths": [
        "${workspaceFolder:Common Project}/common-util/src/main/java"
        //                ^^^^^^^^^^^^^^^ フォルダ名と一致させる
    ]
}
```

### 問題5: モジュール数が多くてVSCodeが遅い

#### 症状
VSCodeの動作が重い、インポートに時間がかかる。

#### 解決方法

**方法1: Java Language Serverのメモリを増やす**

.code-workspace:
```json
{
    "settings": {
        "java.jdt.ls.vmargs": "-Xmx4G -XX:+UseG1GC"
    }
}
```

**方法2: 不要なファイルを除外**

.code-workspace:
```json
{
    "settings": {
        "files.exclude": {
            "**/.gradle": true,
            "**/build": true,
            "**/.settings": true,
            "**/bin": true
        },
        "search.exclude": {
            "**/build": true,
            "**/.gradle": true
        }
    }
}
```

**方法3: 必要なモジュールだけをワークスペースに含める**

開発中のモジュールだけを開く:
```json
{
    "folders": [
        {"path": "/path/to/webapp-project/webapp-web"},
        {"path": "/path/to/webapp-project/webapp-business"},
        {"path": "/path/to/common-project/common-util"}
    ]
}
```

---

## ベストプラクティス

### 1. プロジェクト構成の設計

#### 推奨: 依存関係の方向性を明確に

```
common-project  ← 基盤（他に依存しない）
    ↑
    │ 依存
    │
webapp-project  ← アプリケーション（commonに依存）
```

**避けるべき**: 循環依存
```
common-project ⇄ webapp-project  ← NG
```

### 2. Gradle設定の一元管理

#### ルート gradle.properties で共通設定

```properties
# /path/to/workspace/gradle.properties
org.gradle.jvmargs=-Xmx2g
org.gradle.parallel=true
org.gradle.daemon=true
org.gradle.caching=true

# 共通バージョン
springVersion=5.3.27
hibernateVersion=5.6.15.Final
```

各プロジェクトで参照:
```groovy
// build.gradle
dependencies {
    implementation "org.springframework:spring-context:${springVersion}"
}
```

### 3. VSCode設定のチーム共有

#### .code-workspace.example を提供

```bash
cp my-workspace.code-workspace my-workspace.code-workspace.example
```

.gitignore:
```gitignore
*.code-workspace
!*.code-workspace.example
```

チームメンバーは:
```bash
cp my-workspace.code-workspace.example my-workspace.code-workspace
# パスを自分の環境に合わせて編集
```

---

## まとめ

この構成により、以下が実現できます:

### ✅ 実現できること

1. **複雑なマルチプロジェクト・マルチモジュール構成**
   - ワークスペースに複数プロジェクト配置
   - 各プロジェクトのサブディレクトリに独立したモジュール

2. **プロジェクト間・モジュール間の相互依存**
   - Eclipse `.classpath` で依存関係を定義
   - コード補完、参照ジャンプが動作

3. **Gradleビルド**
   - 外部のGradle設定を活用
   - WARファイルの自動生成

4. **WebLogicリモートデバッグ**
   - VSCodeからWebLogicにアタッチ
   - 複数プロジェクトにまたがるデバッグ
   - 依存モジュールへのステップイン

### 🔧 セットアップ手順まとめ

```bash
# 1. ワークスペースファイル作成
vi my-workspace.code-workspace

# 2. VSCodeで開く
code my-workspace.code-workspace

# 3. Java拡張機能インストール
# （VSCode UIから）

# 4. Gradleで Eclipse設定生成
./gradlew eclipse

# 5. VSCodeリロード
# Ctrl+Shift+P → "Reload Window"

# 6. ビルド
./gradlew clean build

# 7. デプロイ
./gradlew deployToWebLogic

# 8. デバッグ開始
# F5
```

この環境で、複雑な企業向けアプリケーションの開発・デバッグが効率的に行えます。
