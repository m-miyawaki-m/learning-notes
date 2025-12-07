# デコレータとジェネレータ 詳細ガイド

> 対象: Python 3.8+
> 難易度: 中級〜上級

このドキュメントは、Pythonのデコレータとジェネレータについて、より詳細な解説と実践的な例を提供します。

---

## 目次

1. [デコレータ詳細](#デコレータ詳細)
2. [ジェネレータ詳細](#ジェネレータ詳細)
3. [実践的な組み合わせ](#実践的な組み合わせ)

---

## デコレータ詳細

### デコレータの仕組みを深く理解する

#### 基本原理: 関数は第一級オブジェクト

```python
def greet(name):
    return f"Hello, {name}!"

# 関数を変数に代入
say_hello = greet
print(say_hello("Alice"))  # "Hello, Alice!"

# 関数を引数として渡す
def execute_function(func, value):
    return func(value)

result = execute_function(greet, "Bob")  # "Hello, Bob!"

# 関数を返り値として返す
def get_greeter():
    def greet_inner(name):
        return f"Hi, {name}!"
    return greet_inner

greeter = get_greeter()
print(greeter("Charlie"))  # "Hi, Charlie!"
```

#### デコレータの展開

```python
# デコレータを使う
@my_decorator
def say_hello():
    print("Hello!")

# 上記は以下と同等
def say_hello():
    print("Hello!")
say_hello = my_decorator(say_hello)
```

### デコレータの段階的実装

#### Step 1: 最もシンプルなデコレータ

```python
def simple_decorator(func):
    def wrapper():
        print("--- Before ---")
        func()
        print("--- After ---")
    return wrapper

@simple_decorator
def greet():
    print("Hello!")

greet()
# 出力:
# --- Before ---
# Hello!
# --- After ---
```

#### Step 2: 引数を扱えるデコレータ

```python
def decorator_with_args(func):
    def wrapper(*args, **kwargs):
        print(f"Arguments: {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper

@decorator_with_args
def add(a, b):
    return a + b

@decorator_with_args
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

add(3, 5)
# Arguments: (3, 5), {}
# Result: 8

greet("Alice", greeting="Hi")
# Arguments: ('Alice',), {'greeting': 'Hi'}
# Result: Hi, Alice!
```

#### Step 3: メタデータを保持するデコレータ

```python
from functools import wraps

# ❌ メタデータが失われる
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def important_function():
    """This is an important function."""
    pass

print(important_function.__name__)  # "wrapper"
print(important_function.__doc__)   # None

# ✅ メタデータを保持
def good_decorator(func):
    @wraps(func)  # 元の関数のメタデータをコピー
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def important_function():
    """This is an important function."""
    pass

print(important_function.__name__)  # "important_function"
print(important_function.__doc__)   # "This is an important function."
```

### 実用的なデコレータパターン

#### 1. リトライデコレータ

```python
import time
import functools
from typing import Type

def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """失敗時に自動リトライするデコレータ"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed.")
            raise last_exception
        return wrapper
    return decorator

# 使用例
@retry(max_attempts=3, delay=2.0, exceptions=(ConnectionError, TimeoutError))
def fetch_data_from_api():
    import random
    if random.random() < 0.7:  # 70%の確率で失敗
        raise ConnectionError("API connection failed")
    return {"data": "success"}

# result = fetch_data_from_api()
```

#### 2. キャッシュデコレータ（メモ化）

```python
import functools
import time

def custom_cache(maxsize=128):
    """カスタムキャッシュデコレータ"""
    def decorator(func):
        cache = {}
        cache_info = {'hits': 0, 'misses': 0}

        @functools.wraps(func)
        def wrapper(*args):
            if args in cache:
                cache_info['hits'] += 1
                return cache[args]
            else:
                cache_info['misses'] += 1
                result = func(*args)
                if len(cache) >= maxsize:
                    # 最古のエントリを削除（簡易版）
                    cache.pop(next(iter(cache)))
                cache[args] = result
                return result

        def cache_clear():
            cache.clear()
            cache_info['hits'] = 0
            cache_info['misses'] = 0

        def cache_info_func():
            return cache_info.copy()

        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info_func

        return wrapper
    return decorator

@custom_cache(maxsize=100)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(35))  # 初回は遅い
print(fibonacci(35))  # 2回目は瞬時
print(fibonacci.cache_info())  # {'hits': ..., 'misses': ...}
```

#### 3. 権限チェックデコレータ

```python
import functools

class PermissionError(Exception):
    pass

def require_permission(permission: str):
    """特定の権限を要求するデコレータ"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 第1引数がユーザーオブジェクトと仮定
            user = args[0] if args else None
            if not user or not hasattr(user, 'permissions'):
                raise PermissionError("User object required")

            if permission not in user.permissions:
                raise PermissionError(f"Permission '{permission}' required")

            return func(*args, **kwargs)
        return wrapper
    return decorator

class User:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

@require_permission('admin')
def delete_user(user, target_user_id):
    print(f"{user.name} deleted user {target_user_id}")

@require_permission('read')
def view_data(user):
    print(f"{user.name} viewing data")

# 使用例
admin = User("Alice", ['admin', 'read', 'write'])
regular_user = User("Bob", ['read'])

delete_user(admin, 123)  # OK
# delete_user(regular_user, 123)  # PermissionError
```

#### 4. レート制限デコレータ

```python
import time
import functools
from collections import deque

def rate_limit(max_calls: int, time_window: float):
    """一定時間内の呼び出し回数を制限するデコレータ"""
    def decorator(func):
        calls = deque()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # 古い呼び出しを削除
            while calls and calls[0] < now - time_window:
                calls.popleft()

            if len(calls) >= max_calls:
                sleep_time = time_window - (now - calls[0])
                print(f"Rate limit exceeded. Sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                calls.popleft()

            calls.append(time.time())
            return func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_calls=3, time_window=5.0)  # 5秒間に3回まで
def api_call(endpoint):
    print(f"Calling {endpoint} at {time.time():.2f}")
    return "Success"

# テスト
for i in range(5):
    api_call(f"/api/endpoint{i}")
```

#### 5. デバッグデコレータ

```python
import functools
import traceback

def debug(verbose: bool = False):
    """デバッグ情報を出力するデコレータ"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 引数情報
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            print(f"[DEBUG] Calling {func.__name__}({signature})")

            try:
                result = func(*args, **kwargs)
                print(f"[DEBUG] {func.__name__} returned {result!r}")
                return result
            except Exception as e:
                print(f"[DEBUG] {func.__name__} raised {type(e).__name__}: {e}")
                if verbose:
                    traceback.print_exc()
                raise

        return wrapper
    return decorator

@debug(verbose=True)
def divide(a, b):
    return a / b

divide(10, 2)   # 正常
# divide(10, 0)  # エラー（スタックトレース表示）
```

### 複数のデコレータを組み合わせる

```python
@retry(max_attempts=3)
@rate_limit(max_calls=5, time_window=10.0)
@timer
def complex_operation():
    # 処理
    pass

# 適用順序（下から上）
# 1. timer
# 2. rate_limit
# 3. retry
```

---

## ジェネレータ詳細

### ジェネレータの仕組み

#### メモリ効率の比較

```python
import sys

# ❌ リスト: 全データをメモリに保持
def get_numbers_list(n):
    return [i for i in range(n)]

# ✅ ジェネレータ: 必要に応じて生成
def get_numbers_gen(n):
    for i in range(n):
        yield i

numbers_list = get_numbers_list(1000000)
numbers_gen = get_numbers_gen(1000000)

print(f"List size: {sys.getsizeof(numbers_list)} bytes")      # ~8MB
print(f"Generator size: {sys.getsizeof(numbers_gen)} bytes")  # ~128 bytes
```

### yield の動作を理解する

```python
def simple_generator():
    print("Starting")
    yield 1
    print("Between 1 and 2")
    yield 2
    print("Between 2 and 3")
    yield 3
    print("Ending")

gen = simple_generator()
print("Generator created")

print(next(gen))  # "Starting" → 1
print(next(gen))  # "Between 1 and 2" → 2
print(next(gen))  # "Between 2 and 3" → 3
# print(next(gen))  # "Ending" → StopIteration
```

### ジェネレータの実用パターン

#### 1. ファイルの遅延読み込み

```python
def read_large_file(file_path, chunk_size=1024):
    """大きなファイルをチャンク単位で読み込む"""
    with open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

# 使用例
for chunk in read_large_file('large_file.txt'):
    process(chunk)
```

#### 2. 無限ジェネレータ

```python
def fibonacci():
    """無限フィボナッチ数列"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 最初の10個だけ取得
from itertools import islice
first_10 = list(islice(fibonacci(), 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

#### 3. パイプライン処理

```python
def read_lines(file_path):
    """ファイルを1行ずつ読み込む"""
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

def filter_comments(lines):
    """コメント行を除外"""
    for line in lines:
        if not line.startswith('#'):
            yield line

def filter_empty(lines):
    """空行を除外"""
    for line in lines:
        if line:
            yield line

def to_uppercase(lines):
    """大文字に変換"""
    for line in lines:
        yield line.upper()

# パイプライン構築
pipeline = to_uppercase(
    filter_empty(
        filter_comments(
            read_lines('data.txt')
        )
    )
)

# 遅延評価: 実際に使用するまで処理されない
for line in pipeline:
    print(line)
```

#### 4. データのバッチ処理

```python
def batch(iterable, batch_size):
    """イテラブルをバッチに分割"""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:  # 残りを返す
        yield batch

# 使用例
numbers = range(100)
for batch_items in batch(numbers, 10):
    print(f"Processing batch: {batch_items}")
    # データベースに一括挿入など
```

#### 5. ツリー走査

```python
class TreeNode:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

def traverse_tree(node):
    """深さ優先探索でツリーを走査"""
    yield node.value
    for child in node.children:
        yield from traverse_tree(child)

# ツリー構築
root = TreeNode(1, [
    TreeNode(2, [TreeNode(4), TreeNode(5)]),
    TreeNode(3, [TreeNode(6), TreeNode(7)])
])

# 走査
for value in traverse_tree(root):
    print(value)  # 1, 2, 4, 5, 3, 6, 7
```

### send() と throw() を使った双方向通信

```python
def echo_generator():
    """値を受け取ってエコーするジェネレータ"""
    while True:
        received = yield
        print(f"Received: {received}")

gen = echo_generator()
next(gen)  # ジェネレータを開始

gen.send("Hello")  # Received: Hello
gen.send(123)      # Received: 123

# throw() で例外を送信
try:
    gen.throw(ValueError, "Something went wrong")
except ValueError as e:
    print(f"Caught: {e}")
```

### コルーチン的な使い方

```python
def running_average():
    """移動平均を計算するジェネレータ"""
    total = 0
    count = 0
    average = None

    while True:
        value = yield average
        total += value
        count += 1
        average = total / count

# 使用例
avg = running_average()
next(avg)  # 初期化

print(avg.send(10))  # 10.0
print(avg.send(20))  # 15.0
print(avg.send(30))  # 20.0
```

---

## 実践的な組み合わせ

### ジェネレータを返すデコレータ

```python
import functools

def trace_generator(func):
    """ジェネレータの動作をトレースするデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        print(f"[TRACE] Generator {func.__name__} created")

        def traced_gen():
            count = 0
            for value in gen:
                count += 1
                print(f"[TRACE] Yielding value #{count}: {value}")
                yield value
            print(f"[TRACE] Generator {func.__name__} exhausted after {count} values")

        return traced_gen()
    return wrapper

@trace_generator
def count_up_to(n):
    for i in range(1, n + 1):
        yield i

# 使用
for num in count_up_to(3):
    print(f"Got: {num}")
```

### デコレータとジェネレータでデータパイプライン

```python
def pipeline_stage(name):
    """パイプラインステージのデコレータ"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(iterable):
            print(f"[{name}] Stage started")
            count = 0
            for item in func(iterable):
                count += 1
                yield item
            print(f"[{name}] Stage completed: {count} items processed")
        return wrapper
    return decorator

@pipeline_stage("Read")
def read_data():
    """データ読み込み"""
    for i in range(10):
        yield i

@pipeline_stage("Filter")
def filter_even(iterable):
    """偶数のみフィルタ"""
    for item in iterable:
        if item % 2 == 0:
            yield item

@pipeline_stage("Transform")
def square(iterable):
    """二乗する"""
    for item in iterable:
        yield item ** 2

# パイプライン実行
result = list(square(filter_even(read_data())))
print(f"Result: {result}")
```

---

## 学習ロードマップ（詳細版）

### Week 1: デコレータ基礎

#### Day 1-2: 基本概念
- [ ] 関数が第一級オブジェクトであることを理解
- [ ] シンプルなデコレータを自作
- [ ] @構文の仕組みを理解

#### Day 3-4: 実用的なデコレータ
- [ ] functools.wraps の必要性を理解
- [ ] 引数を持つデコレータを実装
- [ ] タイマーデコレータを作成

#### Day 5-7: 高度なデコレータ
- [ ] パラメータ付きデコレータを実装
- [ ] クラスベースのデコレータを実装
- [ ] リトライ、キャッシュデコレータを作成

### Week 2: ジェネレータ基礎

#### Day 1-2: ジェネレータの仕組み
- [ ] yield の動作を理解
- [ ] イテレータとの違いを理解
- [ ] next() と StopIteration

#### Day 3-4: ジェネレータの実装
- [ ] ファイル読み込みジェネレータを作成
- [ ] 無限ジェネレータを実装
- [ ] yield from の使い方

#### Day 5-7: 高度なジェネレータ
- [ ] パイプライン処理を実装
- [ ] send() と throw() を使用
- [ ] コルーチン的な使い方を理解

### Week 3: 実践

#### 実装課題
1. ログローテーション機能付きロガーデコレータ
2. API呼び出しのレート制限デコレータ
3. 大容量ファイル処理ジェネレータ
4. データ変換パイプライン

---

## 参考資料

- [PEP 318 - Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 255 - Simple Generators](https://peps.python.org/pep-0255/)
- [PEP 342 - Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)
- [Python Cookbook - デコレータとメタプログラミング](https://www.oreilly.com/library/view/python-cookbook-3rd/9781449357337/)
- [Fluent Python - Chapter 7: Function Decorators and Closures](https://www.oreilly.com/library/view/fluent-python/9781491946237/)

---

## 練習問題

### デコレータ練習

1. **メモ化デコレータ**: フィボナッチ数列の計算を高速化
2. **バリデーションデコレータ**: 関数の引数を検証
3. **非同期リトライデコレータ**: async関数に対応したリトライ

### ジェネレータ練習

1. **CSVパーサー**: 大容量CSVファイルを1行ずつ処理
2. **ウィンドウジェネレータ**: スライディングウィンドウでデータを返す
3. **マージジェネレータ**: 複数のソート済みジェネレータをマージ

---

## まとめ

### デコレータ
- 関数の振る舞いを拡張する強力な手法
- ログ、キャッシュ、権限チェックなどに有用
- functools.wraps で メタデータを保持

### ジェネレータ
- メモリ効率的なイテレータ
- 大量データ処理やパイプライン構築に最適
- 遅延評価による高速化

### 組み合わせ
- デコレータでジェネレータの動作をトレース
- パイプライン処理での両者の活用
