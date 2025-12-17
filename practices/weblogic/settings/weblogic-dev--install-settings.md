# WebLogic 14 Windows 11 サイレントインストール手順書（開発環境向け）

## 概要

WebLogic 14のWindows 11開発環境でのサイレントインストールを、**レスポンスファイル準備 → JDK確認 → インストール実行 → 検証**の4ステップで手順化します。

---

## 前提条件

- Windows 11 Home/Pro/Enterprise
- JDK 11以降がインストール済み
- ローカル管理者権限
- WebLogic 14インストーラ（`fmw_14.1.x.x_wls.jar`）を入手済み
- 最低5GB以上の空きディスク容量

---

## ステップ1: ディレクトリ構成準備
```powershell
# 作業ディレクトリ作成
New-Item -ItemType Directory -Force -Path C:\Oracle\Middleware
New-Item -ItemType Directory -Force -Path C:\Oracle\automation
New-Item -ItemType Directory -Force -Path C:\Oracle\logs
```

### ディレクトリ構成
```
C:\Oracle\
  ├─ Middleware\        # ORACLE_HOME（インストール先）
  ├─ automation\        # レスポンスファイル、スクリプト
  └─ logs\             # インストールログ
```

---

## ステップ2: レスポンスファイル作成

### 2-1. 開発環境向けレスポンスファイル

ファイル名: `C:\Oracle\automation\wls_install.rsp`
```properties
[ENGINE]

#DO NOT CHANGE THIS.
Response File Version=1.0.0.0.0

[GENERIC]

#Set this to true if you wish to skip software updates
DECLINE_AUTO_UPDATES=true

#My Oracle Support User Name
MOS_USERNAME=

#My Oracle Support Password
MOS_PASSWORD=<SECURE VALUE>

#If the Software updates are already downloaded and available on your local system, then specify the path to the directory where these patches are available and set SPECIFY_DOWNLOAD_LOCATION to true
AUTO_UPDATES_LOCATION=

#Proxy Server Name to connect to My Oracle Support
SOFTWARE_UPDATES_PROXY_SERVER=

#Proxy Server Port
SOFTWARE_UPDATES_PROXY_PORT=

#Proxy Server Username
SOFTWARE_UPDATES_PROXY_USER=

#Proxy Server Password
SOFTWARE_UPDATES_PROXY_PASSWORD=<SECURE VALUE>

#The oracle home location. This can be an existing Oracle Home or a new Oracle Home
ORACLE_HOME=C:\Oracle\Middleware

#Set this variable value to the Installation Type selected
# Options: WebLogic Server, Coherence, Complete with Examples
# 開発環境では Complete with Examples を推奨
INSTALL_TYPE=Complete with Examples

#Provide the My Oracle Support Username. If you wish to ignore Oracle Configuration Manager configuration provide empty string for user name.
MYORACLESUPPORT_USERNAME=

#Provide the My Oracle Support Password
MYORACLESUPPORT_PASSWORD=<SECURE VALUE>

#Set this to true if you wish to decline the security updates. Setting this to true and providing empty string for My Oracle Support username will ignore the Oracle Configuration Manager configuration
DECLINE_SECURITY_UPDATES=true

#Set this to true if My Oracle Support Password is specified
SECURITY_UPDATES_VIA_MYORACLESUPPORT=false

#Provide the Proxy Host
PROXY_HOST=

#Provide the Proxy Port
PROXY_PORT=

#Provide the Proxy Username
PROXY_USER=

#Provide the Proxy Password
PROXY_PWD=<SECURE VALUE>

#Type String (URL format) Indicates the OCM Repeater URL which should be of the format [scheme[Http/Https]]://[repeater host]:[repeater port]
COLLECTOR_SUPPORTHUB_URL=
```

### 2-2. 開発環境向けカスタマイズポイント
```properties
# 開発環境の推奨設定
ORACLE_HOME=C:\Oracle\Middleware              # インストール先
INSTALL_TYPE=Complete with Examples           # サンプル含む完全インストール

# セキュリティ更新を無効化（開発環境では推奨）
DECLINE_AUTO_UPDATES=true
DECLINE_SECURITY_UPDATES=true
```

### 2-3. インストールタイプの選択

| インストールタイプ | 説明 | 推奨環境 | ディスク容量 |
|-------------------|------|----------|------------|
| `WebLogic Server` | 基本機能のみ | 本番環境 | 約2GB |
| `Coherence` | Coherence機能追加 | キャッシュ利用時 | 約2.5GB |
| `Complete with Examples` | 全機能+サンプル | **開発環境** | 約3GB |

---

## ステップ3: インストールスクリプト作成

ファイル名: `C:\Oracle\automation\install_weblogic.ps1`
```powershell
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    WebLogic Server 14 サイレントインストールスクリプト（Windows 11開発環境向け）

.DESCRIPTION
    レスポンスファイルを使用してWebLogic Serverをサイレントインストールします

.PARAMETER InstallerPath
    WebLogicインストーラ(jar)のパス

.PARAMETER ResponseFile
    レスポンスファイルのパス

.PARAMETER JavaHome
    使用するJDKのホームディレクトリ

.EXAMPLE
    .\install_weblogic.ps1 -InstallerPath "C:\Downloads\fmw_14.1.1.0.0_wls.jar"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallerPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ResponseFile = "C:\Oracle\automation\wls_install.rsp",
    
    [Parameter(Mandatory=$false)]
    [string]$JavaHome = $env:JAVA_HOME,
    
    [Parameter(Mandatory=$false)]
    [string]$OracleHome = "C:\Oracle\Middleware",
    
    [Parameter(Mandatory=$false)]
    [string]$LogDir = "C:\Oracle\logs"
)

# ログファイル設定
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "wls_install_$Timestamp.log"
$InventoryLog = Join-Path $LogDir "wls_inventory_$Timestamp.log"

# ログ関数
function Write-Log {
    param([string]$Message)
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

# エラーハンドリング
$ErrorActionPreference = "Stop"

try {
    Write-Log "=========================================="
    Write-Log "WebLogic Server 14 サイレントインストール開始"
    Write-Log "環境: Windows 11 開発環境"
    Write-Log "=========================================="

    # 事前チェック
    Write-Log "事前チェックを実行中..."
    
    # 1. Windows 11確認
    $OSVersion = [System.Environment]::OSVersion.Version
    $OSName = (Get-CimInstance Win32_OperatingSystem).Caption
    Write-Log "OS: $OSName (Version: $OSVersion)"
    
    # 2. インストーラの存在確認
    if (-not (Test-Path $InstallerPath)) {
        throw "インストーラが見つかりません: $InstallerPath"
    }
    Write-Log "✓ インストーラ確認: $InstallerPath"

    # 3. レスポンスファイルの存在確認
    if (-not (Test-Path $ResponseFile)) {
        throw "レスポンスファイルが見つかりません: $ResponseFile"
    }
    Write-Log "✓ レスポンスファイル確認: $ResponseFile"

    # 4. JDKの確認
    if ([string]::IsNullOrEmpty($JavaHome)) {
        # JAVA_HOMEが未設定の場合、一般的なパスを検索
        $PossibleJavaPaths = @(
            "C:\Program Files\Java\jdk-11*",
            "C:\Program Files\Java\jdk-17*",
            "C:\Program Files\Eclipse Adoptium\jdk-11*",
            "C:\Program Files\Eclipse Adoptium\jdk-17*"
        )
        
        foreach ($Path in $PossibleJavaPaths) {
            $Found = Get-Item $Path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($Found) {
                $JavaHome = $Found.FullName
                Write-Log "JDKを自動検出: $JavaHome"
                break
            }
        }
        
        if ([string]::IsNullOrEmpty($JavaHome)) {
            throw "JAVA_HOMEが設定されておらず、JDKも見つかりません。JDK 11以降をインストールしてください。"
        }
    }
    
    if (-not (Test-Path "$JavaHome\bin\java.exe")) {
        throw "JavaがJAVA_HOMEに見つかりません: $JavaHome"
    }
    
    # Javaバージョン確認
    $JavaVersionOutput = & "$JavaHome\bin\java.exe" -version 2>&1
    $JavaVersionLine = $JavaVersionOutput | Select-String "version" | Select-Object -First 1
    Write-Log "✓ Java確認: $JavaVersionLine"
    
    # バージョン番号抽出（簡易チェック）
    if ($JavaVersionOutput -match '"(1\.8|9|10)') {
        Write-Log "警告: WebLogic 14にはJDK 11以降が推奨されます"
    }

    # 5. 既存インストールのチェック
    if (Test-Path "$OracleHome\wlserver") {
        Write-Log "警告: WebLogicが既にインストールされています: $OracleHome"
        Write-Log "開発環境では上書きインストールを推奨しません"
        $Response = Read-Host "続行しますか? (y/N)"
        if ($Response -ne 'y') {
            Write-Log "インストールをキャンセルしました"
            exit 0
        }
    }

    # 6. ディスク容量チェック（開発環境: 最低5GB、推奨10GB）
    $Drive = Split-Path $OracleHome -Qualifier
    $FreeSpace = (Get-PSDrive ($Drive -replace ':')).Free / 1GB
    if ($FreeSpace -lt 5) {
        throw "ディスク空き容量が不足しています: $([math]::Round($FreeSpace, 2))GB（最低5GB必要）"
    }
    Write-Log "✓ ディスク空き容量: $([math]::Round($FreeSpace, 2))GB"
    
    if ($FreeSpace -lt 10) {
        Write-Log "推奨: 開発環境では10GB以上の空き容量を推奨します"
    }

    # 7. Windows Defender除外設定の確認（開発環境で推奨）
    Write-Log "情報: インストール後、Windows DefenderからOracle関連フォルダを除外することを推奨します"
    Write-Log "      除外パス例: $OracleHome"

    # 8. ファイアウォール確認（開発環境）
    Write-Log "情報: WebLogicの管理コンソール（デフォルト:7001）へのアクセスに"
    Write-Log "      ファイアウォールルールが必要な場合があります"

    # インストール実行
    Write-Log "----------------------------------------"
    Write-Log "インストールを開始します..."
    Write-Log "ORACLE_HOME: $OracleHome"
    Write-Log "インストールタイプ: Complete with Examples (開発環境向け)"
    Write-Log "----------------------------------------"

    # インストールコマンド構築
    $JavaExe = Join-Path $JavaHome "bin\java.exe"
    $InstallArgs = @(
        "-jar",
        "`"$InstallerPath`"",
        "-silent",
        "-responseFile", "`"$ResponseFile`"",
        "-invPtrLoc", "`"$InventoryLog`""
    )

    Write-Log "実行コマンド: $JavaExe $($InstallArgs -join ' ')"
    Write-Log "予想所要時間: 5-15分"

    # インストール実行
    $StartTime = Get-Date
    $Process = Start-Process -FilePath $JavaExe `
                              -ArgumentList $InstallArgs `
                              -NoNewWindow `
                              -PassThru `
                              -Wait

    $ElapsedTime = (Get-Date) - $StartTime
    Write-Log "インストール実行時間: $($ElapsedTime.ToString('mm\:ss'))"

    # 結果確認
    if ($Process.ExitCode -eq 0) {
        Write-Log "=========================================="
        Write-Log "✓ インストールが正常に完了しました"
        Write-Log "=========================================="
        
        # インストール検証
        Write-Log "インストール検証中..."
        
        $RequiredPaths = @(
            "$OracleHome\wlserver",
            "$OracleHome\oracle_common",
            "$OracleHome\wlserver\server\bin\setWLSEnv.cmd",
            "$OracleHome\wlserver\samples"  # 開発環境ではサンプル確認
        )
        
        $AllPathsExist = $true
        foreach ($Path in $RequiredPaths) {
            if (Test-Path $Path) {
                Write-Log "✓ 存在確認: $Path"
            } else {
                Write-Log "✗ 見つかりません: $Path"
                $AllPathsExist = $false
            }
        }
        
        if ($AllPathsExist) {
            Write-Log "✓ インストール検証成功"
            
            # バージョン情報取得
            $RegistryPath = "$OracleHome\inventory\registry.xml"
            if (Test-Path $RegistryPath) {
                $Version = Select-String -Path $RegistryPath -Pattern 'version="([^"]+)"' | 
                           Select-Object -First 1 | 
                           ForEach-Object { $_.Matches.Groups[1].Value }
                Write-Log "インストールバージョン: $Version"
            }
            
            # 開発環境向けのサンプル情報
            $SamplesPath = "$OracleHome\wlserver\samples"
            if (Test-Path $SamplesPath) {
                $SampleDirs = Get-ChildItem $SamplesPath -Directory
                Write-Log "利用可能なサンプル: $($SampleDirs.Count)個"
            }
        } else {
            Write-Log "警告: 一部のファイルが見つかりません"
        }
        
        # 次のステップを案内（開発環境向け）
        Write-Log ""
        Write-Log "=========================================="
        Write-Log "次のステップ（開発環境）:"
        Write-Log "=========================================="
        Write-Log "1. 環境変数の設定（推奨）:"
        Write-Log "   [System.Environment]::SetEnvironmentVariable('ORACLE_HOME', '$OracleHome', 'User')"
        Write-Log ""
        Write-Log "2. Windows Defender除外設定（パフォーマンス向上）:"
        Write-Log "   Add-MpPreference -ExclusionPath '$OracleHome'"
        Write-Log ""
        Write-Log "3. ドメイン作成:"
        Write-Log "   .\create_domain.ps1 を実行"
        Write-Log ""
        Write-Log "4. サンプルドメインの確認:"
        Write-Log "   $OracleHome\wlserver\samples"
        Write-Log "=========================================="
        
    } else {
        throw "インストールが失敗しました。終了コード: $($Process.ExitCode)"
    }

} catch {
    Write-Log "=========================================="
    Write-Log "✗ エラーが発生しました"
    Write-Log "エラー内容: $($_.Exception.Message)"
    Write-Log "=========================================="
    Write-Log ""
    Write-Log "トラブルシューティング:"
    Write-Log "1. JDKバージョンの確認（JDK 11以降が必要）"
    Write-Log "2. 管理者権限での実行確認"
    Write-Log "3. ウイルス対策ソフトの一時無効化"
    Write-Log "4. ログファイルの確認: $LogFile"
    exit 1
}

Write-Log "ログファイル: $LogFile"
Write-Log "完了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
```

---

## ステップ4: インストール実行

### 4-1. 実行方法（通常）
```powershell
# PowerShellを管理者権限で起動
# スタートメニュー → PowerShell → 右クリック → 管理者として実行

# 作業ディレクトリに移動
cd C:\Oracle\automation

# 実行ポリシーの確認・変更（初回のみ）
Get-ExecutionPolicy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# スクリプト実行
.\install_weblogic.ps1 -InstallerPath "C:\Downloads\fmw_14.1.1.0.0_wls.jar"
```

### 4-2. パラメータ指定
```powershell
# すべてのパラメータを指定
.\install_weblogic.ps1 `
    -InstallerPath "C:\Downloads\fmw_14.1.1.0.0_wls.jar" `
    -ResponseFile "C:\Oracle\automation\wls_install.rsp" `
    -JavaHome "C:\Program Files\Java\jdk-11.0.16" `
    -OracleHome "C:\Oracle\Middleware"
```

### 4-3. JDK自動検出
```powershell
# JAVA_HOMEが未設定でもOK（自動検出）
.\install_weblogic.ps1 -InstallerPath "C:\Downloads\fmw_14.1.1.0.0_wls.jar"
```

---

## ステップ5: インストール検証

### 5-1. 手動検証
```powershell
# 1. ディレクトリ確認
Test-Path C:\Oracle\Middleware\wlserver
Test-Path C:\Oracle\Middleware\wlserver\samples

# 2. バージョン確認
cd C:\Oracle\Middleware\wlserver\server\bin
.\setWLSEnv.cmd
java weblogic.version

# 期待される出力:
# WebLogic Server 14.1.1.0.0  Tue Dec 15 10:49:50 PST 2020 1900218
```

### 5-2. 検証スクリプト（開発環境向け）

ファイル名: `C:\Oracle\automation\verify_install.ps1`
```powershell
param(
    [string]$OracleHome = "C:\Oracle\Middleware"
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "WebLogic インストール検証（開発環境）" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$Checks = @{
    "ORACLE_HOME存在" = Test-Path $OracleHome
    "wlserver存在" = Test-Path "$OracleHome\wlserver"
    "oracle_common存在" = Test-Path "$OracleHome\oracle_common"
    "setWLSEnv.cmd存在" = Test-Path "$OracleHome\wlserver\server\bin\setWLSEnv.cmd"
    "weblogic.jar存在" = Test-Path "$OracleHome\wlserver\server\lib\weblogic.jar"
    "サンプル存在" = Test-Path "$OracleHome\wlserver\samples"
    "管理コンソール war存在" = Test-Path "$OracleHome\wlserver\server\lib\consoleapp\webapp\console.war"
}

$AllPassed = $true
foreach ($Check in $Checks.GetEnumerator()) {
    $Status = if ($Check.Value) { 
        "✓ PASS" 
    } else { 
        "✗ FAIL"
        $AllPassed = $false 
    }
    $Color = if ($Check.Value) { "Green" } else { "Red" }
    Write-Host "$($Check.Key): " -NoNewline
    Write-Host $Status -ForegroundColor $Color
}

Write-Host ""

# 追加情報（開発環境向け）
if (Test-Path "$OracleHome\wlserver\samples") {
    $SampleDirs = Get-ChildItem "$OracleHome\wlserver\samples" -Directory
    Write-Host "利用可能なサンプル: $($SampleDirs.Count)個" -ForegroundColor Yellow
    foreach ($Dir in $SampleDirs | Select-Object -First 5) {
        Write-Host "  - $($Dir.Name)" -ForegroundColor Gray
    }
    if ($SampleDirs.Count -gt 5) {
        Write-Host "  ... 他 $($SampleDirs.Count - 5)個" -ForegroundColor Gray
    }
    Write-Host ""
}

# 環境変数チェック
Write-Host "環境変数チェック:" -ForegroundColor Cyan
$EnvVars = @{
    "JAVA_HOME" = $env:JAVA_HOME
    "ORACLE_HOME" = $env:ORACLE_HOME
}

foreach ($Var in $EnvVars.GetEnumerator()) {
    $Value = if ($Var.Value) { $Var.Value } else { "(未設定)" }
    $Color = if ($Var.Value) { "Green" } else { "Yellow" }
    Write-Host "  $($Var.Key): " -NoNewline
    Write-Host $Value -ForegroundColor $Color
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if ($AllPassed) {
    Write-Host "✓ インストール検証成功" -ForegroundColor Green
    Write-Host ""
    Write-Host "次のステップ:" -ForegroundColor Yellow
    Write-Host "1. ドメインを作成: .\create_domain.ps1"
    Write-Host "2. サンプルを確認: $OracleHome\wlserver\samples"
    exit 0
} else {
    Write-Host "✗ インストール検証失敗" -ForegroundColor Red
    Write-Host "一部のコンポーネントが見つかりません" -ForegroundColor Red
    exit 1
}
```

### 5-3. 検証実行
```powershell
cd C:\Oracle\automation
.\verify_install.ps1
```

---

## ステップ6: 開発環境向け追加設定

### 6-1. 環境変数設定（推奨）
```powershell
# ユーザー環境変数に設定（推奨）
[System.Environment]::SetEnvironmentVariable('ORACLE_HOME', 'C:\Oracle\Middleware', 'User')
[System.Environment]::SetEnvironmentVariable('WL_HOME', 'C:\Oracle\Middleware\wlserver', 'User')

# 確認
$env:ORACLE_HOME
$env:WL_HOME

# PowerShellを再起動して反映
```

### 6-2. Windows Defender除外設定（パフォーマンス向上）
```powershell
# 管理者権限で実行
Add-MpPreference -ExclusionPath "C:\Oracle\Middleware"
Add-MpPreference -ExclusionPath "C:\Oracle\domains"

# 確認
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### 6-3. ファイアウォール設定（ローカル開発用）
```powershell
# WebLogic管理コンソール用ポート（7001）を開放
New-NetFirewallRule -DisplayName "WebLogic Admin Console" `
                    -Direction Inbound `
                    -LocalPort 7001 `
                    -Protocol TCP `
                    -Action Allow

# 確認
Get-NetFirewallRule -DisplayName "WebLogic Admin Console"
```

### 6-4. パフォーマンスチューニング（開発環境）
```powershell
# ページングファイルサイズ確認
Get-CimInstance Win32_PageFileUsage

# メモリ確認
Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum | 
    ForEach-Object { "合計メモリ: $([math]::Round($_.Sum/1GB, 2))GB" }
```

---

## トラブルシューティング

### よくあるエラーと対処法（Windows 11開発環境）

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `ExecutionPolicy制限` | PowerShell実行ポリシー | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `java.io.FileNotFoundException` | パスに日本語含む | 英数字のみのパスを使用 |
| `Insufficient disk space` | ディスク容量不足 | 最低5GB確保（推奨10GB） |
| `Invalid ORACLE_HOME` | パスにスペース含む | スペースなしのパスを使用 |
| `java version error` | JDKバージョン不適合 | JDK 11または17を使用 |
| `Access Denied` | 管理者権限不足 | PowerShellを管理者として実行 |
| インストールが遅い | Windows Defender | 除外設定を追加 |

### ログ確認
```powershell
# インストールログ
Get-Content C:\Oracle\logs\wls_install_*.log -Tail 50

# エラー行のみ抽出
Get-Content C:\Oracle\logs\wls_install_*.log | Select-String -Pattern "error|fail|exception" -CaseSensitive:$false

# Oracleインベントリログ
$InventoryPath = Join-Path $env:ProgramFiles "Oracle\Inventory\logs"
if (Test-Path $InventoryPath) {
    Get-ChildItem $InventoryPath | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
}
```

---

## 開発環境向けTips

### サンプルドメインの活用
```powershell
# サンプルディレクトリの確認
explorer C:\Oracle\Middleware\wlserver\samples

# 主なサンプル:
# - server\examples: 各種サンプルアプリケーション
# - server\config: 設定ファイルサンプル
```

### IDEとの統合

#### IntelliJ IDEA
1. File → Project Structure → SDKs
2. Add → Application Server → WebLogic
3. WebLogic Home: `C:\Oracle\Middleware\wlserver`

#### Eclipse
1. Window → Preferences → Server → Runtime Environments
2. Add → Oracle → Oracle WebLogic Server 14c
3. WebLogic Home: `C:\Oracle\Middleware`

### よく使うコマンド
```powershell
# WebLogic環境変数設定
cd C:\Oracle\Middleware\wlserver\server\bin
.\setWLSEnv.cmd

# バージョン確認
java weblogic.version

# ドメイン作成ウィザード起動（GUI）
.\config.cmd
```

---

## 次のステップ

インストール完了後は、以下の手順に進みます:

1. **ドメイン作成**: WDTを使用したドメイン作成スクリプトの実行
2. **アプリケーションデプロイ**: サンプルアプリケーションのデプロイ
3. **開発環境統合**: IDEとの連携設定

---

## 付録: 開発環境向けチェックリスト

### インストール前

- [ ] JDK 11または17がインストール済み
- [ ] 最低5GB以上の空きディスク容量
- [ ] 管理者権限の確認
- [ ] ウイルス対策ソフトの確認

### インストール後

- [ ] インストール検証スクリプトの実行
- [ ] 環境変数の設定
- [ ] Windows Defender除外設定
- [ ] ファイアウォール設定（必要に応じて）
- [ ] サンプルの確認

### ドメイン作成前

- [ ] WDTのダウンロード
- [ ] ドメイン設計（ポート番号、管理者パスワードなど）
- [ ] ネットワーク設定の確認

---

## 参考情報

### Oracle公式ドキュメント
- [WebLogic Server 14.1.1 ドキュメント](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/)
- [WebLogic Deploy Tooling](https://oracle.github.io/weblogic-deploy-tooling/)

### システム要件
- **OS**: Windows 11 (22H2以降推奨)
- **Java**: JDK 11.0.15+, JDK 17.0.3+
- **メモリ**: 最低4GB（推奨8GB以上）
- **ディスク**: 最低5GB（推奨10GB以上）

### 推奨JDK
- Oracle JDK 11 / 17
- Eclipse Adoptium (旧AdoptOpenJDK) 11 / 17
- Amazon Corretto 11 / 17

---

**作成日**: 2025-12-18  
**対象バージョン**: WebLogic Server 14.1.x  
**対象OS**: Windows 11 Home/Pro/Enterprise  
**用途**: 開発環境