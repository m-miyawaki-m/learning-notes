# アプリケーションサーバー学習ノート

> 対象: Tomcat, WebLogic
> 環境: Java, Spring, サーブレット

## 学習目標

- サーブレットコンテナとアプリケーションサーバーの違いを理解する
- クラスローディングの仕組みとトラブルシューティングができる
- スレッドプールの最適化ができる
- デプロイメント戦略を理解し、実務で選択できる

---

## 4.2.1 サーブレットコンテナ vs フルスタックAPサーバー

### サーブレットコンテナ（例: Tomcat）

#### 特徴
- Servlet API / JSP の実行環境のみ提供
- 軽量でシンプル
- Java EEの一部のみサポート

#### サポート機能
- ✅ サーブレット
- ✅ JSP
- ✅ WebSocket
- ❌ EJB
- ❌ JMS
- ❌ JTA（分散トランザクション）

#### Tomcatのアーキテクチャ

```
Tomcat
  ├─ Catalina (サーブレットコンテナ)
  ├─ Coyote (HTTPコネクタ)
  └─ Jasper (JSPエンジン)
```

### フルスタックAPサーバー（例: WebLogic）

#### 特徴
- Java EE（Jakarta EE）の完全実装
- エンタープライズ機能を標準装備
- 高可用性・スケーラビリティ機能

#### サポート機能
- ✅ サーブレット / JSP
- ✅ EJB（Enterprise JavaBeans）
- ✅ JMS（メッセージング）
- ✅ JTA（分散トランザクション）
- ✅ JNDI（リソース管理）
- ✅ クラスタリング

### 比較表

| 項目 | Tomcat | WebLogic |
|------|--------|----------|
| **種類** | サーブレットコンテナ | フルスタックAPサーバー |
| **ライセンス** | Apache（無料） | Oracle（商用） |
| **起動速度** | 速い | 遅い |
| **メモリ消費** | 少ない | 多い |
| **管理コンソール** | シンプル | 高機能 |
| **クラスタリング** | 外部ツール必要 | 標準装備 |
| **適用場面** | 中小規模Web | 大規模エンタープライズ |

### 実務での選択基準

**Tomcatを選ぶ場合:**
- シンプルなWeb API / Webアプリケーション
- Spring Bootなどのフレームワークで機能を補完
- クラウドネイティブ環境（コンテナ化）

**WebLogicを選ぶ場合:**
- 大規模トランザクション処理
- 既存の基幹系システムとの連携
- エンタープライズサポートが必要

---

## 4.2.2 クラスローディング

### Javaのクラスローダー階層

```
Bootstrap ClassLoader (JDK標準ライブラリ)
  ↓
Extension ClassLoader (拡張ライブラリ)
  ↓
Application ClassLoader (アプリケーション)
```

### Tomcatのクラスローダー階層

```
Bootstrap ClassLoader
  ↓
System ClassLoader
  ↓
Common ClassLoader (Tomcat共通)
  ↓
WebApp ClassLoader (各Webアプリ独立)
```

#### 重要な特性

1. **親委譲モデル（Parent Delegation）**
   - まず親クラスローダーに委譲
   - 親が見つけられなければ自分で探す

2. **WebApp ClassLoaderの独立性**
   - 各Webアプリが異なるバージョンのライブラリを持てる
   - アプリA: log4j 1.2、アプリB: log4j 2.0 が共存可能

### クラスローディングの順序

#### Tomcatのデフォルト動作

```
1. JVMブートストラップクラス (java.lang.* など)
2. Webアプリの /WEB-INF/classes
3. Webアプリの /WEB-INF/lib/*.jar
4. Tomcat共通ライブラリ
```

#### 親優先モード（delegate=true）

```xml
<!-- context.xml -->
<Loader delegate="true"/>
```

```
1. 親クラスローダー（Tomcat共通）
2. Webアプリのクラスパス
```

### よくある問題と解決策

#### 1. ClassNotFoundException

```
java.lang.ClassNotFoundException: org.springframework.web.servlet.DispatcherServlet
```

**原因:**
- 必要なJARが `/WEB-INF/lib/` にない
- クラスパスの設定ミス

**解決策:**
```bash
# WARファイルの内容を確認
jar -tf myapp.war | grep spring-web

# 依存ライブラリを確認
./gradlew dependencies
```

#### 2. NoClassDefFoundError

```
java.lang.NoClassDefFoundError: org/springframework/core/SpringVersion
```

**原因:**
- クラスファイルは存在するが、その依存クラスが見つからない
- 推移的依存の不足

**解決策:**
- 依存関係ツリーを確認
- 必要な推移的依存を明示的に追加

#### 3. ClassCastException（同名クラスの競合）

```
java.lang.ClassCastException: com.example.User cannot be cast to com.example.User
```

**原因:**
- 同じクラスが異なるクラスローダーから読み込まれている
- Tomcat共通ライブラリとWebアプリのライブラリが競合

**解決策:**
```xml
<!-- WEB-INF/lib/ から除外し、共通ライブラリに配置 -->
<!-- または逆に、共通ライブラリから削除 -->
```

### クラスローディングのデバッグ

```bash
# クラスローディングをトレース
java -verbose:class -jar myapp.jar

# Tomcatでのデバッグ
export CATALINA_OPTS="-verbose:class"
./catalina.sh run
```

---

## 4.2.3 スレッドプール

### スレッドプールの概要

Webサーバーは複数のリクエストを同時処理するため、スレッドプールを使用します。

```
リクエスト1 → スレッド1 (プールから取得)
リクエスト2 → スレッド2 (プールから取得)
リクエスト3 → スレッド3 (プールから取得)
...
リクエストN → 待機（プールが空の場合）
```

### Tomcatのスレッドプール設定

#### server.xml

```xml
<Connector port="8080" protocol="HTTP/1.1"
           maxThreads="200"
           minSpareThreads="10"
           maxConnections="10000"
           acceptCount="100"
           connectionTimeout="20000"/>
```

#### パラメータ説明

| パラメータ | 説明 | デフォルト | 推奨値 |
|-----------|------|-----------|--------|
| `maxThreads` | 最大スレッド数 | 200 | 200〜500 |
| `minSpareThreads` | 常駐スレッド数 | 10 | 25〜50 |
| `maxConnections` | 最大同時接続数 | 10000 | 10000〜20000 |
| `acceptCount` | 待機キュー長 | 100 | 100〜200 |
| `connectionTimeout` | タイムアウト（ms） | 20000 | 30000 |

### Spring Bootでの設定

```yaml
# application.yml
server:
  tomcat:
    threads:
      max: 200        # 最大スレッド数
      min-spare: 10   # 最小アイドルスレッド数
    accept-count: 100 # 待機キューサイズ
    max-connections: 10000
```

### スレッドプールのチューニング

#### 1. スレッド数の決定

**CPU バウンドな処理（計算中心）:**
```
最適スレッド数 = CPUコア数 + 1
```

**I/O バウンドな処理（DB・外部API呼び出し）:**
```
最適スレッド数 = CPUコア数 × (1 + 待機時間 / 処理時間)
```

#### 2. モニタリング

```bash
# Tomcatのスレッド状態確認
curl http://localhost:8080/manager/status/all

# JMX経由での監視
jconsole
```

#### 3. スレッドダンプの取得

```bash
# プロセスID確認
jps

# スレッドダンプ取得
jstack <PID> > thread_dump.txt
```

### スレッドプール枯渇の検出

#### 症状
- レスポンスが遅い
- タイムアウトエラー
- `java.util.concurrent.RejectedExecutionException`

#### 対策

```java
// Spring Bootでの非同期処理
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}
```

---

## 4.2.4 JNDIとリソース管理

### JNDI（Java Naming and Directory Interface）

コンテナが管理するリソース（DB接続など）に名前でアクセスする仕組み。

### データソースの設定例

#### Tomcatの context.xml

```xml
<Context>
    <Resource name="jdbc/MyDB"
              auth="Container"
              type="javax.sql.DataSource"
              maxTotal="20"
              maxIdle="10"
              maxWaitMillis="10000"
              username="dbuser"
              password="dbpass"
              driverClassName="oracle.jdbc.OracleDriver"
              url="jdbc:oracle:thin:@localhost:1521:ORCL"/>
</Context>
```

#### web.xmlでの参照

```xml
<resource-ref>
    <description>Oracle Database</description>
    <res-ref-name>jdbc/MyDB</res-ref-name>
    <res-type>javax.sql.DataSource</res-type>
    <res-auth>Container</res-auth>
</resource-ref>
```

#### Javaコードからのアクセス

```java
Context initContext = new InitialContext();
Context envContext = (Context) initContext.lookup("java:/comp/env");
DataSource ds = (DataSource) envContext.lookup("jdbc/MyDB");

try (Connection conn = ds.getConnection()) {
    // DB操作
}
```

### Spring Bootでの設定

```yaml
# application.yml
spring:
  datasource:
    jndi-name: java:comp/env/jdbc/MyDB
```

または

```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource() throws NamingException {
        JndiDataSourceLookup lookup = new JndiDataSourceLookup();
        return lookup.getDataSource("java:comp/env/jdbc/MyDB");
    }
}
```

### コネクションプールの監視

```sql
-- Oracle: アクティブセッション確認
SELECT username, count(*)
FROM v$session
WHERE username IS NOT NULL
GROUP BY username;
```

---

## 4.2.5 デプロイメント戦略

### 1. Hot Deploy（ホットデプロイ）

#### 概要
サーバーを停止せずにアプリケーションを更新。

#### Tomcatでの設定

```xml
<!-- server.xml -->
<Host name="localhost" appBase="webapps"
      unpackWARs="true" autoDeploy="true">
```

#### メリット・デメリット

**メリット:**
- ダウンタイムゼロ
- 開発時の生産性向上

**デメリット:**
- メモリリーク発生リスク
- クラスローダーの問題
- 本番環境では非推奨

#### 実行方法

```bash
# WARファイルをコピーするだけ
cp myapp.war /opt/tomcat/webapps/

# Tomcatが自動的に検出・デプロイ
```

### 2. Blue-Green デプロイメント

#### 概要
2つの本番環境（BlueとGreen）を用意し、切り替える方式。

```
現行環境（Blue） ← ロードバランサー（本番トラフィック）
新環境（Green）  ← デプロイ・検証中
```

#### 手順

```bash
# 1. Green環境にデプロイ
scp myapp-v2.war green-server:/opt/tomcat/webapps/

# 2. Green環境で動作確認
curl http://green-server:8080/health

# 3. ロードバランサーの向き先をGreenに切り替え
# (nginx / HAProxy / AWS ELB等で設定変更)

# 4. 問題があればすぐにBlueに戻す（ロールバック）
```

#### メリット・デメリット

**メリット:**
- 即座にロールバック可能
- ダウンタイムほぼゼロ
- 本番環境での検証が可能

**デメリット:**
- 2倍のインフラコスト
- データベーススキーマ変更が困難

### 3. Rolling デプロイメント

#### 概要
複数サーバーを段階的に更新。

```
サーバー1: v1 → v2 (更新)
サーバー2: v1 → 稼働中
サーバー3: v1 → 稼働中

サーバー1: v2 → 稼働中
サーバー2: v1 → v2 (更新)
サーバー3: v1 → 稼働中

サーバー1: v2 → 稼働中
サーバー2: v2 → 稼働中
サーバー3: v1 → v2 (更新)
```

#### 実装例（Ansible）

```yaml
- hosts: webservers
  serial: 1  # 1台ずつ実行

  tasks:
    - name: ロードバランサーから除外
      command: remove_from_lb.sh {{ inventory_hostname }}

    - name: アプリケーション停止
      service: name=tomcat state=stopped

    - name: 新バージョンデプロイ
      copy: src=myapp-v2.war dest=/opt/tomcat/webapps/

    - name: アプリケーション起動
      service: name=tomcat state=started

    - name: ヘルスチェック
      uri: url=http://{{ inventory_hostname }}:8080/health

    - name: ロードバランサーに復帰
      command: add_to_lb.sh {{ inventory_hostname }}
```

### 4. Canary デプロイメント

#### 概要
一部のトラフィックのみ新バージョンに流し、段階的に拡大。

```
全トラフィック (100%)
  ├─ 旧バージョン (95%)
  └─ 新バージョン (5%) ← カナリア
```

#### 実装例（Nginx）

```nginx
upstream backend {
    server old-app:8080 weight=95;
    server new-app:8080 weight=5;
}
```

#### メリット
- リスク最小化
- 本番データでの検証
- 問題の早期発見

---

## 学習ロードマップ

### Week 1: 基礎理解
- [ ] Tomcatのインストールと基本操作
- [ ] WARファイルのデプロイ
- [ ] ログの確認方法

### Week 2: クラスローディング
- [ ] クラスローダー階層の理解
- [ ] ClassNotFoundExceptionのトラブルシューティング
- [ ] `verbose:class` でのデバッグ実践

### Week 3: スレッドプール
- [ ] スレッドプール設定のチューニング
- [ ] JMXでのモニタリング
- [ ] スレッドダンプの分析

### Week 4: デプロイ戦略
- [ ] Blue-Greenデプロイの実践
- [ ] JNDIリソースの設定
- [ ] 本番環境へのデプロイ手順書作成

---

## 参考資料

- [Apache Tomcat 10 Documentation](https://tomcat.apache.org/tomcat-10.0-doc/)
- [Oracle WebLogic Server Documentation](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/)
- 書籍『Tomcat ハンドブック』
- [Spring Boot Reference - Embedded Servers](https://docs.spring.io/spring-boot/docs/current/reference/html/web.html#web.servlet.embedded-container)

---

## トラブルシューティング

### Tomcatが起動しない

```bash
# ログ確認
tail -f /opt/tomcat/logs/catalina.out

# ポート競合チェック
netstat -tuln | grep 8080
```

### メモリ不足エラー

```bash
# JVMヒープサイズ調整
export CATALINA_OPTS="-Xms512m -Xmx2048m -XX:MetaspaceSize=256m"
./catalina.sh start
```

### スレッドプール枯渇

```bash
# スレッドダンプで確認
jstack <PID> | grep "http-nio-8080"
```
