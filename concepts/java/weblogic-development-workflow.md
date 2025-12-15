# WebLogic開発ワークフロー学習ノート

> 対象: WebLogic 14.1.1, Java 11, Gradle 7.2
> フレームワーク: Struts 2, Spring
> 開発環境: VSCode + リモートデバッグ

## 学習目標

- Exploded Deployの概念と開発時のメリットを理解する
- WebLogicでのリモートデバッグ設定方法を習得する
- 複数プロジェクト（WAR/lib/conf）の連携ビルドを構築する
- 開発効率を最大化するワークフローを確立する

---

## 1. Exploded Deploy（展開デプロイ）の概念

### 1.1 Exploded Deployとは

**Exploded Deploy**は、アーカイブファイル（EAR/WAR/JAR）を**圧縮せずにディレクトリ構造のまま**デプロイする方式です。

#### 通常のデプロイ（Archived Deploy）

```
アプリケーション
    ↓ ビルド
my-app.ear（ZIPアーカイブ）
    ↓ デプロイ
WebLogicサーバー
    ↓ 展開
/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_user/my-app/
```

**デメリット**:
- コード変更のたびに再ビルド・再デプロイが必要
- デプロイに時間がかかる（1〜2分）
- 開発サイクルが遅い

#### Exploded Deploy

```
アプリケーション
    ↓ ビルド（展開形式）
my-app/（ディレクトリ）
├── META-INF/
├── my-webapp.war/
└── lib/
    ↓ 直接デプロイ
WebLogicサーバー（ディレクトリを参照）
```

**メリット**:
- **ホットデプロイ**: Javaファイル以外の変更が即座に反映
- **高速な開発サイクル**: ビルド時間の削減
- **デバッグしやすい**: ファイルの直接編集・確認が可能

### 1.2 ホットデプロイ可能な変更

| 変更内容 | Exploded | Archived | 再起動 |
|---------|----------|----------|--------|
| JSP/HTML | ✓ 即座 | ✗ 再デプロイ | 不要 |
| JavaScript/CSS | ✓ 即座 | ✗ 再デプロイ | 不要 |
| プロパティファイル | ✓ 即座 | ✗ 再デプロイ | 不要（一部要） |
| Struts設定（struts.xml） | ✓ 即座※ | ✗ 再デプロイ | 不要※ |
| Spring設定（XML） | △ 要設定 | ✗ 再デプロイ | 不要（devtools使用時） |
| Javaソースコード | ✗ 再コンパイル | ✗ 再デプロイ | 要 |
| ライブラリJAR | ✗ 再デプロイ | ✗ 再デプロイ | 要 |

※ Struts 2の`devMode`有効時

### 1.3 Exploded Deploy対応のディレクトリ構造

```
exploded-ear/
├── META-INF/
│   ├── MANIFEST.MF
│   └── application.xml
├── webapp.war/                    # WARもディレクトリ形式
│   ├── META-INF/
│   ├── WEB-INF/
│   │   ├── web.xml
│   │   ├── classes/               # コンパイル済みクラス
│   │   │   └── com/example/
│   │   ├── lib/                   # WAR専用ライブラリ
│   │   └── struts.xml
│   ├── jsp/
│   ├── css/
│   └── js/
├── admin.war/                     # 2つ目のWAR
├── lib/                           # EAR共有ライブラリ
│   ├── common-lib.jar
│   └── struts2-core.jar
└── conf/                          # 設定ファイル（任意）
    └── application.properties
```

---

## 2. 複数プロジェクト構成とGradle設定

### 2.1 プロジェクト構成

```
my-enterprise-project/
├── settings.gradle
├── build.gradle                   # ルート設定
├── common-lib/                    # 共通ライブラリ（JAR）
│   ├── build.gradle
│   └── src/main/java/
├── webapp/                        # メインWebアプリ（WAR）
│   ├── build.gradle
│   └── src/
│       ├── main/
│       │   ├── java/
│       │   ├── resources/
│       │   └── webapp/
│       │       ├── WEB-INF/
│       │       └── jsp/
│       └── test/
├── admin/                         # 管理画面（WAR）
│   ├── build.gradle
│   └── src/
├── shared-config/                 # 共有設定（リソース）
│   ├── build.gradle
│   └── src/main/resources/
└── ear/                           # EARパッケージング
    ├── build.gradle
    └── src/main/application/
        └── META-INF/
            └── weblogic-application.xml
```

### 2.2 settings.gradle

```gradle
rootProject.name = 'my-enterprise-app'

include 'common-lib'
include 'webapp'
include 'admin'
include 'shared-config'
include 'ear'
```

### 2.3 ルート build.gradle

```gradle
plugins {
    id 'java' apply false
    id 'war' apply false
    id 'ear' apply false
}

ext {
    // バージョン管理
    javaVersion = JavaVersion.VERSION_11
    weblogicVersion = '14.1.1.0.0'
    strutsVersion = '2.5.30'
    springVersion = '5.3.27'

    // 開発モード設定
    isDevelopment = project.hasProperty('dev') || System.getenv('ENV') == 'dev'

    // WebLogicホームディレクトリ
    weblogicHome = System.getenv('WEBLOGIC_HOME') ?: '/opt/oracle/middleware'
    domainHome = "${weblogicHome}/user_projects/domains/base_domain"
}

subprojects {
    apply plugin: 'java'

    group = 'com.example'
    version = '1.0.0-SNAPSHOT'

    sourceCompatibility = javaVersion
    targetCompatibility = javaVersion

    repositories {
        mavenCentral()
        // WebLogic JARリポジトリ（ローカル）
        flatDir {
            dirs "${weblogicHome}/wlserver/server/lib"
        }
    }

    // 共通依存関係
    dependencies {
        compileOnly 'javax.servlet:javax.servlet-api:4.0.1'

        // ロギング
        implementation 'org.slf4j:slf4j-api:1.7.36'
        implementation 'ch.qos.logback:logback-classic:1.2.11'

        // テスト
        testImplementation 'junit:junit:4.13.2'
        testImplementation 'org.mockito:mockito-core:4.6.1'
    }

    // Java 11対応のコンパイルオプション
    tasks.withType(JavaCompile) {
        options.encoding = 'UTF-8'
        options.compilerArgs << '-parameters'
    }
}
```

### 2.4 common-lib/build.gradle

```gradle
plugins {
    id 'java-library'
}

dependencies {
    // Struts 2
    api "org.apache.struts:struts2-core:${strutsVersion}"
    api "org.apache.struts:struts2-spring-plugin:${strutsVersion}"

    // Spring Framework
    api "org.springframework:spring-context:${springVersion}"
    api "org.springframework:spring-web:${springVersion}"
    api "org.springframework:spring-jdbc:${springVersion}"

    // ユーティリティ
    api 'org.apache.commons:commons-lang3:3.12.0'
    api 'com.google.guava:guava:31.1-jre'
}

// JARの出力設定
jar {
    manifest {
        attributes(
            'Implementation-Title': 'Common Library',
            'Implementation-Version': version
        )
    }
}
```

### 2.5 webapp/build.gradle

```gradle
plugins {
    id 'war'
}

dependencies {
    // 共通ライブラリ
    implementation project(':common-lib')
    implementation project(':shared-config')

    // Struts 2追加プラグイン
    implementation "org.apache.struts:struts2-convention-plugin:${strutsVersion}"
    implementation "org.apache.struts:struts2-json-plugin:${strutsVersion}"

    // Spring追加機能
    implementation "org.springframework:spring-webmvc:${springVersion}"

    // データベース
    implementation 'org.mybatis:mybatis:3.5.11'
    implementation 'org.mybatis:mybatis-spring:2.0.7'

    // WebLogic固有（コンパイルのみ）
    compileOnly name: 'weblogic'
    compileOnly name: 'wlthint3client'
}

war {
    archiveFileName = 'webapp.war'

    // 開発モード: Exploded形式を優先
    if (rootProject.ext.isDevelopment) {
        // 圧縮を無効化（オプション）
        entryCompression = ZipEntryCompression.STORED
    }

    // Strutsフィルター設定
    webInf {
        from('src/main/resources') {
            include 'struts.xml', 'struts.properties'
        }
    }
}
```

### 2.6 shared-config/build.gradle

```gradle
plugins {
    id 'java-library'
}

// リソースのみのプロジェクト
sourceSets {
    main {
        java.srcDirs = []  // Javaソースなし
        resources.srcDirs = ['src/main/resources']
    }
}

jar {
    archiveFileName = 'shared-config.jar'
}
```

### 2.7 ear/build.gradle（重要）

```gradle
plugins {
    id 'ear'
}

dependencies {
    // WARモジュール
    deploy project(path: ':webapp', configuration: 'archives')
    deploy project(path: ':admin', configuration: 'archives')

    // EAR共有ライブラリ
    earlib project(':common-lib')
    earlib project(':shared-config')

    // Struts/Spring（EAR全体で共有）
    earlib "org.apache.struts:struts2-core:${strutsVersion}"
    earlib "org.springframework:spring-context:${springVersion}"
}

ear {
    archiveFileName = 'my-app.ear'

    deploymentDescriptor {
        applicationName = 'MyEnterpriseApp'

        // コンテキストパス設定
        webModule('webapp.war', '/app')
        webModule('admin.war', '/admin')

        libraryDirectory = 'lib'

        // 初期化順序
        initializeInOrder = true
    }

    // WebLogic固有設定
    withType(org.gradle.plugins.ear.descriptor.DeploymentDescriptor) {
        fileName = 'application.xml'
    }

    // weblogic-application.xmlをコピー
    metaInf {
        from 'src/main/application/META-INF'
    }
}

// ==========================================
// Explodedデプロイ用タスク
// ==========================================

// Exploded EARディレクトリの作成
def explodedDir = file("${buildDir}/exploded")

tasks.register('explodedEar') {
    group = 'deployment'
    description = 'Create exploded EAR directory for development'

    dependsOn ':webapp:war', ':admin:war', ':common-lib:jar', ':shared-config:jar'

    doLast {
        // 既存ディレクトリをクリーンアップ
        delete explodedDir
        mkdir explodedDir

        // META-INFをコピー
        copy {
            from ear.metaInf
            into "${explodedDir}/META-INF"
        }

        // application.xmlを生成してコピー
        copy {
            from "${buildDir}/tmp/ear"
            include 'application.xml'
            into "${explodedDir}/META-INF"
        }

        // WARファイルを展開形式でコピー
        copy {
            from zipTree(project(':webapp').war.archiveFile)
            into "${explodedDir}/webapp.war"
        }

        copy {
            from zipTree(project(':admin').war.archiveFile)
            into "${explodedDir}/admin.war"
        }

        // 共有ライブラリをコピー
        mkdir "${explodedDir}/lib"
        copy {
            from project(':common-lib').jar.archiveFile
            from project(':shared-config').jar.archiveFile
            from configurations.earlib
            into "${explodedDir}/lib"
        }

        println "✓ Exploded EAR created at: ${explodedDir}"
    }
}

// WebLogicへの自動デプロイタスク
tasks.register('deployToWebLogic') {
    group = 'deployment'
    description = 'Deploy exploded EAR to WebLogic domain'

    dependsOn 'explodedEar'

    doLast {
        def deployDir = file("${rootProject.ext.domainHome}/autodeploy")

        if (!deployDir.exists()) {
            throw new GradleException("WebLogic autodeploy directory not found: ${deployDir}")
        }

        def targetDir = file("${deployDir}/my-app")

        // 既存デプロイメントを削除
        if (targetDir.exists()) {
            delete targetDir
        }

        // シンボリックリンクを作成（Linux/Mac）
        if (System.getProperty('os.name').toLowerCase().contains('windows')) {
            // Windowsの場合はコピー
            copy {
                from explodedDir
                into targetDir
            }
            println "✓ Copied to: ${targetDir}"
        } else {
            // Unix系はシンボリックリンク
            exec {
                commandLine 'ln', '-s', explodedDir.absolutePath, targetDir.absolutePath
            }
            println "✓ Symlinked to: ${targetDir}"
        }

        println "✓ Deployed to WebLogic: ${targetDir}"
    }
}

// 開発用: ウォッチモード（変更を自動検知してリビルド）
tasks.register('watchAndDeploy') {
    group = 'deployment'
    description = 'Watch for changes and auto-rebuild'

    doLast {
        println "Watching for changes... (Press Ctrl+C to stop)"

        // Note: 実際のウォッチ機能は外部ツール（Gradle --continuous）を使用
        println "Run: ./gradlew explodedEar --continuous"
    }
}
```

---

## 3. WebLogicリモートデバッグ設定

### 3.1 WebLogicサーバーのデバッグモード起動

#### 方法1: setDomainEnv.sh を編集（推奨）

```bash
# 場所: $DOMAIN_HOME/bin/setDomainEnv.sh

# 既存のJAVA_OPTIONSに追加（ファイル末尾付近）
export debugFlag="true"
export DEBUG_PORT="8453"

if [ "${debugFlag}" = "true" ]; then
    JAVA_OPTIONS="${JAVA_OPTIONS} -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:${DEBUG_PORT}"
    export JAVA_OPTIONS
fi
```

**パラメータ解説**:
- `transport=dt_socket`: ソケット通信を使用
- `server=y`: サーバーモード（WebLogicがデバッガーの接続を待つ）
- `suspend=n`: 起動時に一時停止**しない**（`suspend=y`で起動時から待機）
- `address=*:8453`: すべてのインターフェースでポート8453をリッスン

#### 方法2: 起動スクリプトで直接指定

```bash
# $DOMAIN_HOME/bin/startWebLogic.sh の起動前に環境変数を設定

export JAVA_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8453"

./startWebLogic.sh
```

#### 方法3: WebLogic管理コンソールから設定

1. 管理コンソールにログイン: `http://localhost:7001/console`
2. 「環境」→「サーバー」→ 対象サーバー（AdminServerなど）をクリック
3. 「サーバーの起動」タブ
4. 「引数」フィールドに追加:
   ```
   -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8453
   ```
5. 保存してサーバーを再起動

### 3.2 WebLogicサーバーの起動確認

```bash
# WebLogicを起動
cd $DOMAIN_HOME/bin
./startWebLogic.sh

# デバッグポートがリッスンしているか確認
netstat -an | grep 8453
# または
lsof -i :8453
```

起動ログに以下のようなメッセージが表示されれば成功:
```
Listening for transport dt_socket at address: 8453
```

### 3.3 VSCodeのリモートデバッグ設定

#### .vscode/launch.json

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
            "projectName": "my-enterprise-app",
            "sourcePaths": [
                "${workspaceFolder}/webapp/src/main/java",
                "${workspaceFolder}/admin/src/main/java",
                "${workspaceFolder}/common-lib/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug WebLogic (Remote - Suspend)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "timeout": 30000,
            "sourcePaths": [
                "${workspaceFolder}/webapp/src/main/java",
                "${workspaceFolder}/admin/src/main/java",
                "${workspaceFolder}/common-lib/src/main/java"
            ]
        },
        {
            "type": "java",
            "name": "Debug Specific Module (webapp)",
            "request": "attach",
            "hostName": "localhost",
            "port": 8453,
            "projectName": "webapp",
            "sourcePaths": [
                "${workspaceFolder}/webapp/src/main/java"
            ]
        }
    ]
}
```

### 3.4 デバッグセッションの開始

#### VSCodeでの操作手順

1. **ブレークポイントを設定**
   - デバッグしたいJavaファイルを開く
   - 行番号の左側をクリックして赤いドットを表示

2. **デバッグ構成を選択**
   - VSCode左サイドバーの「実行とデバッグ」アイコンをクリック
   - ドロップダウンから「Debug WebLogic (Remote)」を選択

3. **デバッグを開始**
   - F5キーを押す、または緑の再生ボタンをクリック
   - 下部にオレンジのステータスバーが表示されれば接続成功

4. **アプリケーションを操作**
   - ブラウザで `http://localhost:7001/app/` にアクセス
   - ブレークポイントで処理が停止する

5. **デバッグコントロール**
   - **F10**: ステップオーバー（次の行へ）
   - **F11**: ステップイン（メソッド内部へ）
   - **Shift+F11**: ステップアウト（メソッドから戻る）
   - **F5**: 続行（次のブレークポイントまで実行）

### 3.5 リモートデバッグのトラブルシューティング

#### 問題1: 接続できない（Connection refused）

**症状**:
```
Failed to connect to remote VM. Connection refused.
```

**解決策**:
```bash
# 1. WebLogicが起動しているか確認
ps aux | grep weblogic

# 2. デバッグポートがリッスンしているか確認
netstat -an | grep 8453

# 3. ファイアウォールでポートが開いているか確認（リモートサーバーの場合）
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=8453/tcp --permanent
sudo firewall-cmd --reload

# 4. WebLogicのログを確認
tail -f $DOMAIN_HOME/servers/AdminServer/logs/AdminServer.log
```

#### 問題2: ブレークポイントで停止しない

**原因**: ソースコードとデプロイされたクラスが一致していない

**解決策**:
```bash
# 1. 最新のコードを再ビルド
./gradlew clean :webapp:build

# 2. Explodedデプロイを更新
./gradlew explodedEar

# 3. WebLogicで再デプロイ（管理コンソール）
# または自動デプロイディレクトリを更新

# 4. VSCodeでデバッグセッションを再起動
```

#### 問題3: 変数の値が表示されない

**原因**: コンパイル時に変数情報が削除されている

**解決策**: `build.gradle`でデバッグ情報を有効化
```gradle
tasks.withType(JavaCompile) {
    options.compilerArgs << '-g'  // デバッグ情報を含める
    options.debug = true
    options.debugOptions.debugLevel = 'source,lines,vars'
}
```

---

## 4. Strutsの開発モード設定

### 4.1 struts.properties

```properties
# src/main/resources/struts.properties

# 開発モード（本番環境では必ずfalseにすること）
struts.devMode = true

# 設定ファイルの自動リロード
struts.configuration.xml.reload = true

# 静的コンテンツのリロード
struts.i18n.reload = true

# 詳細なエラーメッセージ表示
struts.ui.theme = xhtml
struts.ui.templateDir = template

# アクションマッピングのキャッシュ無効化
struts.convention.classes.reload = true
```

### 4.2 struts.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE struts PUBLIC
    "-//Apache Software Foundation//DTD Struts Configuration 2.5//EN"
    "http://struts.apache.org/dtds/struts-2.5.dtd">

<struts>
    <!-- 開発モードの有効化 -->
    <constant name="struts.devMode" value="true" />

    <!-- 設定のリロード間隔（秒） -->
    <constant name="struts.configuration.xml.reload" value="true" />

    <!-- 国際化リソースのリロード -->
    <constant name="struts.i18n.reload" value="true" />

    <!-- 詳細なエラー表示 -->
    <constant name="struts.ui.theme" value="simple" />

    <!-- Convention Pluginの設定 -->
    <constant name="struts.convention.action.packages" value="com.example.action" />

    <package name="default" extends="struts-default">
        <!-- アクション定義 -->
    </package>
</struts>
```

---

## 5. Springの開発モード設定

### 5.1 application.properties（Spring Boot使用時）

```properties
# src/main/resources/application.properties

# 開発モード
spring.profiles.active=dev

# 自動リロード（Spring Boot DevTools）
spring.devtools.restart.enabled=true
spring.devtools.livereload.enabled=true

# テンプレートキャッシュ無効化
spring.thymeleaf.cache=false
spring.freemarker.cache=false

# ログレベル
logging.level.root=INFO
logging.level.com.example=DEBUG
logging.level.org.springframework.web=DEBUG
```

### 5.2 applicationContext.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="
           http://www.springframework.org/schema/beans
           http://www.springframework.org/schema/beans/spring-beans.xsd
           http://www.springframework.org/schema/context
           http://www.springframework.org/schema/context/spring-context.xsd">

    <!-- コンポーネントスキャン -->
    <context:component-scan base-package="com.example" />

    <!-- プロパティファイルのリロード設定 -->
    <bean id="propertyConfigurer"
          class="org.springframework.context.support.ReloadableResourceBundleMessageSource">
        <property name="basename" value="classpath:messages" />
        <property name="cacheSeconds" value="1" />  <!-- 開発時は短い間隔 -->
    </bean>

</beans>
```

---

## 6. 開発ワークフロー

### 6.1 初回セットアップ

```bash
# 1. プロジェクトをクローン
git clone https://github.com/yourorg/my-enterprise-app.git
cd my-enterprise-app

# 2. Gradle Wrapperの確認
./gradlew --version
# Gradle 7.2
# Java 11

# 3. 依存関係の解決とビルド
./gradlew clean build

# 4. Exploded EARの作成
./gradlew :ear:explodedEar

# 5. WebLogicへのデプロイ
./gradlew :ear:deployToWebLogic

# 6. WebLogicをデバッグモードで起動
cd $DOMAIN_HOME/bin
./startWebLogic.sh

# 7. VSCodeでデバッグセッションを開始
# F5キーを押す
```

### 6.2 日常的な開発サイクル

#### パターン1: JSP/HTML/CSS/JavaScriptの変更

```bash
# 変更を保存するだけで自動反映（Explodedデプロイの場合）
# ブラウザをリロード（Ctrl+F5）
```

#### パターン2: Javaコードの変更

```bash
# 1. Javaファイルを編集して保存

# 2. 影響を受けるモジュールだけを再ビルド
./gradlew :webapp:compileJava

# 3. クラスファイルをExploded WARにコピー
./gradlew :webapp:classes
cp -r webapp/build/classes/java/main/* \
   ear/build/exploded/webapp.war/WEB-INF/classes/

# 4. WebLogicで自動再デプロイを待つ（数秒）
# またはホットスワップ（JRebelなど）を使用
```

#### パターン3: 設定ファイルの変更（struts.xml, applicationContext.xml）

```bash
# 1. 設定ファイルを編集

# 2. リソースをコピー
./gradlew :webapp:processResources
cp webapp/src/main/resources/struts.xml \
   ear/build/exploded/webapp.war/WEB-INF/

# 3. Struts開発モードが有効なら自動リロード
# Springの場合はコンテキスト再読み込みが必要な場合あり
```

#### パターン4: ライブラリの追加・更新

```bash
# 1. build.gradleで依存関係を追加

# 2. フルリビルド
./gradlew clean :ear:explodedEar

# 3. WebLogicを再起動
cd $DOMAIN_HOME/bin
./stopWebLogic.sh
./startWebLogic.sh
```

### 6.3 効率化のためのGradleタスク

```bash
# 継続ビルドモード（変更を自動検知）
./gradlew :webapp:classes --continuous

# 特定モジュールのみテスト
./gradlew :webapp:test --tests "com.example.UserActionTest"

# 高速ビルド（テストスキップ）
./gradlew :ear:explodedEar -x test

# 並列ビルド
./gradlew :ear:explodedEar --parallel --max-workers=4

# ビルドキャッシュ有効化
./gradlew :ear:explodedEar --build-cache
```

---

## 7. VSCode統合開発環境設定

### 7.1 必須拡張機能

```json
// .vscode/extensions.json
{
    "recommendations": [
        "vscjava.vscode-java-pack",           // Java開発パック
        "vscjava.vscode-gradle",              // Gradle統合
        "vscjava.vscode-spring-boot-dashboard", // Spring管理
        "redhat.vscode-xml",                  // XML編集
        "redhat.vscode-yaml",                 // YAML編集
        "dbaeumer.vscode-eslint",             // JavaScript Lint
        "esbenp.prettier-vscode"              // コードフォーマッター
    ]
}
```

### 7.2 ワークスペース設定

```json
// .vscode/settings.json
{
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.home": "/usr/lib/jvm/java-11-openjdk",

    // Gradleの設定
    "java.import.gradle.enabled": true,
    "java.import.gradle.wrapper.enabled": true,
    "java.import.gradle.home": null,

    // ソースパスの設定
    "java.project.sourcePaths": [
        "webapp/src/main/java",
        "admin/src/main/java",
        "common-lib/src/main/java"
    ],

    // 出力ディレクトリ
    "java.project.outputPath": "bin",

    // コード補完
    "java.completion.importOrder": [
        "java",
        "javax",
        "com.example",
        "org"
    ],

    // ファイル監視から除外
    "files.watcherExclude": {
        "**/build/**": true,
        "**/.gradle/**": true,
        "**/node_modules/**": true
    },

    // 自動保存
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,

    // フォーマッター
    "editor.formatOnSave": true,
    "java.format.settings.url": ".vscode/java-formatter.xml"
}
```

### 7.3 タスク設定（ビルド・デプロイの自動化）

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build All",
            "type": "shell",
            "command": "./gradlew",
            "args": ["clean", "build"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": []
        },
        {
            "label": "Build Exploded EAR",
            "type": "shell",
            "command": "./gradlew",
            "args": [":ear:explodedEar"],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "Deploy to WebLogic",
            "type": "shell",
            "command": "./gradlew",
            "args": [":ear:deployToWebLogic"],
            "dependsOn": "Build Exploded EAR",
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "Start WebLogic",
            "type": "shell",
            "command": "${env:DOMAIN_HOME}/bin/startWebLogic.sh",
            "isBackground": true,
            "problemMatcher": {
                "pattern": {
                    "regexp": "^(.*)$",
                    "file": 1,
                    "location": 2,
                    "message": 3
                },
                "background": {
                    "activeOnStart": true,
                    "beginsPattern": "^.*Starting WebLogic Server.*$",
                    "endsPattern": "^.*Server state changed to RUNNING.*$"
                }
            }
        },
        {
            "label": "Stop WebLogic",
            "type": "shell",
            "command": "${env:DOMAIN_HOME}/bin/stopWebLogic.sh",
            "problemMatcher": []
        },
        {
            "label": "Watch and Deploy",
            "type": "shell",
            "command": "./gradlew",
            "args": [":ear:explodedEar", "--continuous"],
            "isBackground": true,
            "problemMatcher": []
        }
    ]
}
```

### 7.4 キーボードショートカット設定

```json
// .vscode/keybindings.json
[
    {
        "key": "ctrl+shift+b",
        "command": "workbench.action.tasks.runTask",
        "args": "Build Exploded EAR"
    },
    {
        "key": "ctrl+shift+d",
        "command": "workbench.action.tasks.runTask",
        "args": "Deploy to WebLogic"
    },
    {
        "key": "f5",
        "command": "workbench.action.debug.start",
        "when": "!inDebugMode"
    },
    {
        "key": "shift+f5",
        "command": "workbench.action.debug.stop",
        "when": "inDebugMode"
    }
]
```

---

## 8. WebLogic固有の設定

### 8.1 weblogic-application.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<weblogic-application xmlns="http://xmlns.oracle.com/weblogic/weblogic-application"
                      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                      xsi:schemaLocation="http://xmlns.oracle.com/weblogic/weblogic-application
                                          http://xmlns.oracle.com/weblogic/weblogic-application/1.9/weblogic-application.xsd">

    <!-- アプリケーション名 -->
    <application-param>
        <param-name>webapp.encoding.default</param-name>
        <param-value>UTF-8</param-value>
    </application-param>

    <!-- 高速デプロイ（開発モード） -->
    <fast-swap>
        <enabled>true</enabled>
    </fast-swap>

    <!-- クラスローダー設定 -->
    <classloader-structure>
        <classloader-parent-first>false</classloader-parent-first>
    </classloader-structure>

    <!-- 共有ライブラリの参照 -->
    <library-ref>
        <library-name>struts2-lib</library-name>
    </library-ref>

</weblogic-application>
```

### 8.2 weblogic.xml（WAR個別設定）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<weblogic-web-app xmlns="http://xmlns.oracle.com/weblogic/weblogic-web-app"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://xmlns.oracle.com/weblogic/weblogic-web-app
                                      http://xmlns.oracle.com/weblogic/weblogic-web-app/1.9/weblogic-web-app.xsd">

    <!-- コンテキストルート -->
    <context-root>/app</context-root>

    <!-- セッション設定 -->
    <session-descriptor>
        <timeout-secs>3600</timeout-secs>
        <cookie-name>WEBAPP_SESSIONID</cookie-name>
    </session-descriptor>

    <!-- JSPコンパイラ設定 -->
    <jsp-descriptor>
        <page-check-seconds>1</page-check-seconds>  <!-- 開発時は短く -->
        <keepgenerated>true</keepgenerated>
        <working-dir>/tmp/jsp</working-dir>
    </jsp-descriptor>

    <!-- コンテナ記述子 -->
    <container-descriptor>
        <prefer-web-inf-classes>true</prefer-web-inf-classes>
        <prefer-application-packages>
            <package-name>org.slf4j.*</package-name>
            <package-name>org.apache.commons.*</package-name>
        </prefer-application-packages>
    </container-descriptor>

</weblogic-web-app>
```

---

## 9. トラブルシューティング

### 9.1 よくある問題と解決策

#### 問題1: ClassNotFoundException（Explodedデプロイ後）

**症状**:
```
java.lang.ClassNotFoundException: com.example.MyClass
```

**原因**: クラスファイルが正しい場所にコピーされていない

**解決策**:
```bash
# ディレクトリ構造を確認
find ear/build/exploded -name "*.class" | grep MyClass

# 正しい場所にクラスをコピー
cp webapp/build/classes/java/main/com/example/MyClass.class \
   ear/build/exploded/webapp.war/WEB-INF/classes/com/example/

# または完全再ビルド
./gradlew clean :ear:explodedEar :ear:deployToWebLogic
```

#### 問題2: JSPの変更が反映されない

**症状**: JSPファイルを変更してもブラウザに反映されない

**原因**: WebLogicのJSPキャッシュ

**解決策**:
```xml
<!-- weblogic.xml でキャッシュ時間を短縮 -->
<jsp-descriptor>
    <page-check-seconds>0</page-check-seconds>  <!-- 常にチェック -->
    <precompile>false</precompile>
</jsp-descriptor>
```

またはコンパイル済みJSPを削除:
```bash
rm -rf $DOMAIN_HOME/servers/AdminServer/tmp/_WL_user/*/jsp_servlet/
```

#### 問題3: Struts設定の変更が反映されない

**症状**: `struts.xml`を変更してもアクションマッピングが更新されない

**原因**: 開発モードが無効、またはキャッシュの問題

**解決策**:
```properties
# struts.properties で確認
struts.devMode = true
struts.configuration.xml.reload = true
```

WebLogicを再起動せずにリロード:
```bash
# 管理コンソールから「デプロイメント」→ アプリ選択 → 「更新」
# またはwlst.shを使用
java weblogic.WLST
wls> connect('weblogic', 'password', 't3://localhost:7001')
wls> redeploy('my-app')
```

#### 問題4: リモートデバッグでブレークポイントが無効

**症状**: ブレークポイントが灰色になり、停止しない

**原因**: ソースコードとデプロイされたクラスのミスマッチ

**解決策**:
```bash
# 1. タイムスタンプを確認
ls -l webapp/src/main/java/com/example/MyAction.java
ls -l webapp/build/classes/java/main/com/example/MyAction.class

# 2. クリーンビルド
./gradlew clean :webapp:compileJava

# 3. クラスファイルのバージョン確認
javap -verbose webapp/build/classes/java/main/com/example/MyAction.class | grep version

# 4. デバッグ情報の確認
javap -l webapp/build/classes/java/main/com/example/MyAction.class
```

build.gradleでデバッグ情報を強制:
```gradle
tasks.withType(JavaCompile) {
    options.debug = true
    options.debugOptions.debugLevel = 'source,lines,vars'
}
```

---

## 10. パフォーマンス最適化

### 10.1 ビルド時間の短縮

```gradle
// gradle.properties
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g -XX:+HeapDumpOnOutOfMemoryError
```

### 10.2 WebLogicの起動時間短縮

```bash
# setDomainEnv.sh で開発モードを有効化
export JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.management.discover=false"
export JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.ProductionModeEnabled=false"
```

### 10.3 JRebelによるホットスワップ（オプション）

JRebelを使用するとJavaコードの変更をサーバー再起動なしで反映可能:

```xml
<!-- rebel.xml -->
<application xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns="http://www.zeroturnaround.com"
             xsi:schemaLocation="http://www.zeroturnaround.com http://update.zeroturnaround.com/jrebel/rebel-2_3.xsd">

    <classpath>
        <dir name="${project.root}/webapp/build/classes/java/main" />
    </classpath>

    <web>
        <link target="/">
            <dir name="${project.root}/webapp/src/main/webapp" />
        </link>
    </web>

</application>
```

---

## 11. まとめ

### 11.1 開発ワークフロー全体図

```
┌─────────────────────────────────────────────────────────────┐
│ 開発者のワークステーション（VSCode）                            │
│                                                               │
│  1. コード編集                                                 │
│     ├─ Java (Struts Action, Spring Service)                  │
│     ├─ JSP/HTML/CSS/JavaScript                               │
│     └─ 設定ファイル (struts.xml, applicationContext.xml)       │
│                                                               │
│  2. ビルド（Gradle）                                           │
│     ./gradlew :ear:explodedEar                               │
│                                                               │
│  3. デプロイ                                                   │
│     → Exploded EAR → WebLogic autodeploy/                   │
│                                                               │
│  4. デバッグ                                                   │
│     VSCode Debugger ←→ JDWP (port 8453)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ WebLogic Server 14.1.1                                       │
│                                                               │
│  ・Exploded EARを直接参照                                      │
│  ・FastSwap有効（クラスの一部ホットスワップ）                   │
│  ・開発モード（Production Mode: false）                        │
│  ・デバッグポート8453でリッスン                                 │
│                                                               │
│  デプロイ構成:                                                 │
│    /app     → webapp.war (Struts + Spring)                  │
│    /admin   → admin.war                                     │
│    /lib     → 共有ライブラリ                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ ブラウザテスト                                                 │
│  http://localhost:7001/app/                                  │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 チェックリスト

#### 初回セットアップ
- [ ] Java 11インストール確認
- [ ] Gradle 7.2インストール確認
- [ ] WebLogic 14.1.1インストール・ドメイン作成
- [ ] 環境変数設定（JAVA_HOME, WEBLOGIC_HOME, DOMAIN_HOME）
- [ ] VSCode拡張機能インストール
- [ ] プロジェクトビルド成功確認
- [ ] Exploded EAR作成確認
- [ ] WebLogicデバッグモード起動確認
- [ ] VSCodeからリモートデバッグ接続成功

#### 日常開発
- [ ] Struts開発モード有効化（struts.devMode=true）
- [ ] WebLogic FastSwap有効化
- [ ] JSP変更が即座に反映されることを確認
- [ ] Javaコード変更→ビルド→ホットデプロイの流れを確認
- [ ] ブレークポイントで停止することを確認

#### 本番デプロイ前
- [ ] 開発モードを無効化（struts.devMode=false）
- [ ] WebLogic本番モードに変更
- [ ] デバッグポートを無効化
- [ ] Archived EAR形式でビルド
- [ ] パフォーマンステスト実施

---

## 12. 参考資料

- [Oracle WebLogic Server 14.1.1 Documentation](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/)
- [Gradle User Guide - EAR Plugin](https://docs.gradle.org/7.2/userguide/ear_plugin.html)
- [Apache Struts 2 Documentation](https://struts.apache.org/core-developers/)
- [Spring Framework Reference](https://docs.spring.io/spring-framework/docs/5.3.x/reference/html/)
- [VSCode Java Debugging](https://code.visualstudio.com/docs/java/java-debugging)
- [JPDA (Java Platform Debugger Architecture)](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/)

---

## 13. 次のステップ

- [[weblogic-production-deployment.md]] - 本番環境へのデプロイ手順
- [[gradle-advanced-build.md]] - Gradleビルドスクリプトの高度な設定
- [[struts2-spring-integration.md]] - Struts 2とSpringの統合ベストプラクティス
- [[java-debugging-techniques.md]] - Java高度なデバッグテクニック
