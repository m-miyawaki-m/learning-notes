# WebLogic Server 設定ガイド

> 対象: WebLogic Server 12c/14c
> 環境: Java, Oracle Database, Spring

このドキュメントは、WebLogic Serverの実践的な設定手順を記載しています。

---

## 目次

1. [ドメインの作成](#ドメインの作成)
2. [管理サーバー・管理対象サーバーの構成](#管理サーバー管理対象サーバーの構成)
3. [JDBCデータソースの設定](#jdbcデータソースの設定)
4. [アプリケーションのデプロイ](#アプリケーションのデプロイ)
5. [JVMパラメータ設定](#jvmパラメータ設定)
6. [クラスタリング設定](#クラスタリング設定)
7. [WLSTスクリプトによる自動化](#wlstスクリプトによる自動化)
8. [トラブルシューティング](#トラブルシューティング)

---

## ドメインの作成

### 前提条件

- WebLogic Serverがインストール済み
- JAVA_HOME環境変数が設定済み

### 1. Configuration Wizardの起動

#### Linuxの場合

```bash
cd $ORACLE_HOME/oracle_common/common/bin
./config.sh
```

#### Windowsの場合

```cmd
cd %ORACLE_HOME%\oracle_common\common\bin
config.cmd
```

### 2. ドメイン作成手順

#### Step 1: Configuration Type
- **Create a new domain** を選択
- Domain Location: `/opt/oracle/domains/my_domain`

#### Step 2: Templates
- **Basic WebLogic Server Domain** を選択
- 必要に応じて追加テンプレート（JMS, Coherenceなど）を選択

#### Step 3: Administrator Account
```
Name: weblogic
Password: Welcome1（本番環境では複雑なパスワードを使用）
Confirm Password: Welcome1
```

#### Step 4: Domain Mode and JDK
- Domain Mode: **Production**（本番環境）/ **Development**（開発環境）
- JDK: `/usr/lib/jvm/java-11-openjdk`

#### Step 5: Advanced Configuration（必要に応じて選択）
- ☑ Administration Server
- ☑ Node Manager
- ☑ Managed Servers, Clusters and Machines

#### Step 6: Administration Server
```
Name: AdminServer
Listen Address: All Local Addresses
Listen Port: 7001
SSL Listen Port: 7002（SSL有効時）
```

#### Step 7: Node Manager
```
Type: Per Domain Default Location
Credentials: （管理者と同じ）
```

#### Step 8: Configuration Summary
- 設定内容を確認して **Create** をクリック

### 3. ドメインの起動

```bash
# 管理サーバー起動
cd /opt/oracle/domains/my_domain/bin
./startWebLogic.sh

# バックグラウンドで起動
nohup ./startWebLogic.sh > /dev/null 2>&1 &
```

### 4. 管理コンソールへのアクセス

```
URL: http://localhost:7001/console
Username: weblogic
Password: Welcome1
```

---

## 管理サーバー・管理対象サーバーの構成

### 管理サーバー（Admin Server）

管理コンソール、デプロイメント、モニタリングを提供する中央管理サーバー。

### 管理対象サーバー（Managed Server）

実際のアプリケーションを実行するサーバー。

### 管理対象サーバーの作成

#### 管理コンソールでの作成

1. **Environment > Servers** を選択
2. **New** をクリック
3. サーバー情報を入力:

```
Server Name: ManagedServer1
Server Listen Address: localhost
Server Listen Port: 7003
```

4. **Machine** を設定（クラスタリング時に必要）
5. **Finish** をクリック

#### スクリプトでの作成（WLST）

```python
# create_managed_server.py
connect('weblogic', 'Welcome1', 't3://localhost:7001')

edit()
startEdit()

cd('/')
cmo.createServer('ManagedServer1')

cd('/Servers/ManagedServer1')
cmo.setListenPort(7003)
cmo.setListenAddress('localhost')

save()
activate()
disconnect()
```

実行:
```bash
$ORACLE_HOME/oracle_common/common/bin/wlst.sh create_managed_server.py
```

### 管理対象サーバーの起動

```bash
cd /opt/oracle/domains/my_domain/bin
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001
```

---

## JDBCデータソースの設定

### 1. 管理コンソールでの設定

#### Step 1: データソースの作成

1. **Services > Data Sources** を選択
2. **New > Generic Data Source** をクリック

#### Step 2: JDBC Data Source Properties

```
Name: MyAppDS
JNDI Name: jdbc/MyAppDS
Database Type: Oracle
```

#### Step 3: Database Driver

```
Driver: Oracle's Driver (Thin) for Instance connections; Versions:Any
```

#### Step 4: Connection Properties

```
Database Name: ORCL
Host Name: db-server.example.com
Port: 1521
Database User Name: myapp_user
Password: ********
Confirm Password: ********
```

#### Step 5: Test Configuration

**Test Configuration** をクリックして接続テスト

```
Connection test succeeded.
```

#### Step 6: Select Targets

デプロイ先のサーバー/クラスタを選択:
- ☑ ManagedServer1
- ☑ MyCluster

#### 完了

**Finish** をクリック

### 2. 詳細設定

データソースを選択して **Configuration > Connection Pool** タブ:

```
Initial Capacity: 5
Maximum Capacity: 20
Capacity Increment: 1
Statement Cache Size: 10
Test Connections On Reserve: ☑
Test Table Name: SQL SELECT 1 FROM DUAL
```

### 3. WLSTスクリプトでの設定

```python
# create_datasource.py
connect('weblogic', 'Welcome1', 't3://localhost:7001')

edit()
startEdit()

cd('/')
cmo.createJDBCSystemResource('MyAppDS')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS')
cmo.setName('MyAppDS')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDataSourceParams/MyAppDS')
set('JNDINames',jarray.array([String('jdbc/MyAppDS')], String))

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS')
cmo.setUrl('jdbc:oracle:thin:@db-server:1521:ORCL')
cmo.setDriverName('oracle.jdbc.OracleDriver')
cmo.setPassword('mypassword')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS/Properties/MyAppDS')
cmo.createProperty('user')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS/Properties/MyAppDS/Properties/user')
cmo.setValue('myapp_user')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCConnectionPoolParams/MyAppDS')
cmo.setInitialCapacity(5)
cmo.setMaxCapacity(20)
cmo.setTestConnectionsOnReserve(true)
cmo.setTestTableName('SQL SELECT 1 FROM DUAL')

cd('/JDBCSystemResources/MyAppDS')
set('Targets',jarray.array([ObjectName('com.bea:Name=ManagedServer1,Type=Server')], ObjectName))

save()
activate()
disconnect()
```

### 4. アプリケーションからの利用

#### web.xml

```xml
<resource-ref>
    <description>My Application Database</description>
    <res-ref-name>jdbc/MyAppDS</res-ref-name>
    <res-type>javax.sql.DataSource</res-type>
    <res-auth>Container</res-auth>
</resource-ref>
```

#### Javaコード

```java
Context ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("jdbc/MyAppDS");
Connection conn = ds.getConnection();
```

#### Spring Boot設定

```yaml
spring:
  datasource:
    jndi-name: jdbc/MyAppDS
```

---

## アプリケーションのデプロイ

### 1. 管理コンソールでのデプロイ

#### Step 1: Deployments画面

1. **Deployments** を選択
2. **Install** をクリック

#### Step 2: WARファイルのアップロード

```
Path: /path/to/myapp.war
または
Upload your file(s)でローカルからアップロード
```

#### Step 3: Install Application Assistant

- **Install this deployment as an application** を選択

#### Step 4: Optional Settings

```
Name: myapp
Source Path: /opt/oracle/domains/my_domain/applications/myapp.war
```

#### Step 5: Select Targets

デプロイ先を選択:
- ☑ ManagedServer1

#### Step 6: Deployment Plan（オプション）

開発時は **No, I will create my deployment plan later** を選択

#### 完了

**Finish** をクリックしてデプロイ

### 2. アプリケーションの起動

1. **Deployments** でアプリケーションを選択
2. **Control** タブを選択
3. アプリケーションをチェック
4. **Start > Servicing all requests** をクリック

### 3. コマンドラインでのデプロイ（weblogic.Deployer）

```bash
java weblogic.Deployer \
  -adminurl t3://localhost:7001 \
  -username weblogic \
  -password Welcome1 \
  -deploy \
  -name myapp \
  -source /path/to/myapp.war \
  -targets ManagedServer1
```

#### 再デプロイ

```bash
java weblogic.Deployer \
  -adminurl t3://localhost:7001 \
  -username weblogic \
  -password Welcome1 \
  -redeploy \
  -name myapp
```

#### アンデプロイ

```bash
java weblogic.Deployer \
  -adminurl t3://localhost:7001 \
  -username weblogic \
  -password Welcome1 \
  -undeploy \
  -name myapp
```

### 4. WLSTスクリプトでのデプロイ

```python
# deploy_app.py
connect('weblogic', 'Welcome1', 't3://localhost:7001')

deploy('myapp', '/path/to/myapp.war', targets='ManagedServer1', upload='true')

disconnect()
```

実行:
```bash
wlst.sh deploy_app.py
```

### 5. デプロイメント戦略

#### ステージングモード

| モード | 説明 | 用途 |
|--------|------|------|
| **stage** | アプリケーションをステージングディレクトリにコピー | 本番環境 |
| **nostage** | 元の場所から直接実行 | 開発環境 |
| **external_stage** | 手動で配置済みのファイルを使用 | 大規模環境 |

```bash
# nostageモードでデプロイ
java weblogic.Deployer \
  -adminurl t3://localhost:7001 \
  -username weblogic \
  -password Welcome1 \
  -deploy \
  -name myapp \
  -source /path/to/myapp.war \
  -targets ManagedServer1 \
  -nostage
```

---

## JVMパラメータ設定

### 1. setDomainEnv.shの編集

```bash
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

### 2. ヒープサイズの設定

```bash
# 管理サーバー用
if [ "${SERVER_NAME}" = "AdminServer" ] ; then
    USER_MEM_ARGS="-Xms512m -Xmx1024m"
fi

# 管理対象サーバー用
if [ "${SERVER_NAME}" = "ManagedServer1" ] ; then
    USER_MEM_ARGS="-Xms2048m -Xmx4096m"
fi
```

### 3. その他のJVMオプション

```bash
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+UseG1GC"
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:MaxGCPauseMillis=200"
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+PrintGCDetails"
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:+PrintGCDateStamps"
JAVA_OPTIONS="${JAVA_OPTIONS} -Xloggc:/opt/oracle/domains/my_domain/servers/${SERVER_NAME}/logs/gc.log"

# PermGen（Java 7以前）
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:PermSize=256m -XX:MaxPermSize=512m"

# Metaspace（Java 8以降）
JAVA_OPTIONS="${JAVA_OPTIONS} -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m"

# アプリケーション固有の設定
JAVA_OPTIONS="${JAVA_OPTIONS} -Dfile.encoding=UTF-8"
JAVA_OPTIONS="${JAVA_OPTIONS} -Duser.timezone=Asia/Tokyo"

export JAVA_OPTIONS
```

### 4. 管理コンソールでの設定

1. **Environment > Servers** を選択
2. サーバーを選択
3. **Configuration > Server Start** タブ

```
Arguments: -Xms2048m -Xmx4096m -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m
```

### 5. JVMモニタリング

#### GCログの確認

```bash
tail -f /opt/oracle/domains/my_domain/servers/ManagedServer1/logs/gc.log
```

#### JVMメモリ使用状況

```bash
jstat -gcutil <PID> 1000 10
```

---

## クラスタリング設定

### 1. クラスタの作成

#### 管理コンソール

1. **Environment > Clusters** を選択
2. **New** をクリック
3. クラスタ情報を入力:

```
Name: MyCluster
Messaging Mode: unicast（推奨）
```

### 2. 管理対象サーバーをクラスタに追加

1. **Environment > Servers** を選択
2. サーバーを選択
3. **Configuration > General** タブ
4. **Cluster** ドロップダウンから **MyCluster** を選択

### 3. セッションレプリケーションの設定

#### weblogic.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<weblogic-web-app xmlns="http://xmlns.oracle.com/weblogic/weblogic-web-app">
    <session-descriptor>
        <persistent-store-type>replicated</persistent-store-type>
    </session-descriptor>
</weblogic-web-app>
```

### 4. ロードバランサーの設定（Apache HTTP Server）

#### httpd.conf

```apache
LoadModule weblogic_module modules/mod_wl.so

<IfModule mod_weblogic.c>
    WebLogicCluster server1:7003,server2:7003
    MatchExpression *.jsp
    MatchExpression /myapp/*
</IfModule>

<Location /myapp>
    SetHandler weblogic-handler
    WLLogFile /var/log/httpd/weblogic.log
    Debug ON
    WLCookieName JSESSIONID
    WLProxySSL OFF
</Location>
```

---

## WLSTスクリプトによる自動化

### 完全な環境構築スクリプト

```python
# setup_environment.py

# 接続
connect('weblogic', 'Welcome1', 't3://localhost:7001')

edit()
startEdit()

# 管理対象サーバー作成
cd('/')
cmo.createServer('ManagedServer1')
cd('/Servers/ManagedServer1')
cmo.setListenPort(7003)
cmo.setListenAddress('localhost')

# データソース作成
cd('/')
cmo.createJDBCSystemResource('MyAppDS')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS')
cmo.setName('MyAppDS')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDataSourceParams/MyAppDS')
set('JNDINames',jarray.array([String('jdbc/MyAppDS')], String))

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS')
cmo.setUrl('jdbc:oracle:thin:@db-server:1521:ORCL')
cmo.setDriverName('oracle.jdbc.OracleDriver')
cmo.setPassword('mypassword')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS/Properties/MyAppDS')
cmo.createProperty('user')
cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCDriverParams/MyAppDS/Properties/MyAppDS/Properties/user')
cmo.setValue('myapp_user')

cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS/JDBCConnectionPoolParams/MyAppDS')
cmo.setInitialCapacity(5)
cmo.setMaxCapacity(20)

cd('/JDBCSystemResources/MyAppDS')
set('Targets',jarray.array([ObjectName('com.bea:Name=ManagedServer1,Type=Server')], ObjectName))

save()
activate()

# アプリケーションデプロイ
deploy('myapp', '/path/to/myapp.war', targets='ManagedServer1', upload='true')

disconnect()
```

### CI/CDでの自動デプロイスクリプト

```bash
#!/bin/bash
# deploy.sh

APP_NAME="myapp"
WAR_FILE="build/libs/myapp.war"
ADMIN_URL="t3://localhost:7001"
USERNAME="weblogic"
PASSWORD="Welcome1"
TARGET="ManagedServer1"

echo "Deploying ${APP_NAME}..."

# WLSTスクリプト実行
$ORACLE_HOME/oracle_common/common/bin/wlst.sh <<EOF
connect('${USERNAME}', '${PASSWORD}', '${ADMIN_URL}')

try:
    # 既存アプリケーションのアンデプロイ
    undeploy('${APP_NAME}', targets='${TARGET}')
    print 'Undeployed existing application'
except:
    print 'No existing application to undeploy'

# 新しいアプリケーションのデプロイ
deploy('${APP_NAME}', '${WAR_FILE}', targets='${TARGET}', upload='true')
print 'Deployed new application'

disconnect()
EOF

echo "Deployment completed!"
```

---

## トラブルシューティング

### 管理サーバーが起動しない

#### ログの確認

```bash
tail -f /opt/oracle/domains/my_domain/servers/AdminServer/logs/AdminServer.log
```

#### よくある原因

1. **ポートが既に使用中**
```bash
# ポート確認
netstat -tuln | grep 7001

# プロセス確認
ps -ef | grep weblogic
```

2. **メモリ不足**
```bash
# ヒープサイズを調整
vi /opt/oracle/domains/my_domain/bin/setDomainEnv.sh
```

### データソース接続エラー

#### テスト接続

管理コンソール > Services > Data Sources > データソース選択 > Monitoring > Testing

```
Test Connection
```

#### よくある原因

1. **JDBCドライバーが見つからない**
```bash
# ドライバーJARをドメインlibに配置
cp ojdbc8.jar /opt/oracle/domains/my_domain/lib/
```

2. **接続文字列の誤り**
```
jdbc:oracle:thin:@<host>:<port>:<SID>
jdbc:oracle:thin:@<host>:<port>/<SERVICE_NAME>
```

3. **ファイアウォール/ネットワーク問題**
```bash
# 接続確認
telnet db-server 1521
```

### OutOfMemoryError

#### ヒープダンプの取得

```bash
# JVMオプションに追加
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/opt/oracle/domains/my_domain/dumps/
```

#### メモリ使用状況の確認

```bash
# JVMメモリ確認
jmap -heap <PID>

# ヒープダンプ取得
jmap -dump:format=b,file=heap.bin <PID>

# MAT (Eclipse Memory Analyzer)で分析
```

### クラスローディングエラー

#### ログの確認

```bash
grep "ClassNotFoundException\|NoClassDefFoundError" \
  /opt/oracle/domains/my_domain/servers/ManagedServer1/logs/ManagedServer1.log
```

#### フィルタリングクラスローダーの設定

weblogic.xml:
```xml
<weblogic-web-app>
    <container-descriptor>
        <prefer-web-inf-classes>true</prefer-web-inf-classes>
    </container-descriptor>
</weblogic-web-app>
```

### デプロイメントエラー

#### ログの確認

```bash
tail -f /opt/oracle/domains/my_domain/servers/ManagedServer1/logs/ManagedServer1.log
```

#### デプロイメント状態の確認

```bash
java weblogic.Deployer \
  -adminurl t3://localhost:7001 \
  -username weblogic \
  -password Welcome1 \
  -list
```

---

## 参考資料

- [Oracle WebLogic Server 14c Documentation](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.1.0/)
- [WebLogic Scripting Tool (WLST) Reference](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wlstc/)
- [Oracle Fusion Middleware - Deploying Applications](https://docs.oracle.com/middleware/12213/wls/DEPGD/toc.htm)

---

## チートシート

### よく使うコマンド

```bash
# 管理サーバー起動
./startWebLogic.sh

# 管理対象サーバー起動
./startManagedWebLogic.sh ManagedServer1 http://localhost:7001

# サーバー停止
./stopWebLogic.sh
./stopManagedWebLogic.sh ManagedServer1

# Node Manager起動
./startNodeManager.sh

# WLSTコンソール起動
wlst.sh

# ログ確認
tail -f servers/AdminServer/logs/AdminServer.log
```

### WLST基本コマンド

```python
# 接続
connect('weblogic', 'Welcome1', 't3://localhost:7001')

# サーバー状態確認
serverRuntime()
cd('/')
ls()

# アプリケーション一覧
listApplications()

# データソース一覧
cd('/JDBCSystemResources')
ls()

# 切断
disconnect()
exit()
```
