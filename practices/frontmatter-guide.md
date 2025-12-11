---
title: "Frontmatter 完全ガイド：Markdownメタデータ管理の基礎"
category: practices
tags:
  - frontmatter
  - yaml
  - markdown
  - documentation
  - knowledge-management
  - metadata
difficulty: beginner
related:
  - practices/vscode-tasks-complete-guide.md
  - KNOWLEDGE_MAP.md
  - README.md
last_updated: 2025-12-12
---

# Frontmatter 完全ガイド：Markdownメタデータ管理の基礎

> Markdown ファイルに機械可読なメタデータを付与する標準的手法

## 目次

1. [Frontmatter とは](#frontmatter-とは)
2. [なぜ Frontmatter が必要なのか](#なぜ-frontmatter-が必要なのか)
3. [YAML 構文の基礎](#yaml-構文の基礎)
4. [標準的なプロパティ](#標準的なプロパティ)
5. [learning-notes での活用例](#learning-notes-での活用例)
6. [タグ付けのベストプラクティス](#タグ付けのベストプラクティス)
7. [ツール統合](#ツール統合)
8. [自動化とスクリプト連携](#自動化とスクリプト連携)
9. [よくある間違いと落とし穴](#よくある間違いと落とし穴)
10. [関連ドキュメント](#関連ドキュメント)

---

## Frontmatter とは

**Frontmatter（フロントマター）** は、Markdown ファイルの冒頭に記述する **YAML 形式のメタデータブロック** です。

### 基本構造

```markdown
---
title: "ドキュメントのタイトル"
category: practices
tags:
  - tag1
  - tag2
difficulty: intermediate
last_updated: 2025-12-12
---

# ここから本文が始まる

通常の Markdown コンテンツ...
```

### 構成要素

1. **開始デリミタ**: `---` (ハイフン3つ)
2. **YAML メタデータ**: キー・バリューペアの集合
3. **終了デリミタ**: `---` (ハイフン3つ)
4. **空行** (推奨)
5. **本文コンテンツ**

### 重要な特徴

- **機械可読**: プログラムで解析・処理可能
- **人間可読**: テキストエディタで直接編集可能
- **標準化**: Jekyll, Hugo, Obsidian, VSCode 等で広く採用
- **拡張性**: 必要に応じてカスタムプロパティを追加可能

---

## なぜ Frontmatter が必要なのか

### 問題：ドキュメントの急増と管理の限界

**シナリオ**: 技術ノートが 53 ファイルに増加

```
learning-notes/
├── concepts/
│   ├── dependency-injection.md
│   ├── orm-fundamentals.md
│   └── ... (20+ files)
├── practices/
│   ├── vscode-tasks-complete-guide.md
│   ├── weblogic/
│   │   ├── vscode-gradle-wlst-multi-war-deployment.md
│   │   └── ... (15+ files)
│   └── ... (18+ files)
```

**課題**:
- どのドキュメントが初心者向けか分からない
- WebLogic 関連のドキュメントが散在
- ドキュメント同士の関連性が不明
- 全文検索しても文脈が掴めない

### 解決：Frontmatter による構造化

#### Before（Frontmatter なし）
```markdown
# VSCode Tasks 完全ガイド

このドキュメントは VSCode の Tasks 機能について説明します...
```

**問題点**:
- タイトルはあるが、検索には不便
- カテゴリや難易度が本文に埋もれる
- 関連ドキュメントへのリンクが散在
- プログラムで処理できない

#### After（Frontmatter あり）
```markdown
---
title: "VSCode Tasks 完全ガイド"
category: practices
tags:
  - vscode
  - tasks
  - automation
  - build-tools
difficulty: intermediate
related:
  - practices/vscode-workspace-overview.md
  - practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md
last_updated: 2025-12-12
---

# VSCode Tasks 完全ガイド

このドキュメントは VSCode の Tasks 機能について説明します...
```

**改善点**:
- ✅ タグで検索可能 (`tags: vscode`)
- ✅ 難易度が明示的 (`difficulty: intermediate`)
- ✅ 関連ドキュメントが機械可読
- ✅ Python スクリプトで自動インデックス生成可能

### 具体的なメリット

#### 1. 自動インデックス生成

```python
# scripts/generate-tag-index.py
def extract_frontmatter(file_path):
    # Frontmatter を解析
    # → TAG_INDEX.md を自動生成
```

**結果**: [TAG_INDEX.md](../TAG_INDEX.md) で全ドキュメントがタグ別・カテゴリ別に整理

#### 2. ナレッジマップ自動生成

```python
# KNOWLEDGE_MAP.md の自動更新
for doc in all_docs:
    if 'weblogic' in doc.tags:
        weblogic_docs.append(doc)
```

**結果**: [KNOWLEDGE_MAP.md](../KNOWLEDGE_MAP.md) で Mermaid 図を自動生成

#### 3. リンク検証

```python
# scripts/validate-links.py
for doc in all_docs:
    for related_link in doc.frontmatter['related']:
        if not exists(related_link):
            print(f"Broken link: {related_link}")
```

**結果**: リンク切れを自動検出

#### 4. 学習パス推奨

```python
# 初心者向けドキュメントを抽出
beginner_docs = [d for d in all_docs if d.difficulty == 'beginner']
```

**結果**: 難易度に応じた学習ロードマップ生成

---

## YAML 構文の基礎

Frontmatter は **YAML (YAML Ain't Markup Language)** で記述します。

### 1. キー・バリューペア

```yaml
key: value
title: "ドキュメントタイトル"
difficulty: intermediate
```

### 2. 文字列

#### ダブルクォート（推奨）
```yaml
title: "VSCode Tasks 完全ガイド"
```

#### シングルクォート
```yaml
title: 'VSCode Tasks 完全ガイド'
```

#### クォートなし（スペースや特殊文字がない場合のみ）
```yaml
category: practices
difficulty: beginner
```

### 3. リスト（配列）

#### ハイフン形式（推奨：可読性が高い）
```yaml
tags:
  - vscode
  - tasks
  - automation
  - build-tools
```

#### インライン形式
```yaml
tags: [vscode, tasks, automation, build-tools]
```

### 4. ネストされた構造

```yaml
metadata:
  author: "m-miyawaki"
  version: "1.0"
  contributors:
    - "Alice"
    - "Bob"
```

### 5. 日付

```yaml
last_updated: 2025-12-12
created_at: 2024-11-01
```

### 6. ブール値

```yaml
published: true
draft: false
```

### 7. 数値

```yaml
version: 1
rating: 4.5
```

### 8. null 値

```yaml
deprecated: null
alternative: ~
```

### よくある YAML の間違い

#### ❌ NG: インデントが不揃い
```yaml
tags:
  - vscode
   - tasks  # ← スペース1つ多い
```

#### ✅ OK: 正しいインデント（2スペース）
```yaml
tags:
  - vscode
  - tasks
```

#### ❌ NG: タブ文字を使用
```yaml
tags:
→ - vscode  # ← タブ文字はエラー
```

#### ✅ OK: スペース2つ
```yaml
tags:
  - vscode
```

#### ❌ NG: クォートが不完全
```yaml
title: "VSCode Tasks ガイド
```

#### ✅ OK: クォートを閉じる
```yaml
title: "VSCode Tasks ガイド"
```

---

## 標準的なプロパティ

### 必須プロパティ

#### 1. `title` - ドキュメントタイトル

```yaml
title: "VSCode Tasks 完全ガイド"
```

**用途**:
- インデックスページでの表示
- 検索結果のタイトル表示
- ナレッジマップのノード名

**ベストプラクティス**:
- ダブルクォートで囲む
- 具体的で検索しやすい名前
- ファイル名と一致させる（推奨）

#### 2. `category` - カテゴリ

```yaml
category: practices  # または concepts, templates 等
```

**用途**:
- ドキュメントの大分類
- ディレクトリ構造との対応

**learning-notes での標準カテゴリ**:
- `practices` - 実践ガイド
- `concepts` - 概念説明
- `templates` - テンプレート
- `tools` - ツール使用法
- `architecture` - アーキテクチャ設計

#### 3. `tags` - タグ（複数可）

```yaml
tags:
  - vscode
  - tasks
  - automation
  - build-tools
```

**用途**:
- 横断検索
- 関連ドキュメント抽出
- ナレッジマップの関連性表示

**タグ付けのコツ**:
- 技術名（vscode, java, python）
- 機能名（tasks, debugging, testing）
- 用途（automation, deployment, security）
- レイヤー（frontend, backend, database）

### 推奨プロパティ

#### 4. `difficulty` - 難易度

```yaml
difficulty: intermediate  # beginner, intermediate, advanced
```

**用途**:
- 学習パス推奨
- 初心者向けドキュメント抽出

**レベル定義**:
- `beginner` - 前提知識なしで読める
- `intermediate` - 基礎知識が必要
- `advanced` - 実務経験者向け

#### 5. `related` - 関連ドキュメント

```yaml
related:
  - practices/vscode-workspace-overview.md
  - practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md
```

**用途**:
- ドキュメント間の関連性を明示
- リンク検証
- ナレッジマップの関係図生成

**パス指定のルール**:
- リポジトリルートからの相対パス
- 拡張子 `.md` を含める
- 実際にファイルが存在することを確認

#### 6. `last_updated` - 最終更新日

```yaml
last_updated: 2025-12-12
```

**用途**:
- 情報の鮮度確認
- 古いドキュメントの検出

**フォーマット**: `YYYY-MM-DD` (ISO 8601)

### オプションプロパティ

#### 7. `language` - 対象プログラミング言語

```yaml
language:
  - java
  - python
  - gradle
```

**用途**:
- 言語別フィルタリング
- 技術スタック別の分類

#### 8. `status` - ドキュメントステータス

```yaml
status: published  # draft, published, archived, deprecated
```

**用途**:
- 公開状態の管理
- WIP ドキュメントの除外

#### 9. `author` - 著者

```yaml
author: "m-miyawaki"
```

#### 10. `version` - バージョン

```yaml
version: "1.0"
```

#### 11. `description` - 概要説明

```yaml
description: "VSCode の Tasks 機能を使った自動化の完全ガイド"
```

**用途**:
- 検索結果のスニペット表示
- OGP メタタグ生成（ブログ化する場合）

---

## learning-notes での活用例

### 例1: 実践ガイド（practices）

**ファイル**: `practices/vscode-tasks-complete-guide.md`

```yaml
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
  - practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md
language:
  - javascript
  - java
  - python
  - cpp
last_updated: 2025-12-12
---
```

**特徴**:
- 複数言語対応を `language` で明示
- 関連する実践ガイドをリンク
- 中級者向け（`intermediate`）

### 例2: 概念説明（concepts）

**ファイル**: `concepts/dependency-injection/README.md`

```yaml
---
title: "依存性注入（Dependency Injection）の基礎"
category: concepts
tags:
  - design-pattern
  - dependency-injection
  - solid-principles
  - architecture
difficulty: beginner
related:
  - concepts/solid-principles/README.md
  - practices/java/spring/di-ioc.md
language:
  - java
  - typescript
last_updated: 2025-12-12
---
```

**特徴**:
- 言語非依存の概念だが、実装例の言語を明示
- SOLID 原則との関連を明示
- 初心者向け（`beginner`）

### 例3: WebLogic デプロイガイド（advanced）

**ファイル**: `practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md`

```yaml
---
title: "VSCode マルチWARプロジェクト統合デプロイ環境"
category: practices
tags:
  - weblogic
  - gradle
  - wlst
  - deployment
  - multi-module
  - vscode
  - tasks
  - java
difficulty: advanced
related:
  - practices/vscode-tasks-complete-guide.md
  - practices/weblogic/vscode-gradle-weblogic-setup.md
  - practices/weblogic/vscode-complex-multimodule-setup.md
language:
  - java
  - python
  - gradle
last_updated: 2025-12-12
---
```

**特徴**:
- 複数技術スタックを統合（WebLogic + Gradle + VSCode + WLST）
- Python（WLST スクリプト）と Gradle を言語として明示
- 上級者向け（`advanced`）
- 3つの関連ドキュメントを参照

### 例4: テンプレート

**ファイル**: `templates/concept-note-template.md`

```yaml
---
title: "概念ノートテンプレート"
category: templates
tags:
  - template
  - documentation
difficulty: beginner
last_updated: 2025-12-12
---
```

**特徴**:
- `related` は不要（テンプレートのため）
- `language` は不要（汎用テンプレート）

---

## タグ付けのベストプラクティス

### 1. タグの粒度

#### ❌ NG: 細かすぎるタグ
```yaml
tags:
  - vscode
  - vscode-tasks
  - vscode-tasks-json
  - vscode-tasks-automation
  - vscode-tasks-build
```

**問題**: タグが爆発的に増加し、検索が困難

#### ✅ OK: 適切な粒度
```yaml
tags:
  - vscode
  - tasks
  - automation
  - build-tools
```

**利点**: 汎用的で横断検索に有効

### 2. タグの階層構造（推奨しない）

#### ❌ NG: タグ内で階層表現
```yaml
tags:
  - technology/vscode
  - category/practices
  - difficulty/intermediate
```

**問題**: Frontmatter プロパティと重複

#### ✅ OK: フラットな構造 + 専用プロパティ
```yaml
category: practices
difficulty: intermediate
tags:
  - vscode
  - tasks
```

### 3. タグの命名規則

#### 統一すべきポイント

| 対象 | 推奨形式 | 例 |
|------|---------|-----|
| 技術名 | 小文字、ハイフン区切り | `vscode`, `weblogic`, `spring-boot` |
| 機能名 | 小文字、ハイフン区切り | `dependency-injection`, `multi-module` |
| 用途 | 小文字、名詞形 | `automation`, `deployment`, `testing` |
| レイヤー | 小文字 | `frontend`, `backend`, `database` |

#### ❌ NG: 表記ゆれ
```yaml
# ファイル A
tags:
  - VSCode
  - Dependency-Injection

# ファイル B
tags:
  - vscode
  - dependency_injection
```

#### ✅ OK: 統一された表記
```yaml
# 全ファイル共通
tags:
  - vscode
  - dependency-injection
```

### 4. タグ数の目安

#### ❌ NG: タグが少なすぎる
```yaml
tags:
  - vscode
```

**問題**: 検索の粒度が粗い

#### ❌ NG: タグが多すぎる
```yaml
tags:
  - vscode
  - tasks
  - automation
  - build
  - deployment
  - gradle
  - java
  - python
  - weblogic
  - wlst
  - debugging
  - testing
```

**問題**: ノイズが多く、タグの意味が薄れる

#### ✅ OK: 適切なタグ数（3〜7個）
```yaml
tags:
  - vscode
  - tasks
  - automation
  - build-tools
  - deployment
```

### 5. タグの再利用性

#### 推奨タグリスト（learning-notes 標準）

**技術カテゴリ**:
- `vscode`, `eclipse`, `intellij`
- `java`, `javascript`, `typescript`, `python`, `cpp`
- `spring`, `spring-boot`, `mybatis`, `gradle`, `maven`
- `weblogic`, `tomcat`, `docker`
- `oracle`, `mysql`, `postgresql`

**機能カテゴリ**:
- `debugging`, `testing`, `profiling`
- `deployment`, `automation`, `ci-cd`
- `dependency-injection`, `orm`, `aop`, `transaction`
- `security`, `authentication`, `authorization`

**用途カテゴリ**:
- `build-tools`, `tasks`, `workspace`
- `performance`, `optimization`
- `architecture`, `design-pattern`, `solid-principles`

**レイヤーカテゴリ**:
- `frontend`, `backend`, `database`, `infrastructure`

---

## ツール統合

### 1. VSCode

#### VSCode Frontmatter Extension

**拡張機能**: [Front Matter CMS](https://marketplace.visualstudio.com/items?itemName=eliostruyf.vscode-front-matter)

**機能**:
- Frontmatter の GUI 編集
- タグのオートコンプリート
- 日付の自動更新
- カスタムプロパティの定義

**設定例** (`.vscode/settings.json`):
```json
{
  "frontMatter.taxonomy.tags": [
    "vscode",
    "java",
    "weblogic",
    "automation"
  ],
  "frontMatter.taxonomy.categories": [
    "practices",
    "concepts",
    "templates"
  ],
  "frontMatter.content.autoUpdateDate": true
}
```

#### YAML 拡張機能

**拡張機能**: [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

**機能**:
- YAML 構文ハイライト
- エラー検出
- オートフォーマット

### 2. Obsidian

**Frontmatter 対応**: ネイティブサポート

**機能**:
- タグによる検索・フィルタ
- Dataview プラグインで動的クエリ
- グラフビューで関連性可視化

**Dataview クエリ例**:
```dataview
TABLE difficulty, last_updated
FROM "practices"
WHERE contains(tags, "vscode")
SORT last_updated DESC
```

### 3. 静的サイトジェネレータ

#### Jekyll

```yaml
---
layout: post
title: "VSCode Tasks 完全ガイド"
categories: practices
tags: [vscode, tasks, automation]
---
```

#### Hugo

```yaml
---
title: "VSCode Tasks 完全ガイド"
date: 2025-12-12
draft: false
tags: ["vscode", "tasks", "automation"]
---
```

#### Docusaurus

```yaml
---
id: vscode-tasks-guide
title: VSCode Tasks 完全ガイド
sidebar_label: Tasks Guide
tags: [vscode, tasks, automation]
---
```

### 4. Markdown Linter

**ツール**: [markdownlint](https://github.com/DavidAnson/markdownlint)

**Frontmatter チェック**:
```yaml
# .markdownlint.json
{
  "MD041": false  # 最初の行が見出しでなくてもOK（Frontmatter対応）
}
```

---

## 自動化とスクリプト連携

### 1. タグインデックス自動生成

**スクリプト**: `scripts/generate-tag-index.py`

```python
#!/usr/bin/env python3
import re
from pathlib import Path

def extract_frontmatter(file_path):
    """Frontmatter を抽出して辞書で返す"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- で囲まれた部分を抽出
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None

    yaml_content = match.group(1)

    # 簡易 YAML パース（タグのみ）
    tags = []
    for line in yaml_content.split('\n'):
        if line.strip().startswith('- '):
            tags.append(line.strip()[2:])

    return {'tags': tags, 'file': file_path}

# 全 .md ファイルをスキャン
docs = []
for md_file in Path('.').rglob('*.md'):
    fm = extract_frontmatter(md_file)
    if fm:
        docs.append(fm)

# タグ別に集計
tag_index = {}
for doc in docs:
    for tag in doc['tags']:
        if tag not in tag_index:
            tag_index[tag] = []
        tag_index[tag].append(doc['file'])

# TAG_INDEX.md を生成
with open('TAG_INDEX.md', 'w') as f:
    f.write('# タグインデックス\n\n')
    for tag in sorted(tag_index.keys()):
        f.write(f'## {tag}\n\n')
        for file in tag_index[tag]:
            f.write(f'- [{file}]({file})\n')
        f.write('\n')
```

**実行**:
```bash
python3 scripts/generate-tag-index.py
```

**出力**: `TAG_INDEX.md`

### 2. リンク検証

**スクリプト**: `scripts/validate-links.py`

```python
#!/usr/bin/env python3
from pathlib import Path

def validate_links():
    notes_dir = Path('/home/m-miyawaki/dev/learning-notes')

    for md_file in notes_dir.rglob('*.md'):
        fm = extract_frontmatter(md_file)
        if not fm or 'related' not in fm:
            continue

        for link in fm['related']:
            link_path = (notes_dir / link).resolve()
            if not link_path.exists():
                print(f'❌ Broken link in {md_file}:')
                print(f'   {link} → not found')

validate_links()
```

**実行**:
```bash
python3 scripts/validate-links.py
```

### 3. Frontmatter 一括追加

**スクリプト**: `scripts/add-frontmatter.sh`

```bash
#!/bin/bash

TARGET_DIR="${1:-.}"

find "${TARGET_DIR}" -type f -name "*.md" | while read -r file; do
    # 既に Frontmatter が存在するかチェック
    if head -n 1 "$file" | grep -q "^---$"; then
        echo "⏭  スキップ: $file"
        continue
    fi

    # ファイル名から title を生成
    filename=$(basename "$file" .md)
    title=$(echo "$filename" | sed 's/-/ /g' | sed 's/\b\(.)/\u\1/g')

    # Frontmatter を作成
    frontmatter=$(cat <<EOF
---
title: "$title"
category: practices
tags:
  -
difficulty: intermediate
last_updated: $(date +%Y-%m-%d)
---

EOF
)

    # 一時ファイルに書き込み
    temp_file=$(mktemp)
    echo "$frontmatter" > "$temp_file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    echo "✅ 追加完了: $file"
done
```

**実行**:
```bash
bash scripts/add-frontmatter.sh practices/
```

### 4. 古いドキュメント検出

**スクリプト例**:

```python
#!/usr/bin/env python3
from datetime import datetime, timedelta
from pathlib import Path

def find_outdated_docs(days=180):
    """指定日数以上更新されていないドキュメントを検出"""
    threshold = datetime.now() - timedelta(days=days)

    for md_file in Path('.').rglob('*.md'):
        fm = extract_frontmatter(md_file)
        if not fm or 'last_updated' not in fm:
            continue

        last_updated = datetime.strptime(fm['last_updated'], '%Y-%m-%d')
        if last_updated < threshold:
            days_old = (datetime.now() - last_updated).days
            print(f'⚠️  {md_file}: {days_old} 日前')

find_outdated_docs(180)  # 6ヶ月以上更新なし
```

---

## よくある間違いと落とし穴

### 1. デリミタの間違い

#### ❌ NG: ハイフンの数が違う
```yaml
--
title: "Test"
--
```

#### ✅ OK: 必ず3つ
```yaml
---
title: "Test"
---
```

### 2. インデントの間違い

#### ❌ NG: タブ文字を使用
```yaml
tags:
→ - vscode
```

#### ✅ OK: スペース2つ
```yaml
tags:
  - vscode
```

### 3. リストの間違い

#### ❌ NG: ハイフンの後にスペースなし
```yaml
tags:
  -vscode
  -tasks
```

#### ✅ OK: ハイフンの後に必ずスペース
```yaml
tags:
  - vscode
  - tasks
```

### 4. 特殊文字のエスケープ

#### ❌ NG: クォートなしでコロンを使用
```yaml
title: VSCode: 完全ガイド
```

**エラー**: コロンが YAML のキー・バリュー区切りと解釈される

#### ✅ OK: クォートで囲む
```yaml
title: "VSCode: 完全ガイド"
```

### 5. 日付フォーマットの不統一

#### ❌ NG: 様々な形式が混在
```yaml
last_updated: 2025/12/12     # ファイル A
last_updated: 12-12-2025     # ファイル B
last_updated: Dec 12, 2025   # ファイル C
```

#### ✅ OK: ISO 8601 形式で統一
```yaml
last_updated: 2025-12-12
```

### 6. 本文との空行忘れ

#### ❌ NG: 空行なし（一部のパーサーでエラー）
```yaml
---
title: "Test"
---
# 本文の見出し
```

#### ✅ OK: 空行を入れる
```yaml
---
title: "Test"
---

# 本文の見出し
```

### 7. 存在しないファイルへのリンク

#### ❌ NG: リンク先が存在しない
```yaml
related:
  - practices/non-existent-file.md
```

**対策**: `validate-links.py` で定期的にチェック

### 8. タグの表記ゆれ

#### ❌ NG: 同じ概念で異なるタグ
```yaml
# ファイル A
tags:
  - dependency-injection

# ファイル B
tags:
  - DI
  - dependency_injection
```

**対策**: タグ一覧を README.md で明示し、統一ルールを設ける

---

## 実践ワークフロー

### 新規ドキュメント作成時

```bash
# 1. テンプレートからコピー
cp templates/concept-note-template.md concepts/new-concept/README.md

# 2. Frontmatter を編集
vim concepts/new-concept/README.md
```

**Frontmatter 記入例**:
```yaml
---
title: "新しい概念の説明"
category: concepts
tags:
  - design-pattern
  - architecture
difficulty: intermediate
related:
  - concepts/related-concept/README.md
last_updated: 2025-12-12
---
```

```bash
# 3. 本文を記述
# ...

# 4. リンク検証
python3 scripts/validate-links.py

# 5. タグインデックス更新
python3 scripts/generate-tag-index.py

# 6. コミット
git add concepts/new-concept/README.md TAG_INDEX.md
git commit -m "feat: 新しい概念のドキュメント追加"
```

### 既存ドキュメント更新時

```bash
# 1. ドキュメント編集
vim practices/vscode-tasks-complete-guide.md

# 2. last_updated を更新
# Frontmatter 内の last_updated: 2025-12-12 を今日の日付に変更

# 3. リンク検証
python3 scripts/validate-links.py

# 4. コミット
git add practices/vscode-tasks-complete-guide.md
git commit -m "docs: VSCode Tasks ガイドに新しいセクション追加"
```

### 定期メンテナンス

```bash
# 月1回実行

# 1. 古いドキュメント検出
python3 scripts/find-outdated-docs.py

# 2. リンク切れチェック
python3 scripts/validate-links.py

# 3. タグインデックス再生成
python3 scripts/generate-tag-index.py

# 4. ナレッジマップ確認
# KNOWLEDGE_MAP.md を開いて全体構造を俯瞰
```

---

## 関連ドキュメント

- [KNOWLEDGE_MAP.md](../KNOWLEDGE_MAP.md) - Frontmatter を活用したナレッジマップ
- [TAG_INDEX.md](../TAG_INDEX.md) - 自動生成されたタグインデックス
- [README.md](../README.md) - ナレッジマップとスクリプトの使い方
- [practices/vscode-tasks-complete-guide.md](vscode-tasks-complete-guide.md) - Frontmatter 活用例
- [practices/weblogic/vscode-gradle-wlst-multi-war-deployment.md](weblogic/vscode-gradle-wlst-multi-war-deployment.md) - 複雑な Frontmatter の例

---

## まとめ

### Frontmatter の本質

1. **構造化**: 非構造化テキストに機械可読なメタデータを付与
2. **自動化**: プログラムで処理可能 → インデックス生成・検証・可視化
3. **標準化**: 広く採用されている形式（Jekyll, Hugo, Obsidian, VSCode）
4. **拡張性**: 必要に応じてカスタムプロパティを追加可能

### learning-notes での活用

- **53ファイル** を効率的に管理
- **タグベース検索** で関連ドキュメント発見
- **難易度別** で学習パス推奨
- **自動スクリプト** でメンテナンス効率化

### 次のステップ

1. 既存ドキュメントに Frontmatter 追加
   ```bash
   bash scripts/add-frontmatter.sh practices/
   ```

2. タグインデックス生成
   ```bash
   python3 scripts/generate-tag-index.py
   ```

3. ナレッジマップ確認
   - [KNOWLEDGE_MAP.md](../KNOWLEDGE_MAP.md) を開く

4. 定期的なメンテナンス
   - 月1回リンク検証
   - 古いドキュメントの更新

---

**作成日**: 2025-12-12
**最終更新**: 2025-12-12
**対象読者**: learning-notes 利用者全員（初心者〜上級者）
