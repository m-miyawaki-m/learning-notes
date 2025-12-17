# WebLogic ローカルホスト接続設定手順

## 概要

WebLogic起動時にIPアドレスやドメイン名でしか接続できない問題を解決し、`localhost`や`127.0.0.1`でアクセスできるようにする手順です。

---

## 問題の原因

WebLogicサーバーの`ListenAddress`が特定のIPアドレスやホスト名にバインドされている場合、localhostでの接続ができません。

**よくある設定ミス:**
- ListenAddress: `192.168.1.100` → localhostで接続不可
- ListenAddress: `hostname.example.com` → localhostで接続不可
- ListenAddress: 空欄または`0.0.0.0` → すべてのインターフェースで接続可能

---

## 解決方法

### 方法1: WDTモデルファイルで設定（推奨）

ドメイン作成時に正しく設定します。

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
            # localhost接続を有効にする設定
            # 空欄にするとすべてのネットワークインターフェースでリッスン
            ListenAddress: ''
            ListenPort: 7001
            
            # または明示的にlocalhostを指定
            # ListenAddress: localhost
            # ListenPort: 7001
            
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
                    -Djava.net.preferIPv4Stack=true
                    -Dapp.config.location=C:\Oracle\appconfig\dev
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
            
            Log:
                FileName: logs/AdminServer.log
        
        ManagedServer1:
            # Managed Serverも同様に設定
            ListenAddress: ''
            ListenPort: 8001
            Cluster: DevCluster
            
            ServerStart:
                Arguments: >
                    -Xms2048m
                    -Xmx4096m
                    -XX:+UseG1GC
                    -Djava.net.preferIPv4Stack=true
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
                Username: nodemanager
                Password: Welcome1
        
        ManagedServer2:
            ListenAddress: ''
            ListenPort: 8003
            Cluster: DevCluster
            
            ServerStart:
                Arguments: >
                    -Xms2048m
                    -Xmx4096m
                    -XX:+UseG1GC
                    -Djava.net.preferIPv4Stack=true
                ClassPath: C:\Oracle\jdbc_drivers\ojdbc11.jar
                Username: nodemanager
                Password: Welcome1
    
    Cluster:
        DevCluster:
            ClusterMessagingMode: unicast
    
    Machine:
        DevMachine:
            NodeManager:
                # NodeManagerもlocalhostで設定
                ListenAddress: localhost
                ListenPort: 5556
                NMType: Plain

    SecurityConfiguration:
        NodeManagerUsername: nodemanager
        NodeManagerPasswordEncrypted: Welcome1
```

**重要なポイント:**

1. **AdminServer の ListenAddress**
   - `ListenAddress: ''` (空欄) → すべてのインターフェースでリッスン（推奨）
   - `ListenAddress: localhost` → localhost/127.0.0.1のみ
   - `ListenAddress: 0.0.0.0` → すべてのインターフェースでリッスン

2. **Managed Server の ListenAddress**
   - 同様に空欄またはlocalhostを設定

3. **NodeManager の ListenAddress**
   - `localhost`を明示的に指定

---

### 方法2: 既存ドメインの修正（管理コンソール）

すでにドメインが作成されている場合、管理コンソールから変更します。

#### 手順

1. **AdminServerを起動**
   ```powershell
   cd C:\Oracle\domains\dev_domain\bin
   .\startWebLogic.cmd
   ```

2. **管理コンソールにログイン**
   - 現在のIPアドレスでアクセス（例: `http://192.168.1.100:7001/console`）
   - ユーザー名: `weblogic`
   - パスワード: `Welcome1`

3. **AdminServerのListenAddressを変更**
   - 左メニュー: `Environment` → `Servers`
   - `AdminServer`をクリック
   - `Configuration` タブ → `General` サブタブ
   - `Listen Address`を空欄にする、または`localhost`に変更
   - `Listen Port`: `7001`のまま
   - `Save`ボタンをクリック

4. **Managed Serverも同様に変更**
   - `ManagedServer1`, `ManagedServer2`についても同じ手順

5. **変更を有効化**
   - 左上の`Change Center`で`Activate Changes`をクリック

6. **サーバーを再起動**
   ```powershell
   # AdminServerの停止（コンソールでCtrl+C）
   # 再起動
   cd C:\Oracle\domains\dev_domain\bin
   .\startWebLogic.cmd
   ```

7. **localhostでアクセス確認**
   ```
   http://localhost:7001/console
   ```

---

### 方法3: config.xmlを直接編集

**注意**: サーバー停止中のみ実行可能

#### 手順

1. **AdminServerを停止**
   ```powershell
   # 実行中のコンソールでCtrl+C、または
   cd C:\Oracle\domains\dev_domain\bin
   .\stopWebLogic.cmd
   ```

2. **config.xmlをバックアップ**
   ```powershell
   $ConfigPath = "C:\Oracle\domains\dev_domain\config\config.xml"
   Copy-Item $ConfigPath "$ConfigPath.backup_$(Get-Date -Format 'yyyyMMddHHmmss')"
   ```

3. **config.xmlを編集**
   ```powershell
   notepad C:\Oracle\domains\dev_domain\config\config.xml
   ```

4. **ListenAddressを変更**

   **変更前:**
   ```xml
   <server>
       <name>AdminServer</name>
       <listen-address>192.168.1.100</listen-address>
       <listen-port>7001</listen-port>
   </server>
   ```

   **変更後（空欄にする場合）:**
   ```xml
   <server>
       <name>AdminServer</name>
       <listen-address></listen-address>
       <listen-port>7001</listen-port>
   </server>
   ```

   **変更後（localhostを指定する場合）:**
   ```xml
   <server>
       <name>AdminServer</name>
       <listen-address>localhost</listen-address>
       <listen-port>7001</listen-port>
   </server>
   ```

5. **Managed Serverも同様に変更**
   ```xml
   <server>
       <name>ManagedServer1</name>
       <listen-address></listen-address>
       <listen-port>8001</listen-port>
       <cluster>DevCluster</cluster>
   </server>
   ```

6. **ファイルを保存して閉じる**

7. **AdminServerを再起動**
   ```powershell
   cd C:\Oracle\domains\dev_domain\bin
   .\startWebLogic.cmd
   ```

8. **localhostでアクセス確認**
   ```
   http://localhost:7001/console
   ```

---

## 自動修正スクリプト

既存ドメインのListenAddressを一括で修正するスクリプトです。

**ファイル名**: `C:\Oracle\automation\fix_localhost_access.ps1`

```powershell
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    WebLogicドメインのListenAddressをlocalhostアクセス可能に修正

.DESCRIPTION
    config.xmlを編集してすべてのサーバーのListenAddressを空欄にします

.EXAMPLE
    .\fix_localhost_access.ps1 -DomainHome "C:\Oracle\domains\dev_domain"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainHome
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] - $Message" -ForegroundColor $Color
}

try {
    Write-Log "=========================================="
    Write-Log "localhost接続設定修正開始"
    Write-Log "=========================================="

    # config.xmlパス
    $ConfigPath = Join-Path $DomainHome "config\config.xml"
    
    if (-not (Test-Path $ConfigPath)) {
        throw "config.xmlが見つかりません: $ConfigPath"
    }

    # バックアップ作成
    $BackupPath = "$ConfigPath.backup_$(Get-Date -Format 'yyyyMMddHHmmss')"
    Copy-Item $ConfigPath $BackupPath
    Write-Log "バックアップ作成: $BackupPath" "SUCCESS"

    # config.xml読み込み
    [xml]$ConfigXml = Get-Content $ConfigPath -Encoding UTF8

    # すべてのサーバーのListenAddressを修正
    $Servers = $ConfigXml.domain.server
    $ModifiedCount = 0

    foreach ($Server in $Servers) {
        $ServerName = $Server.name
        $CurrentAddress = $Server.'listen-address'
        
        if (![string]::IsNullOrEmpty($CurrentAddress)) {
            Write-Log "修正: $ServerName (現在: $CurrentAddress → 空欄)" "WARN"
            $Server.'listen-address' = ""
            $ModifiedCount++
        } else {
            Write-Log "スキップ: $ServerName (既に空欄)" "INFO"
        }
    }

    if ($ModifiedCount -eq 0) {
        Write-Log "修正が必要なサーバーはありませんでした" "INFO"
    } else {
        # config.xml保存
        $ConfigXml.Save($ConfigPath)
        Write-Log "config.xml保存完了: $ModifiedCount 件のサーバーを修正" "SUCCESS"
        
        Write-Log ""
        Write-Log "=========================================="
        Write-Log "修正完了"
        Write-Log "=========================================="
        Write-Log "次のステップ:" "INFO"
        Write-Log "1. AdminServerを再起動してください" "INFO"
        Write-Log "2. http://localhost:7001/console でアクセス確認" "INFO"
        Write-Log ""
        Write-Log "元に戻す場合:" "WARN"
        Write-Log "Copy-Item $BackupPath $ConfigPath" "WARN"
    }

} catch {
    Write-Log "エラーが発生しました: $($_.Exception.Message)" "ERROR"
    exit 1
}
```

### スクリプトの実行

```powershell
# AdminServerを停止
cd C:\Oracle\domains\dev_domain\bin
# Ctrl+C で停止

# スクリプト実行
cd C:\Oracle\automation
.\fix_localhost_access.ps1 -DomainHome "C:\Oracle\domains\dev_domain"

# AdminServerを再起動
cd C:\Oracle\domains\dev_domain\bin
.\startWebLogic.cmd
```

---

## 検証手順

### 1. ポート確認

```powershell
# AdminServerがすべてのインターフェースでリッスンしているか確認
netstat -an | Select-String ":7001"

# 期待される出力:
# TCP    0.0.0.0:7001           0.0.0.0:0              LISTENING
# または
# TCP    127.0.0.1:7001         0.0.0.0:0              LISTENING
```

### 2. 接続テスト

```powershell
# localhost経由でテスト
Invoke-WebRequest -Uri "http://localhost:7001/console" -UseBasicParsing

# 127.0.0.1経由でテスト
Invoke-WebRequest -Uri "http://127.0.0.1:7001/console" -UseBasicParsing

# IPアドレス経由でテスト
Invoke-WebRequest -Uri "http://192.168.1.100:7001/console" -UseBasicParsing
```

### 3. ブラウザで確認

以下のURLすべてでアクセスできることを確認：

- `http://localhost:7001/console`
- `http://127.0.0.1:7001/console`
- `http://[マシンのIPアドレス]:7001/console`

---

## 推奨設定

### 開発環境

```yaml
Server:
    AdminServer:
        ListenAddress: ''  # 空欄（すべてのインターフェース）
        ListenPort: 7001
```

**メリット:**
- localhost、127.0.0.1、IPアドレスすべてでアクセス可能
- ネットワーク構成変更に強い

### 本番環境

```yaml
Server:
    AdminServer:
        ListenAddress: '10.0.1.100'  # 特定のIPアドレス
        ListenPort: 7001
```

**メリット:**
- セキュリティ向上（特定のネットワークインターフェースのみ）
- 意図しないアクセスを防止

---

## トラブルシューティング

### 問題1: localhostで接続できない

**確認事項:**
```powershell
# 1. サーバーが起動しているか
Get-Process java | Where-Object {$_.CommandLine -like "*weblogic.Server*"}

# 2. ポートがリッスンしているか
netstat -an | Select-String ":7001"

# 3. config.xmlの設定確認
Select-String -Path "C:\Oracle\domains\dev_domain\config\config.xml" -Pattern "listen-address"
```

**対処法:**
- ListenAddressが空欄またはlocalhostになっているか確認
- ファイアウォールでポート7001が許可されているか確認
- サーバーを再起動

### 問題2: IPアドレスでもアクセスできない

**確認事項:**
```powershell
# Windowsファイアウォール確認
Get-NetFirewallRule -DisplayName "*7001*"

# ポート許可
New-NetFirewallRule -DisplayName "WebLogic AdminServer" `
                    -Direction Inbound `
                    -LocalPort 7001 `
                    -Protocol TCP `
                    -Action Allow
```

### 問題3: 設定変更後もlocalhostで接続できない

**原因:** 設定がキャッシュされている可能性

**対処法:**
```powershell
# 1. AdminServerを完全停止
# 2. tmpディレクトリをクリア
Remove-Item "C:\Oracle\domains\dev_domain\servers\AdminServer\tmp" -Recurse -Force
Remove-Item "C:\Oracle\domains\dev_domain\servers\AdminServer\cache" -Recurse -Force

# 3. AdminServerを起動
cd C:\Oracle\domains\dev_domain\bin
.\startWebLogic.cmd
```

---

## まとめ

### localhost接続を有効にする方法

1. **WDTモデルファイル（推奨）**
   - `ListenAddress: ''` で作成時に設定

2. **管理コンソール**
   - GUI経由でListenAddressを変更

3. **config.xml直接編集**
   - サーバー停止中に手動編集

4. **自動修正スクリプト**
   - 既存ドメインを一括修正

### 推奨設定

- **開発環境**: `ListenAddress: ''` (空欄)
- **本番環境**: 特定のIPアドレスを指定

これにより、localhost、127.0.0.1、IPアドレスすべてでWebLogicにアクセス可能になります。