# Python 実践ガイド

> 対象: Python 3.8+
> 環境: venv, pip, VS Code / PyCharm

このドキュメントは、Pythonの実践的な開発手法、ベストプラクティス、よくあるパターンを記載しています。

---

## 目次

1. [環境構築](#環境構築)
2. [プロジェクト構成](#プロジェクト構成)
3. [よくある実装パターン](#よくある実装パターン)
4. [ベストプラクティス](#ベストプラクティス)
5. [デバッグとテスト](#デバッグとテスト)
6. [パフォーマンス最適化](#パフォーマンス最適化)

---

## 環境構築

### Python のインストール確認

```bash
python --version  # または python3 --version
pip --version
```

### 仮想環境の作成（venv）

```bash
# 仮想環境作成
python -m venv venv

# 有効化（Windows）
venv\Scripts\activate

# 有効化（Linux/Mac）
source venv/bin/activate

# 無効化
deactivate
```

### パッケージ管理

```bash
# パッケージインストール
pip install requests

# requirements.txt から一括インストール
pip install -r requirements.txt

# 現在の環境をエクスポート
pip freeze > requirements.txt

# パッケージアップグレード
pip install --upgrade package_name

# パッケージアンインストール
pip uninstall package_name
```

### requirements.txt

```txt
# requirements.txt
requests==2.31.0
flask==3.0.0
pytest==7.4.3
black==23.12.1
mypy==1.7.1
```

---

## プロジェクト構成

### 小規模プロジェクト

```
my_project/
├── venv/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

### 中〜大規模プロジェクト

```
my_project/
├── venv/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   └── test_services/
├── requirements.txt
├── setup.py
└── README.md
```

---

## よくある実装パターン

### 1. 設定ファイル管理

#### config.py

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    DATABASE_URL: str
    API_KEY: str
    DEBUG: bool = False

    @classmethod
    def from_env(cls):
        return cls(
            DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///default.db'),
            API_KEY=os.getenv('API_KEY', ''),
            DEBUG=os.getenv('DEBUG', 'False').lower() == 'true'
        )

# 使用
config = Config.from_env()
print(config.DATABASE_URL)
```

#### .env ファイル

```bash
# .env
DATABASE_URL=postgresql://localhost/mydb
API_KEY=secret_key_here
DEBUG=True
```

```python
# python-dotenv を使用
from dotenv import load_dotenv
load_dotenv()  # .env を読み込む

config = Config.from_env()
```

### 2. ロギング

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """ロガーのセットアップ"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # ファイルハンドラー
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ロガー設定
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 使用
logger = setup_logger('myapp', 'app.log')
logger.info('Application started')
logger.error('An error occurred', exc_info=True)
```

### 3. データベース接続（SQLite）

```python
import sqlite3
from contextlib import contextmanager
from typing import List, Optional

@contextmanager
def get_db_connection(db_path: str):
    """データベース接続のコンテキストマネージャ"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 辞書風アクセス
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with get_db_connection(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')

    def create_user(self, name: str, email: str) -> int:
        with get_db_connection(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO users (name, email) VALUES (?, ?)',
                (name, email)
            )
            return cursor.lastrowid

    def get_user(self, user_id: int) -> Optional[dict]:
        with get_db_connection(self.db_path) as conn:
            row = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_users(self) -> List[dict]:
        with get_db_connection(self.db_path) as conn:
            rows = conn.execute('SELECT * FROM users').fetchall()
            return [dict(row) for row in rows]

# 使用
repo = UserRepository('users.db')
user_id = repo.create_user('Alice', 'alice@example.com')
user = repo.get_user(user_id)
print(user)
```

### 4. Web API クライアント

```python
import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f'{self.base_url}/{endpoint}'
        response = requests.request(
            method,
            url,
            headers=self.headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict:
        return self._request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Dict) -> Dict:
        return self._request('PUT', endpoint, json=data)

    def delete(self, endpoint: str) -> Dict:
        return self._request('DELETE', endpoint)

# 使用
client = APIClient('https://api.example.com', 'your_api_key')

# GETリクエスト
users = client.get('users', params={'page': 1})

# POSTリクエスト
new_user = client.post('users', data={'name': 'Alice', 'email': 'alice@example.com'})
```

### 5. ファイル処理

```python
import csv
import json
from pathlib import Path
from typing import List, Dict

class FileHandler:
    @staticmethod
    def read_json(file_path: str) -> Dict:
        """JSONファイル読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: str, data: Dict, indent: int = 2):
        """JSONファイル書き込み"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

    @staticmethod
    def read_csv(file_path: str) -> List[Dict]:
        """CSV読み込み（辞書形式）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    @staticmethod
    def write_csv(file_path: str, data: List[Dict], fieldnames: List[str]):
        """CSV書き込み"""
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def read_lines(file_path: str) -> List[str]:
        """テキストファイル行読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]

# 使用
data = FileHandler.read_json('config.json')
FileHandler.write_json('output.json', data)

users = FileHandler.read_csv('users.csv')
FileHandler.write_csv('output.csv', users, fieldnames=['id', 'name', 'email'])
```

### 6. コマンドラインツール（argparse）

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='My CLI Tool')

    # 位置引数
    parser.add_argument('input_file', help='Input file path')

    # オプション引数
    parser.add_argument('-o', '--output', help='Output file path', default='output.txt')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('-n', '--number', type=int, default=10, help='Number of items')

    # サブコマンド
    subparsers = parser.add_subparsers(dest='command')

    # add コマンド
    add_parser = subparsers.add_parser('add', help='Add items')
    add_parser.add_argument('items', nargs='+', help='Items to add')

    # remove コマンド
    remove_parser = subparsers.add_parser('remove', help='Remove items')
    remove_parser.add_argument('items', nargs='+', help='Items to remove')

    args = parser.parse_args()

    if args.command == 'add':
        print(f'Adding: {args.items}')
    elif args.command == 'remove':
        print(f'Removing: {args.items}')

if __name__ == '__main__':
    main()
```

```bash
# 使用例
python script.py input.txt -o output.txt -v
python script.py input.txt add item1 item2 item3
python script.py input.txt remove item1
```

---

## ベストプラクティス

### 1. コーディングスタイル（PEP 8）

```python
# ✅ 良い例

# インポート順序: 標準ライブラリ → サードパーティ → ローカル
import os
import sys

import requests
import numpy as np

from my_module import MyClass

# 定数は大文字
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# 関数名はスネークケース
def calculate_total_price(items):
    pass

# クラス名はパスカルケース
class UserService:
    pass

# 1行は79文字以内
def long_function_name(
    var_one, var_two, var_three,
    var_four
):
    pass
```

### 2. 型ヒントの活用

```python
from typing import List, Dict, Optional

def process_users(
    users: List[Dict[str, str]],
    filter_active: bool = True
) -> List[str]:
    """ユーザーリストを処理して名前のリストを返す"""
    result: List[str] = []
    for user in users:
        if filter_active and user.get('active'):
            result.append(user['name'])
    return result
```

### 3. エラーハンドリング

```python
# ❌ 避ける
try:
    result = risky_operation()
except:  # すべての例外をキャッチ
    pass

# ✅ 推奨
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f'Invalid value: {e}')
    raise
except FileNotFoundError as e:
    logger.error(f'File not found: {e}')
    return None
finally:
    cleanup()
```

### 4. with文の活用

```python
# ❌ 避ける
file = open('data.txt', 'r')
content = file.read()
file.close()

# ✅ 推奨
with open('data.txt', 'r') as file:
    content = file.read()
```

### 5. リスト内包表記

```python
# ❌ 避ける
result = []
for item in items:
    if item > 10:
        result.append(item * 2)

# ✅ 推奨
result = [item * 2 for item in items if item > 10]

# ただし、複雑な場合は通常のforループの方が読みやすい
```

---

## デバッグとテスト

### デバッグ

```python
# print デバッグ
print(f'Debug: value = {value}')

# pdb（Pythonデバッガ）
import pdb
pdb.set_trace()  # ここでブレークポイント

# またはブレークポイント関数（Python 3.7+）
breakpoint()

# ロギングでのデバッグ
logger.debug(f'Processing item: {item}')
```

### ユニットテスト（pytest）

```python
# test_calculator.py
import pytest

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# テスト関数
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

# フィクスチャ
@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_with_fixture(sample_data):
    assert len(sample_data) == 5
```

```bash
# テスト実行
pytest
pytest test_calculator.py
pytest -v  # 詳細表示
pytest --cov=src  # カバレッジ表示
```

---

## パフォーマンス最適化

### 1. timeit でパフォーマンス計測

```python
import timeit

# 関数の実行時間計測
def test_function():
    return sum(range(1000))

time = timeit.timeit(test_function, number=10000)
print(f'Time: {time} seconds')
```

### 2. プロファイリング

```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

# プロファイリング実行
cProfile.run('slow_function()', 'profile_stats')

# 結果表示
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### 3. メモ化（functools.lru_cache）

```python
from functools import lru_cache

# ❌ 遅い
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# ✅ 速い
@lru_cache(maxsize=None)
def fibonacci_cached(n):
    if n < 2:
        return n
    return fibonacci_cached(n-1) + fibonacci_cached(n-2)

print(fibonacci_cached(100))  # 瞬時に計算
```

---

## よく使う標準ライブラリ

```python
# 日時
from datetime import datetime, timedelta
now = datetime.now()
tomorrow = now + timedelta(days=1)

# 正規表現
import re
pattern = r'\d{3}-\d{4}'
match = re.search(pattern, '電話番号: 123-4567')

# JSON
import json
data = json.loads('{"name": "Alice"}')
json_str = json.dumps(data, indent=2)

# パス操作
from pathlib import Path
path = Path('data/file.txt')
path.exists()
path.read_text()
path.write_text('content')

# コレクション
from collections import Counter, defaultdict
counter = Counter([1, 2, 2, 3, 3, 3])  # {1: 1, 2: 2, 3: 3}
dd = defaultdict(list)  # 存在しないキーでもエラーなし

# イテレーション
from itertools import chain, combinations
list(chain([1, 2], [3, 4]))  # [1, 2, 3, 4]
list(combinations([1, 2, 3], 2))  # [(1, 2), (1, 3), (2, 3)]
```

---

## 参考資料

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)
- [Real Python Tutorials](https://realpython.com/)
- [Python Patterns](https://python-patterns.guide/)

---

## チートシート

```bash
# 仮想環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# パッケージ管理
pip install package
pip freeze > requirements.txt
pip install -r requirements.txt

# テスト
pytest
pytest -v
pytest --cov

# フォーマット
black src/
flake8 src/

# 型チェック
mypy src/
```
