# ビルドツール学習ノート

> 対象: Gradle, Maven
> 環境: Java, Spring プロジェクト

## 学習目標

- ビルドツールの役割と必要性を理解する
- Gradleの基本的な使い方とビルドスクリプトの読み書きができる
- 依存性管理の仕組みと問題解決ができる
- マルチモジュールプロジェクトの構成を理解する

---

## 4.1.1 ビルドライフサイクル

### 概要
ビルドツールは、ソースコードからデプロイ可能な成果物を生成するまでの一連の処理を定義・実行します。

### Gradleのビルドライフサイクル

```
初期化フェーズ (Initialization)
  ↓
設定フェーズ (Configuration)
  ↓
実行フェーズ (Execution)
```

#### 1. 初期化フェーズ
- `settings.gradle` を読み込み
- どのプロジェクト（サブモジュール）をビルドするか決定
- Project インスタンスを作成

```gradle
// settings.gradle
rootProject.name = 'my-application'
include 'module-a', 'module-b'
```

#### 2. 設定フェーズ
- 全プロジェクトの `build.gradle` を評価
- タスクグラフを構築（どのタスクをどの順序で実行するか）

```gradle
// build.gradle
plugins {
    id 'java'
}

tasks.register('hello') {
    doLast {
        println 'Hello!'
    }
}
```

#### 3. 実行フェーズ
- 依存関係に基づいてタスクを順次実行

```bash
./gradlew build
# compileJava → processResources → classes → jar → assemble → test → check → build
```

### 主要なタスク

| タスク | 説明 |
|--------|------|
| `clean` | ビルド成果物を削除 |
| `compileJava` | Javaソースをコンパイル |
| `processResources` | リソースファイルをコピー |
| `classes` | コンパイルとリソース処理 |
| `jar` | JARファイルを作成 |
| `test` | テストを実行 |
| `build` | 完全なビルド（テスト含む） |
| `assemble` | 成果物の作成（テストなし） |

### 実践例

```bash
# ビルドライフサイクルを確認
./gradlew build --dry-run

# 特定タスクまで実行
./gradlew classes

# タスク依存関係を可視化
./gradlew build --scan
```

---

## 4.1.2 依存性管理（推移的依存、依存競合）

### 依存性管理の基本

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
}
```

### 依存スコープ（Configuration）

| スコープ | 用途 | コンパイル | 実行 | テスト |
|----------|------|-----------|------|--------|
| `implementation` | 実装依存 | ○ | ○ | ○ |
| `api` | API公開依存 | ○ | ○ | ○ |
| `compileOnly` | コンパイルのみ | ○ | × | × |
| `runtimeOnly` | 実行時のみ | × | ○ | ○ |
| `testImplementation` | テスト依存 | × | × | ○ |

### 推移的依存（Transitive Dependencies）

```
あなたのプロジェクト
  └─ spring-boot-starter-web (直接依存)
       └─ spring-web (推移的依存)
            └─ spring-core (推移的依存)
```

- ライブラリが依存している別のライブラリも自動的にダウンロードされる
- 依存の依存も含めて解決される

#### 推移的依存の確認

```bash
# 依存ツリーを表示
./gradlew dependencies

# 特定のコンフィギュレーションのみ
./gradlew dependencies --configuration runtimeClasspath
```

### 依存競合（Dependency Conflict）

#### 問題例

```
プロジェクト
  ├─ library-A → jackson-core:2.15.0
  └─ library-B → jackson-core:2.13.0
```

**どちらのバージョンが使われる？**

#### Gradleの競合解決戦略

1. **デフォルト: 最新バージョンを選択**
   ```
   jackson-core:2.15.0 が使用される
   ```

2. **明示的にバージョン指定**
   ```gradle
   dependencies {
       implementation 'com.fasterxml.jackson.core:jackson-core:2.14.0'
   }
   ```

3. **バージョン強制**
   ```gradle
   configurations.all {
       resolutionStrategy {
           force 'com.fasterxml.jackson.core:jackson-core:2.14.0'
       }
   }
   ```

4. **依存を除外**
   ```gradle
   dependencies {
       implementation('library-A') {
           exclude group: 'com.fasterxml.jackson.core', module: 'jackson-core'
       }
   }
   ```

### 依存競合のトラブルシューティング

```bash
# 競合を可視化
./gradlew dependencyInsight --dependency jackson-core

# ビルドスキャンで詳細分析
./gradlew build --scan
```

---

## 4.1.3 マルチモジュールプロジェクト

### 構成例

```
my-application/
├── settings.gradle
├── build.gradle
├── common/
│   └── build.gradle
├── api/
│   └── build.gradle
└── web/
    └── build.gradle
```

### settings.gradle

```gradle
rootProject.name = 'my-application'

include 'common'
include 'api'
include 'web'
```

### ルートプロジェクトの build.gradle

```gradle
plugins {
    id 'java' apply false
}

subprojects {
    apply plugin: 'java'

    group = 'com.example'
    version = '1.0.0'

    repositories {
        mavenCentral()
    }

    dependencies {
        testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    }
}
```

### モジュール間の依存

```gradle
// web/build.gradle
dependencies {
    implementation project(':common')
    implementation project(':api')
}
```

### メリット

- **コードの再利用**: 共通ロジックを `common` モジュールに集約
- **ビルドの並列化**: モジュール間の依存がなければ並列ビルド可能
- **責務の分離**: API層、ビジネスロジック層、Web層を分離

```bash
# 特定モジュールのみビルド
./gradlew :web:build

# 全モジュールビルド
./gradlew build
```

---

## 4.1.4 タスク/ゴールの概念

### Gradleタスク

タスクは、ビルドプロセスの最小単位です。

#### カスタムタスクの定義

```gradle
// 基本的なタスク
tasks.register('hello') {
    doLast {
        println 'Hello, Gradle!'
    }
}

// 依存関係を持つタスク
tasks.register('prepareData') {
    doLast {
        println 'データ準備中...'
    }
}

tasks.register('processData') {
    dependsOn 'prepareData'
    doLast {
        println 'データ処理中...'
    }
}
```

#### タスクの実行順序制御

```gradle
tasks.named('test') {
    // test タスクの前に必ず実行
    dependsOn 'customPreTest'
}

tasks.register('customPreTest') {
    doLast {
        println 'テスト前処理'
    }
}
```

### Maven ゴール vs Gradle タスク

| Maven ゴール | Gradle タスク | 説明 |
|-------------|--------------|------|
| `clean` | `clean` | ビルド成果物削除 |
| `compile` | `compileJava` | コンパイル |
| `test` | `test` | テスト実行 |
| `package` | `jar` / `war` | パッケージング |
| `install` | `publishToMavenLocal` | ローカルリポジトリへインストール |

---

## 4.1.5 ビルドキャッシュ

### ビルドキャッシュの有効化

```gradle
// gradle.properties
org.gradle.caching=true
```

または

```bash
./gradlew build --build-cache
```

### キャッシュの仕組み

1. **タスクの入力をハッシュ化**
   - ソースコード
   - 依存ライブラリ
   - タスク設定

2. **同じハッシュならキャッシュから取得**
   - 前回のビルド結果を再利用
   - コンパイルをスキップ

3. **キャッシュの種類**
   - **ローカルキャッシュ**: `~/.gradle/caches/build-cache-1/`
   - **リモートキャッシュ**: チーム間で共有可能

### キャッシュ可能なタスクの定義

```gradle
tasks.register('generateCode', GenerateCodeTask) {
    inputs.file('template.txt')
    outputs.file('generated.java')

    doLast {
        // コード生成処理
    }
}
```

### キャッシュの確認

```bash
# キャッシュヒット/ミスを確認
./gradlew build --build-cache --info

# キャッシュをクリア
rm -rf ~/.gradle/caches/build-cache-1/
```

### パフォーマンス改善

```gradle
// 並列ビルド有効化
org.gradle.parallel=true

// デーモン起動
org.gradle.daemon=true

// メモリ設定
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
```

---

## 学習ロードマップ

### Week 1: 基礎
- [ ] Gradleのインストールと基本コマンド
- [ ] `build.gradle` の基本構造理解
- [ ] 依存性の追加とビルド実行

### Week 2: 依存性管理
- [ ] 推移的依存の仕組み理解
- [ ] 依存競合の解決方法実践
- [ ] `dependencies` タスクでの依存ツリー分析

### Week 3: マルチモジュール
- [ ] マルチモジュールプロジェクト構築
- [ ] モジュール間依存の設定
- [ ] 実プロジェクトの構成分析

### Week 4: 最適化
- [ ] カスタムタスク作成
- [ ] ビルドキャッシュの活用
- [ ] ビルド時間の測定と改善

---

## 参考資料

- [Gradle公式ドキュメント](https://docs.gradle.org/)
- [Gradle User Guide - Build Lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html)
- [Gradle User Guide - Dependency Management](https://docs.gradle.org/current/userguide/dependency_management.html)
- 書籍『Gradle徹底入門』（翔泳社）

---

## トラブルシューティング

### よくあるエラー

#### 1. 依存が解決できない
```
Could not resolve: com.example:library:1.0.0
```
**解決策:**
- リポジトリが正しく設定されているか確認
- バージョン番号が正しいか確認

#### 2. ビルドが遅い
**解決策:**
```gradle
// gradle.properties
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true
```

#### 3. OutOfMemoryError
**解決策:**
```gradle
// gradle.properties
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g
```
