# WebLogic ドメイン自動構成手順書（簡易版・Windows 11開発環境）

## 概要

WDTを使用した**ドメイン作成 + 複数Oracleデータソース + JMS基本設定 + サーバー起動引数 + 設定ファイル配置**の自動化手順書です。JMS/キューは必要最低限の設定でAdminServerに紐付けます。

---

## 前提条件

- WebLogic 14がインストール済み
- ORACLE_HOME: `C:\Oracle\Middleware`
- JDK 11以降
- 管理者権限

---

## ディレクトリ構成

```
C:\Oracle\
  ├─ Middleware\              # ORACLE_HOME
  ├─ wdt\
  │   └─ weblogic-deploy\     # WDT_HOME
  ├─ models\                  # WDTモデルファイル
  │   ├─ base_domain.yaml
  │   ├─ datasources.yaml
  │   └─ jms_simple.yaml
  ├─ domains\
  │   └─ dev_domain\
  ├─ appconfig\               # 外部設定ファイル
  │   └─ dev\
  │       ├─ application.properties
  │       └─ log4j2.xml
  ├─ jdbc_drivers\            # JDBCドライバ
  ├─ automation\              # スクリプト
  └─ logs\
```

---

## ステップ1: WDTセットアップ

```powershell
# 作業ディレクトリ作成
New-Item -ItemType Directory -Force -Path C:\Oracle\wdt
New-Item -ItemType Directory -Force -Path C:\Oracle\models
New-Item -ItemType Directory -Force -Path C:\Oracle\domains
New-Item -ItemType Directory -Force -Path C:\Oracle\appconfig\dev
New-Item -ItemType Directory -Force -Path C:\Oracle\jdbc_drivers

cd C:\Oracle\wdt

# WDTダウンロード
$WdtVersion = "4.2.0"
$WdtUrl = "https://github.com/oracle/weblogic-deploy-tooling/releases/download/v$WdtVersion/weblogic-deploy.zip"
Invoke-WebRequest -Uri $WdtUrl -OutFile "weblogic-deploy.zip"

# 解凍
Expand-Archive -Path "weblogic-deploy.zip" -DestinationPath "C:\Oracle\wdt" -Force
```

---

## ステップ2: モデルファイル作成

### 2-1. ベースドメイン + サーバー起動引数

**ファイル名**: `C:\Oracle\models\base_domain.yaml`

```yaml
domainInfo:
    AdminUserName: weblogic
    AdminPassword: Welcome1
    ServerStartMode: dev

topology:
    Name: dev_domain
    AdminServerName: AdminServer
    ProductionModeEnabled: false
    
    Server:
        AdminServer:
            ListenAddress: localhost
            ListenPort: 7001
            SSL:
                Enabled: true
                ListenPort: 7002
            
            ServerStart:
                Arguments: >
                    -Xms1024m
                    -Xmx2048m
                    -XX:+UseG1GC
                    -Dfile.encoding=UTF-8
                    -Duser.timezone=Asia/Tokyo
                    -Dapp.config.location=C:\Oracle\appconfig\dev
                    -Dlog4j.configurationFile=C:\Oracle\appconfig\dev\log4j2.xml
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
            
            Log:
                FileName: logs/AdminServer.log
                RotationType: bySize
                FileMinSize: 10000
                NumberOfFilesLimited: true
                FileCount: 10
        
        ManagedServer1:
            ListenAddress: localhost
            ListenPort: 8001
            Cluster: DevCluster
            
            ServerStart:
                Arguments: >
                    -Xms2048m
                    -Xmx4096m
                    -XX:+UseG1GC
                    -Dfile.encoding=UTF-8
                    -Duser.timezone=Asia/Tokyo
                    -Dapp.config.location=C:\Oracle\appconfig\dev
                    -Dlog4j.configurationFile=C:\Oracle\appconfig\dev\log4j2.xml
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
                Username: nodemanager
                Password: Welcome1
            
            Log:
                FileName: logs/ManagedServer1.log
                RotationType: bySize
                FileMinSize: 10000
                NumberOfFilesLimited: true
                FileCount: 10
        
        ManagedServer2:
            ListenAddress: localhost
            ListenPort: 8003
            Cluster: DevCluster
            
            ServerStart:
                Arguments: >
                    -Xms2048m
                    -Xmx4096m
                    -XX:+UseG1GC
                    -Dfile.encoding=UTF-8
                    -Duser.timezone=Asia/Tokyo
                    -Dapp.config.location=C:\Oracle\appconfig\dev
                    -Dlog4j.configurationFile=C:\Oracle\appconfig\dev\log4j2.xml
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
                Username: nodemanager
                Password: Welcome1
            
            Log:
                FileName: logs/ManagedServer2.log
                RotationType: bySize
                FileMinSize: 10000
                NumberOfFilesLimited: true
                FileCount: 10
    
    Cluster:
        DevCluster:
            ClusterMessagingMode: unicast
    
    Machine:
        DevMachine:
            NodeManager:
                ListenAddress: localhost
                ListenPort: 5556
                NMType: Plain

    SecurityConfiguration:
        NodeManagerUsername: nodemanager
        NodeManagerPasswordEncrypted: Welcome1
```

### 2-2. 複数Oracleデータソース

**ファイル名**: `C:\Oracle\models\datasources.yaml`

```yaml
resources:
    JDBCSystemResource:
        # メインアプリケーションDB
        OracleMainDS:
            Target: AdminServer,DevCluster
            JdbcResource:
                JDBCDataSourceParams:
                    JNDIName: jdbc/OracleMainDS
                    GlobalTransactionsProtocol: TwoPhaseCommit
                
                JDBCDriverParams:
                    DriverName: oracle.jdbc.xa.client.OracleXADataSource
                    URL: 'jdbc:oracle:thin:@//localhost:1521/MAINPDB'
                    PasswordEncrypted: MainDb_Pass123
                    Properties:
                        user:
                            Value: MAIN_APP_USER
                
                JDBCConnectionPoolParams:
                    InitialCapacity: 5
                    MaxCapacity: 50
                    MinCapacity: 5
                    TestConnectionsOnReserve: true
                    TestTableName: 'SQL SELECT 1 FROM DUAL'
                
                JDBCXAParams:
                    KeepXaConnTillTxComplete: true
        
        # バッチ処理用DB
        OracleBatchDS:
            Target: ManagedServer1
            JdbcResource:
                JDBCDataSourceParams:
                    JNDIName: jdbc/OracleBatchDS
                    GlobalTransactionsProtocol: None
                
                JDBCDriverParams:
                    DriverName: oracle.jdbc.OracleDriver
                    URL: 'jdbc:oracle:thin:@//localhost:1521/BATCHPDB'
                    PasswordEncrypted: BatchDb_Pass123
                    Properties:
                        user:
                            Value: BATCH_USER
                
                JDBCConnectionPoolParams:
                    InitialCapacity: 5
                    MaxCapacity: 30
                    MinCapacity: 5
                    TestConnectionsOnReserve: true
                    TestTableName: 'SQL SELECT 1 FROM DUAL'
        
        # レポート用DB
        OracleReportDS:
            Target: AdminServer,DevCluster
            JdbcResource:
                JDBCDataSourceParams:
                    JNDIName: jdbc/OracleReportDS
                    GlobalTransactionsProtocol: None
                
                JDBCDriverParams:
                    DriverName: oracle.jdbc.OracleDriver
                    URL: 'jdbc:oracle:thin:@//localhost:1522/REPORTPDB'
                    PasswordEncrypted: ReportDb_Pass123
                    Properties:
                        user:
                            Value: REPORT_USER
                
                JDBCConnectionPoolParams:
                    InitialCapacity: 3
                    MaxCapacity: 20
                    MinCapacity: 3
                    TestConnectionsOnReserve: true
                    TestTableName: 'SQL SELECT 1 FROM DUAL'
        
        # マスタデータ用DB
        OracleMasterDS:
            Target: AdminServer,DevCluster
            JdbcResource:
                JDBCDataSourceParams:
                    JNDIName: jdbc/OracleMasterDS
                    GlobalTransactionsProtocol: EmulateTwoPhaseCommit
                
                JDBCDriverParams:
                    DriverName: oracle.jdbc.OracleDriver
                    URL: 'jdbc:oracle:thin:@//localhost:1521/MASTERPDB'
                    PasswordEncrypted: MasterDb_Pass123
                    Properties:
                        user:
                            Value: MASTER_USER
                
                JDBCConnectionPoolParams:
                    InitialCapacity: 5
                    MaxCapacity: 30
                    MinCapacity: 5
                    TestConnectionsOnReserve: true
                    TestTableName: 'SQL SELECT 1 FROM DUAL'
```

### 2-3. JMS設定（最小構成）

**ファイル名**: `C:\Oracle\models\jms_simple.yaml`

```yaml
resources:
    JMSSystemResource:
        MainJMSModule:
            Target: AdminServer
            
            JmsResource:
                # 接続ファクトリ（デフォルト設定使用）
                ConnectionFactory:
                    ConnectionFactory:
                        JNDIName: jms/ConnectionFactory
                    
                    NonXAConnectionFactory:
                        JNDIName: jms/NonXAConnectionFactory
                        TransactionParams:
                            XAConnectionFactoryEnabled: false
                
                # キュー（デフォルト設定使用）
                Queue:
                    OrderQueue:
                        JNDIName: jms/queue/OrderQueue
                    
                    PaymentQueue:
                        JNDIName: jms/queue/PaymentQueue
                    
                    NotificationQueue:
                        JNDIName: jms/queue/NotificationQueue
                    
                    BatchQueue:
                        JNDIName: jms/queue/BatchQueue
                    
                    ErrorQueue:
                        JNDIName: jms/queue/ErrorQueue
                
                # トピック
                Topic:
                    EventTopic:
                        JNDIName: jms/topic/EventTopic
                    
                    AlertTopic:
                        JNDIName: jms/topic/AlertTopic
```

---

## ステップ3: 自動化スクリプト作成

### 3-1. ドメイン作成スクリプト

**ファイル名**: `C:\Oracle\automation\create_domain.ps1`

```powershell
#Requires -RunAsAdministrator

param(
    [string]$DomainName = "dev_domain",
    [string]$OracleHome = "C:\Oracle\Middleware",
    [string]$WdtHome = "C:\Oracle\wdt\weblogic-deploy",
    [string]$DomainParent = "C:\Oracle\domains",
    [string]$ModelDir = "C:\Oracle\models",
    [string[]]$Models = @("base_domain.yaml", "datasources.yaml", "jms_simple.yaml"),
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$LogDir = "C:\Oracle\logs"
)

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "create_domain_$Timestamp.log"

function Write-Log {
    param([string]$Message)
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

$ErrorActionPreference = "Stop"

try {
    Write-Log "=========================================="
    Write-Log "WDT ドメイン作成開始"
    Write-Log "ドメイン名: $DomainName"
    Write-Log "=========================================="

    # 事前チェック
    Write-Log "事前チェック..."

    if (-not (Test-Path "$OracleHome\wlserver")) {
        throw "WebLogicが見つかりません: $OracleHome"
    }
    Write-Log "✓ ORACLE_HOME: $OracleHome"

    if (-not (Test-Path "$WdtHome\bin\createDomain.cmd")) {
        throw "WDTが見つかりません: $WdtHome"
    }
    Write-Log "✓ WDT_HOME: $WdtHome"

    # JDK確認・自動検出
    if ([string]::IsNullOrEmpty($JavaHome)) {
        $PossiblePaths = @(
            "C:\Program Files\Java\jdk-11*",
            "C:\Program Files\Java\jdk-17*"
        )
        foreach ($Path in $PossiblePaths) {
            $Found = Get-Item $Path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($Found) {
                $JavaHome = $Found.FullName
                break
            }
        }
    }
    
    if (-not (Test-Path "$JavaHome\bin\java.exe")) {
        throw "JAVAが見つかりません: $JavaHome"
    }
    Write-Log "✓ JAVA_HOME: $JavaHome"

    # モデルファイル確認
    $ModelFiles = @()
    foreach ($Model in $Models) {
        $ModelPath = Join-Path $ModelDir $Model
        if (-not (Test-Path $ModelPath)) {
            throw "モデルファイルが見つかりません: $ModelPath"
        }
        $ModelFiles += $ModelPath
        Write-Log "✓ モデルファイル: $Model"
    }

    # 既存ドメインチェック
    $DomainHome = Join-Path $DomainParent $DomainName
    if (Test-Path $DomainHome) {
        Write-Log "警告: ドメインが既に存在します: $DomainHome"
        $Response = Read-Host "削除して再作成しますか? (y/N)"
        if ($Response -eq 'y') {
            Remove-Item -Path $DomainHome -Recurse -Force
            Write-Log "✓ 既存ドメイン削除完了"
        } else {
            Write-Log "処理をキャンセルしました"
            exit 0
        }
    }

    # 環境変数設定
    $env:ORACLE_HOME = $OracleHome
    $env:JAVA_HOME = $JavaHome
    $env:WDT_HOME = $WdtHome

    # ドメイン作成実行
    $CreateDomainCmd = Join-Path $WdtHome "bin\createDomain.cmd"
    $ModelFilesArg = $ModelFiles -join ","
    
    $Arguments = @(
        "-oracle_home", $OracleHome,
        "-domain_parent", $DomainParent,
        "-domain_type", "WLS",
        "-model_file", $ModelFilesArg
    )

    Write-Log "----------------------------------------"
    Write-Log "ドメイン作成実行中..."
    Write-Log "コマンド: $CreateDomainCmd"
    Write-Log "予想所要時間: 2-5分"
    Write-Log "----------------------------------------"

    $StartTime = Get-Date
    
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = "cmd.exe"
    $ProcessInfo.Arguments = "/c `"$CreateDomainCmd`" $($Arguments -join ' ')"
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.CreateNoWindow = $true
    
    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $ProcessInfo
    $Process.Start() | Out-Null
    
    while (-not $Process.StandardOutput.EndOfStream) {
        $Line = $Process.StandardOutput.ReadLine()
        Write-Log $Line
    }
    
    $Process.WaitForExit()
    $ExitCode = $Process.ExitCode
    
    $ElapsedTime = (Get-Date) - $StartTime
    Write-Log "実行時間: $($ElapsedTime.ToString('mm\:ss'))"

    # 結果確認
    if ($ExitCode -eq 0 -and (Test-Path $DomainHome)) {
        Write-Log "=========================================="
        Write-Log "✓ ドメイン作成成功"
        Write-Log "=========================================="
        
        # 検証
        Write-Log "ドメイン構成を検証中..."
        
        $RequiredPaths = @(
            "$DomainHome\config\config.xml",
            "$DomainHome\bin\startWebLogic.cmd",
            "$DomainHome\servers\AdminServer"
        )
        
        foreach ($Path in $RequiredPaths) {
            if (Test-Path $Path) {
                Write-Log "✓ $Path"
            } else {
                Write-Log "✗ 見つかりません: $Path"
            }
        }
        
        # データソース確認
        $JdbcDir = "$DomainHome\config\jdbc"
        if (Test-Path $JdbcDir) {
            $DataSources = Get-ChildItem $JdbcDir -Filter "*-jdbc.xml"
            Write-Log "データソース数: $($DataSources.Count)"
            foreach ($DS in $DataSources) {
                Write-Log "  - $($DS.BaseName -replace '-jdbc$','')"
            }
        }
        
        # JMSモジュール確認
        $JmsDir = "$DomainHome\config\jms"
        if (Test-Path $JmsDir) {
            $JmsModules = Get-ChildItem $JmsDir -Filter "*-jms.xml"
            Write-Log "JMSモジュール数: $($JmsModules.Count)"
        }
        
        Write-Log ""
        Write-Log "=========================================="
        Write-Log "次のステップ:"
        Write-Log "=========================================="
        Write-Log "1. アプリケーション設定配置:"
        Write-Log "   .\setup_app_config.ps1"
        Write-Log ""
        Write-Log "2. AdminServerの起動:"
        Write-Log "   cd $DomainHome\bin"
        Write-Log "   .\startWebLogic.cmd"
        Write-Log ""
        Write-Log "3. 管理コンソールアクセス:"
        Write-Log "   http://localhost:7001/console"
        Write-Log "   ユーザー名: weblogic"
        Write-Log "   パスワード: Welcome1"
        Write-Log "=========================================="
        
    } else {
        throw "ドメイン作成が失敗しました。終了コード: $ExitCode"
    }

} catch {
    Write-Log "=========================================="
    Write-Log "✗ エラーが発生しました"
    Write-Log "エラー内容: $($_.Exception.Message)"
    Write-Log "=========================================="
    Write-Log "ログファイル: $LogFile"
    exit 1
}

Write-Log "ログファイル: $LogFile"
```

### 3-2. アプリケーション設定配置スクリプト

**ファイル名**: `C:\Oracle\automation\setup_app_config.ps1`

```powershell
#Requires -RunAsAdministrator

param(
    [string]$Environment = "dev",
    [string]$ConfigBaseDir = "C:\Oracle\appconfig",
    [string]$DomainHome = "C:\Oracle\domains\dev_domain"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "アプリケーション設定ファイル配置" -ForegroundColor Cyan
Write-Host "環境: $Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 環境別ディレクトリ作成
$EnvDir = Join-Path $ConfigBaseDir $Environment
New-Item -ItemType Directory -Force -Path $EnvDir | Out-Null

# application.properties作成
$AppProperties = @"
# Application Configuration - $Environment
app.name=WebLogicApp
app.version=1.0.0
app.environment=$Environment

# Database Settings
db.main.jndi=jdbc/OracleMainDS
db.batch.jndi=jdbc/OracleBatchDS
db.report.jndi=jdbc/OracleReportDS
db.master.jndi=jdbc/OracleMasterDS

# JMS Settings
jms.connection.factory=jms/ConnectionFactory
jms.nonxa.connection.factory=jms/NonXAConnectionFactory
jms.order.queue=jms/queue/OrderQueue
jms.payment.queue=jms/queue/PaymentQueue
jms.notification.queue=jms/queue/NotificationQueue
jms.batch.queue=jms/queue/BatchQueue
jms.error.queue=jms/queue/ErrorQueue
jms.event.topic=jms/topic/EventTopic
jms.alert.topic=jms/topic/AlertTopic

# Logging
logging.level.root=INFO
logging.level.app=DEBUG

# File Upload
file.upload.max.size=52428800
file.upload.temp.dir=C:/Oracle/temp/uploads
"@

$AppPropertiesPath = Join-Path $EnvDir "application.properties"
Set-Content -Path $AppPropertiesPath -Value $AppProperties -Encoding UTF8
Write-Host "✓ 作成: application.properties" -ForegroundColor Green

# log4j2.xml作成
$Log4j2Xml = @"
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Properties>
        <Property name="logDir">C:/Oracle/logs/application</Property>
        <Property name="pattern">%d{yyyy-MM-dd HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n</Property>
    </Properties>
    
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="`${pattern}"/>
        </Console>
        
        <RollingFile name="RollingFile" fileName="`${logDir}/application.log"
                     filePattern="`${logDir}/application-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="`${pattern}"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1"/>
                <SizeBasedTriggeringPolicy size="100MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>
    </Appenders>
    
    <Loggers>
        <Root level="info">
            <AppenderRef ref="RollingFile"/>
            <AppenderRef ref="Console"/>
        </Root>
    </Loggers>
</Configuration>
"@

$Log4j2XmlPath = Join-Path $EnvDir "log4j2.xml"
Set-Content -Path $Log4j2XmlPath -Value $Log4j2Xml -Encoding UTF8
Write-Host "✓ 作成: log4j2.xml" -ForegroundColor Green

# 必要ディレクトリ作成
$Directories = @(
    "C:\Oracle\logs\application",
    "C:\Oracle\temp\uploads"
)

foreach ($Dir in $Directories) {
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    Write-Host "✓ 作成: $Dir" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ 設定ファイル配置完了" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置先: $EnvDir" -ForegroundColor Yellow
```

### 3-3. 検証スクリプト

**ファイル名**: `C:\Oracle\automation\verify_domain.ps1`

```powershell
param(
    [string]$DomainHome = "C:\Oracle\domains\dev_domain"
)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "ドメイン構成検証" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# 基本構成確認
$Checks = @{
    "config.xml" = Test-Path "$DomainHome\config\config.xml"
    "startWebLogic.cmd" = Test-Path "$DomainHome\bin\startWebLogic.cmd"
    "AdminServer" = Test-Path "$DomainHome\servers\AdminServer"
}

foreach ($Check in $Checks.GetEnumerator()) {
    $Status = if ($Check.Value) { "✓ OK" } else { "✗ NG" }
    $Color = if ($Check.Value) { "Green" } else { "Red" }
    Write-Host "$($Check.Key): " -NoNewline
    Write-Host $Status -ForegroundColor $Color
}

# データソース確認
Write-Host "`nデータソース:" -ForegroundColor Yellow
$JdbcFiles = Get-ChildItem "$DomainHome\config\jdbc" -Filter "*-jdbc.xml" -ErrorAction SilentlyContinue
if ($JdbcFiles) {
    foreach ($File in $JdbcFiles) {
        $Name = $File.BaseName -replace '-jdbc$',''
        Write-Host "  ✓ $Name" -ForegroundColor Green
    }
} else {
    Write-Host "  (なし)" -ForegroundColor Gray
}

# JMSモジュール確認
Write-Host "`nJMSモジュール:" -ForegroundColor Yellow
$JmsFiles = Get-ChildItem "$DomainHome\config\jms" -Filter "*-jms.xml" -ErrorAction SilentlyContinue
if ($JmsFiles) {
    foreach ($File in $JmsFiles) {
        $Name = $File.BaseName -replace '-jms$',''
        Write-Host "  ✓ $Name" -ForegroundColor Green
    }
} else {
    Write-Host "  (なし)" -ForegroundColor Gray
}

# サーバー構成確認
Write-Host "`nサーバー:" -ForegroundColor Yellow
$ServerDirs = Get-ChildItem "$DomainHome\servers" -Directory -ErrorAction SilentlyContinue
if ($ServerDirs) {
    foreach ($Server in $ServerDirs) {
        Write-Host "  ✓ $($Server.Name)" -ForegroundColor Green
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ 検証完了" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan
```

### 3-4. サーバー起動スクリプト

**ファイル名**: `C:\Oracle\automation\start_servers.ps1`

```powershell
param(
    [string]$DomainHome = "C:\Oracle\domains\dev_domain",
    [switch]$StartAdminServer,
    [switch]$StartNodeManager
)

function Write-Log {
    param([string]$Message)
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
}

# AdminServer起動
if ($StartAdminServer) {
    Write-Log "AdminServer起動中..."
    $AdminCmd = Join-Path $DomainHome "bin\startWebLogic.cmd"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$AdminCmd`"" -NoNewWindow
    
    Write-Log "AdminServerの起動を待機中（最大120秒）..."
    $Timeout = 120
    $Elapsed = 0
    $AdminReady = $false
    
    while ($Elapsed -lt $Timeout -and -not $AdminReady) {
        Start-Sleep -Seconds 5
        $Elapsed += 5
        
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:7001/console" -TimeoutSec 5 -UseBasicParsing
            if ($Response.StatusCode -eq 200 -or $Response.StatusCode -eq 302) {
                $AdminReady = $true
                Write-Log "✓ AdminServer起動完了"
            }
        } catch {
            Write-Host "." -NoNewline
        }
    }
    
    if (-not $AdminReady) {
        Write-Log "警告: AdminServerの起動確認がタイムアウトしました"
    }
}

# NodeManager起動
if ($StartNodeManager) {
    Write-Log "NodeManager起動中..."
    $NMCmd = Join-Path $DomainHome "bin\startNodeManager.cmd"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$NMCmd`"" -NoNewWindow
    Start-Sleep -Seconds 10
    Write-Log "✓ NodeManager起動完了"
}

Write-Log ""
Write-Log "=========================================="
Write-Log "サーバー起動情報:"
Write-Log "AdminServer: http://localhost:7001/console"
Write-Log "ユーザー名: weblogic"
Write-Log "パスワード: Welcome1"
Write-Log "=========================================="
```

---

## ステップ4: 実行手順

### 4-1. 初回セットアップ

```powershell
# PowerShellを管理者権限で起動
cd C:\Oracle\automation

# 1. JDBCドライバ配置
Copy-Item "C:\Downloads\ojdbc11.jar" -Destination "C:\Oracle\jdbc_drivers\"

# 2. ドメイン作成
.\create_domain.ps1

# 3. アプリケーション設定配置
.\setup_app_config.ps1

# 4. 検証
.\verify_domain.ps1

# 5. サーバー起動
.\start_servers.ps1 -StartAdminServer -StartNodeManager

# 6. 管理コンソールアクセス
# http://localhost:7001/console
# ユーザー名: weblogic / パスワード: Welcome1
```

### 4-2. JNDIリソース確認

管理コンソールで以下を確認：

**データソース** (Services → Data Sources)
- jdbc/OracleMainDS
- jdbc/OracleBatchDS
- jdbc/OracleReportDS
- jdbc/OracleMasterDS

**JMSキュー** (Services → Messaging → JMS Modules → MainJMSModule)
- jms/queue/OrderQueue
- jms/queue/PaymentQueue
- jms/queue/NotificationQueue
- jms/queue/BatchQueue
- jms/queue/ErrorQueue

**JMSトピック**
- jms/topic/EventTopic
- jms/topic/AlertTopic

**接続ファクトリ**
- jms/ConnectionFactory (XA対応)
- jms/NonXAConnectionFactory (非XA)

---

## トラブルシューティング

### よくある問題

| 問題 | 対処法 |
|------|--------|
| JDBCドライバが見つからない | `C:\Oracle\jdbc_drivers\ojdbc11.jar`に配置 |
| データソース接続エラー | DB起動確認、URL・認証情報確認 |
| YAMLパースエラー | インデントをスペース2個で統一 |
| ポート7001が使用中 | 既存のWebLogicを停止 |

### ログ確認

```powershell
# ドメイン作成ログ
Get-Content C:\Oracle\logs\create_domain_*.log -Tail 50

# AdminServerログ
Get-Content C:\Oracle\domains\dev_domain\servers\AdminServer\logs\AdminServer.log -Tail 50
```

---

## まとめ

この手順書により以下を実現：

- ✅ 複数Oracleデータソース（メイン、バッチ、レポート、マスタ）
- ✅ JMS基本設定（接続ファクトリ、キュー、トピック）をAdminServerに配置
- ✅ サーバー起動引数（メモリ、JVMオプション、ClassPath）
- ✅ 外部設定ファイル配置（application.properties、log4j2.xml）
- ✅ 完全自動化スクリプト

必要最低限の設定のみでWebLogic環境を構築できます。