#!/usr/bin/env python3
"""
Frontmatter から Mermaid グラフを自動生成

Usage:
    python3 scripts/generate-mermaid-graph.py

Output:
    GRAPH_VIEW.md - Mermaid 形式のナレッジグラフ
"""

import re
from pathlib import Path
from collections import defaultdict


def extract_frontmatter(file_path):
    """
    Markdown ファイルから Frontmatter を抽出

    Returns:
        dict: {title, tags, category, difficulty, related, language, ...}
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # Frontmatter を抽出 (--- で囲まれた部分)
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None

    yaml_content = match.group(1)

    # 簡易 YAML パース
    frontmatter = {
        'file': str(file_path),
        'title': '',
        'tags': [],
        'category': 'uncategorized',
        'difficulty': '',
        'related': [],
        'language': []
    }

    current_key = None
    for line in yaml_content.split('\n'):
        line = line.rstrip()

        # キー: 値 形式
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key in ['title', 'category', 'difficulty']:
                frontmatter[key] = value
                current_key = None
            elif key in ['tags', 'related', 'language']:
                current_key = key
                if value:  # インライン形式の場合
                    frontmatter[key] = [v.strip() for v in value.strip('[]').split(',')]

        # リスト項目
        elif line.strip().startswith('-') and current_key:
            item = line.strip()[1:].strip().strip('"').strip("'")
            if item:
                frontmatter[current_key].append(item)

    return frontmatter


def sanitize_node_id(path):
    """
    ファイルパスを Mermaid のノード ID に変換

    Example:
        practices/vscode-tasks-complete-guide.md → practices_vscode_tasks
    """
    node_id = path.replace('.md', '').replace('/', '_').replace('-', '_')
    # 長すぎる場合は短縮
    parts = node_id.split('_')
    if len(parts) > 4:
        # 最後の2-3要素のみ使用
        node_id = '_'.join(parts[-3:])
    return node_id


def generate_mermaid_graph():
    """
    全ドキュメントの Frontmatter から Mermaid グラフを生成
    """
    notes_dir = Path('/home/m-miyawaki/dev/learning-notes')

    # 全ドキュメントをスキャン
    docs = []
    for md_file in sorted(notes_dir.rglob('*.md')):
        # 除外パス
        if any(part in md_file.parts for part in ['.git', 'node_modules', 'templates']):
            continue

        # README, KNOWLEDGE_MAP, TAG_INDEX, GRAPH_VIEW をスキップ
        if md_file.name in ['README.md', 'KNOWLEDGE_MAP.md', 'TAG_INDEX.md', 'GRAPH_VIEW.md']:
            continue

        fm = extract_frontmatter(md_file)
        if fm and fm.get('title'):
            fm['relative_path'] = str(md_file.relative_to(notes_dir))
            docs.append(fm)

    print(f"✅ {len(docs)} ドキュメントを検出")

    # カテゴリ別・タグ別に集計
    by_category = defaultdict(list)
    by_tag = defaultdict(list)

    for doc in docs:
        by_category[doc['category']].append(doc)
        for tag in doc['tags']:
            by_tag[tag].append(doc)

    # Mermaid グラフ生成
    mermaid_lines = []

    # ヘッダー
    mermaid_lines.append("```mermaid")
    mermaid_lines.append("graph TD")
    mermaid_lines.append("")

    # スタイル定義
    mermaid_lines.append("    %% スタイル定義")
    mermaid_lines.append("    classDef practices fill:#3b82f6,stroke:#1e40af,color:#fff")
    mermaid_lines.append("    classDef concepts fill:#10b981,stroke:#047857,color:#fff")
    mermaid_lines.append("    classDef templates fill:#f59e0b,stroke:#d97706,color:#fff")
    mermaid_lines.append("    classDef beginner fill:#22c55e,stroke:#16a34a,color:#fff")
    mermaid_lines.append("    classDef intermediate fill:#eab308,stroke:#ca8a04,color:#000")
    mermaid_lines.append("    classDef advanced fill:#ef4444,stroke:#dc2626,color:#fff")
    mermaid_lines.append("")

    # ノード定義
    mermaid_lines.append("    %% ノード定義")
    for doc in docs:
        node_id = sanitize_node_id(doc['relative_path'])
        title = doc['title'][:30]  # タイトルを短縮

        # 難易度に応じたアイコン
        icon = ""
        if doc['difficulty'] == 'beginner':
            icon = "🟢 "
        elif doc['difficulty'] == 'intermediate':
            icon = "🟡 "
        elif doc['difficulty'] == 'advanced':
            icon = "🔴 "

        mermaid_lines.append(f'    {node_id}["{icon}{title}"]')

        # カテゴリに応じたスタイル適用
        if doc['category'] in ['practices', 'concepts', 'templates']:
            mermaid_lines.append(f"    class {node_id} {doc['category']}")

    mermaid_lines.append("")

    # リンク定義（related フィールドから）
    mermaid_lines.append("    %% 関連ドキュメントのリンク")
    for doc in docs:
        node_id = sanitize_node_id(doc['relative_path'])
        for related_path in doc['related']:
            # related_path を絶対パスに変換
            related_full_path = notes_dir / related_path
            if related_full_path.exists():
                related_node_id = sanitize_node_id(related_path)
                mermaid_lines.append(f"    {node_id} -.->|関連| {related_node_id}")

    mermaid_lines.append("")
    mermaid_lines.append("```")

    # GRAPH_VIEW.md に書き込み
    output_path = notes_dir / 'GRAPH_VIEW.md'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# ナレッジグラフ（Mermaid 可視化）\n\n")
        f.write("> Frontmatter の `related` フィールドに基づくドキュメント間の関連性を可視化\n\n")
        f.write("## 凡例\n\n")
        f.write("- 🟢 **Beginner** - 初心者向け\n")
        f.write("- 🟡 **Intermediate** - 中級者向け\n")
        f.write("- 🔴 **Advanced** - 上級者向け\n\n")
        f.write("## カテゴリ別の色分け\n\n")
        f.write("- 🔵 **Practices** - 実践ガイド\n")
        f.write("- 🟢 **Concepts** - 概念説明\n")
        f.write("- 🟠 **Templates** - テンプレート\n\n")
        f.write("---\n\n")
        f.write("## 全体グラフ\n\n")
        f.write('\n'.join(mermaid_lines))
        f.write("\n\n---\n\n")

        # カテゴリ別グラフ
        f.write("## カテゴリ別グラフ\n\n")

        for category, category_docs in sorted(by_category.items()):
            f.write(f"### {category.capitalize()}\n\n")
            f.write("```mermaid\n")
            f.write("graph LR\n")

            for doc in category_docs:
                node_id = sanitize_node_id(doc['relative_path'])
                title = doc['title'][:20]
                f.write(f'    {node_id}["{title}"]\n')

            f.write("```\n\n")

        # タグ別統計
        f.write("---\n\n")
        f.write("## タグ別ドキュメント数\n\n")
        f.write("| タグ | ドキュメント数 |\n")
        f.write("|------|---------------|\n")

        for tag, tag_docs in sorted(by_tag.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"| `{tag}` | {len(tag_docs)} |\n")

        f.write("\n---\n\n")
        f.write("**自動生成日時**: このファイルは `scripts/generate-mermaid-graph.py` で自動生成されます。\n\n")
        f.write("**更新方法**:\n")
        f.write("```bash\n")
        f.write("python3 scripts/generate-mermaid-graph.py\n")
        f.write("```\n")

    print(f"✅ GRAPH_VIEW.md を生成しました: {output_path}")
    print(f"   - {len(docs)} ドキュメント")
    print(f"   - {len(by_category)} カテゴリ")
    print(f"   - {len(by_tag)} タグ")


if __name__ == '__main__':
    generate_mermaid_graph()
