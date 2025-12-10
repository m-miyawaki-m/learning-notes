# VSCode ワークスペースと settings.json 概要

## ワークスペースとは

VSCodeのワークスペースは、プロジェクトの設定や状態を保存・管理するための仕組みです。

### ワークスペースの種類

1. **フォルダワークスペース（Single-folder Workspace）**
   - 単一のフォルダを開いた状態
   - 設定は `.vscode/settings.json` に保存
   - 最もシンプルな形態

2. **マルチルートワークスペース（Multi-root Workspace）**
   - 複数のフォルダを同時に開ける
   - `.code-workspace` ファイルで管理
   - 異なるプロジェクトを横断的に作業可能

## settings.json の階層構造

VSCodeの設定には3つのレベルがあり、優先順位は下記の通り：

```
ワークスペース設定（最優先）
  ↓
フォルダ設定
  ↓
ユーザー設定（デフォルト）
```

### 1. ユーザー設定（User Settings）
- **場所**: `~/.config/Code/User/settings.json` (Linux/Mac)
- **場所**: `%APPDATA%\Code\User\settings.json` (Windows)
- **スコープ**: すべてのプロジェクトに適用
- **用途**: エディタの基本設定、テーマ、フォントなど

### 2. ワークスペース設定（Workspace Settings）
- **場所**: `.code-workspace` ファイル内の `settings` セクション
- **スコープ**: ワークスペース全体に適用
- **用途**: 複数フォルダ共通の設定

### 3. フォルダ設定（Folder Settings）
- **場所**: `<フォルダ>/.vscode/settings.json`
- **スコープ**: 特定のフォルダのみに適用
- **用途**: プロジェクト固有の設定

## 基本的な使い分け

| 設定内容 | 推奨レベル | 理由 |
|---------|-----------|------|
| エディタのフォントサイズ | ユーザー設定 | 個人の好みで全プロジェクト共通 |
| テーマ・カラースキーム | ユーザー設定 | 個人の好み |
| Javaのランタイムパス | フォルダ設定 | プロジェクトごとに異なる可能性 |
| ビルドタスク設定 | フォルダ設定 | プロジェクト固有 |
| リンター設定 | フォルダ設定 | プロジェクトのコーディング規約 |
| 複数プロジェクト共通設定 | ワークスペース設定 | マルチルート時の共通設定 |

## マルチルートワークスペースのフォルダ指定方法

### 推奨: 各プロジェクトを個別に指定

複数のプロジェクトを扱う場合、**親ディレクトリではなく、各プロジェクトのパスを個別に指定することを推奨**します。

**理由**:
- ビルドツール（Gradle/Maven/npm等）がプロジェクトルートを正しく検出
- 各プロジェクトの `.vscode/settings.json` が正しく適用される
- `${workspaceFolder}` 変数が各プロジェクトのルートを指す
- Java Language Server等の言語サーバーが正しく動作

```
❌ 非推奨
/workspace              ← これを指定すると問題が起きやすい
├── backend/
├── frontend/
└── shared/

✅ 推奨
各プロジェクトを個別に指定:
- /workspace/backend
- /workspace/frontend
- /workspace/shared
```

詳細は [vscode-workspace-details.md](vscode-workspace-details.md#フォルダ構成の推奨パターン) を参照してください。

## .code-workspace ファイルの基本構造

```json
{
  "folders": [
    {
      "name": "プロジェクトA",
      "path": "/path/to/projectA"  // 各プロジェクトを個別に指定
    },
    {
      "name": "プロジェクトB",
      "path": "/path/to/projectB"  // 親ディレクトリではなく個別指定
    }
  ],
  "settings": {
    "editor.fontSize": 14,
    "files.autoSave": "afterDelay"
  },
  "extensions": {
    "recommendations": [
      "vscjava.vscode-java-pack",
      "redhat.java"
    ]
  }
}
```

## ワークスペースのメリット

1. **環境の再現性**
   - チーム内で同じ設定を共有可能
   - `.vscode` や `.code-workspace` をgit管理

2. **プロジェクトの切り替えが容易**
   - ワークスペースファイルを開くだけで環境が整う
   - 最近使用したワークスペース履歴から選択可能

3. **設定の分離**
   - プロジェクトごとに異なるJavaバージョンを使用
   - プロジェクト固有のリンター・フォーマッター設定

4. **マルチプロジェクト開発**
   - フロントエンドとバックエンドを同時表示
   - モノレポ構成での各パッケージ管理

## よく使う設定項目

### エディタ関連
```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 4,
  "editor.formatOnSave": true,
  "editor.rulers": [80, 120],
  "files.encoding": "utf8"
}
```

### Java開発関連
```json
{
  "java.home": "/usr/lib/jvm/java-11-openjdk",
  "java.configuration.runtimes": [...],
  "java.project.sourcePaths": ["src"],
  "java.project.outputPath": "bin"
}
```

### 除外設定
```json
{
  "files.exclude": {
    "**/.git": true,
    "**/node_modules": true,
    "**/.gradle": true
  },
  "search.exclude": {
    "**/build": true,
    "**/dist": true
  }
}
```

## 設定の確認方法

1. **GUI**: `Ctrl+,` または `Cmd+,` で設定画面を開く
2. **JSON直接編集**: 設定画面右上の「設定（JSON）を開く」アイコン
3. **コマンドパレット**: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

## 次のステップ

詳細な設定例やトラブルシューティングについては、以下を参照：
- [vscode-workspace-details.md](vscode-workspace-details.md) - 詳細設定とベストプラクティス
- [vscode-multi-project-workspace.md](weblogic/vscode-multi-project-workspace.md) - マルチプロジェクト具体例
