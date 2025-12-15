# Javaビルド成果物学習ノート

> 対象: JAR, WAR, EAR
> 環境: Java, Gradle

## 学習目標

- Javaのビルド概念とアーカイブ形式の違いを理解する
- JAR、WAR、EARの用途と構造を把握する
- Gradleでマルチモジュールプロジェクトをビルドする方法を習得する
- EARファイル作成時の注意点とベストプラクティスを学ぶ

---

## 1. ビルドの概念

### 1.1 Javaにおけるビルドとは

ビルドとは、ソースコード（.javaファイル）から実行可能な形式（.classファイルやアーカイブ）に変換する一連のプロセスです。

#### ビルドプロセスの流れ

```
ソースコード (.java)
    ↓ コンパイル
バイトコード (.class)
    ↓ リソース統合
ライブラリ追加
    ↓ パッケージング
成果物 (JAR/WAR/EAR)
    ↓ デプロイ
実行環境
```

#### ビルドツールが行うこと

1. **コンパイル**: `.java` → `.class`
2. **依存性解決**: 必要なライブラリをダウンロード
3. **リソース処理**: プロパティファイル、設定ファイルをコピー
4. **テスト実行**: ユニットテスト、統合テスト
5. **パッケージング**: JAR/WAR/EARファイルの作成
6. **デプロイ準備**: アーティファクトリポジトリへのアップロード

---

## 2. JAR (Java ARchive)

### 2.1 概要

JAR（ジャー）は、Javaクラスファイルとメタデータをまとめた**ZIPベースのアーカイブ形式**です。

### 2.2 用途

- **ライブラリの配布**: 再利用可能なコードをパッケージング
- **スタンドアロンアプリケーション**: 実行可能JAR（Executable JAR）
- **WARやEARの構成要素**: 他のアーカイブに含まれるモジュール

### 2.3 構造

```
my-library.jar
├── META-INF/
│   └── MANIFEST.MF         # マニフェストファイル（メタデータ）
├── com/
│   └── example/
│       ├── App.class
│       └── util/
│           └── Helper.class
└── application.properties  # リソースファイル
```

### 2.4 実行可能JAR

```
# MANIFEST.MFの内容
Manifest-Version: 1.0
Main-Class: com.example.App
Class-Path: lib/dependency1.jar lib/dependency2.jar
```

実行方法:
```bash
java -jar my-app.jar
```

### 2.5 Gradleでのビルド

```gradle
plugins {
    id 'java'
}

jar {
    manifest {
        attributes(
            'Main-Class': 'com.example.App',
            'Implementation-Version': project.version
        )
    }
}

// Fat JAR（依存関係を含む）の作成
tasks.register('fatJar', Jar) {
    archiveClassifier = 'all'
    from {
        configurations.runtimeClasspath.collect {
            it.isDirectory() ? it : zipTree(it)
        }
    }
    with jar
}
```

---

## 3. WAR (Web Application Archive)

### 3.1 概要

WAR（ワー）は、**Webアプリケーション用のアーカイブ形式**で、サーブレットコンテナ（TomcatやJettyなど）にデプロイします。

### 3.2 用途

- サーブレット、JSP、HTMLなどのWebコンテンツの配布
- Spring MVC、JSF、StrutsなどのWebフレームワークアプリ

### 3.3 構造

```
my-webapp.war
├── META-INF/
│   └── MANIFEST.MF
├── WEB-INF/
│   ├── web.xml              # デプロイメント記述子（Servlet 3.0以降は省略可）
│   ├── classes/             # コンパイル済みクラス
│   │   └── com/
│   │       └── example/
│   │           └── servlet/
│   │               └── HelloServlet.class
│   ├── lib/                 # 依存JARファイル
│   │   ├── spring-core.jar
│   │   └── jackson-databind.jar
│   └── views/               # テンプレートファイル（任意）
│       └── index.jsp
├── static/                  # 静的リソース（直接アクセス可能）
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│       └── logo.png
└── index.html
```

#### WEB-INFの重要性

- `WEB-INF/` ディレクトリ内はクライアントから直接アクセス**不可**（セキュリティ保護）
- `WEB-INF/classes/`: アプリケーションのクラスファイル
- `WEB-INF/lib/`: 依存ライブラリのJAR

### 3.4 Gradleでのビルド

```gradle
plugins {
    id 'war'
}

war {
    archiveFileName = 'my-webapp.war'

    // カスタムマニフェスト
    manifest {
        attributes(
            'Implementation-Title': 'My Web Application',
            'Implementation-Version': project.version
        )
    }
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'  // コンテナが提供
}
```

### 3.5 デプロイ方法

```bash
# Tomcatへのデプロイ
cp my-webapp.war $CATALINA_HOME/webapps/

# または自動デプロイディレクトリへコピー
# サーバー再起動で自動展開される
```

---

## 4. EAR (Enterprise Archive)

### 4.1 概要

EAR（イアー）は、**エンタープライズアプリケーション用のアーカイブ形式**で、複数のモジュール（WAR、JAR、EJB-JAR）を一つにまとめます。

### 4.2 用途

- Java EE（Jakarta EE）の完全なエンタープライズアプリケーション
- 複数のWebアプリケーションとEJBを統合
- WildFly、WebLogic、WebSphereなどのアプリケーションサーバーにデプロイ

### 4.3 構造

```
my-enterprise-app.ear
├── META-INF/
│   ├── MANIFEST.MF
│   └── application.xml      # EARデプロイメント記述子
├── my-webapp.war            # Webモジュール
├── my-api.war               # 別のWebモジュール
├── my-ejb.jar               # EJBモジュール
└── lib/                     # 共有ライブラリ
    ├── commons-lang3.jar
    └── my-shared-lib.jar
```

### 4.4 application.xml の例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<application xmlns="http://xmlns.jcp.org/xml/ns/javaee"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
                                 http://xmlns.jcp.org/xml/ns/javaee/application_8.xsd"
             version="8">

    <display-name>My Enterprise Application</display-name>

    <!-- Webモジュール -->
    <module>
        <web>
            <web-uri>my-webapp.war</web-uri>
            <context-root>/app</context-root>
        </web>
    </module>

    <!-- EJBモジュール -->
    <module>
        <ejb>my-ejb.jar</ejb>
    </module>

    <!-- 共有ライブラリディレクトリ -->
    <library-directory>lib</library-directory>
</application>
```

### 4.5 JAR vs WAR vs EAR の比較

| 項目 | JAR | WAR | EAR |
|------|-----|-----|-----|
| **対象** | ライブラリ/アプリ | Webアプリ | エンタープライズアプリ |
| **実行環境** | JVM | サーブレットコンテナ | Java EEサーバー |
| **含まれるもの** | クラス、リソース | Servlet、JSP、HTML、JAR | WAR、JAR、EJB-JAR |
| **デプロイ先例** | - | Tomcat, Jetty | WildFly, WebLogic |
| **主な用途** | 再利用可能コード | Webサービス/UI | 大規模エンタープライズシステム |
| **実行方法** | `java -jar` | コンテナにデプロイ | アプリサーバーにデプロイ |

---

## 5. GradleでマルチモジュールプロジェクトをEARにビルド

### 5.1 プロジェクト構成例

```
my-enterprise-app/
├── settings.gradle
├── build.gradle
├── common/                  # 共通ライブラリ（JAR）
│   └── build.gradle
├── business-logic/          # ビジネスロジック（EJB-JAR）
│   └── build.gradle
├── web-app/                 # Webアプリケーション（WAR）
│   └── build.gradle
└── ear/                     # EARパッケージング
    └── build.gradle
```

### 5.2 settings.gradle

```gradle
rootProject.name = 'my-enterprise-app'

include 'common'
include 'business-logic'
include 'web-app'
include 'ear'
```

### 5.3 ルートの build.gradle

```gradle
plugins {
    id 'java' apply false
}

subprojects {
    group = 'com.example'
    version = '1.0.0-SNAPSHOT'

    repositories {
        mavenCentral()
    }
}
```

### 5.4 common/build.gradle（JAR）

```gradle
plugins {
    id 'java-library'
}

dependencies {
    api 'org.apache.commons:commons-lang3:3.12.0'
    implementation 'org.slf4j:slf4j-api:2.0.0'
}
```

### 5.5 business-logic/build.gradle（EJB-JAR）

```gradle
plugins {
    id 'java-library'
}

dependencies {
    api project(':common')
    implementation 'jakarta.ejb:jakarta.ejb-api:4.0.1'
    implementation 'jakarta.persistence:jakarta.persistence-api:3.1.0'
}
```

### 5.6 web-app/build.gradle（WAR）

```gradle
plugins {
    id 'war'
}

dependencies {
    implementation project(':common')
    implementation project(':business-logic')

    implementation 'jakarta.servlet:jakarta.servlet-api:6.0.0'
    implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'

    providedRuntime 'org.springframework.boot:spring-boot-starter-tomcat'
}

war {
    archiveFileName = 'my-webapp.war'
}
```

### 5.7 ear/build.gradle（EAR）

```gradle
plugins {
    id 'ear'
}

dependencies {
    // EARに含めるモジュール
    deploy project(path: ':web-app', configuration: 'archives')
    deploy project(path: ':business-logic', configuration: 'archives')

    // EAR全体で共有するライブラリ（lib/に配置）
    earlib project(':common')
    earlib 'org.slf4j:slf4j-api:2.0.0'
}

ear {
    archiveFileName = 'my-enterprise-app.ear'

    // application.xml の自動生成設定
    deploymentDescriptor {
        applicationName = 'My Enterprise Application'

        // Webモジュールの設定
        webModule('my-webapp.war', '/app')

        // ライブラリディレクトリ
        libraryDirectory = 'lib'
    }
}
```

---

## 6. EARファイル内のコンテキストパス管理

### 6.1 コンテキストパスとは

コンテキストパス（Context Root）は、Webアプリケーションにアクセスするための**URLのベースパス**です。

```
http://localhost:8080/app/index.html
                      ^^^^ コンテキストパス
```

### 6.2 コンテキストパスの設定方法

#### 方法1: application.xml で設定（EAR推奨）

```xml
<!-- META-INF/application.xml -->
<application>
    <module>
        <web>
            <web-uri>customer-web.war</web-uri>
            <context-root>/customers</context-root>  <!-- ここで設定 -->
        </web>
    </module>
    <module>
        <web>
            <web-uri>admin-web.war</web-uri>
            <context-root>/admin</context-root>
        </web>
    </module>
</application>
```

アクセスURL:
- `http://localhost:8080/customers/` → customer-web.war
- `http://localhost:8080/admin/` → admin-web.war

#### 方法2: Gradle EAR Plugin で設定

```gradle
// ear/build.gradle
ear {
    deploymentDescriptor {
        webModule('customer-web.war', '/customers')  // (WARファイル名, コンテキストパス)
        webModule('admin-web.war', '/admin')
    }
}
```

この設定により、自動的に `application.xml` が生成されます。

#### 方法3: jboss-web.xml でサーバー固有設定（WildFly/JBoss）

```xml
<!-- WARファイル内の WEB-INF/jboss-web.xml -->
<jboss-web>
    <context-root>/customers</context-root>
</jboss-web>
```

#### 方法4: weblogic.xml（WebLogic固有）

```xml
<!-- WARファイル内の WEB-INF/weblogic.xml -->
<weblogic-web-app>
    <context-root>/customers</context-root>
</weblogic-web-app>
```

### 6.3 設定の優先順位

アプリケーションサーバーによって異なりますが、一般的な優先順位:

```
1. サーバー管理コンソールでの設定（デプロイ時の明示的指定）
2. サーバー固有のデプロイメント記述子（jboss-web.xml, weblogic.xml）
3. EARの application.xml
4. WARファイル名（拡張子を除いた部分がデフォルト）
```

### 6.4 複数WARの管理戦略

#### パターン1: 機能別コンテキストパス

```gradle
ear {
    deploymentDescriptor {
        webModule('frontend-web.war', '/app')        // ユーザー向けUI
        webModule('admin-web.war', '/admin')         // 管理画面
        webModule('api-web.war', '/api')             // REST API
        webModule('health-web.war', '/health')       // ヘルスチェック
    }
}
```

アクセス例:
- `http://example.com/app/dashboard`
- `http://example.com/admin/users`
- `http://example.com/api/v1/products`
- `http://example.com/health/status`

#### パターン2: バージョニング付きAPI

```gradle
ear {
    deploymentDescriptor {
        webModule('api-v1.war', '/api/v1')
        webModule('api-v2.war', '/api/v2')
        webModule('web-ui.war', '/')              // ルートパス
    }
}
```

#### パターン3: テナント別（マルチテナント）

```gradle
ear {
    deploymentDescriptor {
        webModule('tenant-a-web.war', '/tenant-a')
        webModule('tenant-b-web.war', '/tenant-b')
        webModule('shared-resources.war', '/resources')
    }
}
```

### 6.5 ルートコンテキストパス（/）の扱い

#### ルートパスの設定

```gradle
ear {
    deploymentDescriptor {
        webModule('main-web.war', '/')  // http://example.com/ で直接アクセス
        webModule('api-web.war', '/api')
    }
}
```

#### 注意点

1. **ルートコンテキストは1つのみ**: 複数のWARをルート（`/`）に設定不可
2. **静的リソースの競合**: ルートWARが全てのリクエストをキャッチする可能性
3. **ウェルカムファイル**: `index.html` や `index.jsp` が自動的に処理される

```xml
<!-- web.xml -->
<welcome-file-list>
    <welcome-file>index.html</welcome-file>
    <welcome-file>index.jsp</welcome-file>
</welcome-file-list>
```

### 6.6 リバースプロキシとの連携

#### 構成例: Nginx + WildFly

```nginx
# nginx.conf
server {
    listen 80;
    server_name example.com;

    # フロントエンドアプリ
    location /app/ {
        proxy_pass http://wildfly:8080/app/;
    }

    # REST API
    location /api/ {
        proxy_pass http://wildfly:8080/api/;
    }

    # 管理画面は認証必須
    location /admin/ {
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://wildfly:8080/admin/;
    }
}
```

EAR設定との対応:
```gradle
ear {
    deploymentDescriptor {
        webModule('frontend.war', '/app')
        webModule('api.war', '/api')
        webModule('admin.war', '/admin')
    }
}
```

### 6.7 動的コンテキストパス（環境別）

#### プロファイル別のコンテキストパス設定

```gradle
// ear/build.gradle
def contextPaths = [
    dev: [
        frontend: '/dev/app',
        api: '/dev/api'
    ],
    staging: [
        frontend: '/staging/app',
        api: '/staging/api'
    ],
    production: [
        frontend: '/app',
        api: '/api'
    ]
]

def env = project.findProperty('env') ?: 'dev'
def paths = contextPaths[env]

ear {
    archiveFileName = "my-app-${env}.ear"

    deploymentDescriptor {
        webModule('frontend.war', paths.frontend)
        webModule('api.war', paths.api)
    }
}
```

ビルド時の指定:
```bash
# 開発環境
./gradlew :ear:ear -Penv=dev
# => /dev/app, /dev/api

# 本番環境
./gradlew :ear:ear -Penv=production
# => /app, /api
```

### 6.8 コンテキストパスに関するトラブルシューティング

#### 問題1: コンテキストパスが反映されない

**症状**:
```
期待: http://localhost:8080/myapp/
実際: http://localhost:8080/my-webapp/
```

**原因**: WARファイル名がデフォルトのコンテキストパスになっている

**解決策**:
```gradle
// application.xmlで明示的に指定
ear {
    deploymentDescriptor {
        webModule('my-webapp.war', '/myapp')  // 明示的指定
    }
}
```

または、WARファイル名を変更:
```gradle
// web-app/build.gradle
war {
    archiveFileName = 'myapp.war'  // コンテキストパスと一致させる
}
```

#### 問題2: 複数WARで同じコンテキストパスを設定

**症状**:
```
ERROR: Duplicate context-root '/app'
```

**解決策**: 各WARに一意のコンテキストパスを割り当てる
```gradle
ear {
    deploymentDescriptor {
        webModule('customer-app.war', '/customers')  // ✓
        webModule('order-app.war', '/orders')        // ✓
    }
}
```

#### 問題3: コンテキストパスとSpring Bootの衝突

**症状**: Spring Boot組み込みTomcatの `server.servlet.context-path` が無視される

**原因**: EARデプロイ時は application.xml の設定が優先

**解決策**: application.properties の設定を削除し、EAR側で管理
```properties
# application.properties（削除または無効化）
# server.servlet.context-path=/app  ← コメントアウト
```

```gradle
// ear/build.gradle で一元管理
ear {
    deploymentDescriptor {
        webModule('spring-boot-app.war', '/app')
    }
}
```

#### 問題4: リダイレクトループ

**症状**: `/app` → `/app/app` → `/app/app/app` のように無限リダイレクト

**原因**: アプリケーションコード内でコンテキストパスを考慮していない

**解決策**: `HttpServletRequest.getContextPath()` を使用
```java
@Controller
public class HomeController {

    @GetMapping("/")
    public String home(HttpServletRequest request) {
        String contextPath = request.getContextPath();  // "/app" を取得
        return "redirect:" + contextPath + "/dashboard";
    }
}
```

または、相対パスを使用:
```java
return "redirect:dashboard";  // コンテキストパス不要
```

### 6.9 ベストプラクティス

#### 1. コンテキストパスの命名規則

```gradle
// ✓ 推奨: 短く、わかりやすく、REST原則に従う
webModule('customer-web.war', '/customers')
webModule('order-web.war', '/orders')
webModule('api-v1.war', '/api/v1')

// ✗ 非推奨: 複雑、階層が深すぎる
webModule('web.war', '/enterprise/customer/management/web/v1')
```

#### 2. application.xml で一元管理

```gradle
// ✓ 推奨: EARで統一管理
ear {
    deploymentDescriptor {
        webModule('app.war', '/app')
    }
}

// ✗ 非推奨: WAR個別の jboss-web.xml に散在
// （サーバー移行時に問題が発生しやすい）
```

#### 3. 環境変数による外部化（上級）

```gradle
ear {
    deploymentDescriptor {
        def contextRoot = System.getenv('APP_CONTEXT_ROOT') ?: '/app'
        webModule('app.war', contextRoot)
    }
}
```

デプロイ時:
```bash
export APP_CONTEXT_ROOT=/production/app
./gradlew :ear:ear
```

#### 4. ドキュメント化

```gradle
// ear/build.gradle
ear {
    deploymentDescriptor {
        // Frontend: ユーザー向けWebアプリケーション
        // アクセスURL: http://example.com/app
        webModule('frontend-web.war', '/app')

        // REST API: バックエンドサービス
        // アクセスURL: http://example.com/api/v1
        webModule('api-v1.war', '/api/v1')

        // Admin Console: 管理者専用画面（IP制限推奨）
        // アクセスURL: http://example.com/admin
        webModule('admin-web.war', '/admin')
    }
}
```

---

## 7. EARビルド時の注意点

### 7.1 依存関係の管理

#### 問題: 重複した依存関係

複数のWARファイルに同じライブラリが含まれると、EARファイルが肥大化し、クラスローダーの競合が発生する可能性があります。

#### 解決策: earlib で共有ライブラリ化

```gradle
// ear/build.gradle
dependencies {
    // 各WARには含めず、EAR全体で共有
    earlib 'com.fasterxml.jackson.core:jackson-databind:2.15.0'
    earlib 'org.springframework:spring-context:6.0.0'
}
```

各モジュールでは `providedCompile` を使用:
```gradle
// web-app/build.gradle
dependencies {
    providedCompile 'com.fasterxml.jackson.core:jackson-databind:2.15.0'
}
```

### 7.2 クラスローダーの理解

Java EEサーバーのクラスローダー階層:

```
Bootstrap ClassLoader
    ↓
System ClassLoader
    ↓
Application Server ClassLoader
    ↓
EAR ClassLoader              ← lib/ 内のJARを読み込む
    ↓
WAR ClassLoader              ← WEB-INF/lib/ を読み込む
    ↓
EJB ClassLoader
```

#### 注意点

- **親優先（Parent-First）**: デフォルトでは親クラスローダーを優先
- **子優先（Child-First）**: サーバー設定で変更可能だが非推奨
- `earlib` で追加したライブラリは全モジュールからアクセス可能
- WARごとに異なるバージョンのライブラリを使う場合は、EARではなくWARに含める

### 7.3 application.xml vs JavaEE 6+のアノテーション

#### 従来の方法（application.xml）

```xml
<application>
    <module>
        <web>
            <web-uri>my-webapp.war</web-uri>
            <context-root>/app</context-root>
        </web>
    </module>
</application>
```

#### 現代的な方法（アノテーション）

JavaEE 6以降では `@WebServlet` などのアノテーションで `application.xml` を省略可能:

```gradle
ear {
    deploymentDescriptor {
        // 必要最小限の設定のみ
        libraryDirectory = 'lib'
    }
}
```

### 7.4 マルチモジュールビルドのベストプラクティス

#### 1. バージョン管理の統一

```gradle
// ルートの build.gradle
ext {
    springVersion = '6.0.0'
    jacksonVersion = '2.15.0'
}

subprojects {
    dependencies {
        constraints {
            implementation "org.springframework:spring-context:${rootProject.ext.springVersion}"
        }
    }
}
```

#### 2. プロジェクト依存の適切なスコープ

```gradle
// web-app/build.gradle
dependencies {
    implementation project(':common')              // コンパイル&実行
    compileOnly project(':business-logic')         // コンパイルのみ（EJB参照）
}
```

#### 3. ビルド順序の制御

```gradle
// ear/build.gradle
tasks.named('ear') {
    dependsOn ':web-app:war', ':business-logic:jar'
}
```

#### 4. プロファイル別ビルド

```gradle
// ear/build.gradle
ear {
    def env = project.findProperty('env') ?: 'dev'
    archiveFileName = "my-app-${env}.ear"

    from("src/main/resources/${env}") {
        into('META-INF')
    }
}
```

実行:
```bash
./gradlew :ear:ear -Penv=production
```

### 7.5 よくある問題とトラブルシューティング

#### 問題1: ClassNotFoundException

**原因**: 必要なJARがEARに含まれていない、またはクラスローダーの範囲外

**解決策**:
```bash
# EARの内容を確認
unzip -l build/libs/my-app.ear

# 必要なライブラリがlib/に含まれているか確認
```

```gradle
// 不足している場合は追加
dependencies {
    earlib 'missing:library:1.0'
}
```

#### 問題2: NoSuchMethodError（メソッドバージョン不一致）

**原因**: 同じライブラリの異なるバージョンが混在

**解決策**:
```bash
# 依存関係ツリーを確認
./gradlew :ear:dependencies

# 強制的にバージョンを統一
./gradlew :ear:dependencyInsight --dependency jackson-databind
```

```gradle
configurations.all {
    resolutionStrategy {
        force 'com.fasterxml.jackson.core:jackson-databind:2.15.0'
    }
}
```

#### 問題3: EARのサイズが大きすぎる

**原因**: 各WARに重複した依存関係が含まれている

**解決策**:
```gradle
// 共通ライブラリをearlibに移行
dependencies {
    earlib project(':common')  // ✓ 共有
    deploy project(':web-app') {
        exclude group: 'com.example', module: 'common'  // ✓ WARから除外
    }
}
```

---

## 8. 実践例: フルスタックのEARビルド

### 8.1 完全な ear/build.gradle

```gradle
plugins {
    id 'ear'
}

dependencies {
    // Webモジュール
    deploy project(path: ':web-app', configuration: 'archives')
    deploy project(path: ':admin-web', configuration: 'archives')

    // EJBモジュール
    deploy project(path: ':business-logic', configuration: 'archives')

    // 共有ライブラリ（EAR全体で利用）
    earlib project(':common')
    earlib 'org.slf4j:slf4j-api:2.0.0'
    earlib 'ch.qos.logback:logback-classic:1.4.0'
    earlib 'com.fasterxml.jackson.core:jackson-databind:2.15.0'

    // EARにのみ必要な設定ファイル
    earlib files('src/main/resources/config.properties')
}

ear {
    archiveFileName = "${project.name}-${project.version}.ear"

    deploymentDescriptor {
        applicationName = 'My Enterprise App'
        initializeInOrder = true  // モジュールを順番に初期化

        // Webモジュール設定
        webModule('my-webapp.war', '/app')
        webModule('admin-web.war', '/admin')

        // セキュリティロール
        securityRole 'admin'
        securityRole 'user'

        // ライブラリディレクトリ
        libraryDirectory = 'lib'
    }

    // カスタムマニフェスト
    manifest {
        attributes(
            'Implementation-Title': 'My Enterprise Application',
            'Implementation-Version': version,
            'Built-By': System.getProperty('user.name'),
            'Built-Date': new Date().format('yyyy-MM-dd HH:mm:ss')
        )
    }
}

// ビルド前にテストを実行
tasks.named('ear') {
    dependsOn ':web-app:test', ':business-logic:test'
}
```

### 8.2 ビルドとデプロイ

```bash
# クリーンビルド
./gradlew clean :ear:ear

# 成果物の確認
ls -lh ear/build/libs/
# => my-enterprise-app-1.0.0-SNAPSHOT.ear

# EARの内容確認
unzip -l ear/build/libs/my-enterprise-app-1.0.0-SNAPSHOT.ear

# WildFlyへのデプロイ
cp ear/build/libs/my-enterprise-app-1.0.0-SNAPSHOT.ear \
   $JBOSS_HOME/standalone/deployments/
```

---

## 9. まとめ

### 9.1 使い分けの指針

| アーカイブ | 使用すべき場合 |
|-----------|---------------|
| **JAR** | ライブラリ配布、スタンドアロンアプリ、マイクロサービス |
| **WAR** | Webアプリケーション単体、Spring Boot Web、REST API |
| **EAR** | 複数モジュール統合、Java EE完全実装、レガシー大規模システム |

### 9.2 現代のトレンド

- **マイクロサービス化**: EARからSpring Boot JAR（実行可能JAR）へ移行が進む
- **コンテナ化**: Docker + Kubernetes環境では単一WARやJARを推奨
- **レガシーシステム**: 既存のJava EE環境ではEARが依然として有効

### 9.3 学習チェックリスト

- [ ] JAR、WAR、EARの構造の違いを説明できる
- [ ] Gradleで各形式のアーカイブをビルドできる
- [ ] マルチモジュールプロジェクトをEARに統合できる
- [ ] クラスローダーの階層を理解している
- [ ] 依存関係の競合を解決できる
- [ ] `earlib` と `deploy` の使い分けができる
- [ ] application.xmlの基本構造を理解している
- [ ] EAR内の複数WARのコンテキストパスを適切に設定できる
- [ ] コンテキストパスの優先順位を理解している
- [ ] 環境別のコンテキストパス管理ができる

---

## 10. 参考資料

- [Gradle EAR Plugin - 公式ドキュメント](https://docs.gradle.org/current/userguide/ear_plugin.html)
- [Jakarta EE 10 Specification](https://jakarta.ee/specifications/platform/10/)
- [WildFly Documentation - Deployment](https://docs.wildfly.org/30/Admin_Guide.html#Deployment)
- 書籍『Professional Java EE Design Patterns』
- [Spring Boot vs Java EE: アーキテクチャ比較](https://www.baeldung.com/spring-boot-vs-java-ee)

---

## 11. 次のステップ

- [[../4.build-deploy/4.1_build-tools/build-tools.md]] - Gradleの詳細な使い方
- [[../4.build-deploy/4.2_application-servers/README.md]] - アプリケーションサーバーへのデプロイ
- [関連ノート] Jakarta EEのエンタープライズ機能（EJB、JPA、JMS）
