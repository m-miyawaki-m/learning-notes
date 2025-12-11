# 技術学習ナレッジベース 目次構成

このリポジトリは、体系的な技術学習のための概念目次とノートを管理します。

## 📚 目次ファイル一覧

### 1. [現環境に必要な概念目次](./01_current-environment-concepts.md)
- **対象**: JavaScript, Java, Spring, Gradle, MyBatis, Oracle DB, Tomcat, WebLogic
- **範囲**: 実務で即使える概念
- **セクション数**: 6セクション（アプリ基礎、Java/Spring、DB、ビルド/デプロイ、JS/フロント、デバッグ）

### 2. [CS基礎概念目次](./02_cs-fundamentals-concepts.md)
- **対象**: ソフトウェアエンジニアとしての基礎知識
- **範囲**: 言語・技術非依存の普遍的概念
- **セクション数**: 10セクション（CS基礎、OS、ネットワーク、設計原則、DB理論、セキュリティ、テスト、Git、パフォーマンス、開発プロセス）

---

## 🗂️ 推奨リポジトリ構成

```
learning-notes/
├── README.md                              # このファイル
├── 01_current-environment-concepts.md     # 現環境概念目次
├── 02_cs-fundamentals-concepts.md         # CS基礎概念目次
│
├── core-concepts/                         # 言語非依存の概念ノート
│   ├── dependency-injection/
│   │   ├── README.md                      # 概念説明
│   │   ├── in-spring.md                   # Spring実装
│   │   └── in-nestjs.md                   # NestJS実装（将来用）
│   ├── orm/
│   ├── async-programming/
│   └── ...
│
├── java-ecosystem/                        # Java関連実装ノート
│   ├── spring/
│   │   ├── README.md                      # 学習計画
│   │   ├── di-ioc.md
│   │   ├── aop.md
│   │   └── transaction.md
│   ├── mybatis/
│   └── gradle/
│
├── javascript-ecosystem/                  # JavaScript関連ノート
│   ├── fundamentals/
│   ├── dom-manipulation/
│   └── async/
│
├── database/                              # DB関連ノート
│   ├── oracle/
│   ├── sql-optimization/
│   └── transaction-theory/
│
├── cs-fundamentals/                       # CS基礎ノート
│   ├── data-structures/
│   ├── algorithms/
│   ├── operating-systems/
│   └── network/
│
├── design/                                # 設計関連ノート
│   ├── solid-principles/
│   ├── design-patterns/
│   └── architecture-patterns/
│
├── security/                              # セキュリティノート
│   ├── web-security/
│   └── auth-authz/
│
├── testing/                               # テスト関連ノート
│   ├── unit-testing/
│   └── integration-testing/
│
├── tools/                                 # ツール関連ノート
│   ├── git/
│   ├── vscode/
│   └── debugging/
│
└── templates/                             # テンプレート
    ├── study-plan-template.md
    ├── concept-note-template.md
    └── progress-tracking-template.md
```

---

## 📋 テンプレート

### 学習計画テンプレート（study-plan-template.md）
```markdown
# {技術名} 学習計画

## 学習目標
- 

## 前提知識
- 

## 学習ロードマップ
### フェーズ1: 基礎
- [ ] 
### フェーズ2: 実践
- [ ] 

## 参考資料
- 

## 進捗記録
- YYYY-MM-DD: 
```

### 概念ノートテンプレート（concept-note-template.md）
```markdown
# {概念名}

## 概要
この概念が解決する問題

## 核心的な考え方
- 

## 実装例
### Java/Spring
\`\`\`java
// コード例
\`\`\`

### TypeScript/NestJS
\`\`\`typescript
// コード例
\`\`\`

## よくある誤解・落とし穴
- 

## 関連概念
- [概念A](../concept-a/README.md)
- [概念B](../concept-b/README.md)

## 参考資料
- 
```

---

## 🗺️ ナレッジマップ

### 📊 全体を可視化

**[KNOWLEDGE_MAP.md](./KNOWLEDGE_MAP.md)** - 全ドキュメントの関連性を可視化したマインドマップ
- Mermaid 図で技術スタック別の関連性を表示
- 学習パス推奨ルート
- タグ一覧と統計情報

**[GRAPH_VIEW.md](./GRAPH_VIEW.md)** - インタラクティブなナレッジグラフ（GitHub Pages 対応）
- Frontmatter の `related` フィールドに基づくドキュメント間の関連性を可視化
- 難易度別・カテゴリ別の色分け
- タグ別ドキュメント統計
- 自動生成（`python3 scripts/generate-mermaid-graph.py`）

**[TAG_INDEX.md](./TAG_INDEX.md)** - タグベースの自動生成インデックス（自動生成）
- タグ別ドキュメント一覧
- カテゴリ別一覧
- 難易度別一覧

### 🏷️ Frontmatter タグシステム

各 Markdown ファイルには以下の Frontmatter を付与：

```yaml
---
title: "VSCode Tasks 完全ガイド"
category: practices
tags:
  - vscode
  - tasks
  - automation
  - build-tools
difficulty: intermediate  # beginner, intermediate, advanced
related:
  - practices/vscode-workspace-overview.md
  - practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md
last_updated: 2025-12-12
---
```

### 🛠️ 管理スクリプト

**タグインデックス生成:**
```bash
python3 scripts/generate-tag-index.py
# → TAG_INDEX.md を自動生成
```

**ナレッジグラフ生成:**
```bash
python3 scripts/generate-mermaid-graph.py
# → GRAPH_VIEW.md を自動生成（GitHub Pages で表示可能）
```

**リンク切れチェック:**
```bash
python3 scripts/validate-links.py
# → 内部リンクの整合性を検証
```

**Frontmatter 一括追加:**
```bash
bash scripts/add-frontmatter.sh practices/
# → 指定ディレクトリの全 .md ファイルに Frontmatter を追加
```

---

## 🚀 使い方

### 1. 新しい概念を学ぶとき
```bash
# 1. KNOWLEDGE_MAP.md で全体構造を確認
# 2. GRAPH_VIEW.md でドキュメント間の関連性を確認
# 3. TAG_INDEX.md で関連ドキュメントを検索
# 4. 該当する目次ファイルで学習範囲を確認
# 5. core-concepts/ または 技術別フォルダに新規ノート作成
# 6. テンプレートを使用してノート作成
# 7. Frontmatter にタグを追加
# 8. python3 scripts/generate-tag-index.py でインデックス更新
# 9. python3 scripts/generate-mermaid-graph.py でグラフ更新
```

### 2. 学習計画を作成してもらうとき
```
Claudeに依頼: 「01_current-environment-concepts.mdの2.1（依存性注入）の学習計画を作成して」
→ 出力をそのまま core-concepts/dependency-injection/README.md として保存
```

### 3. 進捗管理
各概念フォルダに `progress.md` を作成:
```markdown
- [x] 概念理解
- [x] Spring実装学習
- [ ] 実プロジェクトへの適用
- [ ] コードレビューでの説明
```

### 4. 横断検索
```bash
# タグで検索（各ノートにタグを付与している場合）
grep -r "tags:.*dependency-injection" .

# 全文検索
grep -r "SOLID" .
```

---

## 🎯 学習優先順位の提案

### Phase 1: 即実務（1-3ヶ月）
1. `01_current-environment-concepts.md` のセクション1〜4
2. `02_cs-fundamentals-concepts.md` のセクション4（設計原則）
3. `02_cs-fundamentals-concepts.md` のセクション6.1（Webセキュリティ）

### Phase 2: 基礎固め（3-6ヶ月）
1. `02_cs-fundamentals-concepts.md` のセクション2（OS）
2. `02_cs-fundamentals-concepts.md` のセクション5（DB理論）
3. `02_cs-fundamentals-concepts.md` のセクション7（テスト）

### Phase 3: キャリアアップ（6ヶ月〜）
1. `02_cs-fundamentals-concepts.md` のセクション1（CS基礎）
2. `02_cs-fundamentals-concepts.md` のセクション9（パフォーマンス）
3. 新技術探索（Rust, TypeScript等）

---

## 📝 コミットルール例

```
feat: Springの依存性注入について学習ノート追加
progress: データベース最適化セクション完了
refactor: ORMの概念ノートを再構成
docs: 学習計画テンプレート更新
```

---

## 🌐 GitHub Pages で公開する方法

このリポジトリは GitHub Pages でホスティングすることで、Web ブラウザから閲覧可能な技術ドキュメントサイトとして公開できます。

### セットアップ手順

#### 1. GitHub リポジトリにプッシュ

```bash
cd /home/m-miyawaki/dev/learning-notes
git add .
git commit -m "docs: Add knowledge graph and Frontmatter guide"
git push origin main
```

#### 2. GitHub Pages を有効化

1. GitHub リポジトリページにアクセス
2. **Settings** → **Pages** をクリック
3. **Source** を `Deploy from a branch` に設定
4. **Branch** を `main` / `root` に設定
5. **Save** をクリック

#### 3. 公開 URL を確認

数分後、以下の URL でアクセス可能になります：

```
https://<username>.github.io/learning-notes/
```

#### 4. Mermaid の自動レンダリング

GitHub Pages は **Mermaid を自動でレンダリング** します。

- [KNOWLEDGE_MAP.md](./KNOWLEDGE_MAP.md) の Mermaid 図が表示される
- [GRAPH_VIEW.md](./GRAPH_VIEW.md) のナレッジグラフが表示される
- インタラクティブなグラフとして閲覧可能

### カスタムドメインの設定（オプション）

独自ドメインを使用する場合：

1. GitHub Pages 設定で **Custom domain** を設定
2. DNS レコードを追加：
   ```
   CNAME レコード: www → <username>.github.io
   A レコード: @ → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   ```

### Jekyll テーマの適用（オプション）

GitHub Pages は Jekyll をサポートしています。テーマを適用する場合：

**`_config.yml` を作成:**

```yaml
title: "技術学習ナレッジベース"
description: "体系的な技術学習のための概念目次とノート"
theme: jekyll-theme-cayman  # または minima, slate, etc.
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge
```

**再デプロイ:**

```bash
git add _config.yml
git commit -m "feat: Add Jekyll theme"
git push origin main
```

### 自動更新ワークフロー（GitHub Actions）

Frontmatter を更新したら自動でグラフを再生成する GitHub Actions ワークフロー：

**`.github/workflows/update-graphs.yml`:**

```yaml
name: Update Knowledge Graphs

on:
  push:
    branches:
      - main
    paths:
      - 'practices/**/*.md'
      - 'concepts/**/*.md'

jobs:
  update-graphs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Generate graphs
        run: |
          python3 scripts/generate-tag-index.py
          python3 scripts/generate-mermaid-graph.py

      - name: Commit changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add TAG_INDEX.md GRAPH_VIEW.md
          git diff --quiet && git diff --staged --quiet || git commit -m "docs: Auto-update knowledge graphs"
          git push
```

---

## 🔗 便利なリンク

- [現環境概念目次](./01_current-environment-concepts.md) - 実務直結の概念
- [CS基礎概念目次](./02_cs-fundamentals-concepts.md) - エンジニアの基礎体力
- [GRAPH_VIEW.md](./GRAPH_VIEW.md) - ナレッジグラフ（GitHub Pages で閲覧推奨）
- [Frontmatter 完全ガイド](./practices/frontmatter-guide.md) - メタデータ管理の基礎

---

## 📌 Tips

1. **重複管理**: 同じ概念が複数技術に登場する場合
   - `core-concepts/` に概念ノート作成
   - 各技術フォルダからリンクで参照

2. **検索性向上**: 各ノートの先頭にタグを付与
   ```markdown
   Tags: #java #spring #dependency-injection #design-pattern
   ```

3. **定期レビュー**: 月1回、cross-reference.mdを更新して全体を俯瞰

4. **実践記録**: 実プロジェクトで適用した概念は `projects/` フォルダに事例として記録
