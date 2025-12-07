# 環境管理学習ノート

> 対象: 開発/ステージング/本番環境
> ツール: Spring Profiles, 環境変数, Docker

## 学習目標

- 開発・ステージング・本番環境の分離の重要性を理解する
- 設定の外部化とセキュリティベストプラクティスを習得する
- Spring Profilesを使った環境別設定管理ができる
- 環境変数を使った安全な設定管理ができる

---

## 4.3.1 開発/ステージング/本番環境の分離

### 環境の定義

| 環境 | 目的 | データ | 特徴 |
|------|------|--------|------|
| **開発（Development）** | 機能開発・デバッグ | ダミーデータ | ログ詳細、自動リロード |
| **ステージング（Staging）** | 統合テスト・リハーサル | 本番コピー（一部マスク） | 本番と同構成 |
| **本番（Production）** | エンドユーザー提供 | 実データ | 高可用性、監視 |

### なぜ分離が必要か

#### 1. リスク分離
```
開発環境での実験 → ステージングで検証 → 本番に適用
```
- 開発での失敗が本番に影響しない
- 新機能の安全な検証

#### 2. データ保護
```
開発環境: テストデータ（個人情報なし）
本番環境: 実データ（厳重管理）
```

#### 3. パフォーマンス影響の回避
```
開発環境: デバッグログ有効、パフォーマンス低下OK
本番環境: 最小限のログ、パフォーマンス最適化
```

### 環境別の設定例

#### データベース接続

```yaml
# application-dev.yml (開発環境)
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    username: sa
    password:
  jpa:
    show-sql: true  # SQLログ表示
    hibernate:
      ddl-auto: create-drop  # 起動時にテーブル再作成

---
# application-staging.yml (ステージング環境)
spring:
  datasource:
    url: jdbc:oracle:thin:@staging-db:1521:STGDB
    username: stg_user
    password: ${DB_PASSWORD}  # 環境変数から取得
  jpa:
    show-sql: false
    hibernate:
      ddl-auto: validate  # スキーマ検証のみ

---
# application-prod.yml (本番環境)
spring:
  datasource:
    url: jdbc:oracle:thin:@prod-db:1521:PRDDB
    username: prd_user
    password: ${DB_PASSWORD}
  jpa:
    show-sql: false
    hibernate:
      ddl-auto: none
```

#### ログレベル

```yaml
# application-dev.yml
logging:
  level:
    root: DEBUG
    com.example: TRACE
  pattern:
    console: "%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"

---
# application-prod.yml
logging:
  level:
    root: WARN
    com.example: INFO
  file:
    name: /var/log/myapp/application.log
  pattern:
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
```

### インフラ構成の分離

```
開発環境:
  - ローカルマシン or 共有開発サーバー
  - 単一インスタンス
  - コスト重視

ステージング環境:
  - 本番と同等の構成（スケールは小）
  - 本番デプロイのリハーサル

本番環境:
  - 冗長化構成（複数サーバー）
  - ロードバランサー
  - 高可用性、監視
```

---

## 4.3.2 環境変数と設定の外部化

### 12 Factor App - Config原則

> 設定は環境変数に保存し、コードと分離する

### 悪い例: ハードコード

```java
// ❌ 本番パスワードがコードに埋め込まれている
@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource dataSource() {
        DataSourceBuilder builder = DataSourceBuilder.create();
        builder.url("jdbc:oracle:thin:@prod-db:1521:PRDDB");
        builder.username("prod_user");
        builder.password("SuperSecret123");  // ❌ 危険！
        return builder.build();
    }
}
```

**問題点:**
- パスワードがGitにコミットされる
- 環境ごとにコード変更が必要
- セキュリティリスク

### 良い例: 環境変数の使用

```java
// ✅ 環境変数から取得
@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource dataSource() {
        DataSourceBuilder builder = DataSourceBuilder.create();
        builder.url(System.getenv("DB_URL"));
        builder.username(System.getenv("DB_USERNAME"));
        builder.password(System.getenv("DB_PASSWORD"));
        return builder.build();
    }
}
```

### Spring Bootでの設定外部化

#### 1. application.ymlで環境変数参照

```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

app:
  api:
    key: ${API_KEY}
    secret: ${API_SECRET}
```

#### 2. 環境変数の設定

```bash
# Linux/Mac
export DB_URL=jdbc:oracle:thin:@localhost:1521:ORCL
export DB_USERNAME=myuser
export DB_PASSWORD=mypassword

# 起動時に指定
DB_PASSWORD=secret ./gradlew bootRun
```

```powershell
# Windows PowerShell
$env:DB_URL="jdbc:oracle:thin:@localhost:1521:ORCL"
$env:DB_PASSWORD="mypassword"
```

#### 3. .envファイル（開発環境のみ）

```bash
# .env（Gitには含めない）
DB_URL=jdbc:h2:mem:testdb
DB_USERNAME=sa
DB_PASSWORD=
API_KEY=dev-api-key-12345
```

**.gitignoreに追加:**
```gitignore
.env
*.env
application-local.yml
```

### Dockerでの環境変数管理

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      - DB_URL=jdbc:oracle:thin:@db:1521:ORCL
      - DB_USERNAME=appuser
      - DB_PASSWORD=${DB_PASSWORD}  # .envから読み込み
    env_file:
      - .env  # 複数の環境変数をファイルから読み込み
```

### 設定優先順位（Spring Boot）

```
1. コマンドライン引数
   java -jar app.jar --server.port=9000

2. 環境変数
   export SERVER_PORT=9000

3. application-{profile}.yml
   application-prod.yml

4. application.yml (デフォルト)
```

---

## 4.3.3 プロファイル管理

### Spring Profilesの基本

Profileは、環境ごとに異なるBeanや設定を切り替える仕組みです。

### プロファイル別設定ファイル

```
src/main/resources/
  ├── application.yml           # 共通設定
  ├── application-dev.yml       # 開発環境
  ├── application-staging.yml   # ステージング環境
  └── application-prod.yml      # 本番環境
```

### application.yml（共通設定）

```yaml
spring:
  application:
    name: my-application

# 全環境共通の設定
server:
  servlet:
    context-path: /api

logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
```

### application-dev.yml（開発環境）

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
  h2:
    console:
      enabled: true  # H2コンソール有効化

logging:
  level:
    com.example: DEBUG

# 開発用の外部API（モック）
external:
  api:
    url: http://localhost:8081/mock
```

### application-prod.yml（本番環境）

```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

logging:
  level:
    com.example: INFO
  file:
    name: /var/log/myapp/app.log

# 本番用の外部API
external:
  api:
    url: https://api.production.com
```

### プロファイルの有効化

#### 1. 環境変数

```bash
export SPRING_PROFILES_ACTIVE=prod
java -jar myapp.jar
```

#### 2. コマンドライン引数

```bash
java -jar myapp.jar --spring.profiles.active=prod
```

#### 3. application.yml

```yaml
spring:
  profiles:
    active: dev  # デフォルトプロファイル
```

#### 4. IDE（IntelliJ IDEA / Eclipse）

**IntelliJ IDEA:**
```
Run → Edit Configurations
→ Environment variables: SPRING_PROFILES_ACTIVE=dev
```

### プロファイル別Bean定義

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        // H2インメモリDB
        return DataSourceBuilder.create()
            .url("jdbc:h2:mem:testdb")
            .build();
    }

    @Bean
    @Profile("prod")
    public DataSource prodDataSource() {
        // 本番Oracle DB（JNDIから取得）
        JndiDataSourceLookup lookup = new JndiDataSourceLookup();
        return lookup.getDataSource("java:comp/env/jdbc/ProdDB");
    }
}
```

### 複数プロファイルの同時使用

```bash
# 本番環境 + キャッシュ有効
export SPRING_PROFILES_ACTIVE=prod,cache

java -jar myapp.jar
```

```yaml
# application-cache.yml
spring:
  cache:
    type: redis
```

### プロファイル別のテスト

```java
@SpringBootTest
@ActiveProfiles("test")  // テスト用プロファイル
class UserServiceTest {

    @Autowired
    private UserService userService;

    @Test
    void testFindUser() {
        // テスト用DB（H2）に対して実行
    }
}
```

---

## セキュリティベストプラクティス

### 1. 機密情報はコードに含めない

**❌ 悪い例:**
```yaml
# application.yml（Gitにコミット）
spring:
  datasource:
    password: SuperSecret123  # ❌
```

**✅ 良い例:**
```yaml
# application.yml
spring:
  datasource:
    password: ${DB_PASSWORD}  # 環境変数から取得
```

### 2. 本番用設定ファイルをGitに含めない

```gitignore
# .gitignore
application-prod.yml
application-local.yml
.env
secrets/
```

### 3. シークレット管理サービスの利用

#### AWS Secrets Manager

```java
@Configuration
public class SecretsConfig {

    @Bean
    public DataSource dataSource() {
        // AWS Secrets Managerから認証情報取得
        String secret = getSecretFromAWS("myapp/database");
        // JSONパース
        DatabaseCredentials creds = parseSecret(secret);

        return DataSourceBuilder.create()
            .url(creds.getUrl())
            .username(creds.getUsername())
            .password(creds.getPassword())
            .build();
    }
}
```

#### HashiCorp Vault

```yaml
spring:
  cloud:
    vault:
      uri: https://vault.example.com
      token: ${VAULT_TOKEN}
      database:
        enabled: true
        role: myapp-role
```

### 4. 環境変数の検証

```java
@Component
public class ConfigValidator implements ApplicationListener<ApplicationReadyEvent> {

    @Value("${DB_PASSWORD:}")
    private String dbPassword;

    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        if (dbPassword.isEmpty()) {
            throw new IllegalStateException("DB_PASSWORD must be set!");
        }
    }
}
```

---

## 実務での環境管理フロー

### 1. ローカル開発

```bash
# プロファイル: dev
# データベース: H2インメモリ
# 外部API: モック

export SPRING_PROFILES_ACTIVE=dev
./gradlew bootRun
```

### 2. ステージングデプロイ

```bash
# プロファイル: staging
# データベース: ステージング用Oracle
# 環境変数はCI/CDツールで注入

# GitLab CI例
docker run -e SPRING_PROFILES_ACTIVE=staging \
           -e DB_URL=$STAGING_DB_URL \
           -e DB_PASSWORD=$STAGING_DB_PASSWORD \
           myapp:latest
```

### 3. 本番デプロイ

```bash
# プロファイル: prod
# データベース: 本番Oracle（JNDI経由）
# シークレットはAWS Secrets Manager

# Kubernetes例
kubectl create secret generic db-secret \
  --from-literal=password=$PROD_DB_PASSWORD

kubectl apply -f deployment.yaml
```

---

## 学習ロードマップ

### Week 1: 環境分離の理解
- [ ] 開発/ステージング/本番の役割理解
- [ ] 環境ごとの設定ファイル作成
- [ ] プロファイルの切り替え実践

### Week 2: 環境変数の活用
- [ ] 環境変数の設定と参照
- [ ] .envファイルの使い方
- [ ] Dockerでの環境変数管理

### Week 3: Spring Profiles
- [ ] プロファイル別Bean定義
- [ ] 複数プロファイルの組み合わせ
- [ ] テストでのプロファイル利用

### Week 4: セキュリティ
- [ ] 機密情報の外部化実践
- [ ] .gitignoreの適切な設定
- [ ] シークレット管理ツールの調査

---

## 参考資料

- [Spring Boot Reference - Profiles](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.profiles)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Spring Boot Reference - External Configuration](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)

---

## トラブルシューティング

### プロファイルが有効にならない

```bash
# 現在のプロファイルを確認
java -jar myapp.jar --debug | grep "The following profiles are active"
```

### 環境変数が読み込まれない

```java
// デバッグ用コード
@Component
public class EnvChecker implements ApplicationListener<ApplicationReadyEvent> {
    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        System.out.println("DB_URL: " + System.getenv("DB_URL"));
        System.out.println("Active Profiles: " +
            Arrays.toString(event.getApplicationContext().getEnvironment().getActiveProfiles()));
    }
}
```

### 設定の優先順位がわからない

```bash
# 全設定値と読み込み元を表示
java -jar myapp.jar --debug
```
