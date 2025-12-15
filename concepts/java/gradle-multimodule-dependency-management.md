# Gradleマルチモジュール依存関係管理学習ノート

> 対象: Gradle 7.2+, マルチモジュールプロジェクト
> 環境: EARビルド、ライブラリ重複排除、ビルド順序制御

## 学習目標

- マルチモジュール間の依存関係を正しく設定する
- ライブラリの重複を完全に排除する方法を習得する
- ビルド順序を制御してJAR間の依存を解決する
- EARのlibディレクトリへのライブラリ配置を管理する
- 依存関係の可視化とトラブルシューティング方法を学ぶ

---

## 1. マルチモジュールプロジェクトの依存関係設計

### 1.1 プロジェクト構成例

```
my-enterprise-app/
├── settings.gradle
├── build.gradle                 # ルート設定
├── common-utils/                # 共通ユーティリティ（JAR）
│   ├── build.gradle
│   └── src/main/java/
│       └── com/example/utils/
├── domain-model/                # ドメインモデル（JAR）
│   ├── build.gradle             # common-utilsに依存
│   └── src/main/java/
│       └── com/example/model/
├── business-logic/              # ビジネスロジック（JAR）
│   ├── build.gradle             # domain-modelに依存
│   └── src/main/java/
│       └── com/example/service/
├── webapp/                      # Webアプリ（WAR）
│   ├── build.gradle             # business-logicに依存
│   └── src/
├── admin/                       # 管理画面（WAR）
│   ├── build.gradle             # business-logicに依存
│   └── src/
└── ear/                         # EARパッケージング
    └── build.gradle
```

### 1.2 依存関係グラフ

```
ear
 ├── webapp.war
 │   └── business-logic.jar
 │       └── domain-model.jar
 │           └── common-utils.jar
 ├── admin.war
 │   └── business-logic.jar (同じ)
 │       └── domain-model.jar (同じ)
 │           └── common-utils.jar (同じ)
 └── lib/
     ├── common-utils.jar        ← EAR共有
     ├── domain-model.jar        ← EAR共有
     ├── business-logic.jar      ← EAR共有
     ├── spring-context.jar      ← 外部ライブラリ
     └── ...
```

---

## 2. ear-libs集約プロジェクトパターン（推奨）

### 2.1 概要

EARで共有するライブラリを一つのプロジェクト(`ear-libs`)にまとめて管理するパターンです。
このアプローチにより、バージョン管理が一元化され、各モジュールでの依存関係宣言が簡潔になります。

### 2.2 プロジェクト構成

```
my-enterprise-app/
├── settings.gradle
├── build.gradle
├── ear-libs/                   # ★ EAR共有ライブラリ集約プロジェクト
│   └── build.gradle
├── common-utils/               # JARモジュール
│   └── build.gradle
├── domain-model/               # JARモジュール
│   └── build.gradle
├── business-logic/             # JARモジュール
│   └── build.gradle
├── webapp/                     # WARモジュール
│   └── build.gradle
├── admin/                      # WARモジュール
│   └── build.gradle
└── ear/                        # EARモジュール
    └── build.gradle
```

### 2.3 settings.gradle

```gradle
rootProject.name = 'my-enterprise-app'

include 'ear-libs'           // ★ 追加
include 'common-utils'
include 'domain-model'
include 'business-logic'
include 'webapp'
include 'admin'
include 'ear'
```

### 2.4 ear-libs/build.gradle

```gradle
plugins {
    id 'java-library'  // ★ java-libraryプラグインを使用
}

dependencies {
    // ==========================================
    // EARで共有する全ての外部ライブラリ
    // ==========================================

    // Spring Framework
    api "org.springframework:spring-context:${rootProject.ext.springVersion}"
    api "org.springframework:spring-web:${rootProject.ext.springVersion}"
    api "org.springframework:spring-webmvc:${rootProject.ext.springVersion}"
    api "org.springframework:spring-jdbc:${rootProject.ext.springVersion}"
    api "org.springframework:spring-tx:${rootProject.ext.springVersion}"

    // Struts 2
    api "org.apache.struts:struts2-core:${rootProject.ext.strutsVersion}"
    api "org.apache.struts:struts2-spring-plugin:${rootProject.ext.strutsVersion}"

    // Jackson
    api "com.fasterxml.jackson.core:jackson-databind:${rootProject.ext.jacksonVersion}"

    // MyBatis
    api "org.mybatis:mybatis:${rootProject.ext.mybatisVersion}"
    api "org.mybatis:mybatis-spring:2.0.7"

    // ユーティリティ
    api 'org.apache.commons:commons-lang3:3.12.0'
    api 'com.google.guava:guava:31.1-jre'

    // Jakarta EE API
    api 'jakarta.persistence:jakarta.persistence-api:3.1.0'
    api 'jakarta.validation:jakarta.validation-api:3.0.2'

    // データベースドライバ
    api 'org.postgresql:postgresql:42.6.0'
}

// ==========================================
// ★ 重要: JARファイルは生成しない
// ==========================================
jar.enabled = false

// このプロジェクトは依存関係の集約のみを行い、
// 実際のJARファイルは生成しません
```

**重要ポイント**:
- `api` を使用: 全ての依存モジュールにライブラリを伝播させる
- `jar.enabled = false`: このプロジェクト自体はJARを生成しない（依存関係定義のみ）

### 2.5 JARモジュールでの使用方法

```gradle
// common-utils/build.gradle

plugins {
    id 'java-library'
}

dependencies {
    // ==========================================
    // ★ ear-libsプロジェクトへの依存
    // ==========================================
    // ✓ 正しい: api を使用
    api project(':ear-libs')

    // ❌ 間違い: compileOnly を使用
    // compileOnly project(':ear-libs')
    // → テスト実行時に依存ライブラリが見つからずエラーになる

    // ==========================================
    // common-utils固有のライブラリ（あれば）
    // ==========================================
    // これはcommon-utilsでのみ使用し、他のモジュールには公開しない
    implementation 'some-internal-library:1.0.0'
}

jar {
    archiveFileName = 'common-utils.jar'
}
```

```gradle
// domain-model/build.gradle

plugins {
    id 'java-library'
}

dependencies {
    // ==========================================
    // プロジェクト内依存
    // ==========================================
    api project(':common-utils')  // common-utilsとその依存をAPIとして公開
    api project(':ear-libs')      // EAR共有ライブラリへのアクセス

    // domain-model固有のライブラリ（あれば）
    implementation 'joda-time:joda-time:2.12.5'
}

jar {
    archiveFileName = 'domain-model.jar'
}
```

```gradle
// business-logic/build.gradle

plugins {
    id 'java-library'
}

dependencies {
    // ==========================================
    // プロジェクト内依存
    // ==========================================
    api project(':domain-model')  // domain-modelを経由してcommon-utils、ear-libsも利用可能

    // business-logic固有の追加ライブラリ（あれば）
    implementation 'some-business-lib:1.0.0'
}

jar {
    archiveFileName = 'business-logic.jar'
}
```

**なぜ `api` を使うのか？**

1. **テストの実行**: `compileOnly`を使うと、テスト実行時に依存ライブラリがクラスパスに含まれず、テストが失敗します
2. **推移的依存**: `api`を使うことで、依存モジュールも同じライブラリを利用できます
3. **物理的重複の回避**: 後述の`providedCompile`と`earlib`の組み合わせで実現します

### 2.6 WARモジュールでの使用方法

```gradle
// webapp/build.gradle

plugins {
    id 'war'
}

dependencies {
    // ==========================================
    // ★ プロジェクト内依存
    // ==========================================
    // ✓ 正しい: providedCompile を使用
    providedCompile project(':business-logic')
    providedCompile project(':ear-libs')

    // これにより:
    // - コンパイル時: 依存ライブラリにアクセス可能
    // - パッケージング時: WEB-INF/lib/に含めない（EARのlib/から提供される）

    // ==========================================
    // ★ webapp固有のライブラリ
    // ==========================================
    // webappでのみ使用するライブラリはimplementationで指定
    // → WEB-INF/lib/に配置される
    implementation 'javax.servlet:jstl:1.2'
    implementation 'commons-fileupload:commons-fileupload:1.5'

    // ==========================================
    // コンパイル時のみ
    // ==========================================
    compileOnly 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveFileName = 'webapp.war'
}
```

```gradle
// admin/build.gradle

plugins {
    id 'war'
}

dependencies {
    providedCompile project(':business-logic')
    providedCompile project(':ear-libs')

    // admin固有のライブラリ
    implementation 'org.apache.poi:poi:5.2.0'        // Excel出力
    implementation 'org.apache.poi:poi-ooxml:5.2.0'

    compileOnly 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveFileName = 'admin.war'
}
```

**なぜ `providedCompile` を使うのか？**

- WARファイルの`WEB-INF/lib/`に含めたくないライブラリに使用
- EARの`lib/`ディレクトリから提供されることを想定
- ファイルサイズの削減と、クラスローダーの競合回避

### 2.7 EARモジュールでの使用方法

```gradle
// ear/build.gradle

plugins {
    id 'ear'
}

dependencies {
    // ==========================================
    // WARモジュールのデプロイ
    // ==========================================
    deploy project(path: ':webapp', configuration: 'archives')
    deploy project(path: ':admin', configuration: 'archives')

    // ==========================================
    // ★ プロジェクト内JARモジュール
    // ==========================================
    earlib project(':common-utils')
    earlib project(':domain-model')
    earlib project(':business-logic')

    // ==========================================
    // ★ ear-libsの依存関係を自動登録
    // ==========================================
    // 方法1: afterEvaluateで自動的に登録（推奨）
}

// ==========================================
// ear-libsの全依存関係をearlibに自動追加
// ==========================================
afterEvaluate {
    project(':ear-libs').configurations.api.allDependencies.each { dep ->
        if (dep instanceof ExternalModuleDependency) {
            dependencies.add('earlib', "${dep.group}:${dep.name}:${dep.version}")
        }
    }
}

ear {
    archiveFileName = "${project.name}-${project.version}.ear"

    deploymentDescriptor {
        applicationName = 'My Enterprise Application'

        webModule('webapp.war', '/app')
        webModule('admin.war', '/admin')

        libraryDirectory = 'lib'
        initializeInOrder = true
    }
}

// ビルド順序の制御
tasks.named('ear') {
    dependsOn ':common-utils:jar'
    dependsOn ':domain-model:jar'
    dependsOn ':business-logic:jar'
    dependsOn ':webapp:war'
    dependsOn ':admin:war'
}
```

**`afterEvaluate`ブロックの説明**:
- `ear-libs`の`api`設定に含まれる全ての外部依存関係を自動的に`earlib`に追加
- ear-libsで管理するライブラリが増えても、EARのbuild.gradleを変更する必要がない
- メンテナンス性が大幅に向上

### 2.8 依存関係スコープ早見表

| モジュール種別 | ear-libsへの依存 | プロジェクト内JARへの依存 | 理由 |
|------------|----------------|-------------------|------|
| **JAR** (common-utils等) | `api project(':ear-libs')` | `api project(':other-jar')` | テスト実行に必要、推移的依存のため |
| **WAR** (webapp等) | `providedCompile project(':ear-libs')` | `providedCompile project(':jar-module')` | WEB-INF/lib/に含めない、EARが提供 |
| **EAR** | `afterEvaluate`で自動登録 | `earlib project(':jar-module')` | lib/ディレクトリに配置 |

### 2.8.1 依存関係の書き方まとめ

**基本原則**: 各モジュールは`ear-libs`に依存することで、共有ライブラリを利用できます。

#### JARモジュールの場合

```gradle
// 最小限の構成（推奨）
dependencies {
    api project(':ear-libs')  // これだけで全ての共有ライブラリが利用可能
}

// 他のJARモジュールに依存する場合
dependencies {
    api project(':common-utils')  // プロジェクト内JAR
    api project(':ear-libs')      // 共有ライブラリ（明示的に書くことを推奨）
}

// 推移的依存を活用する場合
dependencies {
    // domain-modelを通じて、common-utilsとear-libsも利用可能
    api project(':domain-model')

    // 明示的にear-libsを書く必要はないが、わかりやすさのため書いても良い
    // api project(':ear-libs')  // オプション
}
```

#### WARモジュールの場合

```gradle
dependencies {
    // ★重要: WARでは providedCompile を使う
    providedCompile project(':business-logic')  // プロジェクト内JAR
    providedCompile project(':ear-libs')        // 共有ライブラリ

    // WAR固有のライブラリのみ implementation
    implementation 'javax.servlet:jstl:1.2'
    implementation 'commons-fileupload:commons-fileupload:1.5'
}
```

**なぜJARとWARで違うのか？**

1. **JARモジュール**:
   - `api`を使う理由: テスト実行時にクラスパスに含める必要がある
   - JARファイル自体にはライブラリを含めない（Gradleはこれを自動処理）

2. **WARモジュール**:
   - `providedCompile`を使う理由: `WEB-INF/lib/`に含めないため
   - コンパイル時は利用できるが、パッケージング時は除外される
   - 実行時はEARの`lib/`から提供されることを想定

### 2.9 メリット

1. **一元管理**: 全ての共有ライブラリのバージョンを一箇所で管理
2. **記述の簡潔化**: 各モジュールは`project(':ear-libs')`を参照するだけ
3. **重複排除の確実性**: `providedCompile` + `earlib`の組み合わせで自動的に重複を回避
4. **メンテナンス性**: ライブラリの追加・変更がear-libsのみで完結
5. **テスト実行の安定性**: JARモジュールで`api`を使うため、テストが正常に実行される

### 2.10 注意点

**❌ よくある間違い**:

```gradle
// JARモジュールでcompileOnlyを使う（間違い）
dependencies {
    compileOnly project(':ear-libs')  // ❌ テストが失敗する
}
```

```bash
# テスト実行時のエラー例
> Task :common-utils:test FAILED

java.lang.ClassNotFoundException: org.springframework.context.ApplicationContext
```

**✓ 正しい方法**:

```gradle
// JARモジュールではapiを使う
dependencies {
    api project(':ear-libs')  // ✓ テストも正常に実行される
}
```

---

## 3. ライブラリ重複排除の完全ガイド

### 3.1 settings.gradle

```gradle
rootProject.name = 'my-enterprise-app'

// モジュールの定義
include 'common-utils'
include 'domain-model'
include 'business-logic'
include 'webapp'
include 'admin'
include 'ear'
```

### 3.2 ルート build.gradle

```gradle
// ==========================================
// 共通設定
// ==========================================
buildscript {
    repositories {
        mavenCentral()
    }
}

plugins {
    id 'java' apply false
    id 'war' apply false
    id 'ear' apply false
}

// ==========================================
// バージョン一元管理（重要！）
// ==========================================
ext {
    // 外部ライブラリバージョン
    springVersion = '5.3.27'
    strutsVersion = '2.5.30'
    mybatisVersion = '3.5.13'
    jacksonVersion = '2.15.0'
    lombokVersion = '1.18.26'
    slf4jVersion = '1.7.36'
    logbackVersion = '1.2.12'

    // プロジェクトバージョン
    projectVersion = '1.0.0-SNAPSHOT'
}

// ==========================================
// 全プロジェクト共通設定
// ==========================================
allprojects {
    group = 'com.example'
    version = rootProject.ext.projectVersion

    repositories {
        mavenCentral()
        mavenLocal()
    }
}

// ==========================================
// サブプロジェクト共通設定
// ==========================================
subprojects {
    apply plugin: 'java'

    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11

    // ==========================================
    // 依存関係の除外設定（グローバル）
    // ==========================================
    configurations.all {
        // 古いロギングライブラリを除外
        exclude group: 'commons-logging', module: 'commons-logging'
        exclude group: 'log4j', module: 'log4j'
        exclude group: 'org.slf4j', module: 'slf4j-log4j12'

        // 重複するServlet APIを除外
        exclude group: 'javax.servlet', module: 'servlet-api'
    }

    // ==========================================
    // 依存関係解決戦略
    // ==========================================
    configurations.all {
        resolutionStrategy {
            // バージョン競合時は最新を選択
            failOnVersionConflict()  // または preferProjectModules()

            // 強制的にバージョンを統一
            force "org.springframework:spring-context:${rootProject.ext.springVersion}"
            force "org.springframework:spring-web:${rootProject.ext.springVersion}"
            force "org.springframework:spring-jdbc:${rootProject.ext.springVersion}"
            force "com.fasterxml.jackson.core:jackson-databind:${rootProject.ext.jacksonVersion}"
        }
    }

    // ==========================================
    // 共通依存関係
    // ==========================================
    dependencies {
        // ロギング（全モジュール共通）
        implementation "org.slf4j:slf4j-api:${rootProject.ext.slf4jVersion}"

        // Lombok（コンパイル時のみ）
        compileOnly "org.projectlombok:lombok:${rootProject.ext.lombokVersion}"
        annotationProcessor "org.projectlombok:lombok:${rootProject.ext.lombokVersion}"

        // テスト
        testImplementation 'org.junit.jupiter:junit-jupiter:5.9.3'
        testImplementation 'org.mockito:mockito-core:5.2.0'
    }
}
```

---

## 4. 各モジュールのビルド設定

### 4.1 common-utils/build.gradle

```gradle
plugins {
    id 'java-library'  // API依存関係を公開するためにjava-libraryを使用
}

dependencies {
    // このモジュールが公開するAPI（他モジュールから利用可能）
    api 'org.apache.commons:commons-lang3:3.12.0'
    api 'com.google.guava:guava:31.1-jre'

    // このモジュール内部でのみ使用
    implementation "ch.qos.logback:logback-classic:${rootProject.ext.logbackVersion}"
}

// JARファイル設定
jar {
    archiveFileName = 'common-utils.jar'

    manifest {
        attributes(
            'Implementation-Title': 'Common Utilities',
            'Implementation-Version': version
        )
    }
}
```

**重要ポイント**:
- `api`: 他モジュールにも公開される依存関係
- `implementation`: このモジュール内部でのみ使用

### 4.2 domain-model/build.gradle

```gradle
plugins {
    id 'java-library'
}

dependencies {
    // ==========================================
    // プロジェクト内依存（重要！）
    // ==========================================
    // common-utilsに依存
    api project(':common-utils')  // domain-modelのAPIとして公開

    // ==========================================
    // 外部ライブラリ
    // ==========================================
    // JPA（ドメインモデルで使用）
    api 'jakarta.persistence:jakarta.persistence-api:3.1.0'

    // バリデーション
    api 'jakarta.validation:jakarta.validation-api:3.0.2'

    // 日付処理
    implementation 'joda-time:joda-time:2.12.5'
}

jar {
    archiveFileName = 'domain-model.jar'
}
```

### 4.3 business-logic/build.gradle

```gradle
plugins {
    id 'java-library'
}

dependencies {
    // ==========================================
    // プロジェクト内依存
    // ==========================================
    api project(':domain-model')  // domain-modelを経由してcommon-utilsも利用可能

    // ==========================================
    // 外部ライブラリ
    // ==========================================
    // Spring Framework
    api "org.springframework:spring-context:${rootProject.ext.springVersion}"
    api "org.springframework:spring-jdbc:${rootProject.ext.springVersion}"
    api "org.springframework:spring-tx:${rootProject.ext.springVersion}"

    // MyBatis
    implementation "org.mybatis:mybatis:${rootProject.ext.mybatisVersion}"
    implementation "org.mybatis:mybatis-spring:2.0.7"

    // データベースドライバ（実行時のみ）
    runtimeOnly 'org.postgresql:postgresql:42.6.0'
}

jar {
    archiveFileName = 'business-logic.jar'
}
```

### 4.4 webapp/build.gradle

```gradle
plugins {
    id 'war'
}

dependencies {
    // ==========================================
    // プロジェクト内依存
    // ==========================================
    // ★重要: EARのlibに配置するため、providedCompile を使用
    providedCompile project(':business-logic')

    // ==========================================
    // 外部ライブラリ（EAR共有）
    // ==========================================
    // Spring Web（EARのlibに配置）
    providedCompile "org.springframework:spring-web:${rootProject.ext.springVersion}"
    providedCompile "org.springframework:spring-webmvc:${rootProject.ext.springVersion}"

    // Struts 2（EARのlibに配置）
    providedCompile "org.apache.struts:struts2-core:${rootProject.ext.strutsVersion}"
    providedCompile "org.apache.struts:struts2-spring-plugin:${rootProject.ext.strutsVersion}"

    // ==========================================
    // WAR固有のライブラリ（WEB-INF/libに配置）
    // ==========================================
    // JSPタグライブラリ（webappでのみ使用）
    implementation 'javax.servlet:jstl:1.2'

    // ファイルアップロード（webappでのみ使用）
    implementation 'commons-fileupload:commons-fileupload:1.5'

    // ==========================================
    // コンパイル時のみ
    // ==========================================
    compileOnly 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveFileName = 'webapp.war'
}
```

**重要**:
- `providedCompile`: EARのlibに配置されるため、WARには含めない
- `implementation`: WAR固有のライブラリのみ

### 4.5 admin/build.gradle

```gradle
plugins {
    id 'war'
}

dependencies {
    // webappと同じ構成
    providedCompile project(':business-logic')

    providedCompile "org.springframework:spring-web:${rootProject.ext.springVersion}"
    providedCompile "org.springframework:spring-webmvc:${rootProject.ext.springVersion}"
    providedCompile "org.apache.struts:struts2-core:${rootProject.ext.strutsVersion}"

    // admin固有のライブラリ
    implementation 'org.apache.poi:poi:5.2.0'  // Excel出力（adminのみ）
    implementation 'org.apache.poi:poi-ooxml:5.2.0'

    compileOnly 'javax.servlet:javax.servlet-api:4.0.1'
}

war {
    archiveFileName = 'admin.war'
}
```

---

## 5. EARビルド設定（重要）

### 5.1 ear/build.gradle

```gradle
plugins {
    id 'ear'
}

dependencies {
    // ==========================================
    // WARモジュールのデプロイ
    // ==========================================
    deploy project(path: ':webapp', configuration: 'archives')
    deploy project(path: ':admin', configuration: 'archives')

    // ==========================================
    // EAR共有ライブラリ（lib/に配置）
    // ==========================================

    // ★プロジェクト内モジュール
    earlib project(':common-utils')
    earlib project(':domain-model')
    earlib project(':business-logic')

    // ★外部ライブラリ（バージョン統一）
    // Spring Framework
    earlib "org.springframework:spring-context:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-web:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-webmvc:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-jdbc:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-tx:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-aop:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-beans:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-core:${rootProject.ext.springVersion}"
    earlib "org.springframework:spring-expression:${rootProject.ext.springVersion}"

    // Struts 2
    earlib "org.apache.struts:struts2-core:${rootProject.ext.strutsVersion}"
    earlib "org.apache.struts:struts2-spring-plugin:${rootProject.ext.strutsVersion}"

    // Jackson（JSON処理）
    earlib "com.fasterxml.jackson.core:jackson-databind:${rootProject.ext.jacksonVersion}"
    earlib "com.fasterxml.jackson.core:jackson-core:${rootProject.ext.jacksonVersion}"
    earlib "com.fasterxml.jackson.core:jackson-annotations:${rootProject.ext.jacksonVersion}"

    // MyBatis
    earlib "org.mybatis:mybatis:${rootProject.ext.mybatisVersion}"
    earlib "org.mybatis:mybatis-spring:2.0.7"

    // ロギング
    earlib "org.slf4j:slf4j-api:${rootProject.ext.slf4jVersion}"
    earlib "ch.qos.logback:logback-classic:${rootProject.ext.logbackVersion}"
    earlib "ch.qos.logback:logback-core:${rootProject.ext.logbackVersion}"

    // ユーティリティ
    earlib 'org.apache.commons:commons-lang3:3.12.0'
    earlib 'com.google.guava:guava:31.1-jre'

    // Jakarta EE API
    earlib 'jakarta.persistence:jakarta.persistence-api:3.1.0'
    earlib 'jakarta.validation:jakarta.validation-api:3.0.2'

    // データベースドライバ
    earlib 'org.postgresql:postgresql:42.6.0'
}

ear {
    archiveFileName = "${project.name}-${project.version}.ear"

    deploymentDescriptor {
        applicationName = 'My Enterprise Application'

        // Webモジュールの登録
        webModule('webapp.war', '/app')
        webModule('admin.war', '/admin')

        // 共有ライブラリディレクトリ
        libraryDirectory = 'lib'

        // 初期化順序
        initializeInOrder = true
    }

    // weblogic-application.xmlをコピー
    metaInf {
        from 'src/main/application/META-INF'
    }
}

// ==========================================
// ビルド順序の制御（重要！）
// ==========================================
tasks.named('ear') {
    // EARビルド前に各モジュールをビルド
    dependsOn ':common-utils:jar'
    dependsOn ':domain-model:jar'
    dependsOn ':business-logic:jar'
    dependsOn ':webapp:war'
    dependsOn ':admin:war'
}
```

---

## 6. ビルド順序の明示的制御

### 6.1 dependsOnによる順序制御

```gradle
// ear/build.gradle

// ==========================================
// 方法1: dependsOnで明示的に指定
// ==========================================
tasks.named('ear') {
    dependsOn ':common-utils:jar'
    dependsOn ':domain-model:jar'
    dependsOn ':business-logic:jar'
    dependsOn ':webapp:war'
    dependsOn ':admin:war'
}

// ==========================================
// 方法2: mustRunAfterで順序を強制
// ==========================================
project(':domain-model') {
    tasks.named('jar') {
        mustRunAfter ':common-utils:jar'
    }
}

project(':business-logic') {
    tasks.named('jar') {
        mustRunAfter ':domain-model:jar'
    }
}

project(':webapp') {
    tasks.named('war') {
        mustRunAfter ':business-logic:jar'
    }
}

// ==========================================
// 方法3: shouldRunAfterで推奨順序を設定
// ==========================================
tasks.named('ear') {
    shouldRunAfter subprojects.collect { it.tasks.withType(Jar) }
    shouldRunAfter subprojects.collect { it.tasks.withType(War) }
}
```

### 6.2 ビルド順序の可視化

```bash
# ビルド順序を確認（Dry Run）
./gradlew :ear:ear --dry-run

# 実行される順序:
# :common-utils:compileJava
# :common-utils:processResources
# :common-utils:classes
# :common-utils:jar
# :domain-model:compileJava
# :domain-model:processResources
# :domain-model:classes
# :domain-model:jar
# :business-logic:compileJava
# :business-logic:processResources
# :business-logic:classes
# :business-logic:jar
# :webapp:compileJava
# :webapp:processResources
# :webapp:classes
# :webapp:war
# :admin:compileJava
# :admin:processResources
# :admin:classes
# :admin:war
# :ear:ear
```

---

## 7. ライブラリ重複の検出と排除

### 7.1 重複検出タスク

```gradle
// ルート build.gradle

// ==========================================
// カスタムタスク: 重複ライブラリ検出
// ==========================================
tasks.register('detectDuplicateDependencies') {
    group = 'verification'
    description = 'Detect duplicate dependencies across modules'

    doLast {
        def earLibs = project(':ear').configurations.earlib.resolvedConfiguration.resolvedArtifacts
        def webappLibs = project(':webapp').configurations.runtimeClasspath.resolvedConfiguration.resolvedArtifacts
        def adminLibs = project(':admin').configurations.runtimeClasspath.resolvedConfiguration.resolvedArtifacts

        println "\n========================================="
        println "EAR lib/ ライブラリ:"
        println "========================================="
        earLibs.each { artifact ->
            println "  ${artifact.moduleVersion.id}"
        }

        println "\n========================================="
        println "webapp WEB-INF/lib/ ライブラリ:"
        println "========================================="
        def webappOnlyLibs = webappLibs.findAll { webappArtifact ->
            !earLibs.any { earArtifact ->
                earArtifact.moduleVersion.id.module == webappArtifact.moduleVersion.id.module
            }
        }
        webappOnlyLibs.each { artifact ->
            println "  ${artifact.moduleVersion.id}"
        }

        println "\n========================================="
        println "admin WEB-INF/lib/ ライブラリ:"
        println "========================================="
        def adminOnlyLibs = adminLibs.findAll { adminArtifact ->
            !earLibs.any { earArtifact ->
                earArtifact.moduleVersion.id.module == adminArtifact.moduleVersion.id.module
            }
        }
        adminOnlyLibs.each { artifact ->
            println "  ${artifact.moduleVersion.id}"
        }

        // 重複チェック
        println "\n========================================="
        println "⚠ 重複の可能性:"
        println "========================================="
        def duplicates = webappLibs.findAll { webappArtifact ->
            earLibs.any { earArtifact ->
                earArtifact.moduleVersion.id.module == webappArtifact.moduleVersion.id.module
            }
        }

        if (duplicates.isEmpty()) {
            println "  ✓ 重複なし"
        } else {
            duplicates.each { artifact ->
                println "  ❌ ${artifact.moduleVersion.id} がWARとEARの両方に含まれています"
            }
            throw new GradleException("重複ライブラリが検出されました")
        }
    }
}

// EARビルド前に重複チェックを実行
project(':ear') {
    tasks.named('ear') {
        dependsOn rootProject.tasks.named('detectDuplicateDependencies')
    }
}
```

実行:
```bash
./gradlew detectDuplicateDependencies
```

### 7.2 依存関係ツリーの確認

```bash
# EARの依存関係ツリー
./gradlew :ear:dependencies --configuration earlib

# webappの依存関係ツリー
./gradlew :webapp:dependencies --configuration runtimeClasspath

# 特定ライブラリの依存経路を追跡
./gradlew :webapp:dependencyInsight --dependency spring-core --configuration runtimeClasspath
```

---

## 8. 実践例: 完全な設定

### 8.1 完全なディレクトリ構造

```
my-enterprise-app/
├── settings.gradle
├── build.gradle
├── gradle.properties
├── common-utils/
│   ├── build.gradle
│   └── src/main/java/com/example/utils/
│       ├── StringUtil.java
│       └── DateUtil.java
├── domain-model/
│   ├── build.gradle
│   └── src/main/java/com/example/model/
│       ├── User.java
│       └── Order.java
├── business-logic/
│   ├── build.gradle
│   └── src/main/java/com/example/service/
│       ├── UserService.java
│       └── OrderService.java
├── webapp/
│   ├── build.gradle
│   └── src/
│       ├── main/
│       │   ├── java/com/example/web/
│       │   │   └── UserAction.java
│       │   └── webapp/
│       │       ├── WEB-INF/
│       │       │   ├── web.xml
│       │       │   └── struts.xml
│       │       └── index.jsp
│       └── test/
├── admin/
│   ├── build.gradle
│   └── src/
└── ear/
    ├── build.gradle
    └── src/main/application/META-INF/
        ├── application.xml
        └── weblogic-application.xml
```

### 8.2 ビルド実行

```bash
# 1. 全モジュールのビルド
./gradlew clean build

# 2. EARファイルの作成
./gradlew :ear:ear

# 3. 成果物の確認
ls -lh ear/build/libs/
# => my-enterprise-app-1.0.0-SNAPSHOT.ear

# 4. EARの内容確認
unzip -l ear/build/libs/my-enterprise-app-1.0.0-SNAPSHOT.ear

# 5. 重複チェック
./gradlew detectDuplicateDependencies
```

### 8.3 EARの内容（期待される構造）

```
my-enterprise-app-1.0.0-SNAPSHOT.ear
├── META-INF/
│   ├── MANIFEST.MF
│   ├── application.xml
│   └── weblogic-application.xml
├── webapp.war
├── admin.war
└── lib/
    ├── common-utils-1.0.0-SNAPSHOT.jar       ← プロジェクトJAR
    ├── domain-model-1.0.0-SNAPSHOT.jar       ← プロジェクトJAR
    ├── business-logic-1.0.0-SNAPSHOT.jar     ← プロジェクトJAR
    ├── spring-context-5.3.27.jar             ← 外部ライブラリ
    ├── spring-web-5.3.27.jar
    ├── spring-webmvc-5.3.27.jar
    ├── spring-jdbc-5.3.27.jar
    ├── struts2-core-2.5.30.jar
    ├── jackson-databind-2.15.0.jar
    ├── mybatis-3.5.13.jar
    ├── slf4j-api-1.7.36.jar
    ├── logback-classic-1.2.12.jar
    ├── commons-lang3-3.12.0.jar
    ├── guava-31.1-jre.jar
    └── postgresql-42.6.0.jar
```

### 8.4 WARの内容（期待される構造）

```bash
unzip -l ear/build/libs/my-enterprise-app-1.0.0-SNAPSHOT.ear webapp.war
```

```
webapp.war
├── META-INF/
│   └── MANIFEST.MF
├── WEB-INF/
│   ├── web.xml
│   ├── struts.xml
│   ├── classes/
│   │   └── com/example/web/
│   │       └── UserAction.class
│   └── lib/
│       ├── jstl-1.2.jar              ← webapp固有のライブラリのみ
│       └── commons-fileupload-1.5.jar
└── index.jsp

# ✓ Spring、Struts、business-logic.jarなどはWEB-INF/libに含まれていない
# → すべてEARのlib/から読み込まれる
```

---

## 9. トラブルシューティング

### 9.1 問題: ライブラリが重複している

**症状**:
```
EAR: 150MB（期待: 80MB）
webapp.war/WEB-INF/lib/に spring-context-5.3.27.jar
EAR/lib/にも spring-context-5.3.27.jar
```

**診断**:
```bash
# WARの内容確認
unzip -l build/libs/my-app.ear webapp.war | grep spring-context

# 出力:
# WEB-INF/lib/spring-context-5.3.27.jar  ← 重複！
```

**解決策**:
```gradle
// webapp/build.gradle

dependencies {
    // ❌ 間違い
    // implementation "org.springframework:spring-context:${rootProject.ext.springVersion}"

    // ✓ 正しい
    providedCompile "org.springframework:spring-context:${rootProject.ext.springVersion}"
}
```

### 9.2 問題: ビルド順序が正しくない

**症状**:
```
> Task :business-logic:compileJava FAILED
error: cannot find symbol
  symbol: class User
  location: package com.example.model
```

**原因**: `domain-model`が先にビルドされていない

**解決策**:
```gradle
// business-logic/build.gradle

// dependenciesで依存を宣言すれば自動的にビルド順序が決まる
dependencies {
    api project(':domain-model')  // ← これで自動的にdomain-modelが先にビルドされる
}

// または明示的に
tasks.named('compileJava') {
    dependsOn ':domain-model:jar'
}
```

### 9.3 問題: バージョン競合

**症状**:
```
> Could not resolve all dependencies for configuration ':webapp:runtimeClasspath'.
   > Conflict found for the following module:
       - org.springframework:spring-core between versions 5.3.27 and 6.0.0
```

**診断**:
```bash
./gradlew :webapp:dependencies --configuration runtimeClasspath | grep spring-core
```

**解決策**:
```gradle
// ルート build.gradle

subprojects {
    configurations.all {
        resolutionStrategy {
            // バージョンを強制
            force "org.springframework:spring-core:${rootProject.ext.springVersion}"
        }
    }
}
```

### 9.4 問題: ClassNotFoundException（実行時）

**症状**:
```
java.lang.ClassNotFoundException: com.example.utils.StringUtil
```

**原因**: `common-utils.jar`がEARのlib/に含まれていない

**診断**:
```bash
unzip -l build/libs/my-app.ear | grep common-utils
# 何も表示されない → 含まれていない！
```

**解決策**:
```gradle
// ear/build.gradle

dependencies {
    // ✓ 追加
    earlib project(':common-utils')
}
```

---

## 10. ベストプラクティス

### 10.1 バージョン管理

```gradle
// gradle.properties（推奨）
springVersion=5.3.27
strutsVersion=2.5.30
mybatisVersion=3.5.13

// または build.gradle
ext {
    versions = [
        spring: '5.3.27',
        struts: '2.5.30'
    ]
}
```

### 10.2 依存スコープの使い分け

| スコープ | 用途 | 例 |
|---------|------|---|
| `api` | 他モジュールに公開 | プロジェクト内JARの依存関係 |
| `implementation` | 内部使用のみ | 実装詳細のライブラリ |
| `providedCompile` | 実行環境が提供 | EARのlib/に配置されるライブラリ |
| `compileOnly` | コンパイル時のみ | Servlet API、Lombok |
| `runtimeOnly` | 実行時のみ | JDBCドライバ |

### 10.3 プロジェクト間依存の原則

```gradle
// ✓ 推奨: APIとして公開
api project(':domain-model')

// ✓ 推奨: 内部使用のみ
implementation project(':internal-utils')

// ❌ 非推奨: プロジェクト間でcompileOnlyは使わない
compileOnly project(':domain-model')  // 実行時にエラー
```

---

## 11. まとめ

### 11.1 ライブラリ重複排除のチェックリスト

- [ ] ルートbuild.gradleでバージョンを一元管理
- [ ] WARモジュールでは共有ライブラリに`providedCompile`を使用
- [ ] EARビルドで全ての共有ライブラリを`earlib`に指定
- [ ] `detectDuplicateDependencies`タスクで重複を検出
- [ ] EARとWARの内容を`unzip -l`で確認
- [ ] ビルド後のファイルサイズが妥当か確認

### 11.2 ビルド順序制御のチェックリスト

- [ ] プロジェクト間依存を`dependencies`で宣言
- [ ] 必要に応じて`dependsOn`で明示的に指定
- [ ] `--dry-run`でビルド順序を確認
- [ ] 並列ビルド時も順序が保たれることを確認

### 11.3 推奨ビルドコマンド

```bash
# 開発時
./gradlew :ear:ear --build-cache --parallel

# 本番ビルド
./gradlew clean build :ear:ear -Penv=production

# 重複チェック付き
./gradlew detectDuplicateDependencies :ear:ear
```

---

## 12. 参考資料

- [Gradle Multi-Project Builds](https://docs.gradle.org/current/userguide/multi_project_builds.html)
- [Gradle Dependency Management](https://docs.gradle.org/current/userguide/dependency_management.html)
- [Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html)

---

## 13. 次のステップ

- [[gradle-advanced-build.md]] - Gradle高度なビルドスクリプト
- [[java-build-artifacts.md]] - JavaビルドアーティファクトとEAR
- [[weblogic-development-workflow.md]] - WebLogic開発ワークフロー
