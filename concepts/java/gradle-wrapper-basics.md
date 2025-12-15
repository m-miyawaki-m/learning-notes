# Gradle Wrapper（gradlew）基礎学習ノート

> 対象: Gradle初学者、Java開発者
> 環境: Windows, macOS, Linux

## 学習目標

- Gradle Wrapperとは何かを理解する
- gradlewとgradleコマンドの違いを把握する
- Gradle Wrapperの仕組みと利点を学ぶ
- gradlewの基本的な使い方をマスターする

---

## 1. Gradle Wrapperとは

### 1.1 概要

**Gradle Wrapper**（グラドル・ラッパー）は、Gradleビルドツールを**プロジェクトにバンドル**する仕組みです。

```
┌─────────────────────────────────────────┐
│ あなたのプロジェクト                      │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Gradle Wrapper (gradlew)         │  │
│  │                                  │  │
│  │ ・Gradleの特定バージョンを       │  │
│  │   自動的にダウンロード           │  │
│  │ ・プロジェクト専用のGradle       │  │
│  └──────────────────────────────────┘  │
│                                         │
│  build.gradle                           │
│  settings.gradle                        │
│  src/                                   │
└─────────────────────────────────────────┘
```

### 1.2 なぜGradle Wrapperが必要なのか

#### 問題: Gradleをシステムにインストールする場合

```bash
# 開発者Aのマシン
$ gradle --version
Gradle 7.2

# 開発者Bのマシン
$ gradle --version
Gradle 8.0

# ビルドが失敗する可能性がある！
```

**問題点**:
- ✗ 各開発者が異なるGradleバージョンを使用
- ✗ CIサーバーのGradleバージョンが開発環境と異なる
- ✗ 新しい開発者が環境構築に時間がかかる
- ✗ プロジェクトに必要なGradleバージョンが不明

#### 解決策: Gradle Wrapperを使用

```bash
# どのマシンでも同じGradleバージョンが使用される
$ ./gradlew --version
Gradle 7.2

# プロジェクト指定のバージョンが自動的にダウンロードされる！
```

**メリット**:
- ✓ プロジェクトごとに異なるGradleバージョンを使用可能
- ✓ Gradleのインストール不要
- ✓ ビルドの再現性が保証される
- ✓ 新しい開発者がすぐにビルドできる

---

## 2. gradlewの正体

### 2.1 gradlewファイルの実体

プロジェクトルートに以下のファイルが存在します：

```
my-project/
├── gradlew              ← Unix/Linux/macOS用のシェルスクリプト
├── gradlew.bat          ← Windows用のバッチスクリプト
└── gradle/
    └── wrapper/
        ├── gradle-wrapper.jar       ← Wrapper実行用のJavaプログラム
        └── gradle-wrapper.properties ← Gradleバージョン設定ファイル
```

### 2.2 各ファイルの役割

#### gradlew（シェルスクリプト）

```bash
#!/bin/sh
# Unix/Linux/macOS用のラッパースクリプト
# Javaを探して、gradle-wrapper.jarを実行する
```

**実行方法**:
```bash
./gradlew build
```

#### gradlew.bat（バッチスクリプト）

```batch
@rem Windows用のラッパースクリプト
@rem Javaを探して、gradle-wrapper.jarを実行する
```

**実行方法**:
```cmd
gradlew.bat build
REM または単に
gradlew build
```

#### gradle-wrapper.jar

- **Gradle Wrapperの本体**（小さなJavaプログラム）
- 指定されたGradleバージョンをダウンロード・実行する

#### gradle-wrapper.properties

```properties
# Gradleの配布URL
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

**重要**: `distributionUrl`がGradleのバージョンを指定します。

---

## 3. gradlewの動作の仕組み

### 3.1 初回実行時の流れ

```
1. ./gradlew build を実行
         ↓
2. gradlewスクリプトが gradle-wrapper.jar を起動
         ↓
3. gradle-wrapper.properties を読み込み
         ↓
4. 指定されたGradleをダウンロード（初回のみ）
   → ~/.gradle/wrapper/dists/ に保存
         ↓
5. ダウンロードしたGradleを実行
         ↓
6. build.gradle のタスクを実行
         ↓
7. ビルド完了
```

### 3.2 2回目以降の実行

```
1. ./gradlew build を実行
         ↓
2. キャッシュされたGradleを確認
   → ~/.gradle/wrapper/dists/gradle-7.2-bin/ に存在
         ↓
3. キャッシュを使用（ダウンロードなし）
         ↓
4. ビルド実行
```

### 3.3 実際のファイルの場所

```bash
# Gradleのダウンロード先（キャッシュ）
~/.gradle/wrapper/dists/
└── gradle-7.2-bin/
    └── 2dnblmf4td7x66yl1d74lt32g/
        └── gradle-7.2/
            ├── bin/
            │   └── gradle        ← 実際のGradle実行ファイル
            └── lib/
                └── gradle-*.jar

# 初回実行時のダウンロード例
$ ./gradlew build
Downloading https://services.gradle.org/distributions/gradle-7.2-bin.zip
..........10%.........20%.........30%
✓ ダウンロード完了
```

---

## 4. gradlewとgradleの違い

### 4.1 コマンド比較

| 項目 | `gradlew` | `gradle` |
|------|-----------|----------|
| **正式名称** | Gradle Wrapper | Gradle CLI |
| **実行ファイル** | `./gradlew` (スクリプト) | `gradle` (システムコマンド) |
| **Gradleの取得方法** | プロジェクトが自動ダウンロード | 事前にシステムにインストール |
| **バージョン管理** | プロジェクトで指定 | システム全体で統一 |
| **インストール** | 不要 | 必要 |
| **推奨** | ✓ 推奨（チーム開発） | △ 個人開発のみ |

### 4.2 実行例

#### gradlew（推奨）

```bash
# プロジェクト指定のバージョン（7.2）を使用
$ ./gradlew --version

------------------------------------------------------------
Gradle 7.2
------------------------------------------------------------

Build time:   2021-08-17 09:59:03 UTC
Revision:     a773786b58bb28710e3dc96c4d1a7063628952ad

Kotlin:       1.5.21
Groovy:       3.0.8
Ant:          Apache Ant(TM) version 1.10.9 compiled on September 27 2020
JVM:          11.0.12 (Oracle Corporation 11.0.12+8-LTS-237)
OS:           Linux 5.4.0-42-generic amd64
```

#### gradle（非推奨）

```bash
# システムにインストールされたバージョンを使用
$ gradle --version

------------------------------------------------------------
Gradle 8.0
------------------------------------------------------------
# プロジェクトが期待するバージョンと異なる可能性がある！
```

---

## 5. gradlewの基本的な使い方

### 5.1 実行権限の付与（Linux/macOS）

```bash
# 初回のみ: 実行権限を付与
chmod +x gradlew

# これで実行可能になる
./gradlew build
```

### 5.2 基本コマンド

#### ビルド

```bash
# プロジェクト全体をビルド
./gradlew build

# クリーンビルド（前回の成果物を削除してからビルド）
./gradlew clean build
```

#### テスト

```bash
# テストを実行
./gradlew test

# 特定のテストのみ実行
./gradlew test --tests "com.example.MyTest"
```

#### タスク一覧表示

```bash
# 利用可能なタスク一覧を表示
./gradlew tasks

# すべてのタスク（内部タスク含む）を表示
./gradlew tasks --all
```

#### 依存関係の確認

```bash
# 依存関係ツリーを表示
./gradlew dependencies

# 特定の設定の依存関係のみ表示
./gradlew dependencies --configuration runtimeClasspath
```

#### バージョン確認

```bash
# Gradleバージョンとプロジェクト情報を表示
./gradlew --version

# プロジェクト情報を表示
./gradlew properties
```

### 5.3 よく使うオプション

```bash
# スタックトレースを表示（エラー時）
./gradlew build --stacktrace

# 詳細なログを表示
./gradlew build --info

# デバッグログを表示
./gradlew build --debug

# ビルドキャッシュを使用
./gradlew build --build-cache

# オフラインモード（ネットワークアクセスなし）
./gradlew build --offline

# 並列実行
./gradlew build --parallel

# 継続モード（ファイル変更を監視して自動実行）
./gradlew build --continuous
```

---

## 6. Gradle Wrapperのセットアップ

### 6.1 新しいプロジェクトでのセットアップ

#### 方法1: Gradleがインストール済みの場合

```bash
# プロジェクトディレクトリに移動
cd my-project

# Gradle Wrapperを生成
gradle wrapper --gradle-version 7.2

# 生成されたファイル
ls -la
# gradlew
# gradlew.bat
# gradle/wrapper/gradle-wrapper.jar
# gradle/wrapper/gradle-wrapper.properties
```

#### 方法2: Gradleがない場合

1. 既存プロジェクトからコピー:
   ```bash
   # 別のプロジェクトからコピー
   cp -r other-project/gradlew .
   cp -r other-project/gradlew.bat .
   cp -r other-project/gradle .

   chmod +x gradlew
   ```

2. 手動でダウンロード:
   - [Gradle公式サイト](https://gradle.org/)から一時的にGradleをダウンロード
   - `gradle wrapper`を実行
   - ダウンロードしたGradleを削除

### 6.2 Gradleバージョンの変更

#### 方法1: gradle-wrapper.propertiesを直接編集

```properties
# gradle/wrapper/gradle-wrapper.properties
distributionUrl=https\://services.gradle.org/distributions/gradle-7.6-bin.zip
#                                                          ^^^^^^
#                                                          バージョンを変更
```

変更後、次回実行時に新バージョンが自動ダウンロードされます:
```bash
./gradlew build
# Gradle 7.6をダウンロード...
```

#### 方法2: wrapperタスクを使用

```bash
# Gradleバージョンを8.0に更新
./gradlew wrapper --gradle-version 8.0

# 配布形式も指定可能
./gradlew wrapper --gradle-version 7.6 --distribution-type all
```

**配布形式**:
- `bin`: バイナリのみ（デフォルト、軽量）
- `all`: ソースとドキュメント含む（IDE補完に有用）

---

## 7. gradle-wrapper.propertiesの詳細

```properties
# Gradleのダウンロード先ベースディレクトリ
distributionBase=GRADLE_USER_HOME
# → ~/.gradle/ を指す

# ダウンロード先の相対パス
distributionPath=wrapper/dists
# → ~/.gradle/wrapper/dists/

# GradleのダウンロードURL（重要！）
distributionUrl=https\://services.gradle.org/distributions/gradle-7.2-bin.zip
# ↑ バージョンと配布形式を指定

# ZIPファイルの保存先ベース
zipStoreBase=GRADLE_USER_HOME

# ZIPファイルの保存先相対パス
zipStorePath=wrapper/dists

# バリデーション（オプション、Gradle 6.6+）
distributionSha256Sum=f581709a9c35e9cb92e16f585d2c4bc99b2b1a5f85d2badbd3dc6bff59e1e6dd
# ↑ ダウンロードしたZIPのチェックサム検証（セキュリティ強化）
```

### 7.1 配布URLのバリエーション

```properties
# バイナリのみ（軽量、約100MB）
distributionUrl=https\://services.gradle.org/distributions/gradle-7.2-bin.zip

# 完全版（ソース・ドキュメント含む、約200MB）
distributionUrl=https\://services.gradle.org/distributions/gradle-7.2-all.zip

# スナップショット版（開発版）
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-20221201000000+0000-bin.zip

# カスタムミラー（企業内リポジトリなど）
distributionUrl=https\://internal-repo.company.com/gradle/gradle-7.2-bin.zip
```

---

## 8. よくある問題と解決策

### 8.1 「Permission denied」エラー（Linux/macOS）

**症状**:
```bash
$ ./gradlew build
-bash: ./gradlew: Permission denied
```

**原因**: 実行権限がない

**解決策**:
```bash
chmod +x gradlew
./gradlew build
```

### 8.2 ダウンロードが失敗する

**症状**:
```bash
$ ./gradlew build
Exception in thread "main" java.net.UnknownHostException: services.gradle.org
```

**原因**: ネットワーク接続の問題、プロキシ設定

**解決策**:

#### プロキシ設定（gradle.properties）

```properties
# ~/.gradle/gradle.properties または プロジェクトルート/gradle.properties
systemProp.http.proxyHost=proxy.example.com
systemProp.http.proxyPort=8080
systemProp.http.proxyUser=username
systemProp.http.proxyPassword=password

systemProp.https.proxyHost=proxy.example.com
systemProp.https.proxyPort=8080
systemProp.https.proxyUser=username
systemProp.https.proxyPassword=password
```

#### 手動ダウンロード

```bash
# 1. Gradleを手動でダウンロード
wget https://services.gradle.org/distributions/gradle-7.2-bin.zip

# 2. 指定された場所に配置
mkdir -p ~/.gradle/wrapper/dists/gradle-7.2-bin/xxxxx/
unzip gradle-7.2-bin.zip -d ~/.gradle/wrapper/dists/gradle-7.2-bin/xxxxx/

# 3. 再実行
./gradlew build
```

### 8.3 「Could not determine java version」エラー

**症状**:
```bash
$ ./gradlew build
ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
```

**原因**: Javaがインストールされていない、またはパスが通っていない

**解決策**:

```bash
# Javaのインストール確認
java -version

# JAVA_HOMEの設定（Linux/macOS）
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export PATH=$JAVA_HOME/bin:$PATH

# JAVA_HOMEの設定（Windows）
set JAVA_HOME=C:\Program Files\Java\jdk-11
set PATH=%JAVA_HOME%\bin;%PATH%

# 永続化（Linux/macOS）
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk' >> ~/.bashrc
source ~/.bashrc
```

### 8.4 古いGradleバージョンがキャッシュされている

**症状**: バージョンを変更したのに古いバージョンが使われる

**解決策**:
```bash
# Gradleキャッシュをクリア
rm -rf ~/.gradle/caches/
rm -rf ~/.gradle/wrapper/dists/

# 再実行（新しいバージョンをダウンロード）
./gradlew --version
./gradlew build
```

---

## 9. Gradle Wrapperのベストプラクティス

### 9.1 バージョン管理

```bash
# gradlewファイルはGitにコミットする（推奨）
git add gradlew gradlew.bat gradle/

# .gitignore の設定
# ただし、Wrapperファイルは除外しない！
!gradle/wrapper/gradle-wrapper.jar
!gradle/wrapper/gradle-wrapper.properties
```

**.gitignore例**:
```gitignore
# Gradleビルド成果物は除外
.gradle/
build/

# ただし、Wrapperは除外しない
!gradle/wrapper/gradle-wrapper.jar
!gradle/wrapper/gradle-wrapper.properties
```

### 9.2 チーム開発での統一

```bash
# プロジェクトのREADMEに記載
## ビルド方法

このプロジェクトはGradle Wrapperを使用します。
Gradleのインストールは不要です。

### Linux/macOS
./gradlew build

### Windows
gradlew.bat build
```

### 9.3 CIサーバーでの使用

```yaml
# GitHub Actions の例
name: Build

on: [push, pull_request]

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

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Build with Gradle Wrapper
        run: ./gradlew build
        # ← gradleではなくgradlewを使用！
```

---

## 10. gradlewコマンドチートシート

### 10.1 ビルド関連

```bash
./gradlew build              # ビルド
./gradlew clean              # 成果物削除
./gradlew clean build        # クリーンビルド
./gradlew assemble           # テストなしでビルド
./gradlew jar                # JARファイル作成
./gradlew war                # WARファイル作成
./gradlew bootJar            # Spring Boot実行可能JAR
```

### 10.2 テスト関連

```bash
./gradlew test               # テスト実行
./gradlew test --tests "*MyTest"  # 特定テスト実行
./gradlew test --rerun-tasks # キャッシュ無視して再実行
./gradlew check              # テスト+品質チェック
```

### 10.3 依存関係

```bash
./gradlew dependencies       # 依存関係ツリー
./gradlew dependencyInsight --dependency spring-core
./gradlew buildEnvironment   # ビルドスクリプトの依存関係
```

### 10.4 情報表示

```bash
./gradlew tasks              # タスク一覧
./gradlew tasks --all        # すべてのタスク
./gradlew projects           # サブプロジェクト一覧
./gradlew properties         # プロジェクトプロパティ
./gradlew --version          # バージョン情報
```

### 10.5 デバッグ

```bash
./gradlew build --info       # 詳細ログ
./gradlew build --debug      # デバッグログ
./gradlew build --stacktrace # スタックトレース
./gradlew build --scan       # ビルドスキャン
./gradlew build --dry-run    # 実行せずタスク順序確認
```

### 10.6 パフォーマンス

```bash
./gradlew build --build-cache      # ビルドキャッシュ有効
./gradlew build --parallel         # 並列実行
./gradlew build --offline          # オフラインモード
./gradlew build --continuous       # 変更監視モード
./gradlew build --profile          # プロファイリング
```

---

## 11. まとめ

### 11.1 Gradle Wrapperの重要ポイント

- ✓ **gradlew = プロジェクト専用のGradle実行スクリプト**
- ✓ **Gradleのインストール不要**（自動ダウンロード）
- ✓ **プロジェクトごとに異なるGradleバージョンを使用可能**
- ✓ **ビルドの再現性を保証**（チーム開発・CI/CDで必須）
- ✓ **Gitにコミットする**（gradlew、gradlew.bat、gradle/wrapper/）

### 11.2 gradlew vs gradle

| 状況 | 推奨コマンド |
|------|-------------|
| チーム開発 | `./gradlew` ✓ |
| CI/CD | `./gradlew` ✓ |
| 本番環境 | `./gradlew` ✓ |
| 個人プロジェクト | `./gradlew` または `gradle` |

**結論**: 基本的に常に`./gradlew`を使用すべき

### 11.3 最初の一歩

```bash
# 1. プロジェクトをクローン
git clone https://github.com/yourorg/yourproject.git
cd yourproject

# 2. 実行権限を付与（Linux/macOS）
chmod +x gradlew

# 3. ビルド実行
./gradlew build

# これだけ！Gradleのインストールは不要
```

---

## 12. 参考資料

- [Gradle Wrapper公式ドキュメント](https://docs.gradle.org/current/userguide/gradle_wrapper.html)
- [Gradle User Guide](https://docs.gradle.org/current/userguide/userguide.html)
- [Gradle Releases](https://gradle.org/releases/)

---

## 13. 次のステップ

- [[build-tools.md]] - Gradleビルドツールの基礎
- [[gradle-advanced-build.md]] - Gradle高度なビルドスクリプト
- [[weblogic-development-workflow.md]] - WebLogic開発ワークフロー
- [[java-build-artifacts.md]] - JavaビルドアーティファクトとEAR
