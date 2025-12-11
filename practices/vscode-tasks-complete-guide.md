---
title: "VSCode Tasks 完全ガイド"
category: practices
tags:
  - vscode
  - tasks
  - automation
  - build-tools
  - debugging
difficulty: intermediate
related:
  - practices/vscode-workspace-overview.md
  - practices/vscode-workspace-details.md
  - practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md
language:
  - javascript
  - java
  - python
  - cpp
last_updated: 2025-12-12
---

# VSCode Tasks 完全ガイド

> タスクランナー × ビルド自動化 × デバッグ連携 × カスタムコマンド実行

このドキュメントでは、VSCode の Tasks（タスク）機能について、概念から実践的な使い方、高度なカスタマイズ方法まで包括的に解説します。

---

## 目次

1. [Tasks とは](#tasksとは)
2. [Tasks の基本概念](#tasksの基本概念)
3. [tasks.json の基本構造](#tasksjsonの基本構造)
4. [タスクの種類](#タスクの種類)
5. [タスクの実行方法](#タスクの実行方法)
6. [プロパティ詳細解説](#プロパティ詳細解説)
7. [実践的な例](#実践的な例)
8. [タスクの組み合わせ（dependsOn）](#タスクの組み合わせdependson)
9. [問題マッチャー（Problem Matchers）](#問題マッチャーproblem-matchers)
10. [変数（Variables）の活用](#変数variablesの活用)
11. [タスクとデバッグの連携](#タスクとデバッグの連携)
12. [ワークスペースの活用とタスクの連携](#ワークスペースの活用とタスクの連携)
13. [言語別のタスク設定例](#言語別のタスク設定例)
14. [トラブルシューティング](#トラブルシューティング)
15. [ベストプラクティス](#ベストプラクティス)
16. [関連ドキュメント](#関連ドキュメント)

---

## Tasks とは

### 概要

**Tasks（タスク）** は、VSCode 内から外部コマンドやスクリプトを実行するための機能です。ビルド、テスト実行、リンティング、デプロイなど、開発プロセスで繰り返し実行するコマンドを自動化できます。

### Tasks が解決する課題

**従来の問題点:**
```bash
# 毎回ターミナルで手動実行
$ cd /path/to/project
$ ./gradlew build
$ ./gradlew test
$ ./gradlew deploy
```

**Tasks による解決:**
- キーボードショートカットで実行（`Ctrl+Shift+B`）
- コマンドパレットから選択実行
- エラー出力を VSCode の問題パネルに統合
- ビルド前にファイル自動保存
- デバッグ起動前に自動ビルド

### Tasks の主な用途

| 用途 | 例 |
|------|-----|
| **ビルド** | `npm run build`, `gradle build`, `mvn compile` |
| **テスト実行** | `npm test`, `pytest`, `gradle test` |
| **リンティング** | `eslint src/`, `flake8 .`, `checkstyle` |
| **デプロイ** | `deploy.sh`, WLST スクリプト実行 |
| **コード生成** | `protoc`, `swagger-codegen` |
| **データベース操作** | マイグレーション、シード実行 |
| **Docker操作** | `docker build`, `docker-compose up` |

---

## Tasks の基本概念

### 設定ファイルの配置

Tasks は `.vscode/tasks.json` ファイルで定義します：

```
project/
├── .vscode/
│   └── tasks.json          ← タスク定義ファイル
├── src/
└── package.json
```

### ワークスペースとタスクスコープ

| スコープ | 設定場所 | 適用範囲 |
|---------|---------|---------|
| **フォルダタスク** | `.vscode/tasks.json` | 単一プロジェクト |
| **ワークスペースタスク** | `.code-workspace` ファイル内 | マルチルートワークスペース全体 |
| **グローバルタスク** | ユーザー設定 | 全プロジェクト共通 |

### タスクの実行フロー

```
ユーザー操作
   ↓
タスク選択（Ctrl+Shift+P → "Tasks: Run Task"）
   ↓
tasks.json から定義を読み込み
   ↓
前提タスク（dependsOn）を実行
   ↓
メインタスク実行
   ↓
出力をターミナルパネルに表示
   ↓
問題マッチャーでエラー検出
   ↓
問題パネルにエラー表示
```

---

## tasks.json の基本構造

### 最小構成

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Hello World",
      "type": "shell",
      "command": "echo 'Hello, World!'"
    }
  ]
}
```

**必須プロパティ:**
- `version`: 常に `"2.0.0"`
- `tasks`: タスク定義の配列
- `label`: タスクの名前（一意である必要がある）
- `type`: タスクの種類（`shell` または `process`）
- `command`: 実行するコマンド

### 標準的な構成

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build Project",
      "type": "shell",
      "command": "npm run build",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": ["$tsc"]
    }
  ]
}
```

---

## タスクの種類

### 1. Shell タスク（type: "shell"）

シェル経由でコマンドを実行します。パイプ、リダイレクト、環境変数展開が使えます。

```json
{
  "label": "List Files",
  "type": "shell",
  "command": "ls -la | grep '.json'"
}
```

**特徴:**
- ✅ パイプ、リダイレクトが使える
- ✅ シェルの機能（`&&`, `||`, `;` など）が使える
- ✅ 環境変数展開が可能
- ❌ オーバーヘッドがやや大きい

### 2. Process タスク（type: "process"）

コマンドを直接実行します（シェルを介さない）。

```json
{
  "label": "Run Python Script",
  "type": "process",
  "command": "python3",
  "args": ["script.py", "--verbose"]
}
```

**特徴:**
- ✅ 高速（シェルのオーバーヘッドなし）
- ✅ 引数の扱いが明確
- ❌ パイプ、リダイレクトは使えない
- ❌ シェルの機能は使えない

**使い分け:**
- シェル機能が必要 → `shell`
- シンプルなコマンド実行 → `process`（高速）

---

## タスクの実行方法

### 1. コマンドパレットから実行

```
Ctrl+Shift+P → "Tasks: Run Task" → タスクを選択
```

### 2. キーボードショートカット

| ショートカット | 機能 |
|--------------|------|
| `Ctrl+Shift+B` | デフォルトビルドタスクを実行 |
| `Ctrl+Shift+T` | デフォルトテストタスクを実行 |

**デフォルトタスクの設定:**

```json
{
  "label": "Build",
  "group": {
    "kind": "build",
    "isDefault": true
  }
}
```

### 3. メニューから実行

```
Terminal → Run Task... → タスクを選択
```

### 4. タスクの自動実行

**ファイル保存時に自動実行:**

```json
{
  "label": "Auto Lint",
  "type": "shell",
  "command": "eslint ${file}",
  "runOptions": {
    "runOn": "folderOpen"
  }
}
```

---

## プロパティ詳細解説

### 基本プロパティ

#### label（必須）

タスクの名前。コマンドパレットに表示されます。

```json
{
  "label": "Build Production",
  "label": "Deploy to Staging",
  "label": "Run Tests"
}
```

**ルール:**
- ワークスペース内で一意である必要がある
- わかりやすい名前を付ける
- 日本語も使用可能

#### type（必須）

タスクのタイプを指定。

```json
{
  "type": "shell",    // シェル経由で実行
  "type": "process"   // 直接実行
}
```

#### command（必須）

実行するコマンド。

```json
{
  "command": "npm run build",           // shell タイプ
  "command": "python3",                 // process タイプ
  "command": "./gradlew build"
}
```

#### args

コマンドの引数（主に `process` タイプで使用）。

```json
{
  "type": "process",
  "command": "python3",
  "args": [
    "script.py",
    "--input", "${workspaceFolder}/data.json",
    "--output", "${workspaceFolder}/result.csv"
  ]
}
```

**shell タイプの場合:**

```json
{
  "type": "shell",
  "command": "npm",
  "args": ["run", "build", "--", "--production"]
}
```

---

### グループ化（group）

タスクをグループに分類し、デフォルトタスクを設定します。

```json
{
  "group": "build"                    // 文字列形式（シンプル）
}

{
  "group": {
    "kind": "build",                  // グループ種別
    "isDefault": true                 // デフォルトタスクに設定
  }
}
```

**グループの種類:**

| グループ | 説明 | ショートカット |
|---------|------|---------------|
| `build` | ビルドタスク | `Ctrl+Shift+B` |
| `test` | テストタスク | `Ctrl+Shift+T` |
| `none` | グループなし | - |

**複数のビルドタスク例:**

```json
{
  "tasks": [
    {
      "label": "Build Development",
      "group": "build",
      "command": "npm run build:dev"
    },
    {
      "label": "Build Production",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "command": "npm run build:prod"
    }
  ]
}
```

---

### プレゼンテーション（presentation）

タスク実行時の表示方法を制御します。

```json
{
  "presentation": {
    "reveal": "always",          // ターミナルの表示タイミング
    "panel": "shared",           // パネルの共有方法
    "focus": false,              // 実行時にフォーカスするか
    "echo": true,                // コマンドをエコーするか
    "showReuseMessage": true,    // 再利用メッセージを表示するか
    "clear": false,              // 実行前にクリアするか
    "close": false               // 完了後にパネルを閉じるか
  }
}
```

#### reveal

| 値 | 説明 |
|----|------|
| `always` | 常にターミナルを表示 |
| `never` | ターミナルを表示しない |
| `silent` | エラーがある場合のみ表示 |

```json
{
  "presentation": {
    "reveal": "always"    // ビルド出力を常に確認したい場合
  }
}

{
  "presentation": {
    "reveal": "silent"    // 成功時は非表示、失敗時のみ表示
  }
}
```

#### panel

| 値 | 説明 |
|----|------|
| `shared` | 他のタスクとターミナルを共有 |
| `dedicated` | このタスク専用のターミナルを使用 |
| `new` | 常に新しいターミナルを作成 |

```json
{
  "presentation": {
    "panel": "dedicated"  // ログを残したい長時間実行タスク
  }
}

{
  "presentation": {
    "panel": "shared"     // 短時間のビルドタスク
  }
}
```

#### focus

```json
{
  "presentation": {
    "focus": true         // 実行時にターミナルにフォーカス
  }
}

{
  "presentation": {
    "focus": false        // エディタのフォーカスを維持
  }
}
```

#### clear

```json
{
  "presentation": {
    "clear": true         // 実行前に出力をクリア（推奨）
  }
}
```

---

### オプション（options）

実行環境のカスタマイズ。

```json
{
  "options": {
    "cwd": "${workspaceFolder}/subdir",    // 作業ディレクトリ
    "env": {                                // 環境変数
      "NODE_ENV": "production",
      "DEBUG": "true"
    },
    "shell": {
      "executable": "/bin/bash",            // 使用するシェル
      "args": ["-c"]
    }
  }
}
```

**作業ディレクトリの変更:**

```json
{
  "label": "Build Subproject",
  "type": "shell",
  "command": "npm run build",
  "options": {
    "cwd": "${workspaceFolder}/packages/frontend"
  }
}
```

**環境変数の設定:**

```json
{
  "label": "Deploy to Production",
  "type": "shell",
  "command": "./deploy.sh",
  "options": {
    "env": {
      "ENVIRONMENT": "production",
      "API_KEY": "${env:DEPLOY_API_KEY}"
    }
  }
}
```

---

### 実行オプション（runOptions）

```json
{
  "runOptions": {
    "runOn": "default",           // default または folderOpen
    "instanceLimit": 1,           // 同時実行数の制限
    "reevaluateOnRerun": true     // 再実行時に変数を再評価
  }
}
```

**ワークスペースを開いた時に自動実行:**

```json
{
  "label": "Initialize Environment",
  "type": "shell",
  "command": "npm install",
  "runOptions": {
    "runOn": "folderOpen"
  }
}
```

---

## タスクの組み合わせ（dependsOn）

### 基本的な依存関係

```json
{
  "tasks": [
    {
      "label": "Build",
      "type": "shell",
      "command": "npm run build"
    },
    {
      "label": "Deploy",
      "type": "shell",
      "command": "./deploy.sh",
      "dependsOn": ["Build"]
    }
  ]
}
```

**実行順序:**
```
Deploy タスクを実行
  ↓
1. Build タスクを実行
  ↓
2. Deploy タスクを実行
```

### 複数の依存タスク

```json
{
  "label": "Full Build",
  "dependsOn": ["Clean", "Lint", "Compile", "Test"]
}
```

**デフォルトは順次実行（sequential）**

### 並列実行

```json
{
  "label": "Build All",
  "dependsOn": ["Build Frontend", "Build Backend", "Build Mobile"],
  "dependsOrder": "parallel"
}
```

**parallel 指定で並列実行:**
```
Build All タスクを実行
  ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Build Frontend  │ Build Backend   │ Build Mobile    │
│   (並列実行)    │   (並列実行)    │   (並列実行)    │
└─────────────────┴─────────────────┴─────────────────┘
```

### 実践的な例: フルビルドパイプライン

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Clean",
      "type": "shell",
      "command": "rm -rf build dist"
    },
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "npm install"
    },
    {
      "label": "Lint",
      "type": "shell",
      "command": "npm run lint"
    },
    {
      "label": "Compile TypeScript",
      "type": "shell",
      "command": "tsc"
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "npm test"
    },
    {
      "label": "Build Production",
      "type": "shell",
      "command": "npm run build:prod",
      "dependsOn": ["Clean", "Install Dependencies"],
      "dependsOrder": "sequence"
    },
    {
      "label": "Full Pipeline",
      "dependsOn": ["Lint", "Compile TypeScript", "Run Tests", "Build Production"],
      "dependsOrder": "sequence",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

---

## 問題マッチャー（Problem Matchers）

### 概要

問題マッチャーは、タスクの出力からエラーや警告を検出し、VSCode の「問題」パネルに表示する機能です。

### ビルトイン問題マッチャー

VSCode には多数の問題マッチャーが組み込まれています：

| 問題マッチャー | 用途 |
|--------------|------|
| `$tsc` | TypeScript コンパイラ |
| `$eslint-compact` | ESLint（compact形式） |
| `$eslint-stylish` | ESLint（stylish形式） |
| `$jshint` | JSHint |
| `$gcc` | GCC |
| `$msCompile` | Visual C++ |
| `$go` | Go コンパイラ |
| `$python` | Python トレースバック |

### 使用例

```json
{
  "label": "Compile TypeScript",
  "type": "shell",
  "command": "tsc",
  "problemMatcher": ["$tsc"]
}
```

**複数の問題マッチャー:**

```json
{
  "label": "Build and Lint",
  "type": "shell",
  "command": "npm run build && npm run lint",
  "problemMatcher": ["$tsc", "$eslint-stylish"]
}
```

### カスタム問題マッチャー

独自の出力形式に対応する問題マッチャーを作成できます。

**出力例（Gradle）:**
```
/path/to/MyClass.java:42: error: cannot find symbol
  symbol:   variable foo
  location: class MyClass
```

**カスタム問題マッチャー:**

```json
{
  "label": "Gradle Build",
  "type": "shell",
  "command": "./gradlew build",
  "problemMatcher": {
    "owner": "java",
    "fileLocation": ["absolute"],
    "pattern": {
      "regexp": "^(.*):(\\d+):\\s+(warning|error):\\s+(.*)$",
      "file": 1,
      "line": 2,
      "severity": 3,
      "message": 4
    }
  }
}
```

**正規表現パターンの要素:**

| キャプチャグループ | プロパティ | 説明 |
|------------------|-----------|------|
| 1 | `file` | ファイルパス |
| 2 | `line` | 行番号 |
| 3 | `severity` | 重要度（error/warning） |
| 4 | `message` | エラーメッセージ |

### 複数行の問題マッチャー

```json
{
  "problemMatcher": {
    "owner": "python",
    "fileLocation": ["relative", "${workspaceFolder}"],
    "pattern": [
      {
        "regexp": "^\\s*File \"(.+)\", line (\\d+)",
        "file": 1,
        "line": 2
      },
      {
        "regexp": "^\\s*(.+)Error: (.+)$",
        "severity": 1,
        "message": 2
      }
    ]
  }
}
```

### バックグラウンドタスクの問題マッチャー

ウォッチモードなど、継続的に実行されるタスク用：

```json
{
  "label": "Watch TypeScript",
  "type": "shell",
  "command": "tsc --watch",
  "isBackground": true,
  "problemMatcher": {
    "owner": "typescript",
    "fileLocation": "relative",
    "pattern": {
      "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
      "file": 1,
      "line": 2,
      "column": 3,
      "severity": 4,
      "message": 5
    },
    "background": {
      "activeOnStart": true,
      "beginsPattern": "^\\s*\\d{1,2}:\\d{2}:\\d{2} (AM|PM) - File change detected",
      "endsPattern": "^\\s*\\d{1,2}:\\d{2}:\\d{2} (AM|PM) - Compilation complete"
    }
  }
}
```

---

## 変数（Variables）の活用

### VSCode 組み込み変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `${workspaceFolder}` | ワークスペースのルートパス | `/home/user/project` |
| `${workspaceFolderBasename}` | ワークスペース名 | `project` |
| `${file}` | 現在開いているファイルのパス | `/home/user/project/src/main.js` |
| `${fileBasename}` | ファイル名 | `main.js` |
| `${fileBasenameNoExtension}` | 拡張子なしファイル名 | `main` |
| `${fileDirname}` | ファイルのディレクトリパス | `/home/user/project/src` |
| `${fileExtname}` | ファイルの拡張子 | `.js` |
| `${relativeFile}` | ワークスペースからの相対パス | `src/main.js` |
| `${relativeFileDirname}` | 相対ディレクトリパス | `src` |
| `${cwd}` | タスク起動時の作業ディレクトリ | `/home/user/project` |
| `${lineNumber}` | カーソルの行番号 | `42` |
| `${selectedText}` | 選択中のテキスト | `function foo()` |

### 環境変数

```json
{
  "command": "deploy",
  "args": ["--host", "${env:DEPLOY_HOST}"]
}
```

### 入力変数（Input Variables）

ユーザーに入力を求める変数：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Deploy to Environment",
      "type": "shell",
      "command": "./deploy.sh ${input:environment}",
      "presentation": {
        "reveal": "always"
      }
    }
  ],
  "inputs": [
    {
      "id": "environment",
      "type": "pickString",
      "description": "Select deployment environment",
      "options": [
        "development",
        "staging",
        "production"
      ],
      "default": "development"
    }
  ]
}
```

**入力タイプの種類:**

| タイプ | 説明 | 例 |
|--------|------|-----|
| `promptString` | 自由入力 | コミットメッセージ入力 |
| `pickString` | 選択肢から選択 | 環境選択 |
| `command` | コマンドの出力を使用 | Git ブランチ一覧 |

**promptString の例:**

```json
{
  "inputs": [
    {
      "id": "commitMessage",
      "type": "promptString",
      "description": "Enter commit message",
      "default": "Update files"
    }
  ]
}
```

**command の例（Git ブランチ選択）:**

```json
{
  "inputs": [
    {
      "id": "gitBranch",
      "type": "command",
      "command": "git.getBranches"
    }
  ]
}
```

### 実践例: 現在のファイルをコンパイル

```json
{
  "label": "Compile Current File",
  "type": "shell",
  "command": "gcc",
  "args": [
    "${file}",
    "-o",
    "${fileDirname}/${fileBasenameNoExtension}"
  ],
  "group": "build",
  "presentation": {
    "reveal": "always",
    "panel": "shared"
  }
}
```

**実行例:**
- `/home/user/project/src/main.c` を開いている状態で実行
- `gcc /home/user/project/src/main.c -o /home/user/project/src/main`

---

## タスクとデバッグの連携

### ビルド後にデバッグ起動

**launch.json:**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Program",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/dist/main.js",
      "preLaunchTask": "Build",        // ← デバッグ前にビルドタスク実行
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    }
  ]
}
```

**tasks.json:**

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build",
      "type": "shell",
      "command": "npm run build",
      "group": "build",
      "problemMatcher": ["$tsc"]
    }
  ]
}
```

**実行フロー:**
```
F5 キーを押す
  ↓
preLaunchTask "Build" を実行
  ↓
ビルド完了を待機
  ↓
デバッガーを起動
```

### ウォッチモードとの連携

```json
{
  "label": "Watch TypeScript",
  "type": "shell",
  "command": "tsc --watch",
  "isBackground": true,
  "problemMatcher": {
    "$tsc-watch"
  }
}
```

**launch.json:**

```json
{
  "name": "Attach to Process",
  "type": "node",
  "request": "attach",
  "port": 9229,
  "preLaunchTask": "Watch TypeScript"
}
```

---

## ワークスペースの活用とタスクの連携

### ワークスペースとタスクの関係

VSCode では、**ワークスペース**（`.code-workspace`）と **Tasks** を組み合わせることで、複数のプロジェクトやサブモジュールを効率的に管理できます。

### マルチルートワークスペースとタスク

#### ワークスペース構成の種類

**1. 単一フォルダワークスペース:**
```
project/
├── .vscode/
│   └── tasks.json          ← このフォルダ専用のタスク
└── src/
```

**2. マルチルートワークスペース:**
```
workspace.code-workspace    ← ワークスペース定義ファイル

workspace/
├── project-a/
│   └── .vscode/
│       └── tasks.json      ← project-a 専用タスク
├── project-b/
│   └── .vscode/
│       └── tasks.json      ← project-b 専用タスク
└── project-c/
    └── .vscode/
        └── tasks.json      ← project-c 専用タスク
```

---

### パターン1: マルチルートワークスペースでのタスク管理

複数のプロジェクトを `.code-workspace` ファイルで統合管理します。

#### workspace.code-workspace（ワークスペース定義）

```json
{
  "folders": [
    {
      "name": "Frontend",
      "path": "frontend"
    },
    {
      "name": "Backend",
      "path": "backend"
    },
    {
      "name": "Mobile",
      "path": "mobile"
    }
  ],
  "settings": {
    "files.exclude": {
      "**/node_modules": true,
      "**/.git": true
    }
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Build All Projects",
        "dependsOn": [
          "Frontend: Build",
          "Backend: Build",
          "Mobile: Build"
        ],
        "dependsOrder": "parallel",
        "group": {
          "kind": "build",
          "isDefault": true
        },
        "presentation": {
          "reveal": "always",
          "panel": "dedicated"
        }
      },
      {
        "label": "Start Development Environment",
        "dependsOn": [
          "Backend: Start Server",
          "Frontend: Start Dev Server"
        ],
        "dependsOrder": "parallel",
        "presentation": {
          "reveal": "always",
          "panel": "dedicated"
        }
      }
    ]
  }
}
```

#### frontend/.vscode/tasks.json（Frontend 専用タスク）

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Frontend: Build",
      "type": "shell",
      "command": "npm run build",
      "options": {
        "cwd": "${workspaceFolder:Frontend}"
      },
      "group": "build",
      "problemMatcher": ["$tsc"],
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "Frontend: Start Dev Server",
      "type": "shell",
      "command": "npm run dev",
      "options": {
        "cwd": "${workspaceFolder:Frontend}"
      },
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Frontend: Test",
      "type": "shell",
      "command": "npm test",
      "options": {
        "cwd": "${workspaceFolder:Frontend}"
      },
      "group": "test"
    }
  ]
}
```

#### backend/.vscode/tasks.json（Backend 専用タスク）

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Backend: Build",
      "type": "shell",
      "command": "./gradlew build",
      "options": {
        "cwd": "${workspaceFolder:Backend}"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "Backend: Start Server",
      "type": "shell",
      "command": "./gradlew bootRun",
      "options": {
        "cwd": "${workspaceFolder:Backend}"
      },
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Backend: Test",
      "type": "shell",
      "command": "./gradlew test",
      "options": {
        "cwd": "${workspaceFolder:Backend}"
      },
      "group": "test"
    }
  ]
}
```

**利点:**
- ✅ 各プロジェクトが独立したタスク定義を持つ
- ✅ ワークスペースレベルで統合タスクを定義可能
- ✅ `Ctrl+Shift+B` で全プロジェクトを一括ビルド

---

### パターン2: サブモジュールプロジェクトでのタスク管理

Git でプロジェクトが管理されているが、実際のコードは各サブモジュールに存在する場合の構成です。

#### プロジェクト構造

```
workspace/
├── workspace.code-workspace
├── project-a/                    # 親プロジェクト（Gradle マルチモジュール）
│   ├── common-lib/              # サブモジュール
│   │   └── src/
│   ├── business-logic/          # サブモジュール
│   │   └── src/
│   ├── webapp/                  # サブモジュール
│   │   └── src/
│   ├── settings.gradle
│   └── build.gradle
└── project-b/
    ├── core/
    ├── api/
    └── webapp/
```

#### workspace.code-workspace（サブモジュール個別登録）

```json
{
  "folders": [
    {
      "name": "project-a-common",
      "path": "project-a/common-lib"
    },
    {
      "name": "project-a-business",
      "path": "project-a/business-logic"
    },
    {
      "name": "project-a-webapp",
      "path": "project-a/webapp"
    },
    {
      "name": "project-b-core",
      "path": "project-b/core"
    },
    {
      "name": "project-b-api",
      "path": "project-b/api"
    },
    {
      "name": "project-b-webapp",
      "path": "project-b/webapp"
    }
  ],
  "settings": {
    "java.project.referencedLibraries": [
      "project-*/*/lib/**/*.jar"
    ],
    "java.configuration.updateBuildConfiguration": "automatic"
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Build All Modules",
        "type": "shell",
        "command": "./gradlew build",
        "options": {
          "cwd": "${workspaceFolder}/../project-a"
        },
        "group": {
          "kind": "build",
          "isDefault": true
        },
        "presentation": {
          "reveal": "always",
          "panel": "shared"
        }
      },
      {
        "label": "Build project-a WAR",
        "type": "shell",
        "command": "./gradlew :project-a:webapp:build",
        "options": {
          "cwd": "${workspaceFolder}/.."
        },
        "group": "build"
      },
      {
        "label": "Deploy project-a",
        "type": "shell",
        "command": "./gradlew :project-a:webapp:deployThisWar",
        "options": {
          "cwd": "${workspaceFolder}/.."
        },
        "dependsOn": ["Build project-a WAR"],
        "presentation": {
          "reveal": "always",
          "panel": "dedicated"
        }
      }
    ]
  }
}
```

**利点:**
- ✅ サブモジュールごとに独立した編集環境
- ✅ ワークスペースレベルで統合ビルドタスクを定義
- ✅ 言語サーバーのパフォーマンス向上

**使用場面:**
- 各サブモジュールが独自の `.classpath` を持つ場合
- サブモジュール間の依存が明確に分離されている場合
- 特定のサブモジュールのみを頻繁に編集する場合

---

### パターン3: ハイブリッド方式（親プロジェクト + 主要サブモジュール）

親プロジェクトと主要なサブモジュールの両方を登録する方法です。

#### workspace.code-workspace

```json
{
  "folders": [
    {
      "name": "workspace-root",
      "path": "."
    },
    {
      "name": "project-a-webapp",
      "path": "project-a/webapp"
    },
    {
      "name": "project-b-webapp",
      "path": "project-b/webapp"
    }
  ],
  "settings": {
    "files.exclude": {
      "project-a/": true,
      "project-b/": true
    }
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Build All WARs",
        "type": "shell",
        "command": "./gradlew buildAllWars",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": {
          "kind": "build",
          "isDefault": true
        }
      },
      {
        "label": "Deploy All WARs",
        "type": "shell",
        "command": "./gradlew deployAllWars",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "dependsOn": ["Build All WARs"]
      }
    ]
  }
}
```

**利点:**
- ✅ ルートレベルでのビルドスクリプト・デプロイスクリプト管理
- ✅ 頻繁に編集する webapp モジュールへの高速アクセス
- ✅ files.exclude で重複表示を防止

---

### ワークスペース変数の活用

マルチルートワークスペースでは、特別な変数が使えます。

#### ワークスペース専用変数

| 変数 | 説明 | 例 |
|------|------|-----|
| `${workspaceFolder}` | 最初のワークスペースフォルダ | `/home/user/workspace/project-a` |
| `${workspaceFolder:name}` | 指定した名前のワークスペースフォルダ | `${workspaceFolder:Frontend}` |
| `${workspaceFolderBasename}` | ワークスペース名 | `project-a` |

#### 実用例

```json
{
  "tasks": [
    {
      "label": "Build Frontend",
      "type": "shell",
      "command": "npm run build",
      "options": {
        "cwd": "${workspaceFolder:Frontend}"    // ← Frontend フォルダで実行
      }
    },
    {
      "label": "Deploy Backend",
      "type": "shell",
      "command": "./deploy.sh",
      "options": {
        "cwd": "${workspaceFolder:Backend}",    // ← Backend フォルダで実行
        "env": {
          "DEPLOY_PATH": "${workspaceFolder:Backend}/dist"
        }
      }
    }
  ]
}
```

---

### 実践例: WebLogic マルチモジュールプロジェクト

[VSCode マルチWARプロジェクト統合デプロイ環境](weblogic/vscode-gradle-wlst-multi-war-deployment.md) で解説されている構成とタスクの統合例です。

#### workspace.code-workspace

```json
{
  "folders": [
    {
      "name": "workspace-root",
      "path": "."
    },
    {
      "name": "project-a-webapp",
      "path": "project-a/webapp"
    },
    {
      "name": "project-b-webapp",
      "path": "project-b/webapp"
    },
    {
      "name": "project-c-webapp",
      "path": "project-c/webapp"
    }
  ],
  "settings": {
    "java.project.referencedLibraries": [
      "project-*/*/lib/**/*.jar"
    ],
    "files.exclude": {
      "project-a/": true,
      "project-b/": true,
      "project-c/": true
    }
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "WebLogic: Build All WARs",
        "type": "shell",
        "command": "./gradlew buildAllWars",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": "build",
        "presentation": {
          "reveal": "always",
          "panel": "shared"
        }
      },
      {
        "label": "WebLogic: Deploy All WARs",
        "type": "shell",
        "command": "./gradlew deployAllWars",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "dependsOn": ["WebLogic: Build All WARs"],
        "group": "build",
        "presentation": {
          "reveal": "always",
          "panel": "dedicated"
        }
      },
      {
        "label": "WebLogic: Deploy project-a",
        "type": "shell",
        "command": "./gradlew :project-a:webapp:deployThisWar",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": "build"
      },
      {
        "label": "WebLogic: Redeploy project-a (Quick)",
        "type": "shell",
        "command": "./gradlew :project-a:webapp:redeployThisWar",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": {
          "kind": "build",
          "isDefault": true
        }
      },
      {
        "label": "WebLogic: Deploy project-b",
        "type": "shell",
        "command": "./gradlew :project-b:webapp:deployThisWar",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": "build"
      },
      {
        "label": "WebLogic: Redeploy project-b (Quick)",
        "type": "shell",
        "command": "./gradlew :project-b:webapp:redeployThisWar",
        "options": {
          "cwd": "${workspaceFolder:workspace-root}"
        },
        "group": "build"
      }
    ]
  }
}
```

**ワークフロー:**

1. **初回セットアップ:**
   ```
   Ctrl+Shift+P → "Tasks: Run Task" → "WebLogic: Deploy All WARs"
   ```

2. **日常的な開発（project-a を編集中）:**
   ```
   Ctrl+Shift+B (デフォルトタスク "Redeploy project-a (Quick)" を実行)
   ```

3. **複数プロジェクトの一括再ビルド:**
   ```
   Ctrl+Shift+P → "Tasks: Run Task" → "WebLogic: Build All WARs"
   ```

---

### タスクのスコープとオーバーライド

#### 優先順位

マルチルートワークスペースでは、タスクは以下の優先順位で解決されます:

```
1. フォルダ固有タスク（.vscode/tasks.json）
   ↓
2. ワークスペースタスク（.code-workspace内のtasksセクション）
   ↓
3. ユーザーグローバルタスク
```

#### タスクのオーバーライド例

**ワークスペース共通タスク（.code-workspace）:**

```json
{
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Build",
        "type": "shell",
        "command": "echo 'Workspace build'"
      }
    ]
  }
}
```

**プロジェクト固有タスク（project-a/.vscode/tasks.json）:**

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build",
      "type": "shell",
      "command": "./gradlew build"    // ← こちらが優先される
    }
  ]
}
```

**実行:**
- `project-a` のファイルを開いている状態で "Build" タスク実行 → Gradle ビルドが実行される
- 他のフォルダで "Build" タスク実行 → ワークスペース共通タスクが実行される

---

### ワークスペース設定のベストプラクティス

#### 1. タスク命名規則の統一

```json
{
  "tasks": [
    {
      "label": "Frontend: Build",      // ← プロジェクト名をプレフィックスに
      "label": "Backend: Build",
      "label": "Mobile: Build"
    }
  ]
}
```

**理由:**
- コマンドパレットで見つけやすい
- どのプロジェクトのタスクか一目瞭然

#### 2. cwd の明示的な指定

```json
{
  "tasks": [
    {
      "label": "Build Frontend",
      "command": "npm run build",
      "options": {
        "cwd": "${workspaceFolder:Frontend}"    // ← 必ず指定
      }
    }
  ]
}
```

**理由:**
- 実行ディレクトリが明確
- 想定外のディレクトリでの実行を防止

#### 3. 統合タスクの活用

```json
{
  "tasks": [
    {
      "label": "Build: All Projects",
      "dependsOn": [
        "Frontend: Build",
        "Backend: Build",
        "Mobile: Build"
      ],
      "dependsOrder": "parallel",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

**理由:**
- `Ctrl+Shift+B` で全プロジェクトを一括ビルド
- CI/CD パイプラインと同じフローを再現

#### 4. files.exclude で重複を防止

```json
{
  "folders": [
    {
      "name": "workspace-root",
      "path": "."
    },
    {
      "name": "frontend",
      "path": "frontend"
    }
  ],
  "settings": {
    "files.exclude": {
      "frontend/": true    // ← workspace-root から frontend を除外
    }
  }
}
```

**理由:**
- サイドバーで同じファイルが重複表示されない
- ファイル検索結果が重複しない

---

### まとめ: ワークスペースとタスクの使い分け

| 構成パターン | 使用場面 | タスク配置 |
|------------|---------|-----------|
| **単一フォルダ** | 単一プロジェクト | `.vscode/tasks.json` |
| **マルチルート（プロジェクトレベル）** | 複数の独立したプロジェクト | `.code-workspace` + 各フォルダの `.vscode/tasks.json` |
| **マルチルート（サブモジュールレベル）** | サブモジュールを個別管理 | `.code-workspace` + ルートの Gradle タスク |
| **ハイブリッド** | ルート管理 + 主要モジュール編集 | `.code-workspace` + 必要に応じて `.vscode/tasks.json` |

---

## 実践的な例

### 1. Node.js / TypeScript プロジェクト

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "npm install",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "Compile TypeScript",
      "type": "shell",
      "command": "tsc",
      "group": "build",
      "problemMatcher": ["$tsc"],
      "presentation": {
        "reveal": "silent",
        "panel": "shared"
      }
    },
    {
      "label": "Watch TypeScript",
      "type": "shell",
      "command": "tsc --watch",
      "isBackground": true,
      "problemMatcher": ["$tsc-watch"],
      "presentation": {
        "reveal": "never"
      }
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "npm test",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Lint",
      "type": "shell",
      "command": "eslint src/**/*.ts",
      "problemMatcher": ["$eslint-stylish"],
      "presentation": {
        "reveal": "silent"
      }
    },
    {
      "label": "Build Production",
      "type": "shell",
      "command": "npm run build",
      "dependsOn": ["Compile TypeScript", "Lint"],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": []
    }
  ]
}
```

### 2. Java / Gradle プロジェクト

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Gradle: Clean",
      "type": "shell",
      "command": "./gradlew clean",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "Gradle: Build",
      "type": "shell",
      "command": "./gradlew build",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "shared",
        "clear": true
      }
    },
    {
      "label": "Gradle: Test",
      "type": "shell",
      "command": "./gradlew test",
      "group": "test",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Gradle: Clean Build",
      "type": "shell",
      "command": "./gradlew clean build",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "Run Application",
      "type": "shell",
      "command": "./gradlew bootRun",
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ]
}
```

### 3. Python プロジェクト

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Create Virtual Environment",
      "type": "shell",
      "command": "python3 -m venv venv",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "pip install -r requirements.txt",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Lint with Flake8",
      "type": "shell",
      "command": "flake8 src/",
      "problemMatcher": {
        "owner": "python",
        "fileLocation": ["relative", "${workspaceFolder}"],
        "pattern": {
          "regexp": "^(.+):(\\d+):(\\d+):\\s+(E\\d+)\\s+(.+)$",
          "file": 1,
          "line": 2,
          "column": 3,
          "code": 4,
          "message": 5
        }
      }
    },
    {
      "label": "Run Application",
      "type": "shell",
      "command": "python3 src/main.py",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ]
}
```

### 4. Docker 操作

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Docker: Build Image",
      "type": "shell",
      "command": "docker build -t ${input:imageName} .",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Docker: Run Container",
      "type": "shell",
      "command": "docker run -p 8080:8080 ${input:imageName}",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Docker Compose: Up",
      "type": "shell",
      "command": "docker-compose up -d",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "Docker Compose: Down",
      "type": "shell",
      "command": "docker-compose down",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "Docker: Clean",
      "type": "shell",
      "command": "docker system prune -f",
      "presentation": {
        "reveal": "always"
      }
    }
  ],
  "inputs": [
    {
      "id": "imageName",
      "type": "promptString",
      "description": "Enter Docker image name",
      "default": "myapp:latest"
    }
  ]
}
```

### 5. WebLogic デプロイ（前述のドキュメント連携）

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "WebLogic: Build All WARs",
      "type": "shell",
      "command": "./gradlew buildAllWars",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    },
    {
      "label": "WebLogic: Deploy All WARs",
      "type": "shell",
      "command": "./gradlew deployAllWars",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "clear": true
      }
    },
    {
      "label": "WebLogic: Redeploy project-a",
      "type": "shell",
      "command": "./gradlew :project-a:webapp:redeployThisWar",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    }
  ]
}
```

---

## 言語別のタスク設定例

### JavaScript / Node.js

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "npm: install",
      "type": "shell",
      "command": "npm install"
    },
    {
      "label": "npm: build",
      "type": "shell",
      "command": "npm run build",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": ["$tsc"]
    },
    {
      "label": "npm: test",
      "type": "shell",
      "command": "npm test",
      "group": "test"
    },
    {
      "label": "npm: dev",
      "type": "shell",
      "command": "npm run dev",
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ]
}
```

### Python

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Python: Run Current File",
      "type": "shell",
      "command": "python3 ${file}",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "pytest: Run All Tests",
      "type": "shell",
      "command": "pytest -v",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Black: Format Code",
      "type": "shell",
      "command": "black ${workspaceFolder}/src"
    }
  ]
}
```

### Java

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "javac: Compile Current File",
      "type": "shell",
      "command": "javac",
      "args": ["-d", "${workspaceFolder}/bin", "${file}"],
      "group": "build",
      "presentation": {
        "reveal": "silent"
      }
    },
    {
      "label": "java: Run Current Class",
      "type": "shell",
      "command": "java",
      "args": [
        "-cp",
        "${workspaceFolder}/bin",
        "${fileBasenameNoExtension}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Maven: Clean Install",
      "type": "shell",
      "command": "mvn clean install",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

### C/C++

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build with GCC",
      "type": "shell",
      "command": "gcc",
      "args": [
        "-g",
        "${file}",
        "-o",
        "${fileDirname}/${fileBasenameNoExtension}"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": ["$gcc"]
    },
    {
      "label": "Run Current Program",
      "type": "shell",
      "command": "${fileDirname}/${fileBasenameNoExtension}",
      "dependsOn": ["Build with GCC"],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ]
}
```

---

## トラブルシューティング

### 問題: タスクが見つからない

**症状:**
```
Tasks: Run Task を選択しても、タスクが表示されない
```

**解決策:**

1. **tasks.json の存在確認:**
   ```bash
   ls .vscode/tasks.json
   ```

2. **JSON 構文エラーのチェック:**
   - VSCode の「問題」パネルで JSON エラーを確認
   - `Ctrl+Shift+P` → "Tasks: Configure Task" で自動修正

3. **ワークスペースの再読み込み:**
   ```
   Ctrl+Shift+P → "Developer: Reload Window"
   ```

### 問題: タスクが実行されない

**症状:**
```
タスクを選択しても何も起こらない、またはエラーが出る
```

**解決策:**

1. **コマンドパスの確認:**
   ```json
   {
     "command": "/full/path/to/command"
   }
   ```

2. **作業ディレクトリの確認:**
   ```json
   {
     "options": {
       "cwd": "${workspaceFolder}"
     }
   }
   ```

3. **ターミナルで手動実行してテスト:**
   ```bash
   cd /path/to/workspace
   npm run build  # コマンドが実際に動作するか確認
   ```

### 問題: 問題マッチャーが機能しない

**症状:**
```
エラーが出ているのに「問題」パネルに表示されない
```

**解決策:**

1. **出力形式の確認:**
   - ターミナルの出力と問題マッチャーのパターンを照合

2. **デバッグ出力を有効化:**
   ```json
   {
     "problemMatcher": {
       "owner": "custom",
       "fileLocation": ["relative", "${workspaceFolder}"],
       "pattern": {
         "regexp": "^(.*):(\\d+):\\s+(.*)$",
         "file": 1,
         "line": 2,
         "message": 3
       }
     }
   }
   ```

3. **ビルトイン問題マッチャーを試す:**
   ```json
   {
     "problemMatcher": ["$tsc", "$eslint-stylish"]
   }
   ```

### 問題: 環境変数が認識されない

**症状:**
```
${env:MY_VAR} が展開されない
```

**解決策:**

1. **環境変数の設定確認:**
   ```bash
   echo $MY_VAR
   ```

2. **VSCode の再起動:**
   - 環境変数変更後は VSCode を再起動

3. **tasks.json 内で明示的に設定:**
   ```json
   {
     "options": {
       "env": {
         "MY_VAR": "value"
       }
     }
   }
   ```

### 問題: dependsOn のタスクが実行されない

**症状:**
```
依存タスクが実行されずにメインタスクだけ実行される
```

**解決策:**

1. **label の一致確認:**
   ```json
   {
     "label": "Build",  // ← この名前と
     "dependsOn": ["Build"]  // ← この名前が一致しているか
   }
   ```

2. **循環依存のチェック:**
   ```json
   // NG: 循環依存
   {
     "label": "A",
     "dependsOn": ["B"]
   },
   {
     "label": "B",
     "dependsOn": ["A"]
   }
   ```

---

## ベストプラクティス

### 1. タスクの命名規則

**推奨:**
```json
{
  "label": "Build: Production",
  "label": "Test: Unit Tests",
  "label": "Deploy: Staging"
}
```

**NG:**
```json
{
  "label": "build",
  "label": "test1",
  "label": "task"
}
```

**理由:**
- コマンドパレットで見つけやすい
- グループ化が明確
- 大文字始まりで統一

### 2. グループとデフォルトタスクの適切な設定

```json
{
  "tasks": [
    {
      "label": "Build: Development",
      "group": "build"
    },
    {
      "label": "Build: Production",
      "group": {
        "kind": "build",
        "isDefault": true  // ← 最も使うタスクをデフォルトに
      }
    }
  ]
}
```

### 3. プレゼンテーションの適切な設定

```json
{
  "tasks": [
    {
      "label": "Build",
      "presentation": {
        "reveal": "silent",  // ← 成功時は非表示
        "panel": "shared",   // ← 短時間タスクは共有
        "clear": true        // ← 前回の出力をクリア
      }
    },
    {
      "label": "Watch",
      "presentation": {
        "reveal": "always",    // ← 常に表示
        "panel": "dedicated",  // ← 専用パネル
        "focus": false         // ← フォーカスしない
      }
    }
  ]
}
```

### 4. 変数の活用

**ハードコーディングを避ける:**

```json
// NG
{
  "command": "python3 /home/user/project/src/main.py"
}

// OK
{
  "command": "python3 ${workspaceFolder}/src/main.py"
}
```

### 5. 問題マッチャーの設定

```json
{
  "tasks": [
    {
      "label": "Lint",
      "problemMatcher": ["$eslint-stylish"],  // ← 必ず設定
      "presentation": {
        "reveal": "silent"  // ← エラー時のみ表示
      }
    }
  ]
}
```

### 6. 依存関係の明確化

```json
{
  "tasks": [
    {
      "label": "Clean",
      "command": "rm -rf dist"
    },
    {
      "label": "Build",
      "command": "tsc",
      "dependsOn": ["Clean"]  // ← 依存関係を明示
    }
  ]
}
```

### 7. コメントの活用

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build Production",
      // プロダクションビルド用タスク
      // - TypeScript コンパイル
      // - ミニファイ
      // - ソースマップ生成
      "type": "shell",
      "command": "npm run build:prod"
    }
  ]
}
```

**注:** JSON5 形式ではコメントが使えますが、VSCode はデフォルトで許可しています。

---

## 関連ドキュメント

### 開発環境設定
- **[VSCode ワークスペースと settings.json 概要](vscode-workspace-overview.md)** - ワークスペース基本設定
- **[VSCode ショートカット完全リファレンス](vscode-shortcuts-reference.md)** - ショートカット一覧

### WebLogic 連携
- **[VSCode マルチWARプロジェクト統合デプロイ環境](weblogic/vscode-gradle-wlst-multi-war-deployment.md)** - Tasks を使った WebLogic デプロイ自動化

### 公式ドキュメント
- [VSCode Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [VSCode Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)

---

> このドキュメントは継続的に更新されます。質問や改善提案があれば、プロジェクトの Issue に投稿してください。
