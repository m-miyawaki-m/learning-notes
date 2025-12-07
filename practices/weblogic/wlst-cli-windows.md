# WebLogic WLST（CLI）設定ガイド - Windows環境

> 対象: WebLogic Server 14c (14.1.1.0)
> 環境: Windows 10/11, PowerShell/Command Prompt

このドキュメントは、Windows環境でWLST（WebLogic Scripting Tool）を使用してCLIでWebLogicを設定する方法を記載しています。

参考: [Oracle WebLogic Server 14.1.1.0 Installation Guide](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlsig/installing-weblogic-server-developers.html)

---

## 目次

1. [WLST基礎](#wlst基礎)
2. [ドメイン作成（CLI）](#ドメイン作成cli)
3. [データソース設定（CLI）](#データソース設定cli)
4. [JMS設定（CLI）](#jms設定cli)
5. [完全自動化スクリプト例](#完全自動化スクリプト例)
6. [PowerShellラッパースクリプト](#powershellラッパースクリプト)

---

## WLST基礎

### WLSTとは

**WLST (WebLogic Scripting Tool)** は、Jythonベースのスクリプト環境で、WebLogicの設定・管理をCLIで実行できます。

### WLSTの起動（Windows）

#### Command Prompt

```cmd
cd C:\Oracle\Middleware\Oracle_Home\oracle_common\common\bin
wlst.cmd
```

#### PowerShell

```powershell
cd C:\Oracle\Middleware\Oracle_Home\oracle_common\common\bin
.\wlst.cmd
```

#### 環境変数の設定（推奨）

```powershell
# システム環境変数に追加
[System.Environment]::SetEnvironmentVariable("ORACLE_HOME", "C:\Oracle\Middleware\Oracle_Home", "Machine")

# PATHに追加
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
$newPath = $currentPath + ";C:\Oracle\Middleware\Oracle_Home\oracle_common\common\bin"
[System.Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
```

設定後、新しいコマンドプロンプトで：

```cmd
wlst
```

### WLSTモード

#### オフラインモード
- ドメイン未起動時に使用
- ドメイン作成、設定ファイル編集

#### オンラインモード
- 稼働中のドメインに接続
- リアルタイム設定変更、モニタリング

---

## ドメイン作成（CLI）

### 方法1: WLSTスクリプトでドメイン作成

#### create_domain.py

```python
# create_domain.py
# WebLogic 14c用ドメイン作成スクリプト（Windows）

# ドメイン設定
domain_name = 'my_domain'
domain_path = 'C:/Oracle/Middleware/user_projects/domains/' + domain_name
admin_username = 'weblogic'
admin_password = 'Welcome1'
admin_port = 7001

# テンプレート選択
template_path = 'C:/Oracle/Middleware/Oracle_Home/wlserver/common/templates/wls/wls.jar'

print '==========================================='
print 'WebLogic Domain Creation Script'
print '==========================================='
print 'Domain Name: ' + domain_name
print 'Domain Path: ' + domain_path
print '==========================================='

# ドメイン読み込み（新規作成）
readTemplate(template_path)

# 管理者アカウント設定
cd('/')
cd('Security/base_domain/User/weblogic')
cmo.setPassword(admin_password)

# 管理サーバー設定
cd('/')
cd('Servers/AdminServer')
set('ListenAddress', '')
set('ListenPort', admin_port)

# ドメイン名設定
cd('/')
set('Name', domain_name)

# ドメイン書き込み
setOption('OverwriteDomain', 'true')
writeDomain(domain_path)
closeTemplate()

print '==========================================='
print 'Domain created successfully!'
print 'Domain location: ' + domain_path
print '==========================================='
print ''
print 'To start the domain:'
print '  cd ' + domain_path + '\\bin'
print '  startWebLogic.cmd'

exit()
```

#### 実行方法（Windows）

```cmd
cd C:\Oracle\Middleware\Oracle_Home\oracle_common\common\bin
wlst.cmd C:\scripts\create_domain.py
```

### 方法2: 対話的ドメイン作成

```cmd
wlst.cmd
```

```python
# WLSTコンソールで実行
readTemplate('C:/Oracle/Middleware/Oracle_Home/wlserver/common/templates/wls/wls.jar')

cd('/')
cd('Security/base_domain/User/weblogic')
cmo.setPassword('Welcome1')

cd('/')
cd('Servers/AdminServer')
set('ListenAddress', '')
set('ListenPort', 7001)

setOption('OverwriteDomain', 'true')
writeDomain('C:/Oracle/Middleware/user_projects/domains/my_domain')
closeTemplate()

exit()
```

### ドメインの起動（Windows）

```cmd
cd C:\Oracle\Middleware\user_projects\domains\my_domain\bin
startWebLogic.cmd
```

---

## データソース設定（CLI）

### create_datasource.py

```python
# create_datasource.py
# Oracle JDBC データソース作成スクリプト

# 接続情報
admin_url = 't3://localhost:7001'
admin_username = 'weblogic'
admin_password = 'Welcome1'

# データソース設定
datasource_name = 'MyAppDS'
jndi_name = 'jdbc/MyAppDS'
db_url = 'jdbc:oracle:thin:@localhost:1521:ORCL'
db_username = 'myapp_user'
db_password = 'myapp_password'
target_server = 'AdminServer'  # または 'ManagedServer1'

print '==========================================='
print 'Creating JDBC DataSource: ' + datasource_name
print '==========================================='

# 管理サーバーに接続
connect(admin_username, admin_password, admin_url)

# 編集モード開始
edit()
startEdit()

# データソース作成
cd('/')
cmo.createJDBCSystemResource(datasource_name)

cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name)
cmo.setName(datasource_name)

# JNDI名設定
cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name + '/JDBCDataSourceParams/' + datasource_name)
set('JNDINames', jarray.array([String(jndi_name)], String))

# ドライバー設定
cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name + '/JDBCDriverParams/' + datasource_name)
cmo.setUrl(db_url)
cmo.setDriverName('oracle.jdbc.OracleDriver')
cmo.setPassword(db_password)

# ユーザー名設定
cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name + '/JDBCDriverParams/' + datasource_name + '/Properties/' + datasource_name)
cmo.createProperty('user')

cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name + '/JDBCDriverParams/' + datasource_name + '/Properties/' + datasource_name + '/Properties/user')
cmo.setValue(db_username)

# コネクションプール設定
cd('/JDBCSystemResources/' + datasource_name + '/JDBCResource/' + datasource_name + '/JDBCConnectionPoolParams/' + datasource_name)
cmo.setInitialCapacity(5)
cmo.setMaxCapacity(20)
cmo.setMinCapacity(5)
cmo.setCapacityIncrement(1)
cmo.setTestConnectionsOnReserve(true)
cmo.setTestTableName('SQL SELECT 1 FROM DUAL')
cmo.setSecondsToTrustAnIdlePoolConnection(10)
cmo.setShrinkFrequencySeconds(900)

# ターゲット設定
cd('/JDBCSystemResources/' + datasource_name)
set('Targets', jarray.array([ObjectName('com.bea:Name=' + target_server + ',Type=Server')], ObjectName))

# 変更を保存・有効化
save()
activate()

print '==========================================='
print 'DataSource created successfully!'
print 'JNDI Name: ' + jndi_name
print 'Target: ' + target_server
print '==========================================='

disconnect()
exit()
```

### 実行方法

```cmd
wlst.cmd C:\scripts\create_datasource.py
```

### データソースのテスト

```python
# test_datasource.py

connect('weblogic', 'Welcome1', 't3://localhost:7001')

# データソースのテスト
cd('/JDBCSystemResources/MyAppDS/JDBCResource/MyAppDS')
test = cmo.testPool()

if test == 'Success':
    print 'DataSource test successful!'
else:
    print 'DataSource test failed!'

disconnect()
exit()
```

---

## JMS設定（CLI）

### create_jms.py

```python
# create_jms.py
# JMSサーバー、キュー、接続ファクトリ作成スクリプト

# 接続情報
admin_url = 't3://localhost:7001'
admin_username = 'weblogic'
admin_password = 'Welcome1'

# JMS設定
jms_module_name = 'MyJMSModule'
jms_server_name = 'MyJMSServer'
queue_name = 'MyQueue'
queue_jndi = 'jms/MyQueue'
cf_name = 'MyConnectionFactory'
cf_jndi = 'jms/MyConnectionFactory'
target_server = 'AdminServer'

print '==========================================='
print 'Creating JMS Resources'
print '==========================================='

connect(admin_username, admin_password, admin_url)

edit()
startEdit()

# JMSサーバー作成
cd('/')
cmo.createJMSServer(jms_server_name)

cd('/JMSServers/' + jms_server_name)
set('Targets', jarray.array([ObjectName('com.bea:Name=' + target_server + ',Type=Server')], ObjectName))

# JMSモジュール作成
cd('/')
cmo.createJMSSystemResource(jms_module_name)

cd('/JMSSystemResources/' + jms_module_name)
set('Targets', jarray.array([ObjectName('com.bea:Name=' + target_server + ',Type=Server')], ObjectName))

# サブデプロイメント作成
cd('/JMSSystemResources/' + jms_module_name)
cmo.createSubDeployment('MySubDeployment')

cd('/JMSSystemResources/' + jms_module_name + '/SubDeployments/MySubDeployment')
set('Targets', jarray.array([ObjectName('com.bea:Name=' + jms_server_name + ',Type=JMSServer')], ObjectName))

# 接続ファクトリ作成
cd('/JMSSystemResources/' + jms_module_name + '/JMSResource/' + jms_module_name)
cmo.createConnectionFactory(cf_name)

cd('/JMSSystemResources/' + jms_module_name + '/JMSResource/' + jms_module_name + '/ConnectionFactories/' + cf_name)
cmo.setJNDIName(cf_jndi)
cmo.setSubDeploymentName('MySubDeployment')

# キュー作成
cd('/JMSSystemResources/' + jms_module_name + '/JMSResource/' + jms_module_name)
cmo.createQueue(queue_name)

cd('/JMSSystemResources/' + jms_module_name + '/JMSResource/' + jms_module_name + '/Queues/' + queue_name)
cmo.setJNDIName(queue_jndi)
cmo.setSubDeploymentName('MySubDeployment')

save()
activate()

print '==========================================='
print 'JMS Resources created successfully!'
print 'Queue JNDI: ' + queue_jndi
print 'Connection Factory JNDI: ' + cf_jndi
print '==========================================='

disconnect()
exit()
```

---

## 完全自動化スクリプト例

### setup_complete_environment.py

```python
# setup_complete_environment.py
# WebLogic環境の完全自動セットアップ

import sys

# ========================================
# 設定値
# ========================================
DOMAIN_NAME = 'my_domain'
DOMAIN_PATH = 'C:/Oracle/Middleware/user_projects/domains/' + DOMAIN_NAME
ADMIN_USERNAME = 'weblogic'
ADMIN_PASSWORD = 'Welcome1'
ADMIN_PORT = 7001

MANAGED_SERVER_NAME = 'ManagedServer1'
MANAGED_SERVER_PORT = 7003

DATASOURCE_NAME = 'MyAppDS'
DATASOURCE_JNDI = 'jdbc/MyAppDS'
DB_URL = 'jdbc:oracle:thin:@localhost:1521:ORCL'
DB_USERNAME = 'myapp_user'
DB_PASSWORD = 'myapp_password'

JMS_MODULE = 'MyJMSModule'
JMS_SERVER = 'MyJMSServer'
QUEUE_NAME = 'MyQueue'
QUEUE_JNDI = 'jms/MyQueue'

# ========================================
# ドメイン作成
# ========================================
def create_domain():
    print '=========================================='
    print 'Step 1: Creating Domain'
    print '=========================================='

    template = 'C:/Oracle/Middleware/Oracle_Home/wlserver/common/templates/wls/wls.jar'
    readTemplate(template)

    cd('/')
    cd('Security/base_domain/User/weblogic')
    cmo.setPassword(ADMIN_PASSWORD)

    cd('/')
    cd('Servers/AdminServer')
    set('ListenAddress', '')
    set('ListenPort', ADMIN_PORT)

    cd('/')
    set('Name', DOMAIN_NAME)

    setOption('OverwriteDomain', 'true')
    writeDomain(DOMAIN_PATH)
    closeTemplate()

    print 'Domain created: ' + DOMAIN_PATH
    print ''

# ========================================
# 管理対象サーバー作成
# ========================================
def create_managed_server():
    print '=========================================='
    print 'Step 2: Creating Managed Server'
    print '=========================================='

    edit()
    startEdit()

    cd('/')
    cmo.createServer(MANAGED_SERVER_NAME)

    cd('/Servers/' + MANAGED_SERVER_NAME)
    cmo.setListenPort(MANAGED_SERVER_PORT)
    cmo.setListenAddress('localhost')

    save()
    activate()

    print 'Managed Server created: ' + MANAGED_SERVER_NAME
    print ''

# ========================================
# データソース作成
# ========================================
def create_datasource():
    print '=========================================='
    print 'Step 3: Creating DataSource'
    print '=========================================='

    edit()
    startEdit()

    cd('/')
    cmo.createJDBCSystemResource(DATASOURCE_NAME)

    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME)
    cmo.setName(DATASOURCE_NAME)

    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME + '/JDBCDataSourceParams/' + DATASOURCE_NAME)
    set('JNDINames', jarray.array([String(DATASOURCE_JNDI)], String))

    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME + '/JDBCDriverParams/' + DATASOURCE_NAME)
    cmo.setUrl(DB_URL)
    cmo.setDriverName('oracle.jdbc.OracleDriver')
    cmo.setPassword(DB_PASSWORD)

    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME + '/JDBCDriverParams/' + DATASOURCE_NAME + '/Properties/' + DATASOURCE_NAME)
    cmo.createProperty('user')
    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME + '/JDBCDriverParams/' + DATASOURCE_NAME + '/Properties/' + DATASOURCE_NAME + '/Properties/user')
    cmo.setValue(DB_USERNAME)

    cd('/JDBCSystemResources/' + DATASOURCE_NAME + '/JDBCResource/' + DATASOURCE_NAME + '/JDBCConnectionPoolParams/' + DATASOURCE_NAME)
    cmo.setInitialCapacity(5)
    cmo.setMaxCapacity(20)
    cmo.setTestConnectionsOnReserve(true)
    cmo.setTestTableName('SQL SELECT 1 FROM DUAL')

    cd('/JDBCSystemResources/' + DATASOURCE_NAME)
    set('Targets', jarray.array([ObjectName('com.bea:Name=' + MANAGED_SERVER_NAME + ',Type=Server')], ObjectName))

    save()
    activate()

    print 'DataSource created: ' + DATASOURCE_JNDI
    print ''

# ========================================
# JMS作成
# ========================================
def create_jms():
    print '=========================================='
    print 'Step 4: Creating JMS Resources'
    print '=========================================='

    edit()
    startEdit()

    # JMSサーバー
    cd('/')
    cmo.createJMSServer(JMS_SERVER)
    cd('/JMSServers/' + JMS_SERVER)
    set('Targets', jarray.array([ObjectName('com.bea:Name=' + MANAGED_SERVER_NAME + ',Type=Server')], ObjectName))

    # JMSモジュール
    cd('/')
    cmo.createJMSSystemResource(JMS_MODULE)
    cd('/JMSSystemResources/' + JMS_MODULE)
    set('Targets', jarray.array([ObjectName('com.bea:Name=' + MANAGED_SERVER_NAME + ',Type=Server')], ObjectName))

    # サブデプロイメント
    cmo.createSubDeployment('MySubDeployment')
    cd('/JMSSystemResources/' + JMS_MODULE + '/SubDeployments/MySubDeployment')
    set('Targets', jarray.array([ObjectName('com.bea:Name=' + JMS_SERVER + ',Type=JMSServer')], ObjectName))

    # キュー
    cd('/JMSSystemResources/' + JMS_MODULE + '/JMSResource/' + JMS_MODULE)
    cmo.createQueue(QUEUE_NAME)
    cd('/JMSSystemResources/' + JMS_MODULE + '/JMSResource/' + JMS_MODULE + '/Queues/' + QUEUE_NAME)
    cmo.setJNDIName(QUEUE_JNDI)
    cmo.setSubDeploymentName('MySubDeployment')

    save()
    activate()

    print 'JMS Queue created: ' + QUEUE_JNDI
    print ''

# ========================================
# メイン処理
# ========================================
print '=========================================='
print 'WebLogic Complete Environment Setup'
print '=========================================='
print ''

# ドメイン作成（オフラインモード）
create_domain()

print 'Please start the AdminServer before continuing...'
print 'Command: ' + DOMAIN_PATH + '\\bin\\startWebLogic.cmd'
print ''
print 'After AdminServer is running, run this script in online mode:'
print 'wlst.cmd setup_complete_environment_online.py'

exit()
```

### setup_complete_environment_online.py

```python
# setup_complete_environment_online.py
# オンラインモードでの設定（ドメイン起動後）

ADMIN_URL = 't3://localhost:7001'
ADMIN_USERNAME = 'weblogic'
ADMIN_PASSWORD = 'Welcome1'

print 'Connecting to AdminServer...'
connect(ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_URL)

# ここで create_managed_server(), create_datasource(), create_jms() を実行

create_managed_server()
create_datasource()
create_jms()

print '=========================================='
print 'Setup Complete!'
print '=========================================='

disconnect()
exit()
```

---

## PowerShellラッパースクリプト

### setup-weblogic.ps1

```powershell
# setup-weblogic.ps1
# WebLogic環境セットアップのPowerShellラッパー

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "all"
)

$ORACLE_HOME = "C:\Oracle\Middleware\Oracle_Home"
$WLST = "$ORACLE_HOME\oracle_common\common\bin\wlst.cmd"
$SCRIPTS_DIR = "C:\scripts\weblogic"

function Write-Step {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Create-Domain {
    Write-Step "Creating Domain..."
    & $WLST "$SCRIPTS_DIR\create_domain.py"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Domain created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Domain creation failed!" -ForegroundColor Red
        exit 1
    }
}

function Start-AdminServer {
    Write-Step "Starting AdminServer..."
    $DOMAIN_PATH = "C:\Oracle\Middleware\user_projects\domains\my_domain"

    Start-Process -FilePath "$DOMAIN_PATH\bin\startWebLogic.cmd" -NoNewWindow

    Write-Host "Waiting for AdminServer to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
}

function Create-Resources {
    Write-Step "Creating Resources (DataSource, JMS)..."
    & $WLST "$SCRIPTS_DIR\create_datasource.py"
    & $WLST "$SCRIPTS_DIR\create_jms.py"

    Write-Host "Resources created successfully!" -ForegroundColor Green
}

# メイン処理
switch ($Action) {
    "domain" {
        Create-Domain
    }
    "start" {
        Start-AdminServer
    }
    "resources" {
        Create-Resources
    }
    "all" {
        Create-Domain
        Start-AdminServer
        Create-Resources
    }
    default {
        Write-Host "Invalid action: $Action" -ForegroundColor Red
        Write-Host "Valid actions: domain, start, resources, all"
        exit 1
    }
}

Write-Host "`nSetup completed!" -ForegroundColor Green
```

### 実行方法

```powershell
# 全て実行
.\setup-weblogic.ps1 -Action all

# ドメインのみ作成
.\setup-weblogic.ps1 -Action domain

# AdminServer起動のみ
.\setup-weblogic.ps1 -Action start

# リソース作成のみ
.\setup-weblogic.ps1 -Action resources
```

---

## CI/CD統合（Windows）

### GitLab CI例

```yaml
# .gitlab-ci.yml (Windows Runner)

stages:
  - build
  - deploy

variables:
  ORACLE_HOME: "C:\\Oracle\\Middleware\\Oracle_Home"
  DOMAIN_PATH: "C:\\Oracle\\Middleware\\user_projects\\domains\\my_domain"

build:
  stage: build
  tags:
    - windows
  script:
    - .\gradlew.bat clean build
  artifacts:
    paths:
      - build\libs\*.war

deploy:
  stage: deploy
  tags:
    - windows
  script:
    - |
      $env:WLST = "$env:ORACLE_HOME\oracle_common\common\bin\wlst.cmd"
      & $env:WLST C:\scripts\deploy_app.py
  only:
    - main
```

### deploy_app.py

```python
# deploy_app.py

import os

admin_url = 't3://localhost:7001'
admin_user = 'weblogic'
admin_pass = os.environ.get('WEBLOGIC_PASSWORD', 'Welcome1')

app_name = 'myapp'
war_file = 'C:/builds/myapp/build/libs/myapp.war'
target = 'ManagedServer1'

connect(admin_user, admin_pass, admin_url)

try:
    undeploy(app_name, targets=target)
    print 'Undeployed existing application'
except:
    print 'No existing application'

deploy(app_name, war_file, targets=target, upload='true')
print 'Deployed successfully!'

disconnect()
exit()
```

---

## トラブルシューティング（Windows）

### WLSTが起動しない

```cmd
# JAVA_HOME確認
echo %JAVA_HOME%

# 設定されていない場合
set JAVA_HOME=C:\Program Files\Java\jdk-11

# PATHに追加
set PATH=%JAVA_HOME%\bin;%PATH%
```

### スクリプト実行時のエラー

```python
# エラーハンドリング追加
try:
    connect('weblogic', 'Welcome1', 't3://localhost:7001')
except:
    print 'Connection failed!'
    dumpStack()
    exit(exitcode=1)
```

### Windowsパスの扱い

```python
# バックスラッシュをスラッシュに
domain_path = 'C:/Oracle/Middleware/user_projects/domains/my_domain'

# または Raw文字列
domain_path = r'C:\Oracle\Middleware\user_projects\domains\my_domain'
```

---

## 参考資料

- [Oracle WebLogic Server 14.1.1.0 Documentation](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/)
- [WebLogic Scripting Tool Reference](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wlstc/)
- [Installing WebLogic Server for Developers](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlsig/installing-weblogic-server-developers.html)
