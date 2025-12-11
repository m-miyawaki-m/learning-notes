#!/bin/bash
#
# Frontmatter 一括追加スクリプト
#
# 既存の Markdown ファイルに Frontmatter を追加します。
# 既に Frontmatter がある場合はスキップします。
#
# Usage:
#   bash scripts/add-frontmatter.sh [directory]
#
# Example:
#   bash scripts/add-frontmatter.sh practices/
#

set -e

# デフォルトディレクトリ
TARGET_DIR="${1:-.}"

# カラー出力
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📝 Frontmatter 追加スクリプト${NC}"
echo -e "対象ディレクトリ: ${TARGET_DIR}\n"

# カウンター
PROCESSED=0
SKIPPED=0
ADDED=0

# Markdown ファイルを検索
find "${TARGET_DIR}" -type f -name "*.md" ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/sample/*" | while read -r file; do
    # README, KNOWLEDGE_MAP, TAG_INDEX をスキップ
    if [[ "$(basename "$file")" =~ ^(README|KNOWLEDGE_MAP|TAG_INDEX)\.md$ ]]; then
        continue
    fi

    PROCESSED=$((PROCESSED + 1))

    # 既に Frontmatter が存在するかチェック
    if head -n 1 "$file" | grep -q "^---$"; then
        echo -e "${YELLOW}⏭  スキップ:${NC} $file (既に Frontmatter あり)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # ファイル名から title を生成
    filename=$(basename "$file" .md)
    title=$(echo "$filename" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

    # カテゴリ推測
    category="uncategorized"
    if [[ "$file" =~ /practices/ ]]; then
        category="practices"
    elif [[ "$file" =~ /concepts/ ]]; then
        category="concepts"
    elif [[ "$file" =~ /templates/ ]]; then
        category="templates"
    fi

    # タグ推測（ディレクトリ名から）
    tags=""
    if [[ "$file" =~ /weblogic/ ]]; then
        tags="  - weblogic"
    elif [[ "$file" =~ /vscode/ ]] || [[ "$filename" =~ vscode ]]; then
        tags="  - vscode"
    elif [[ "$file" =~ /java/ ]]; then
        tags="  - java"
    elif [[ "$file" =~ /javascript/ ]]; then
        tags="  - javascript"
    elif [[ "$file" =~ /python/ ]]; then
        tags="  - python"
    fi

    # 現在の日付
    today=$(date +%Y-%m-%d)

    # Frontmatter を作成
    frontmatter=$(cat <<EOF
---
title: "$title"
category: $category
tags:
$tags
difficulty: intermediate
last_updated: $today
---

EOF
)

    # 一時ファイルに書き込み
    temp_file=$(mktemp)
    echo "$frontmatter" > "$temp_file"
    cat "$file" >> "$temp_file"

    # 元のファイルを置き換え
    mv "$temp_file" "$file"

    echo -e "${GREEN}✅ 追加完了:${NC} $file"
    ADDED=$((ADDED + 1))
done

# 結果サマリー
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ 完了${NC}"
echo -e "  処理: ${PROCESSED} ファイル"
echo -e "  追加: ${ADDED} ファイル"
echo -e "  スキップ: ${SKIPPED} ファイル"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}📌 次のステップ:${NC}"
echo -e "  1. 各ファイルの Frontmatter を手動で調整"
echo -e "  2. タグインデックスを生成: ${BLUE}python3 scripts/generate-tag-index.py${NC}"
echo -e "  3. リンクを検証: ${BLUE}python3 scripts/validate-links.py${NC}"
