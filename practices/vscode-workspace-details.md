# VSCode ワークスペースと settings.json 詳細ガイド

## 目次
1. [ワークスペース詳細設定](#ワークスペース詳細設定)
2. [settings.json 詳細項目](#settingsjson-詳細項目)
3. [マルチルートワークスペース実践](#マルチルートワークスペース実践)
4. [言語別設定](#言語別設定)
5. [拡張機能との連携](#拡張機能との連携)
6. [トラブルシューティング](#トラブルシューティング)

---

## ワークスペース詳細設定

### フォルダ構成の推奨パターン

#### パターン1: 各プロジェクトを個別指定（推奨）

```json
{
  "folders": [
    {
      "name": "Backend",
      "path": "/home/user/projects/backend"
    },
    {
      "name": "Frontend",
      "path": "/home/user/projects/frontend"
    },
    {
      "name": "Shared",
      "path": "/home/user/projects/shared"
    }
  ]
}
```

**メリット**:
- 各プロジェクトのルートが明確
- プロジェクト固有の `.vscode/settings.json` が正しく認識される
- Java/Gradle/Maven等のビルドツールがプロジェクトルートを正しく検出
- `${workspaceFolder}` 変数が各プロジェクトのルートを指す
- 不要なファイルがエクスプローラーに表示されない

**デメリット**:
- `.code-workspace` ファイルの記述が少し長くなる

#### パターン2: 親ディレクトリを指定（非推奨）

```json
{
  "folders": [
    {
      "name": "Projects",
      "path": "/home/user/projects"  // 親ディレクトリをまとめて指定
    }
  ]
}
```

**デメリット**:
- プロジェクトルートが曖昧になる
- ビルドツールがプロジェクトを正しく認識できない場合がある
- Java Language Serverが複数のプロジェクトを混同する可能性
- `${workspaceFolder}` が親ディレクトリを指してしまう
- 関連のないファイル（README、設定ファイル等）も表示される
- 各プロジェクトの `.vscode/settings.json` が無視される可能性

**メリット**:
- 設定がシンプル（フォルダ1つだけ指定）
- 親ディレクトリ内のファイルも参照したい場合は便利

#### 推奨される使い分け

| シナリオ | 推奨パターン | 理由 |
|---------|------------|------|
| 複数の独立したプロジェクト開発 | パターン1（個別指定） | ビルドツールが正しく動作 |
| モノレポ（単一リポジトリ内に複数パッケージ） | パターン1（個別指定） | 各パッケージを明確に分離 |
| 単純なファイル閲覧・編集 | パターン2（親ディレクトリ） | 構造確認が主目的の場合 |
| Java/Gradle/Mavenプロジェクト | パターン1（個別指定） | **必須**：ビルドツールがルートを検出 |

#### 実例: Gradle マルチプロジェクトの場合

**❌ 非推奨（親ディレクトリ指定）**:
```json
{
  "folders": [
    {
      "name": "All Projects",
      "path": "/home/user/workspace"
    }
  ]
}
```
→ Gradle が `backend/build.gradle` や `frontend/build.gradle` を正しく検出できない

**✅ 推奨（個別指定）**:
```json
{
  "folders": [
    {
      "name": "Backend (Java 17)",
      "path": "/home/user/workspace/backend"
    },
    {
      "name": "Frontend (Node.js)",
      "path": "/home/user/workspace/frontend"
    }
  ]
}
```
→ 各プロジェクトのビルドファイルが正しく認識される

### .code-workspace ファイルの詳細構造

```json
{
  "folders": [
    {
      "name": "バックエンド",
      "path": "../backend",
      "settings": {
        // このフォルダ固有の設定を上書き
        "java.home": "/usr/lib/jvm/java-17-openjdk"
      }
    },
    {
      "name": "フロントエンド",
      "path": "../frontend",
      "settings": {
        "typescript.tsdk": "node_modules/typescript/lib"
      }
    },
    {
      "name": "共通ライブラリ",
      "path": "../shared-lib"
    }
  ],
  "settings": {
    // ワークスペース全体の設定
    "editor.formatOnSave": true,
    "files.autoSave": "onFocusChange",
    "terminal.integrated.cwd": "${workspaceFolder}",

    // 除外パターン
    "files.exclude": {
      "**/.git": true,
      "**/.svn": true,
      "**/.DS_Store": true,
      "**/node_modules": true,
      "**/.gradle": true,
      "**/build": true,
      "**/bin": true
    },

    "search.exclude": {
      "**/node_modules": true,
      "**/bower_components": true,
      "**/*.code-search": true,
      "**/build": true,
      "**/dist": true,
      "**/.gradle": true
    }
  },
  "extensions": {
    "recommendations": [
      "vscjava.vscode-java-pack",
      "redhat.java",
      "vscjava.vscode-gradle",
      "dbaeumer.vscode-eslint",
      "esbenp.prettier-vscode"
    ],
    "unwantedRecommendations": [
      "ms-vscode.csharp"
    ]
  },
  "launch": {
    // デバッグ設定の共有
    "version": "0.2.0",
    "configurations": [
      {
        "type": "java",
        "name": "バックエンド起動",
        "request": "launch",
        "mainClass": "com.example.Application",
        "projectName": "backend"
      }
    ]
  },
  "tasks": {
    // タスク設定の共有
    "version": "2.0.0",
    "tasks": [
      {
        "label": "全プロジェクトビルド",
        "dependsOn": ["バックエンドビルド", "フロントエンドビルド"]
      }
    ]
  }
}
```

### パス指定の種類

| 記法 | 説明 | 例 |
|------|------|-----|
| 絶対パス | フルパス指定 | `/home/user/project` |
| 相対パス | `.code-workspace` からの相対 | `../backend` |
| `${workspaceFolder}` | 現在のワークスペースフォルダ | ランタイムで解決 |
| `${workspaceFolder:name}` | 特定フォルダのパス | `${workspaceFolder:backend}` |
| `${env:VAR}` | 環境変数 | `${env:JAVA_HOME}` |

---

## settings.json 詳細項目

### Java開発の詳細設定

```json
{
  // Java ランタイム設定
  "java.home": "/usr/lib/jvm/java-11-openjdk",

  // 複数バージョンのJava管理
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-1.8",
      "path": "/usr/lib/jvm/java-8-openjdk",
      "default": false
    },
    {
      "name": "JavaSE-11",
      "path": "/usr/lib/jvm/java-11-openjdk",
      "default": true
    },
    {
      "name": "JavaSE-17",
      "path": "/usr/lib/jvm/java-17-openjdk"
    }
  ],

  // プロジェクト構造設定
  "java.project.sourcePaths": ["src/main/java"],
  "java.project.outputPath": "bin",
  "java.project.referencedLibraries": [
    "lib/**/*.jar",
    "/path/to/external/libs/**/*.jar"
  ],

  // ビルドツール設定
  "java.import.gradle.enabled": true,
  "java.import.gradle.wrapper.enabled": true,
  "java.import.gradle.home": "/opt/gradle",
  "java.import.gradle.java.home": "/usr/lib/jvm/java-11-openjdk",
  "java.import.gradle.offline.enabled": false,

  // コード補完・分析
  "java.completion.enabled": true,
  "java.completion.guessMethodArguments": true,
  "java.completion.favoriteStaticMembers": [
    "org.junit.Assert.*",
    "org.junit.jupiter.api.Assertions.*",
    "org.mockito.Mockito.*"
  ],

  // フォーマッター
  "java.format.enabled": true,
  "java.format.settings.url": "${workspaceFolder}/.vscode/java-formatter.xml",
  "java.format.settings.profile": "GoogleStyle",

  // リファクタリング
  "java.codeGeneration.useBlocks": true,
  "java.codeGeneration.generateComments": false,

  // Language Server設定
  "java.jdt.ls.vmargs": "-XX:+UseParallelGC -XX:GCTimeRatio=4 -XX:AdaptiveSizePolicyWeight=90 -Dsun.zip.disableMemoryMapping=true -Xmx2G -Xms100m"
}
```

### エディタ詳細設定

```json
{
  // 表示設定
  "editor.fontSize": 14,
  "editor.fontFamily": "'JetBrains Mono', 'Fira Code', Consolas, monospace",
  "editor.fontLigatures": true,
  "editor.lineHeight": 1.5,
  "editor.letterSpacing": 0.5,
  "editor.renderWhitespace": "boundary",
  "editor.rulers": [80, 120],

  // 編集動作
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.detectIndentation": true,
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.trimAutoWhitespace": true,

  // 保存時の動作
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,

  // 文字コード
  "files.encoding": "utf8",
  "files.eol": "\n",
  "files.autoGuessEncoding": false,

  // IntelliSense
  "editor.quickSuggestions": {
    "other": true,
    "comments": false,
    "strings": true
  },
  "editor.suggestSelection": "first",
  "editor.acceptSuggestionOnCommitCharacter": true,
  "editor.acceptSuggestionOnEnter": "on",
  "editor.tabCompletion": "on",

  // ミニマップ
  "editor.minimap.enabled": true,
  "editor.minimap.maxColumn": 120,
  "editor.minimap.renderCharacters": false,

  // ブレッドクラム
  "breadcrumbs.enabled": true,
  "breadcrumbs.filePath": "on",
  "breadcrumbs.symbolPath": "on"
}
```

### ファイルとフォルダの除外設定

```json
{
  // エクスプローラーから除外
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/Thumbs.db": true,
    "**/.classpath": true,
    "**/.project": true,
    "**/.settings": true,
    "**/.factorypath": true,
    "**/.gradle": true,
    "**/build": true,
    "**/bin": true,
    "**/target": true,
    "**/node_modules": true,
    "**/.next": true,
    "**/dist": true,
    "**/out": true,
    "**/*.class": true,
    "**/.idea": true
  },

  // 検索から除外
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/*.code-search": true,
    "**/build": true,
    "**/dist": true,
    "**/target": true,
    "**/.gradle": true,
    "**/.m2": true,
    "**/coverage": true,
    "**/.nyc_output": true,
    "**/*.min.js": true,
    "**/*.map": true
  },

  // ファイル監視から除外
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.hg/store/**": true,
    "**/.gradle/**": true,
    "**/build/**": true,
    "**/target/**": true
  }
}
```

### ターミナル設定

```json
{
  "terminal.integrated.defaultProfile.linux": "bash",
  "terminal.integrated.profiles.linux": {
    "bash": {
      "path": "/bin/bash",
      "icon": "terminal-bash"
    },
    "zsh": {
      "path": "/bin/zsh"
    }
  },
  "terminal.integrated.cwd": "${workspaceFolder}",
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.fontFamily": "monospace",
  "terminal.integrated.scrollback": 10000,
  "terminal.integrated.shell.linux": "/bin/bash"
}
```

---

## マルチルートワークスペース実践

### ケース1: フロント・バック分離プロジェクト

```json
{
  "folders": [
    {
      "name": "🔧 Backend (Spring Boot)",
      "path": "../backend",
      "settings": {
        "java.home": "/usr/lib/jvm/java-17-openjdk",
        "spring-boot.ls.java.home": "/usr/lib/jvm/java-17-openjdk",
        "files.exclude": {
          "**/target": true,
          "**/.gradle": true
        }
      }
    },
    {
      "name": "🎨 Frontend (React)",
      "path": "../frontend",
      "settings": {
        "typescript.tsdk": "node_modules/typescript/lib",
        "files.exclude": {
          "**/node_modules": true,
          "**/.next": true,
          "**/dist": true
        }
      }
    },
    {
      "name": "📚 Documentation",
      "path": "../docs"
    }
  ],
  "settings": {
    "editor.formatOnSave": true,
    "files.autoSave": "onFocusChange"
  }
}
```

### ケース2: モノレポ構成

```json
{
  "folders": [
    {
      "name": "Root",
      "path": "."
    },
    {
      "name": "packages/api",
      "path": "packages/api"
    },
    {
      "name": "packages/web",
      "path": "packages/web"
    },
    {
      "name": "packages/mobile",
      "path": "packages/mobile"
    },
    {
      "name": "packages/shared",
      "path": "packages/shared"
    }
  ]
}
```

### ケース3: レガシーとモダンの混在

```json
{
  "folders": [
    {
      "name": "Legacy System (Java 8)",
      "path": "../legacy",
      "settings": {
        "java.configuration.runtimes": [
          {
            "name": "JavaSE-1.8",
            "path": "/usr/lib/jvm/java-8-openjdk",
            "default": true
          }
        ]
      }
    },
    {
      "name": "New System (Java 17)",
      "path": "../new-system",
      "settings": {
        "java.configuration.runtimes": [
          {
            "name": "JavaSE-17",
            "path": "/usr/lib/jvm/java-17-openjdk",
            "default": true
          }
        ]
      }
    }
  ]
}
```

---

## 言語別設定

### 言語固有の設定を上書き

```json
{
  "editor.formatOnSave": true,

  "[java]": {
    "editor.defaultFormatter": "redhat.java",
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  },

  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.tabSize": 2
  },

  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.tabSize": 2,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },

  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.tabSize": 4
  },

  "[json]": {
    "editor.defaultFormatter": "vscode.json-language-features",
    "editor.tabSize": 2
  },

  "[xml]": {
    "editor.defaultFormatter": "redhat.vscode-xml",
    "editor.tabSize": 2
  },

  "[markdown]": {
    "editor.wordWrap": "on",
    "editor.quickSuggestions": false
  },

  "[yaml]": {
    "editor.insertSpaces": true,
    "editor.tabSize": 2,
    "editor.autoIndent": "advanced"
  }
}
```

---

## 拡張機能との連携

### ESLint設定

```json
{
  "eslint.enable": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "eslint.workingDirectories": [
    {"mode": "auto"}
  ],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Prettier設定

```json
{
  "prettier.enable": true,
  "prettier.requireConfig": true,
  "prettier.configPath": ".prettierrc",
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### GitLens設定

```json
{
  "gitlens.advanced.messages": {
    "suppressShowKeyBindingsNotice": true
  },
  "gitlens.views.repositories.location": "scm",
  "gitlens.views.fileHistory.location": "explorer",
  "gitlens.currentLine.enabled": true,
  "gitlens.hovers.currentLine.over": "line"
}
```

---

## トラブルシューティング

### Java Language Serverが起動しない

**症状**: Java補完が効かない、import解決できない

**確認項目**:
```json
{
  // 1. Java Homeが正しいか確認
  "java.home": "/usr/lib/jvm/java-11-openjdk",

  // 2. VMArgsのメモリサイズを確認
  "java.jdt.ls.vmargs": "-Xmx2G",

  // 3. インポート設定を確認
  "java.import.gradle.enabled": true,
  "java.import.gradle.wrapper.enabled": true
}
```

**解決手順**:
1. コマンドパレット → "Java: Clean Language Server Workspace"
2. VSCode再起動
3. Gradleプロジェクトを再インポート

### 設定が反映されない

**優先順位の確認**:
```
ワークスペース設定 > フォルダ設定 > ユーザー設定
```

**確認方法**:
1. `Ctrl+Shift+P` → "Preferences: Open Settings (UI)"
2. 右上のタブで「User」「Workspace」「Folder」を切り替え
3. 設定項目にカーソルを合わせると、現在どのレベルで設定されているかが表示される

### .code-workspace ファイルが認識されない

**原因**:
- JSONの構文エラー
- パスの指定ミス
- 相対パスの基準間違い

**確認**:
```bash
# JSONの検証
cat workspace.code-workspace | python3 -m json.tool

# パスの確認
ls -la <指定したパス>
```

### Gradle同期エラー

```json
{
  // Gradle Wrapper利用を強制
  "java.import.gradle.wrapper.enabled": true,

  // オフラインモード無効化
  "java.import.gradle.offline.enabled": false,

  // Gradle Home指定（Wrapper使わない場合）
  "java.import.gradle.home": "/opt/gradle",

  // Gradle用のJava指定
  "java.import.gradle.java.home": "/usr/lib/jvm/java-11-openjdk"
}
```

### ファイル除外が効かない

```json
{
  // 3箇所すべてで設定する
  "files.exclude": { "**/.gradle": true },
  "search.exclude": { "**/.gradle": true },
  "files.watcherExclude": { "**/.gradle/**": true }
}
```

---

## ベストプラクティス

### 1. チーム開発での設定共有

```
project/
├── .vscode/
│   ├── settings.json      # Git管理する（プロジェクト共通設定）
│   ├── extensions.json    # Git管理する（推奨拡張機能）
│   ├── launch.json        # Git管理する（デバッグ設定）
│   └── tasks.json         # Git管理する（タスク設定）
└── .gitignore            # .vscode/ は除外しない
```

**.gitignore設定例**:
```
# VSCode個人設定は除外
.vscode/*.local.json
.vscode/.history/

# ワークスペースファイルの個人設定
*.code-workspace

# ただし、チーム共有用は含める（任意）
!project.code-workspace
```

### 2. 環境変数の活用

```json
{
  "java.home": "${env:JAVA_HOME}",
  "terminal.integrated.env.linux": {
    "PROJECT_ROOT": "${workspaceFolder}",
    "CUSTOM_LIB": "${workspaceFolder}/lib"
  }
}
```

### 3. 設定のコメント活用

```jsonc
{
  // プロジェクト: ECサイトバックエンド
  // 更新日: 2025-12-10
  // 担当: 開発チーム

  "java.home": "/usr/lib/jvm/java-17-openjdk",  // Java 17必須
  "editor.tabSize": 4,  // チームコーディング規約

  // 以下は性能問題があるため無効化
  // "java.autobuild.enabled": true
}
```

---

## 参考リンク

- [VSCode公式ドキュメント - Workspace](https://code.visualstudio.com/docs/editor/workspaces)
- [VSCode公式ドキュメント - Settings](https://code.visualstudio.com/docs/getstarted/settings)
- [関連ドキュメント](vscode-multi-project-workspace.md) - マルチプロジェクト実例
- [関連ドキュメント](vscode-shortcuts-reference.md) - キーボードショートカット
