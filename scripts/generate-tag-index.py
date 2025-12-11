#!/usr/bin/env python3
"""
タグインデックス自動生成スクリプト

Markdown ファイルの Frontmatter からタグを抽出し、
TAG_INDEX.md を自動生成します。

Usage:
    python3 scripts/generate-tag-index.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def extract_frontmatter(file_path):
    """
    Markdown ファイルから Frontmatter を抽出

    Returns:
        dict: Frontmatter の内容（title, tags, category, etc.）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Frontmatter の検出（--- で囲まれた部分）
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()

                # 簡易的な YAML パーサー（タグのみ抽出）
                metadata = {}

                # title
                title_match = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', frontmatter_text, re.MULTILINE)
                if title_match:
                    metadata['title'] = title_match.group(1).strip('"\'')

                # tags（リスト形式）
                tags = []
                in_tags_section = False
                for line in frontmatter_text.split('\n'):
                    line = line.strip()

                    if line.startswith('tags:'):
                        in_tags_section = True
                        # インライン形式: tags: [tag1, tag2]
                        inline_match = re.search(r'tags:\s*\[(.+)\]', line)
                        if inline_match:
                            tags_str = inline_match.group(1)
                            tags = [t.strip().strip('"\'') for t in tags_str.split(',')]
                            in_tags_section = False
                    elif in_tags_section:
                        if line.startswith('-'):
                            tag = line[1:].strip().strip('"\'')
                            if tag:
                                tags.append(tag)
                        elif line and not line.startswith(' ') and ':' in line:
                            # 次のセクションに移動
                            in_tags_section = False

                metadata['tags'] = tags

                # category
                category_match = re.search(r'category:\s*(.+)', frontmatter_text)
                if category_match:
                    metadata['category'] = category_match.group(1).strip()

                # difficulty
                difficulty_match = re.search(r'difficulty:\s*(.+)', frontmatter_text)
                if difficulty_match:
                    metadata['difficulty'] = difficulty_match.group(1).strip()

                return metadata

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return {}


def generate_tag_index():
    """
    全 Markdown ファイルをスキャンしてタグインデックスを生成
    """
    notes_dir = Path('/home/m-miyawaki/dev/learning-notes')

    # タグ → ファイルのマッピング
    tags_index = defaultdict(list)

    # カテゴリ → ファイルのマッピング
    category_index = defaultdict(list)

    # 難易度 → ファイルのマッピング
    difficulty_index = defaultdict(list)

    # 全ファイル情報
    all_files = []

    # Markdown ファイルをスキャン
    for md_file in sorted(notes_dir.rglob('*.md')):
        # .git, node_modules, sample を除外
        if any(part in md_file.parts for part in ['.git', 'node_modules', 'sample']):
            continue

        # README, KNOWLEDGE_MAP, TAG_INDEX を除外
        if md_file.name in ['README.md', 'KNOWLEDGE_MAP.md', 'TAG_INDEX.md']:
            continue

        frontmatter = extract_frontmatter(md_file)

        if frontmatter:
            rel_path = md_file.relative_to(notes_dir)
            title = frontmatter.get('title', md_file.stem)

            file_info = {
                'path': str(rel_path),
                'title': title,
                'tags': frontmatter.get('tags', []),
                'category': frontmatter.get('category', 'uncategorized'),
                'difficulty': frontmatter.get('difficulty', 'intermediate')
            }

            all_files.append(file_info)

            # タグインデックスに追加
            for tag in file_info['tags']:
                tags_index[tag].append(file_info)

            # カテゴリインデックスに追加
            category_index[file_info['category']].append(file_info)

            # 難易度インデックスに追加
            difficulty_index[file_info['difficulty']].append(file_info)

    # TAG_INDEX.md を生成
    output_file = notes_dir / 'TAG_INDEX.md'

    with open(output_file, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write('# タグインデックス\n\n')
        f.write('> 自動生成されたタグベースのドキュメントインデックス\n\n')
        f.write(f'最終更新: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write('---\n\n')

        # 統計情報
        f.write('## 📊 統計情報\n\n')
        f.write(f'- **総ドキュメント数**: {len(all_files)}\n')
        f.write(f'- **総タグ数**: {len(tags_index)}\n')
        f.write(f'- **カテゴリ数**: {len(category_index)}\n\n')
        f.write('---\n\n')

        # タグ一覧（アルファベット順）
        f.write('## 🏷️ タグ別インデックス\n\n')

        for tag in sorted(tags_index.keys()):
            files = tags_index[tag]
            f.write(f'### `{tag}` ({len(files)} documents)\n\n')

            for file_info in sorted(files, key=lambda x: x['title']):
                difficulty_emoji = {
                    'beginner': '🟢',
                    'intermediate': '🟡',
                    'advanced': '🔴'
                }.get(file_info['difficulty'], '⚪')

                f.write(f'- {difficulty_emoji} [{file_info["title"]}]({file_info["path"]})')

                # 他のタグも表示
                other_tags = [t for t in file_info['tags'] if t != tag]
                if other_tags:
                    f.write(f' `{" ".join(["#" + t for t in other_tags[:3]])}`')

                f.write('\n')

            f.write('\n')

        f.write('---\n\n')

        # カテゴリ別インデックス
        f.write('## 📁 カテゴリ別インデックス\n\n')

        for category in sorted(category_index.keys()):
            files = category_index[category]
            f.write(f'### {category.title()} ({len(files)} documents)\n\n')

            for file_info in sorted(files, key=lambda x: x['title']):
                difficulty_emoji = {
                    'beginner': '🟢',
                    'intermediate': '🟡',
                    'advanced': '🔴'
                }.get(file_info['difficulty'], '⚪')

                f.write(f'- {difficulty_emoji} [{file_info["title"]}]({file_info["path"]})')

                if file_info['tags']:
                    f.write(f' `{" ".join(["#" + t for t in file_info["tags"][:3]])}`')

                f.write('\n')

            f.write('\n')

        f.write('---\n\n')

        # 難易度別インデックス
        f.write('## 📈 難易度別インデックス\n\n')

        difficulty_order = ['beginner', 'intermediate', 'advanced']
        difficulty_names = {
            'beginner': '初級 🟢',
            'intermediate': '中級 🟡',
            'advanced': '上級 🔴'
        }

        for difficulty in difficulty_order:
            if difficulty in difficulty_index:
                files = difficulty_index[difficulty]
                f.write(f'### {difficulty_names[difficulty]} ({len(files)} documents)\n\n')

                for file_info in sorted(files, key=lambda x: x['title']):
                    f.write(f'- [{file_info["title"]}]({file_info["path"]})')

                    if file_info['tags']:
                        f.write(f' `{" ".join(["#" + t for t in file_info["tags"][:3]])}`')

                    f.write(f' *({file_info["category"]})*\n')

                f.write('\n')

        f.write('---\n\n')

        # フッター
        f.write('## 🔄 更新方法\n\n')
        f.write('このファイルは自動生成されています。手動で編集しないでください。\n\n')
        f.write('```bash\n')
        f.write('# インデックスの再生成\n')
        f.write('python3 scripts/generate-tag-index.py\n')
        f.write('```\n\n')
        f.write('---\n\n')
        f.write('> Generated by `scripts/generate-tag-index.py`\n')

    print(f'✅ TAG_INDEX.md を生成しました')
    print(f'   - {len(all_files)} ドキュメント')
    print(f'   - {len(tags_index)} タグ')
    print(f'   - {len(category_index)} カテゴリ')


if __name__ == '__main__':
    generate_tag_index()
