# ナレッジグラフ（Mermaid 可視化）

> Frontmatter の `related` フィールドに基づくドキュメント間の関連性を可視化

## 凡例

- 🟢 **Beginner** - 初心者向け
- 🟡 **Intermediate** - 中級者向け
- 🔴 **Advanced** - 上級者向け

## カテゴリ別の色分け

- 🔵 **Practices** - 実践ガイド
- 🟢 **Concepts** - 概念説明
- 🟠 **Templates** - テンプレート

---

## 全体グラフ

```mermaid
graph TD

    %% スタイル定義
    classDef practices fill:#3b82f6,stroke:#1e40af,color:#fff
    classDef concepts fill:#10b981,stroke:#047857,color:#fff
    classDef templates fill:#f59e0b,stroke:#d97706,color:#fff
    classDef beginner fill:#22c55e,stroke:#16a34a,color:#fff
    classDef intermediate fill:#eab308,stroke:#ca8a04,color:#000
    classDef advanced fill:#ef4444,stroke:#dc2626,color:#fff

    %% ノード定義
    practices_frontmatter_guide["🟢 Frontmatter 完全ガイド：Markdownメタデー"]
    class practices_frontmatter_guide practices
    tasks_complete_guide["🟡 VSCode Tasks 完全ガイド"]
    class tasks_complete_guide practices
    multi_war_deployment["🔴 VSCode マルチWARプロジェクト統合デプロイ環境"]
    class multi_war_deployment practices

    %% 関連ドキュメントのリンク
    practices_frontmatter_guide -.->|関連| tasks_complete_guide
    practices_frontmatter_guide -.->|関連| KNOWLEDGE_MAP
    practices_frontmatter_guide -.->|関連| README
    tasks_complete_guide -.->|関連| practices_vscode_workspace_overview
    tasks_complete_guide -.->|関連| practices_vscode_workspace_details
    tasks_complete_guide -.->|関連| multi_war_deployment
    multi_war_deployment -.->|関連| tasks_complete_guide
    multi_war_deployment -.->|関連| gradle_weblogic_setup
    multi_war_deployment -.->|関連| complex_multimodule_setup
    multi_war_deployment -.->|関連| wlst_cli_windows

```

---

## カテゴリ別グラフ

### Practices

```mermaid
graph LR
    practices_frontmatter_guide["Frontmatter 完全ガイド：Ma"]
    tasks_complete_guide["VSCode Tasks 完全ガイド"]
    multi_war_deployment["VSCode マルチWARプロジェクト統"]
```

---

## タグ別ドキュメント数

| タグ | ドキュメント数 |
|------|---------------|
| `vscode` | 2 |
| `tasks` | 2 |
| `frontmatter` | 1 |
| `yaml` | 1 |
| `markdown` | 1 |
| `documentation` | 1 |
| `knowledge-management` | 1 |
| `metadata` | 1 |
| `automation` | 1 |
| `build-tools` | 1 |
| `debugging` | 1 |
| `weblogic` | 1 |
| `gradle` | 1 |
| `wlst` | 1 |
| `deployment` | 1 |
| `multi-module` | 1 |
| `java` | 1 |

---

**自動生成日時**: このファイルは `scripts/generate-mermaid-graph.py` で自動生成されます。

**更新方法**:
```bash
python3 scripts/generate-mermaid-graph.py
```
