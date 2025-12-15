# Gradle高度なビルドスクリプト学習ノート

> 対象: Gradle 7.2+, Java 11+
> 環境: マルチモジュールプロジェクト、エンタープライズアプリケーション

## 学習目標

- Gradleの高度なビルドテクニックを習得する
- カスタムタスクとプラグインの作成方法を理解する
- ビルドパフォーマンスの最適化手法を学ぶ
- 環境別ビルドと条件分岐を実装する
- 継続的インテグレーション（CI）との統合方法を習得する

---

## 1. プロジェクト構造とビルドスクリプトの設計

### 1.1 推奨されるディレクトリ構造

```
my-enterprise-project/
├── gradle/
│   ├── wrapper/
│   │   ├── gradle-wrapper.jar
│   │   └── gradle-wrapper.properties
│   └── scripts/                      # カスタムビルドスクリプト
│       ├── dependencies.gradle       # 依存関係の一元管理
│       ├── quality.gradle            # コード品質チェック
│       ├── publishing.gradle         # アーティファクト公開
│       └── versioning.gradle         # バージョン管理
├── buildSrc/                         # カスタムプラグイン
│   ├── build.gradle
│   └── src/main/groovy/
│       └── com/example/plugins/
│           ├── DeployPlugin.groovy
│           └── DatabaseMigrationPlugin.groovy
├── config/                           # ビルド設定ファイル
│   ├── checkstyle/
│   ├── pmd/
│   └── spotbugs/
├── scripts/                          # シェルスクリプト
│   ├── deploy.sh
│   └── start-local.sh
├── settings.gradle                   # プロジェクト構成
├── gradle.properties                 # グローバル設定
├── build.gradle                      # ルートビルドスクリプト
├── module-a/
│   └── build.gradle
├── module-b/
│   └── build.gradle
└── ear/
    └── build.gradle
```

### 1.2 gradle.properties（グローバル設定）

```properties
# ==========================================
# プロジェクト情報
# ==========================================
group=com.example
version=1.0.0-SNAPSHOT
description=Enterprise Application

# ==========================================
# Java設定
# ==========================================
javaVersion=11
sourceCompatibility=11
targetCompatibility=11
encoding=UTF-8

# ==========================================
# Gradleパフォーマンス設定
# ==========================================
# Gradleデーモンの有効化
org.gradle.daemon=true

# 並列実行
org.gradle.parallel=true
org.gradle.workers.max=4

# ビルドキャッシュ
org.gradle.caching=true

# オンデマンド設定
org.gradle.configureondemand=true

# JVMヒープサイズ
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8

# ==========================================
# 依存関係バージョン
# ==========================================
springVersion=5.3.27
strutsVersion=2.5.30
mybatisVersion=3.5.13
logbackVersion=1.2.12
junitVersion=5.9.3

# ==========================================
# WebLogic設定
# ==========================================
weblogicHome=/opt/oracle/middleware
weblogicVersion=14.1.1.0.0
domainName=base_domain

# ==========================================
# 環境別設定
# ==========================================
# 環境: dev, test, staging, production
environment=dev

# デバッグポート
debugPort=8453

# データベース接続（環境変数で上書き可能）
db.host=localhost
db.port=5432
db.name=myapp_dev
db.username=devuser
db.password=devpass

# ==========================================
# ビルドフラグ
# ==========================================
# テストスキップ（開発時のみ）
skipTests=false

# コード品質チェックのスキップ
skipQualityChecks=false

# ドキュメント生成
generateJavadoc=true

# ソースJAR生成
buildSourceJar=true
```

---

## 2. ルートbuild.gradleの高度な設定

### 2.1 プラグインとビルドスクリプトブロック

```gradle
// ==========================================
// ビルドスクリプト依存関係
// ==========================================
buildscript {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }

    dependencies {
        // カスタムプラグイン
        classpath 'com.github.spotbugs.snom:spotbugs-gradle-plugin:5.0.13'
        classpath 'com.github.ben-manes:gradle-versions-plugin:0.46.0'
    }
}

// ==========================================
// トップレベルプラグイン
// ==========================================
plugins {
    id 'java' apply false
    id 'war' apply false
    id 'ear' apply false
    id 'idea'
    id 'eclipse'
    id 'com.github.ben-manes.versions' version '0.46.0'
}

// ==========================================
// 外部スクリプトの読み込み
// ==========================================
apply from: 'gradle/scripts/dependencies.gradle'
apply from: 'gradle/scripts/versioning.gradle'

// ==========================================
// 全プロジェクト共通設定
// ==========================================
allprojects {
    group = project.property('group')
    version = project.property('version')

    repositories {
        mavenCentral()
        mavenLocal()

        // 企業内リポジトリ
        maven {
            name = 'CorporateNexus'
            url = uri('https://nexus.example.com/repository/maven-public/')
            credentials {
                username = project.findProperty('nexusUser') ?: System.getenv('NEXUS_USER')
                password = project.findProperty('nexusPassword') ?: System.getenv('NEXUS_PASSWORD')
            }
        }

        // WebLogic JARリポジトリ
        flatDir {
            dirs "${project.property('weblogicHome')}/wlserver/server/lib"
        }
    }
}

// ==========================================
// サブプロジェクト共通設定
// ==========================================
subprojects {
    apply plugin: 'java'
    apply plugin: 'checkstyle'
    apply plugin: 'pmd'
    apply plugin: 'com.github.spotbugs'

    sourceCompatibility = JavaVersion.toVersion(project.property('javaVersion'))
    targetCompatibility = JavaVersion.toVersion(project.property('javaVersion'))

    // ==========================================
    // 依存関係管理
    // ==========================================
    configurations {
        // コンパイル時のみの依存関係
        compileOnly

        // テスト実装
        testImplementation.extendsFrom compileOnly

        // 全モジュールから除外する依存関係
        all {
            exclude group: 'commons-logging', module: 'commons-logging'
            exclude group: 'log4j', module: 'log4j'
        }
    }

    dependencies {
        // 共通依存関係
        implementation 'org.slf4j:slf4j-api:1.7.36'
        implementation 'ch.qos.logback:logback-classic:' + project.property('logbackVersion')

        compileOnly 'javax.servlet:javax.servlet-api:4.0.1'
        compileOnly 'org.projectlombok:lombok:1.18.26'
        annotationProcessor 'org.projectlombok:lombok:1.18.26'

        // テスト依存関係
        testImplementation "org.junit.jupiter:junit-jupiter:${project.property('junitVersion')}"
        testImplementation 'org.mockito:mockito-core:5.2.0'
        testImplementation 'org.mockito:mockito-junit-jupiter:5.2.0'
        testImplementation 'org.assertj:assertj-core:3.24.2'
        testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
    }

    // ==========================================
    // コンパイル設定
    // ==========================================
    tasks.withType(JavaCompile) {
        options.encoding = project.property('encoding')
        options.compilerArgs << '-parameters'  // メソッドパラメータ名を保持
        options.compilerArgs << '-Xlint:unchecked'
        options.compilerArgs << '-Xlint:deprecation'

        // デバッグ情報を含める
        options.debug = true
        options.debugOptions.debugLevel = 'source,lines,vars'
    }

    // ==========================================
    // テスト設定
    // ==========================================
    tasks.named('test') {
        useJUnitPlatform()

        // テストログ詳細化
        testLogging {
            events 'passed', 'skipped', 'failed'
            exceptionFormat 'full'
            showStandardStreams = false
            showCauses = true
            showStackTraces = true
        }

        // テスト並列実行
        maxParallelForks = Runtime.runtime.availableProcessors().intdiv(2) ?: 1

        // システムプロパティの引き継ぎ
        systemProperty 'environment', project.property('environment')
        systemProperty 'user.timezone', 'Asia/Tokyo'

        // レポート出力
        reports {
            html.required = true
            junitXml.required = true
        }

        // テストスキップオプション
        onlyIf { !project.hasProperty('skipTests') || project.property('skipTests') != 'true' }
    }

    // ==========================================
    // コード品質チェック
    // ==========================================
    checkstyle {
        toolVersion = '10.9.3'
        configFile = file("${rootProject.projectDir}/config/checkstyle/checkstyle.xml")
        ignoreFailures = false
        maxWarnings = 0
    }

    pmd {
        toolVersion = '6.55.0'
        ruleSetFiles = files("${rootProject.projectDir}/config/pmd/pmd-rules.xml")
        ignoreFailures = false
        consoleOutput = true
    }

    spotbugs {
        toolVersion = '4.7.3'
        effort = 'max'
        reportLevel = 'medium'
        ignoreFailures = false
    }

    // ==========================================
    // JARマニフェスト設定
    // ==========================================
    tasks.withType(Jar) {
        manifest {
            attributes(
                'Implementation-Title': project.name,
                'Implementation-Version': project.version,
                'Implementation-Vendor': project.group,
                'Built-By': System.getProperty('user.name'),
                'Built-Date': new Date().format('yyyy-MM-dd HH:mm:ss'),
                'Built-JDK': System.getProperty('java.version'),
                'Built-Gradle': gradle.gradleVersion
            )
        }

        // 再現可能なビルド（タイムスタンプを固定）
        preserveFileTimestamps = false
        reproducibleFileOrder = true
    }

    // ==========================================
    // ソースJAR生成
    // ==========================================
    tasks.register('sourcesJar', Jar) {
        archiveClassifier = 'sources'
        from sourceSets.main.allSource
    }

    // ==========================================
    // JavadocJAR生成
    // ==========================================
    tasks.register('javadocJar', Jar) {
        archiveClassifier = 'javadoc'
        from javadoc
    }

    // ==========================================
    // アーティファクト設定
    // ==========================================
    if (project.property('buildSourceJar').toBoolean()) {
        artifacts {
            archives sourcesJar
            archives javadocJar
        }
    }
}

// ==========================================
// カスタムタスク: 依存関係レポート
// ==========================================
tasks.register('dependencyReport') {
    group = 'reporting'
    description = 'Generate dependency report for all subprojects'

    doLast {
        subprojects.each { subproject ->
            println "\n=== ${subproject.name} ==="
            subproject.configurations.runtimeClasspath.each { file ->
                println "  - ${file.name}"
            }
        }
    }
}

// ==========================================
// カスタムタスク: バージョン更新チェック
// ==========================================
tasks.named('dependencyUpdates') {
    rejectVersionIf {
        isNonStable(it.candidate.version)
    }
}

def isNonStable(String version) {
    def stableKeyword = ['RELEASE', 'FINAL', 'GA'].any { version.toUpperCase().contains(it) }
    def regex = /^[0-9,.v-]+(-r)?$/
    return !stableKeyword && !(version ==~ regex)
}

// ==========================================
// カスタムタスク: クリーン全体
// ==========================================
tasks.register('cleanAll') {
    group = 'build'
    description = 'Clean all build outputs including Gradle cache'

    dependsOn 'clean'

    doLast {
        delete "${rootProject.buildDir}"
        delete "${rootProject.projectDir}/.gradle"

        subprojects.each { subproject ->
            delete "${subproject.buildDir}"
        }

        println "✓ All build outputs cleaned"
    }
}

// ==========================================
// カスタムタスク: 環境情報表示
// ==========================================
tasks.register('showEnvironment') {
    group = 'help'
    description = 'Display build environment information'

    doLast {
        println """
        ========================================
        Build Environment
        ========================================
        Project: ${project.name} ${project.version}
        Environment: ${project.property('environment')}
        Java Version: ${System.getProperty('java.version')}
        Gradle Version: ${gradle.gradleVersion}
        OS: ${System.getProperty('os.name')} ${System.getProperty('os.version')}
        User: ${System.getProperty('user.name')}
        Working Directory: ${project.projectDir}
        Build Directory: ${project.buildDir}
        ========================================
        """

        println "\nActive Properties:"
        project.properties.findAll { it.key.startsWith('db.') || it.key == 'environment' }.each { key, value ->
            println "  ${key} = ${value}"
        }
    }
}
```

---

## 3. 環境別ビルド設定

### 3.1 環境ごとの設定ファイル

#### gradle-dev.properties

```properties
environment=dev
db.host=localhost
db.port=5432
db.name=myapp_dev
db.username=devuser
db.password=devpass
logLevel=DEBUG
enableDebug=true
minifyAssets=false
```

#### gradle-test.properties

```properties
environment=test
db.host=test-db.example.com
db.port=5432
db.name=myapp_test
db.username=testuser
db.password=testpass
logLevel=INFO
enableDebug=true
minifyAssets=false
```

#### gradle-production.properties

```properties
environment=production
db.host=prod-db.example.com
db.port=5432
db.name=myapp_prod
db.username=produser
db.password=${DB_PASSWORD}  # 環境変数から読み込み
logLevel=WARN
enableDebug=false
minifyAssets=true
```

### 3.2 環境別設定の読み込み

```gradle
// build.gradle

// 環境プロパティファイルの読み込み
def env = project.hasProperty('env') ? project.property('env') : 'dev'
def envPropertiesFile = file("gradle-${env}.properties")

if (envPropertiesFile.exists()) {
    envPropertiesFile.withInputStream { stream ->
        def envProps = new Properties()
        envProps.load(stream)
        envProps.each { key, value ->
            // 環境変数で上書き可能
            def envValue = System.getenv(key.toString().toUpperCase().replace('.', '_'))
            project.ext.set(key, envValue ?: value)
        }
    }
    println "✓ Loaded environment: ${env}"
} else {
    println "⚠ Environment file not found: ${envPropertiesFile}"
}

// 使用例
subprojects {
    tasks.register('generateConfig') {
        doLast {
            def configFile = file("${buildDir}/resources/main/application.properties")
            configFile.parentFile.mkdirs()

            configFile.text = """\
                # Generated configuration for ${project.ext.environment}
                app.name=${project.name}
                app.version=${project.version}
                app.environment=${project.ext.environment}

                # Database
                db.host=${project.ext.get('db.host')}
                db.port=${project.ext.get('db.port')}
                db.name=${project.ext.get('db.name')}
                db.username=${project.ext.get('db.username')}
                db.password=${project.ext.get('db.password')}

                # Logging
                log.level=${project.ext.get('logLevel')}
                """.stripIndent()

            println "✓ Generated config: ${configFile}"
        }
    }

    processResources.dependsOn generateConfig
}
```

### 3.3 ビルド実行（環境指定）

```bash
# 開発環境
./gradlew build -Penv=dev

# テスト環境
./gradlew build -Penv=test

# 本番環境（環境変数でパスワード指定）
export DB_PASSWORD=secret_password
./gradlew build -Penv=production

# 環境情報の表示
./gradlew showEnvironment -Penv=production
```

---

## 4. カスタムタスクの作成

### 4.1 基本的なカスタムタスク

```gradle
// ==========================================
// シンプルなカスタムタスク
// ==========================================
tasks.register('hello') {
    group = 'custom'
    description = 'Print hello message'

    doLast {
        println "Hello from ${project.name}!"
    }
}

// ==========================================
// 入力パラメータ付きタスク
// ==========================================
tasks.register('greet') {
    group = 'custom'
    description = 'Greet with a custom name'

    doLast {
        def name = project.findProperty('name') ?: 'World'
        println "Hello, ${name}!"
    }
}

// 実行: ./gradlew greet -Pname=John

// ==========================================
// 依存関係のあるタスク
// ==========================================
tasks.register('prepareData') {
    group = 'custom'
    description = 'Prepare data files'

    doLast {
        def dataDir = file("${buildDir}/data")
        dataDir.mkdirs()

        file("${dataDir}/sample.txt").text = "Sample data"
        println "✓ Data prepared in ${dataDir}"
    }
}

tasks.register('processData') {
    group = 'custom'
    description = 'Process prepared data'

    dependsOn 'prepareData'

    doLast {
        def dataFile = file("${buildDir}/data/sample.txt")
        println "Processing: ${dataFile.text}"
        println "✓ Data processed"
    }
}

// ==========================================
// 入出力を持つタスク（キャッシュ可能）
// ==========================================
tasks.register('generateReport', GenerateReportTask) {
    inputFile = file('src/main/resources/data.csv')
    outputFile = file("${buildDir}/reports/report.html")
}

abstract class GenerateReportTask extends DefaultTask {
    @InputFile
    abstract RegularFileProperty getInputFile()

    @OutputFile
    abstract RegularFileProperty getOutputFile()

    @TaskAction
    void generate() {
        def input = inputFile.get().asFile
        def output = outputFile.get().asFile

        output.parentFile.mkdirs()

        // レポート生成ロジック
        output.text = """
            <html>
            <body>
                <h1>Report</h1>
                <p>Generated from: ${input.name}</p>
                <p>Date: ${new Date()}</p>
            </body>
            </html>
        """.stripIndent()

        println "✓ Report generated: ${output}"
    }
}
```

### 4.2 複雑なカスタムタスク例

```gradle
// ==========================================
// データベースマイグレーションタスク
// ==========================================
tasks.register('migrateDatabase') {
    group = 'database'
    description = 'Run database migrations'

    doLast {
        def dbHost = project.ext.get('db.host')
        def dbPort = project.ext.get('db.port')
        def dbName = project.ext.get('db.name')
        def dbUser = project.ext.get('db.username')
        def dbPass = project.ext.get('db.password')

        println "Migrating database: ${dbName}@${dbHost}:${dbPort}"

        // Flywayなどのマイグレーションツールを実行
        exec {
            commandLine 'flyway',
                '-url=jdbc:postgresql://' + dbHost + ':' + dbPort + '/' + dbName,
                '-user=' + dbUser,
                '-password=' + dbPass,
                'migrate'
        }

        println "✓ Database migration completed"
    }
}

// ==========================================
// Docker Composeタスク
// ==========================================
tasks.register('dockerUp') {
    group = 'docker'
    description = 'Start Docker Compose services'

    doLast {
        exec {
            commandLine 'docker-compose', '-f', 'docker-compose.yml', 'up', '-d'
        }

        println "✓ Docker services started"
        println "  - Database: localhost:5432"
        println "  - Redis: localhost:6379"
    }
}

tasks.register('dockerDown') {
    group = 'docker'
    description = 'Stop Docker Compose services'

    doLast {
        exec {
            commandLine 'docker-compose', '-f', 'docker-compose.yml', 'down'
        }

        println "✓ Docker services stopped"
    }
}

tasks.register('dockerLogs') {
    group = 'docker'
    description = 'Show Docker Compose logs'

    doLast {
        exec {
            commandLine 'docker-compose', '-f', 'docker-compose.yml', 'logs', '-f'
        }
    }
}

// ==========================================
// 統合テスト用タスク
// ==========================================
tasks.register('integrationTest', Test) {
    group = 'verification'
    description = 'Run integration tests'

    useJUnitPlatform {
        includeTags 'integration'
    }

    shouldRunAfter test

    testClassesDirs = sourceSets.test.output.classesDirs
    classpath = sourceSets.test.runtimeClasspath

    // 統合テスト専用設定
    systemProperty 'spring.profiles.active', 'integration-test'

    doFirst {
        println "Running integration tests..."
    }

    doLast {
        println "✓ Integration tests completed"
    }
}

// テストタスクの依存関係
check.dependsOn integrationTest

// ==========================================
// アセット最適化タスク
// ==========================================
tasks.register('optimizeAssets') {
    group = 'build'
    description = 'Minify JavaScript and CSS files'

    onlyIf { project.ext.get('minifyAssets').toBoolean() }

    doLast {
        def webappDir = file('src/main/webapp')
        def buildWebappDir = file("${buildDir}/webapp")

        buildWebappDir.mkdirs()

        // JavaScriptの最小化
        fileTree(webappDir) {
            include '**/*.js'
            exclude '**/*.min.js'
        }.each { jsFile ->
            def minFile = new File(buildWebappDir, jsFile.name.replace('.js', '.min.js'))

            // 実際の最小化ツール（UglifyJS、Terserなど）を呼び出す
            exec {
                commandLine 'npx', 'terser', jsFile.absolutePath, '-o', minFile.absolutePath, '-c', '-m'
                ignoreExitValue = true
            }

            println "  Minified: ${jsFile.name} -> ${minFile.name}"
        }

        // CSSの最小化
        fileTree(webappDir) {
            include '**/*.css'
            exclude '**/*.min.css'
        }.each { cssFile ->
            def minFile = new File(buildWebappDir, cssFile.name.replace('.css', '.min.css'))

            exec {
                commandLine 'npx', 'cssnano', cssFile.absolutePath, minFile.absolutePath
                ignoreExitValue = true
            }

            println "  Minified: ${cssFile.name} -> ${minFile.name}"
        }

        println "✓ Assets optimized"
    }
}

// WARビルド前にアセット最適化を実行
tasks.withType(War) {
    dependsOn optimizeAssets
}
```

---

## 5. buildSrcによるカスタムプラグイン

### 5.1 buildSrc/build.gradle

```gradle
plugins {
    id 'groovy-gradle-plugin'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'com.jcraft:jsch:0.1.55'
    implementation 'org.apache.commons:commons-lang3:3.12.0'
}
```

### 5.2 カスタムプラグイン: DeployPlugin

```groovy
// buildSrc/src/main/groovy/com/example/plugins/DeployPlugin.groovy
package com.example.plugins

import org.gradle.api.Plugin
import org.gradle.api.Project
import com.jcraft.jsch.*

class DeployPlugin implements Plugin<Project> {
    @Override
    void apply(Project project) {
        // 拡張機能の登録
        def extension = project.extensions.create('deployment', DeploymentExtension)

        // デプロイタスクの登録
        project.tasks.register('deployToRemote') {
            group = 'deployment'
            description = 'Deploy application to remote server'

            doLast {
                def config = extension

                println "Deploying to ${config.host}:${config.port}"
                println "  User: ${config.username}"
                println "  Target: ${config.deployPath}"

                // SCPでファイル転送
                def earFile = project.file("${project.buildDir}/libs/${project.name}.ear")

                if (!earFile.exists()) {
                    throw new RuntimeException("EAR file not found: ${earFile}")
                }

                // JSch（SSH/SCP）を使用
                JSch jsch = new JSch()

                if (config.privateKeyPath) {
                    jsch.addIdentity(config.privateKeyPath)
                }

                Session session = jsch.getSession(config.username, config.host, config.port)

                if (config.password) {
                    session.setPassword(config.password)
                }

                Properties sessionConfig = new Properties()
                sessionConfig.put("StrictHostKeyChecking", "no")
                session.setConfig(sessionConfig)

                try {
                    session.connect()

                    // SCPでファイル送信
                    Channel channel = session.openChannel("sftp")
                    channel.connect()
                    ChannelSftp sftpChannel = (ChannelSftp) channel

                    sftpChannel.put(earFile.absolutePath, "${config.deployPath}/${earFile.name}")

                    println "✓ File uploaded: ${earFile.name}"

                    // WebLogicの再デプロイコマンド実行（オプション）
                    if (config.redeployCommand) {
                        Channel execChannel = session.openChannel("exec")
                        ((ChannelExec) execChannel).setCommand(config.redeployCommand)
                        execChannel.connect()
                        execChannel.disconnect()

                        println "✓ Redeploy command executed"
                    }

                    sftpChannel.disconnect()

                } finally {
                    session.disconnect()
                }

                println "✓ Deployment completed"
            }
        }

        // 健全性チェックタスク
        project.tasks.register('checkDeployment') {
            group = 'deployment'
            description = 'Check if deployment is successful'

            doLast {
                def config = extension

                if (!config.healthCheckUrl) {
                    println "⚠ No health check URL configured"
                    return
                }

                println "Checking: ${config.healthCheckUrl}"

                def url = new URL(config.healthCheckUrl)
                def connection = url.openConnection()
                connection.setRequestMethod("GET")
                connection.setConnectTimeout(5000)
                connection.setReadTimeout(5000)

                def responseCode = connection.getResponseCode()

                if (responseCode == 200) {
                    println "✓ Deployment is healthy (HTTP ${responseCode})"
                } else {
                    throw new RuntimeException("Deployment check failed (HTTP ${responseCode})")
                }
            }
        }
    }
}

// 拡張機能クラス
class DeploymentExtension {
    String host = 'localhost'
    int port = 22
    String username = 'deploy'
    String password = null
    String privateKeyPath = null
    String deployPath = '/opt/deployments'
    String redeployCommand = null
    String healthCheckUrl = null
}
```

### 5.3 プラグインの使用

```gradle
// ear/build.gradle

plugins {
    id 'ear'
    id 'com.example.plugins.DeployPlugin'
}

deployment {
    host = 'app-server.example.com'
    port = 22
    username = 'weblogic'
    privateKeyPath = "${System.getProperty('user.home')}/.ssh/id_rsa"
    deployPath = '/opt/oracle/middleware/user_projects/domains/base_domain/autodeploy'
    redeployCommand = '/opt/scripts/redeploy.sh my-app'
    healthCheckUrl = 'http://app-server.example.com:7001/app/health'
}

// デプロイワークフロー
tasks.register('fullDeploy') {
    group = 'deployment'
    description = 'Build, deploy, and check deployment'

    dependsOn 'ear', 'deployToRemote', 'checkDeployment'

    tasks.findByName('deployToRemote').mustRunAfter 'ear'
    tasks.findByName('checkDeployment').mustRunAfter 'deployToRemote'
}
```

---

## 6. ビルドパフォーマンスの最適化

### 6.1 ビルドキャッシュの活用

```gradle
// settings.gradle
buildCache {
    local {
        enabled = true
        directory = file("${rootDir}/.gradle/build-cache")
        removeUnusedEntriesAfterDays = 7
    }

    // リモートビルドキャッシュ（オプション）
    remote(HttpBuildCache) {
        url = 'https://build-cache.example.com/'
        enabled = System.getenv('CI') == 'true'
        push = System.getenv('CI_MAIN_BRANCH') == 'true'

        credentials {
            username = System.getenv('BUILD_CACHE_USER')
            password = System.getenv('BUILD_CACHE_PASSWORD')
        }
    }
}
```

### 6.2 並列実行とワーカー設定

```gradle
// gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=4
org.gradle.configureondemand=true

// CPU数に応じた動的設定
org.gradle.workers.max=${Runtime.runtime.availableProcessors()}
```

### 6.3 増分ビルドの最適化

```gradle
subprojects {
    // コンパイルタスクの増分化
    tasks.withType(JavaCompile) {
        options.incremental = true
    }

    // テストタスクの増分化
    tasks.named('test') {
        outputs.upToDateWhen { false }  // 常に実行する場合
        // または
        inputs.files(fileTree('src/test/java'))
        outputs.dir("${buildDir}/test-results")
    }

    // カスタムタスクの増分化
    tasks.register('processTemplates') {
        inputs.dir('src/main/templates')
        outputs.dir("${buildDir}/generated-sources")

        doLast {
            // テンプレート処理
        }
    }
}
```

### 6.4 依存関係の解決最適化

```gradle
configurations.all {
    // 動的バージョンのキャッシュ時間
    resolutionStrategy.cacheDynamicVersionsFor 10, 'minutes'

    // スナップショットのキャッシュ時間
    resolutionStrategy.cacheChangingModulesFor 4, 'hours'

    // 依存関係の検証を無効化（ビルド高速化、非推奨）
    // resolutionStrategy.disableDependencyVerification()
}

// 依存関係のダウンロード並列化
repositories {
    mavenCentral()
    maven {
        url 'https://repo.example.com/maven'
        metadataSources {
            mavenPom()
            artifact()
        }
    }
}
```

### 6.5 ビルドスキャン

```gradle
plugins {
    id 'com.gradle.enterprise' version '3.13'
}

gradleEnterprise {
    buildScan {
        termsOfServiceUrl = 'https://gradle.com/terms-of-service'
        termsOfServiceAgree = 'yes'

        publishAlways()

        tag 'CI'
        tag System.getenv('CI_BRANCH_NAME')

        link 'Repository', 'https://github.com/yourorg/yourrepo'

        buildFinished {
            println "Build scan: ${buildScanUri}"
        }
    }
}
```

---

## 7. CI/CD統合

### 7.1 GitHub Actions向け設定

```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 11
        uses: actions/setup-java@v3
        with:
          java-version: '11'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Build with Gradle
        run: ./gradlew build -Penv=test --build-cache --parallel

      - name: Run tests
        run: ./gradlew test integrationTest

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: '**/build/reports/tests/**'

      - name: Build EAR
        run: ./gradlew :ear:ear

      - name: Upload EAR artifact
        uses: actions/upload-artifact@v3
        with:
          name: application-ear
          path: ear/build/libs/*.ear
```

### 7.2 Gradle用CI最適化スクリプト

```gradle
// build.gradle

// CI環境の検出
def isCi = System.getenv('CI') == 'true'

if (isCi) {
    // CI専用設定
    allprojects {
        tasks.withType(Test) {
            // 詳細なテストログ
            testLogging {
                events 'passed', 'skipped', 'failed', 'standardOut', 'standardError'
                showStandardStreams = true
            }

            // JUnit XMLレポート
            reports {
                junitXml.required = true
                html.required = true
            }
        }

        // ビルドキャッシュを強制有効化
        tasks.withType(AbstractCompile) {
            options.incremental = true
        }
    }

    // CI専用タスク
    tasks.register('ciTest') {
        group = 'CI'
        description = 'Run all tests for CI'

        dependsOn 'test', 'integrationTest', 'check'
    }

    tasks.register('ciBuild') {
        group = 'CI'
        description = 'Full CI build'

        dependsOn 'clean', 'build', 'ciTest', ':ear:ear'
    }
}
```

---

## 8. ビルドスクリプトのベストプラクティス

### 8.1 DRY原則（Don't Repeat Yourself）

```gradle
// gradle/scripts/dependencies.gradle

ext {
    versions = [
        spring: '5.3.27',
        struts: '2.5.30',
        mybatis: '3.5.13',
        junit: '5.9.3'
    ]

    libs = [
        spring: [
            context: "org.springframework:spring-context:${versions.spring}",
            web: "org.springframework:spring-web:${versions.spring}",
            jdbc: "org.springframework:spring-jdbc:${versions.spring}"
        ],
        struts: [
            core: "org.apache.struts:struts2-core:${versions.struts}",
            spring: "org.apache.struts:struts2-spring-plugin:${versions.struts}"
        ],
        test: [
            junit: "org.junit.jupiter:junit-jupiter:${versions.junit}",
            mockito: 'org.mockito:mockito-core:5.2.0'
        ]
    ]
}

// 使用例
// build.gradle
apply from: 'gradle/scripts/dependencies.gradle'

dependencies {
    implementation libs.spring.context
    implementation libs.spring.web
    implementation libs.struts.core

    testImplementation libs.test.junit
    testImplementation libs.test.mockito
}
```

### 8.2 型安全な設定（Kotlin DSL）

```kotlin
// build.gradle.kts
plugins {
    java
    war
    ear
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework:spring-context:5.3.27")
    testImplementation("org.junit.jupiter:junit-jupiter:5.9.3")
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}

tasks.register("hello") {
    group = "custom"
    description = "Print hello message"

    doLast {
        println("Hello from Kotlin DSL!")
    }
}
```

### 8.3 ビルドロジックの分離

```
my-project/
├── buildSrc/
│   └── src/main/groovy/
│       └── com/example/
│           ├── tasks/
│           │   ├── DeployTask.groovy
│           │   └── MigrationTask.groovy
│           ├── plugins/
│           │   └── DeployPlugin.groovy
│           └── extensions/
│               └── DeploymentExtension.groovy
├── gradle/scripts/
│   ├── dependencies.gradle
│   ├── quality.gradle
│   └── publishing.gradle
└── build.gradle
```

---

## 9. デバッグとトラブルシューティング

### 9.1 ビルドのデバッグ

```bash
# スタックトレース付きビルド
./gradlew build --stacktrace

# より詳細なスタックトレース
./gradlew build --full-stacktrace

# デバッグログ有効化
./gradlew build --debug

# 情報ログ
./gradlew build --info

# タスクの実行順序を確認（Dry Run）
./gradlew build --dry-run

# ビルドスキャン
./gradlew build --scan

# プロファイリング
./gradlew build --profile
```

### 9.2 依存関係の診断

```bash
# 依存関係ツリー
./gradlew dependencies

# 特定の設定の依存関係
./gradlew dependencies --configuration runtimeClasspath

# 依存関係の詳細分析
./gradlew dependencyInsight --dependency spring-core

# 依存関係の更新チェック
./gradlew dependencyUpdates

# 重複した依存関係の検出
./gradlew buildEnvironment
```

### 9.3 キャッシュのクリア

```bash
# ローカルビルドキャッシュのクリア
rm -rf ~/.gradle/caches/
rm -rf .gradle/

# 特定プロジェクトのクリーン
./gradlew clean

# 全プロジェクトの完全クリーン
./gradlew cleanAll

# デーモンの停止
./gradlew --stop
```

---

## 10. まとめ

### 10.1 高度なビルド機能チェックリスト

- [ ] 環境別ビルド設定を実装している
- [ ] カスタムタスクで繰り返し作業を自動化している
- [ ] ビルドキャッシュを活用している
- [ ] 並列ビルドを有効化している
- [ ] 増分ビルドを活用している
- [ ] buildSrcでビルドロジックを整理している
- [ ] CI/CDパイプラインに統合している
- [ ] ビルドスクリプトがDRY原則に従っている
- [ ] コード品質チェックを自動化している
- [ ] デプロイメントを自動化している

### 10.2 パフォーマンス最適化チェックリスト

- [ ] `org.gradle.parallel=true`
- [ ] `org.gradle.caching=true`
- [ ] `org.gradle.configureondemand=true`
- [ ] `org.gradle.daemon=true`
- [ ] JVMヒープサイズを適切に設定
- [ ] 依存関係のキャッシュ戦略を設定
- [ ] 不要な依存関係を除外
- [ ] ビルドスキャンでボトルネックを特定

---

## 11. 参考資料

- [Gradle User Guide](https://docs.gradle.org/current/userguide/userguide.html)
- [Gradle Build Performance Guide](https://docs.gradle.org/current/userguide/performance.html)
- [Gradle Plugin Development](https://docs.gradle.org/current/userguide/custom_plugins.html)
- [Gradle Best Practices](https://docs.gradle.org/current/userguide/authoring_maintainable_build_scripts.html)

---

## 12. 次のステップ

- [[weblogic-development-workflow.md]] - WebLogic開発ワークフロー
- [[java-build-artifacts.md]] - JavaビルドアーティファクトとEAR
- [[ci-cd-pipeline.md]] - CI/CDパイプラインの構築
