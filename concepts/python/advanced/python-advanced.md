# Python 高度な概念

> 対象: Python 3.8+
> 前提: Python基礎を習得済み

## 学習目標

- デコレータの仕組みと実装ができる
- ジェネレータとイテレータを理解し使える
- コンテキストマネージャを実装できる
- 並行処理・並列処理の違いと実装方法を理解する
- 型ヒントを活用できる

---

## デコレータ

### 基本概念

デコレータは関数を引数として受け取り、新しい関数を返す関数です。

```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# 出力:
# Before function
# Hello!
# After function
```

### 引数を持つ関数のデコレータ

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(3, 5)  # 8
```

### functools.wraps

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # メタデータ保持
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### 実用例: ログ出力

```python
import functools
import time

def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__} with {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

add(3, 5)
# [LOG] Calling add with (3, 5), {}
# [LOG] add returned 8
```

### 実用例: 実行時間計測

```python
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()
# slow_function took 1.0012 seconds
```

### パラメータ付きデコレータ

```python
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

### クラスベースのデコレータ

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # Call 1 of say_hello
say_hello()  # Call 2 of say_hello
```

---

## ジェネレータとイテレータ

### イテレータ

```python
# リストはイテラブル
numbers = [1, 2, 3, 4, 5]

# イテレータ取得
iterator = iter(numbers)

# 次の要素を取得
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3

# forループは内部でイテレータを使用
for num in numbers:
    print(num)
```

### カスタムイテレータ

```python
class Counter:
    def __init__(self, max_value):
        self.max_value = max_value
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.max_value:
            raise StopIteration
        self.current += 1
        return self.current

counter = Counter(5)
for num in counter:
    print(num)  # 1, 2, 3, 4, 5
```

### ジェネレータ関数

```python
def count_up_to(max_value):
    count = 1
    while count <= max_value:
        yield count  # 値を返すが、状態を保持
        count += 1

# ジェネレータオブジェクト作成
gen = count_up_to(5)

print(next(gen))  # 1
print(next(gen))  # 2

# forループで使用
for num in count_up_to(5):
    print(num)  # 1, 2, 3, 4, 5
```

### ジェネレータ式

```python
# リスト内包表記
squares_list = [x**2 for x in range(10)]  # リスト全体をメモリに保持

# ジェネレータ式（メモリ効率的）
squares_gen = (x**2 for x in range(10))

for square in squares_gen:
    print(square)
```

### 実用例: 大量データの処理

```python
def read_large_file(file_path):
    """ファイルを1行ずつ読み込むジェネレータ"""
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# メモリ効率的
for line in read_large_file('large_file.txt'):
    process(line)
```

### yield from

```python
def generator1():
    yield 1
    yield 2

def generator2():
    yield 3
    yield 4

def combined():
    yield from generator1()
    yield from generator2()

for value in combined():
    print(value)  # 1, 2, 3, 4
```

---

## コンテキストマネージャ

### with文

```python
# withを使わない場合
file = open('data.txt', 'r')
try:
    content = file.read()
finally:
    file.close()

# withを使う場合（推奨）
with open('data.txt', 'r') as file:
    content = file.read()
# 自動的にfile.close()が呼ばれる
```

### カスタムコンテキストマネージャ（クラスベース）

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()
        # 例外を再送出する場合はFalseを返す
        return False

with FileManager('data.txt', 'r') as file:
    content = file.read()
```

### contextlib.contextmanager

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()

with file_manager('data.txt', 'r') as file:
    content = file.read()
```

### 実用例: データベース接続

```python
@contextmanager
def database_connection(db_url):
    conn = connect_to_database(db_url)
    try:
        yield conn
    finally:
        conn.close()

with database_connection('postgresql://localhost/mydb') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    results = cursor.fetchall()
```

### 実用例: 一時的な設定変更

```python
@contextmanager
def temporary_config(key, value):
    old_value = config.get(key)
    config.set(key, value)
    try:
        yield
    finally:
        config.set(key, old_value)

with temporary_config('debug', True):
    # デバッグモードで実行
    run_tests()
# 元の設定に戻る
```

---

## 並行処理・並列処理

### threading（並行処理 - I/Oバウンド）

```python
import threading
import time

def download_file(url):
    print(f"Downloading {url}...")
    time.sleep(2)  # ダウンロードをシミュレート
    print(f"Finished {url}")

# スレッドを作成して実行
threads = []
urls = ['url1', 'url2', 'url3']

for url in urls:
    thread = threading.Thread(target=download_file, args=(url,))
    threads.append(thread)
    thread.start()

# 全スレッドの完了を待つ
for thread in threads:
    thread.join()

print("All downloads complete")
```

### multiprocessing（並列処理 - CPUバウンド）

```python
import multiprocessing
import time

def cpu_intensive_task(n):
    """CPU集約的なタスク"""
    result = sum(i * i for i in range(n))
    return result

if __name__ == '__main__':
    # プロセスを作成して実行
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(cpu_intensive_task, [1000000, 2000000, 3000000])

    print(results)
```

### concurrent.futures

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

def task(n):
    time.sleep(1)
    return n * n

# スレッドプール
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    results = [future.result() for future in futures]

# プロセスプール
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(task, range(10)))
```

### asyncio（非同期I/O）

```python
import asyncio

async def fetch_data(url):
    print(f"Fetching {url}...")
    await asyncio.sleep(2)  # 非同期待機
    print(f"Finished {url}")
    return f"Data from {url}"

async def main():
    # 複数の非同期タスクを並行実行
    tasks = [
        fetch_data('url1'),
        fetch_data('url2'),
        fetch_data('url3')
    ]
    results = await asyncio.gather(*tasks)
    print(results)

# 実行
asyncio.run(main())
```

### 使い分け

| 処理タイプ | 推奨手法 | 用途 |
|----------|---------|------|
| **I/Oバウンド** | `asyncio`, `threading` | ファイル読み書き、ネットワーク通信 |
| **CPUバウンド** | `multiprocessing` | 重い計算処理、データ処理 |

---

## 型ヒント（Type Hints）

### 基本的な型ヒント

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

# 変数の型ヒント
age: int = 30
name: str = "Alice"
is_valid: bool = True
```

### コレクションの型ヒント

```python
from typing import List, Dict, Tuple, Set, Optional

def process_numbers(numbers: List[int]) -> int:
    return sum(numbers)

def get_user_info() -> Dict[str, str]:
    return {"name": "Alice", "email": "alice@example.com"}

def get_coordinates() -> Tuple[float, float]:
    return (10.5, 20.3)

# Optional: None の可能性がある
def find_user(user_id: int) -> Optional[str]:
    if user_id > 0:
        return "Alice"
    return None
```

### Union型

```python
from typing import Union

def process_input(value: Union[int, str]) -> str:
    if isinstance(value, int):
        return str(value * 2)
    return value.upper()

# Python 3.10+
def process_input(value: int | str) -> str:
    pass
```

### ジェネリクス

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# 使用
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
```

### Callable

```python
from typing import Callable

def apply_function(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = apply_function(add, 3, 5)  # 8
```

### Protocol（構造的部分型）

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # OK
render(Square())  # OK
```

---

## データクラス

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Person:
    name: str
    age: int
    email: str = ""  # デフォルト値
    friends: List[str] = field(default_factory=list)

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

# 自動生成: __init__, __repr__, __eq__
person = Person("Alice", 30, "alice@example.com")
print(person)  # Person(name='Alice', age=30, email='alice@example.com', friends=[])

# 不変データクラス
@dataclass(frozen=True)
class Point:
    x: float
    y: float

point = Point(10.0, 20.0)
# point.x = 15.0  # エラー: frozen
```

---

## リスト内包表記の高度な使い方

```python
# ネストした内包表記
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 辞書内包表記
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# セット内包表記
unique_lengths = {len(word) for word in ['apple', 'banana', 'cherry']}
# {5, 6}

# 条件付き
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# if-else
result = [x if x % 2 == 0 else -x for x in range(5)]
# [0, -1, 2, -3, 4]
```

---

## 学習ロードマップ

### Week 1: デコレータとジェネレータ
- [ ] デコレータの仕組み理解
- [ ] 実用的なデコレータ作成
- [ ] ジェネレータの実装と活用

### Week 2: 並行処理
- [ ] threading, multiprocessing の違い理解
- [ ] asyncio の基礎
- [ ] 適切な手法の選択

### Week 3: 型ヒント
- [ ] 基本的な型ヒント
- [ ] ジェネリクス、Protocol
- [ ] mypyでの型チェック

### Week 4: 実践
- [ ] 実プロジェクトで高度な機能を活用
- [ ] パフォーマンス最適化
- [ ] コードレビュー

---

## 参考資料

- [Python公式ドキュメント - デコレータ](https://docs.python.org/ja/3/glossary.html#term-decorator)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 557 - Data Classes](https://peps.python.org/pep-0557/)
- 書籍『Effective Python』
- 書籍『Fluent Python』

---

## チートシート

```python
# デコレータ
@decorator
def func():
    pass

# ジェネレータ
def gen():
    yield value

# コンテキストマネージャ
with context_manager() as resource:
    use(resource)

# 型ヒント
def func(arg: type) -> return_type:
    pass

# データクラス
@dataclass
class MyClass:
    field: type
```
