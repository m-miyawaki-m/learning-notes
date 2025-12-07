# Python 基礎概念

> 対象: Python 3.8+
> 環境: CPython, 仮想環境（venv）

## 学習目標

- Pythonの基本概念と特徴を理解する
- データ型と制御構文を使いこなせる
- 関数とモジュールを適切に使える
- オブジェクト指向プログラミングの基礎を理解する

---

## Pythonの特徴

### 1. インタープリタ型言語

```python
# コンパイル不要、即座に実行可能
print("Hello, Python!")
```

### 2. 動的型付け

```python
# 型宣言不要
x = 10        # int
x = "Hello"   # str（再代入で型変更可能）
x = [1, 2, 3] # list
```

### 3. インデントによるブロック構造

```python
# インデント（通常4スペース）でブロックを表現
if True:
    print("True")
    if True:
        print("Nested")
```

### 4. 豊富な標準ライブラリ

```python
import os
import json
import datetime
import re
```

---

## データ型

### 1. 数値型

#### int（整数）

```python
x = 10
y = -5
z = 1_000_000  # アンダースコアで区切り可能

# 巨大な整数も扱える
big_num = 12345678901234567890
```

#### float（浮動小数点数）

```python
pi = 3.14
e = 2.71828
scientific = 1.5e-10  # 科学的記法
```

#### 演算

```python
# 基本演算
10 + 5   # 15（加算）
10 - 5   # 5（減算）
10 * 5   # 50（乗算）
10 / 5   # 2.0（除算、常にfloat）
10 // 3  # 3（整数除算）
10 % 3   # 1（剰余）
2 ** 3   # 8（べき乗）

# 型変換
int(3.14)    # 3
float(10)    # 10.0
str(123)     # "123"
```

### 2. 文字列（str）

```python
# シングル/ダブルクォート
s1 = 'Hello'
s2 = "World"

# 複数行文字列
multiline = """
This is
a multiline
string
"""

# フォーマット済み文字列リテラル（f-string）
name = "Alice"
age = 30
print(f"Name: {name}, Age: {age}")  # "Name: Alice, Age: 30"

# 文字列操作
s = "Hello, World!"
s.upper()       # "HELLO, WORLD!"
s.lower()       # "hello, world!"
s.replace("World", "Python")  # "Hello, Python!"
s.split(", ")   # ["Hello", "World!"]
s.startswith("Hello")  # True
s.endswith("!")        # True
len(s)          # 13

# スライス
s[0]      # "H"
s[0:5]    # "Hello"
s[7:]     # "World!"
s[:5]     # "Hello"
s[-1]     # "!"
s[::-1]   # "!dlroW ,olleH" (逆順)
```

### 3. ブール型（bool）

```python
is_valid = True
is_empty = False

# 比較演算子
10 > 5    # True
10 < 5    # False
10 == 10  # True
10 != 5   # True
10 >= 10  # True

# 論理演算子
True and False   # False
True or False    # True
not True         # False

# 真偽値評価
bool(0)        # False
bool("")       # False
bool([])       # False
bool(None)     # False
bool(1)        # True
bool("text")   # True
bool([1, 2])   # True
```

### 4. None（null相当）

```python
x = None

if x is None:
    print("x is None")

# is と == の違い
x == None   # 動作するが非推奨
x is None   # 推奨
```

---

## コレクション型

### 1. リスト（list）- 可変、順序あり

```python
# 作成
numbers = [1, 2, 3, 4, 5]
mixed = [1, "two", 3.0, True]
nested = [[1, 2], [3, 4]]

# アクセス
numbers[0]     # 1
numbers[-1]    # 5（末尾）
numbers[1:3]   # [2, 3]（スライス）

# 変更
numbers[0] = 10
numbers.append(6)           # [10, 2, 3, 4, 5, 6]
numbers.insert(0, 0)        # [0, 10, 2, 3, 4, 5, 6]
numbers.remove(10)          # 値で削除
numbers.pop()               # 末尾を削除して返す
numbers.pop(0)              # インデックス指定で削除

# 操作
len(numbers)    # 長さ
numbers.sort()  # ソート（破壊的）
sorted(numbers) # ソート（新しいリスト）
numbers.reverse()  # 反転（破壊的）
numbers.extend([7, 8])  # リスト結合

# リスト内包表記
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]
```

### 2. タプル（tuple）- 不変、順序あり

```python
# 作成
point = (10, 20)
single = (1,)  # 要素1つの場合はカンマ必須

# アクセス（リストと同様）
point[0]  # 10

# アンパック
x, y = point  # x=10, y=20

# 用途：関数の複数戻り値
def get_coordinates():
    return (10, 20)

x, y = get_coordinates()
```

### 3. 辞書（dict）- キーと値のマッピング

```python
# 作成
person = {
    "name": "Alice",
    "age": 30,
    "city": "Tokyo"
}

# アクセス
person["name"]           # "Alice"
person.get("name")       # "Alice"
person.get("country", "Unknown")  # デフォルト値

# 変更
person["age"] = 31       # 更新
person["email"] = "alice@example.com"  # 追加
del person["city"]       # 削除
person.pop("email")      # 削除して値を返す

# 操作
person.keys()      # dict_keys(['name', 'age'])
person.values()    # dict_values(['Alice', 31])
person.items()     # dict_items([('name', 'Alice'), ('age', 31)])

# 存在確認
"name" in person   # True

# 辞書内包表記
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

### 4. セット（set）- 重複なし、順序なし

```python
# 作成
numbers = {1, 2, 3, 4, 5}
empty_set = set()  # 空セットは set() で作成

# 操作
numbers.add(6)
numbers.remove(1)    # 存在しない場合はKeyError
numbers.discard(1)   # 存在しなくてもエラーなし

# 集合演算
a = {1, 2, 3}
b = {3, 4, 5}

a | b  # {1, 2, 3, 4, 5} 和集合
a & b  # {3} 積集合
a - b  # {1, 2} 差集合
a ^ b  # {1, 2, 4, 5} 対称差

# 重複削除
unique = list(set([1, 2, 2, 3, 3, 3]))  # [1, 2, 3]
```

---

## 制御構文

### 1. if文

```python
x = 10

if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

# 三項演算子
result = "Even" if x % 2 == 0 else "Odd"
```

### 2. forループ

```python
# リストのループ
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# rangeを使った数値ループ
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):     # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8
    print(i)

# enumerateでインデックスと値
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# 辞書のループ
person = {"name": "Alice", "age": 30}
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(key, value)
```

### 3. whileループ

```python
count = 0
while count < 5:
    print(count)
    count += 1

# 無限ループ
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == 'quit':
        break
```

### 4. break / continue

```python
# break: ループを抜ける
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: 次の反復へ
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
```

---

## 関数

### 基本的な関数

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")  # "Hello, Alice!"
```

### デフォルト引数

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")              # "Hello, Alice!"
greet("Alice", "Hi")        # "Hi, Alice!"
greet("Alice", greeting="Hey")  # "Hey, Alice!"
```

### 可変長引数

```python
# *args: 位置引数のタプル
def sum_all(*args):
    return sum(args)

sum_all(1, 2, 3)        # 6
sum_all(1, 2, 3, 4, 5)  # 15

# **kwargs: キーワード引数の辞書
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="Tokyo")
```

### ラムダ式（無名関数）

```python
# 通常の関数
def square(x):
    return x ** 2

# ラムダ式
square = lambda x: x ** 2

# よくある使用例
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
# [1, 4, 9, 16, 25]

evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4]
```

### アノテーション（型ヒント）

```python
def greet(name: str, age: int) -> str:
    return f"Hello, {name}! You are {age} years old."

# 実行時には型チェックされない（IDEやmypyで利用）
result = greet("Alice", 30)
```

---

## クラスとオブジェクト指向

### 基本的なクラス

```python
class Person:
    # コンストラクタ
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # メソッド
    def greet(self):
        return f"Hello, I'm {self.name}"

    def birthday(self):
        self.age += 1

# インスタンス化
alice = Person("Alice", 30)
print(alice.greet())  # "Hello, I'm Alice"
alice.birthday()
print(alice.age)      # 31
```

### クラス変数とインスタンス変数

```python
class Dog:
    # クラス変数（全インスタンスで共有）
    species = "Canis familiaris"

    def __init__(self, name, age):
        # インスタンス変数（インスタンスごとに独立）
        self.name = name
        self.age = age

buddy = Dog("Buddy", 5)
miles = Dog("Miles", 3)

print(buddy.species)  # "Canis familiaris"
print(Dog.species)    # "Canis familiaris"
```

### 継承

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # "Buddy says Woof!"
print(cat.speak())  # "Whiskers says Meow!"
```

### 特殊メソッド（マジックメソッド）

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        # print()で呼ばれる
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        # REPLで呼ばれる
        return f"Point(x={self.x}, y={self.y})"

    def __add__(self, other):
        # + 演算子
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        # == 演算子
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
p2 = Point(3, 4)
p3 = p1 + p2
print(p3)  # "Point(4, 6)"
```

---

## モジュールとパッケージ

### モジュールのインポート

```python
# 標準ライブラリ
import math
print(math.sqrt(16))  # 4.0

# 別名をつける
import datetime as dt
now = dt.datetime.now()

# 特定の関数のみインポート
from math import sqrt, pi
print(sqrt(16))  # 4.0
print(pi)        # 3.141592653589793

# 全てインポート（非推奨）
from math import *
```

### 自作モジュール

```python
# mymodule.py
def greet(name):
    return f"Hello, {name}!"

PI = 3.14159
```

```python
# main.py
import mymodule

print(mymodule.greet("Alice"))
print(mymodule.PI)

# または
from mymodule import greet, PI
print(greet("Bob"))
```

---

## 例外処理

```python
# 基本的なtry-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Division by zero!")

# 複数の例外
try:
    value = int("abc")
except ValueError:
    print("Invalid value")
except TypeError:
    print("Invalid type")

# 例外オブジェクトを取得
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")

# else: 例外が発生しなかった場合
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Error")
else:
    print(f"Result: {result}")

# finally: 必ず実行
try:
    file = open("data.txt")
    # 処理
except FileNotFoundError:
    print("File not found")
finally:
    print("Cleanup")

# 例外を発生させる
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age
```

---

## ファイル操作

```python
# ファイル読み込み
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)

# 1行ずつ読み込み
with open("data.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line.strip())

# 全行をリストで取得
with open("data.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# ファイル書き込み
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello, World!\n")
    file.write("Second line\n")

# 追記モード
with open("output.txt", "a", encoding="utf-8") as file:
    file.write("Appended line\n")

# JSONファイル
import json

# 読み込み
with open("data.json", "r") as file:
    data = json.load(file)

# 書き込み
data = {"name": "Alice", "age": 30}
with open("output.json", "w") as file:
    json.dump(data, file, indent=2)
```

---

## 学習ロードマップ

### Week 1: 基礎文法
- [ ] データ型と変数
- [ ] 制御構文（if, for, while）
- [ ] 関数の定義と使用

### Week 2: コレクション
- [ ] リスト、タプル、辞書、セット
- [ ] リスト内包表記
- [ ] コレクションの操作

### Week 3: オブジェクト指向
- [ ] クラスの定義
- [ ] 継承とポリモーフィズム
- [ ] 特殊メソッド

### Week 4: 実践
- [ ] モジュールとパッケージ
- [ ] ファイル操作
- [ ] 例外処理
- [ ] 簡単なプログラム作成

---

## 参考資料

- [Python公式ドキュメント](https://docs.python.org/ja/3/)
- [Python チュートリアル](https://docs.python.org/ja/3/tutorial/)
- 書籍『入門 Python 3』
- 書籍『Effective Python』
- [Real Python](https://realpython.com/)

---

## チートシート

```python
# データ型
int, float, str, bool, None

# コレクション
list = [1, 2, 3]
tuple = (1, 2, 3)
dict = {"key": "value"}
set = {1, 2, 3}

# 制御構文
if condition:
    pass
elif other_condition:
    pass
else:
    pass

for item in items:
    pass

while condition:
    pass

# 関数
def function(arg, default="value"):
    return result

# クラス
class MyClass:
    def __init__(self, value):
        self.value = value

# 例外
try:
    risky_operation()
except Exception as e:
    handle_error(e)
finally:
    cleanup()
```
