#!/usr/bin/env python3
"""
リンク切れチェックスクリプト

Markdown ファイル内の内部リンクをチェックして、
リンク切れを検出します。

Usage:
    python3 scripts/validate-links.py
"""

import os
import re
from pathlib import Path
from urllib.parse import unquote


def extract_markdown_links(file_path):
    """
    Markdown ファイルからリンクを抽出

    Returns:
        list: リンクのリスト [(link_text, link_url, line_number), ...]
    """
    links = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Markdown リンク形式: [text](url)
                for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
                    link_text = match.group(1)
                    link_url = match.group(2)

                    # アンカーリンクを除去
                    link_url = link_url.split('#')[0]

                    # 空のリンクや外部リンクを除外
                    if link_url and not link_url.startswith(('http://', 'https://', 'mailto:')):
                        links.append((link_text, link_url, line_num))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return links


def validate_links():
    """
    全 Markdown ファイルのリンクを検証
    """
    notes_dir = Path('/home/m-miyawaki/dev/learning-notes')
    broken_links = []

    print('🔍 リンク検証を開始...\n')

    for md_file in sorted(notes_dir.rglob('*.md')):
        # .git, node_modules を除外
        if any(part in md_file.parts for part in ['.git', 'node_modules']):
            continue

        links = extract_markdown_links(md_file)

        for link_text, link_url, line_num in links:
            # 相対パス解決
            link_path = (md_file.parent / link_url).resolve()

            # URLデコード
            link_path_str = unquote(str(link_path))
            link_path = Path(link_path_str)

            # ファイルの存在確認
            if not link_path.exists():
                rel_file = md_file.relative_to(notes_dir)
                broken_links.append({
                    'file': str(rel_file),
                    'line': line_num,
                    'link_text': link_text,
                    'link_url': link_url,
                    'resolved_path': str(link_path.relative_to(notes_dir)) if notes_dir in link_path.parents else str(link_path)
                })

    # 結果表示
    if broken_links:
        print(f'❌ {len(broken_links)} 個のリンク切れを検出しました:\n')

        current_file = None
        for link in broken_links:
            if link['file'] != current_file:
                current_file = link['file']
                print(f'\n📄 {current_file}')

            print(f'   行 {link["line"]}: [{link["link_text"]}]({link["link_url"]})')
            print(f'      → {link["resolved_path"]} が見つかりません')

        return False
    else:
        print('✅ リンク切れは検出されませんでした')
        return True


if __name__ == '__main__':
    success = validate_links()
    exit(0 if success else 1)
