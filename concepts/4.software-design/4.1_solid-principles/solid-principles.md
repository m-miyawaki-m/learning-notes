# SOLID原則

> オブジェクト指向設計における5つの基本原則

## 学習目標
- 各SOLID原則の意味と目的を理解する
- 原則違反のコードを識別できるようになる
- リファクタリングによる原則適用方法を習得する
- 実務での適用判断ができるようになる

---

## 1. 単一責任の原則（Single Responsibility Principle: SRP）

### 定義
**クラスを変更する理由は1つだけであるべき**

「責任」とは「変更の理由」のこと。複数の理由で変更されるクラスは、複数の責任を持っている。

### 違反例

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def calculate_pay(self):
        """給与計算 - 経理部門が変更理由"""
        return self.salary * 1.1

    def save(self):
        """データ保存 - IT部門が変更理由"""
        with open('employees.txt', 'a') as f:
            f.write(f"{self.name},{self.salary}\n")

    def generate_report(self):
        """レポート生成 - 人事部門が変更理由"""
        return f"Employee Report: {self.name}"
```

**問題点**: 3つの異なる部門（経理、IT、人事）が変更を要求する可能性がある

### 改善例

```python
# 責任を分離
class Employee:
    """従業員データのみを保持"""
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

class PayCalculator:
    """給与計算の責任"""
    def calculate_pay(self, employee):
        return employee.salary * 1.1

class EmployeeRepository:
    """データ永続化の責任"""
    def save(self, employee):
        with open('employees.txt', 'a') as f:
            f.write(f"{employee.name},{employee.salary}\n")

class ReportGenerator:
    """レポート生成の責任"""
    def generate_report(self, employee):
        return f"Employee Report: {employee.name}"
```

### 判断基準
- このクラスを変更する理由は何か？
- 複数の部門/チームが変更を要求する可能性があるか？
- メソッドが異なるレベルの抽象度を持っているか？

---

## 2. 開放閉鎖の原則（Open/Closed Principle: OCP）

### 定義
**ソフトウェアエンティティは拡張に対して開いており、修正に対して閉じているべき**

新機能追加時に既存コードを変更せず、新しいコードを追加するだけで済むようにする。

### 違反例

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Circle:
    def __init__(self, radius):
        self.radius = radius

class AreaCalculator:
    def calculate_area(self, shapes):
        total = 0
        for shape in shapes:
            if isinstance(shape, Rectangle):
                total += shape.width * shape.height
            elif isinstance(shape, Circle):
                total += 3.14 * shape.radius ** 2
            # 新しい図形を追加するたびにこのメソッドを修正する必要がある
        return total
```

**問題点**: 新しい図形（三角形など）を追加するたびに`AreaCalculator`を修正する必要がある

### 改善例

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    """抽象基底クラス"""
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

class Triangle(Shape):
    """新しい図形を追加しても既存コードを変更不要"""
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    """変更不要 - 拡張に対して開いている"""
    def calculate_area(self, shapes):
        return sum(shape.area() for shape in shapes)
```

### 実現手法
1. **抽象化**: インターフェースや抽象クラスを使用
2. **ポリモーフィズム**: 継承やダックタイピング
3. **依存性注入**: 具象クラスではなく抽象に依存

---

## 3. リスコフの置換原則（Liskov Substitution Principle: LSP）

### 定義
**派生クラスは基底クラスと置換可能であるべき**

サブタイプは、そのスーパータイプが使用されている場所で使用できなければならない。

### 違反例

```python
class Bird:
    def fly(self):
        return "Flying"

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying"

class Penguin(Bird):
    def fly(self):
        # ペンギンは飛べない！
        raise Exception("Penguins can't fly")

def make_bird_fly(bird: Bird):
    """Birdを期待しているが、Penguinで失敗する"""
    return bird.fly()

# make_bird_fly(Penguin())  # Exception!
```

**問題点**: `Penguin`は`Bird`の代わりに使えない（置換原則違反）

### 改善例

```python
class Bird:
    """鳥の基本動作"""
    def eat(self):
        return "Eating"

class FlyingBird(Bird):
    """飛べる鳥"""
    def fly(self):
        return "Flying"

class Sparrow(FlyingBird):
    def fly(self):
        return "Sparrow flying"

class Penguin(Bird):
    """飛べない鳥はFlyingBirdを継承しない"""
    def swim(self):
        return "Penguin swimming"

def make_bird_fly(bird: FlyingBird):
    """FlyingBirdのみを受け取る"""
    return bird.fly()
```

### 違反の兆候
- サブクラスで例外をスローしてメソッドを無効化
- メソッドで何もしない（空実装）
- 型チェック（`isinstance`）を頻繁に使用

### 契約による設計（Design by Contract）
- **事前条件**: サブクラスは事前条件を強化できない
- **事後条件**: サブクラスは事後条件を弱化できない
- **不変条件**: サブクラスは不変条件を維持しなければならない

---

## 4. インターフェース分離の原則（Interface Segregation Principle: ISP）

### 定義
**クライアントは使用しないメソッドへの依存を強制されるべきではない**

大きなインターフェースを小さな専用インターフェースに分割する。

### 違反例

```python
from abc import ABC, abstractmethod

class Worker(ABC):
    """すべての労働者に過剰な要求"""
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

class Human(Worker):
    def work(self):
        return "Working"

    def eat(self):
        return "Eating"

    def sleep(self):
        return "Sleeping"

class Robot(Worker):
    def work(self):
        return "Working"

    def eat(self):
        # ロボットは食べない
        pass

    def sleep(self):
        # ロボットは寝ない
        pass
```

**問題点**: `Robot`は使わないメソッド（`eat`, `sleep`）を実装する必要がある

### 改善例

```python
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    """必要なインターフェースのみを実装"""
    def work(self):
        return "Working"

    def eat(self):
        return "Eating"

    def sleep(self):
        return "Sleeping"

class Robot(Workable):
    """必要なインターフェースのみを実装"""
    def work(self):
        return "Working"
```

### 実践のポイント
- インターフェースは小さく保つ（1-3メソッド程度）
- クライアントごとに専用インターフェースを設計
- 役割ベースのインターフェース設計（Role Interface）

---

## 5. 依存性逆転の原則（Dependency Inversion Principle: DIP）

### 定義
**高レベルモジュールは低レベルモジュールに依存すべきではない。両者は抽象に依存すべき**

具体的な実装ではなく、抽象（インターフェース）に依存する。

### 違反例

```python
class MySQLDatabase:
    def connect(self):
        return "MySQL connected"

    def execute_query(self, query):
        return f"MySQL: {query}"

class UserService:
    """具体的なMySQLDatabaseに直接依存"""
    def __init__(self):
        self.db = MySQLDatabase()  # 強い結合

    def get_user(self, user_id):
        return self.db.execute_query(f"SELECT * FROM users WHERE id={user_id}")

# PostgreSQLに変更したい場合、UserServiceを修正する必要がある
```

**問題点**:
- `UserService`（高レベル）が`MySQLDatabase`（低レベル）に直接依存
- データベースを変更するとビジネスロジックも変更が必要

### 改善例

```python
from abc import ABC, abstractmethod

# 抽象に依存
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

class MySQLDatabase(Database):
    def connect(self):
        return "MySQL connected"

    def execute_query(self, query):
        return f"MySQL: {query}"

class PostgreSQLDatabase(Database):
    def connect(self):
        return "PostgreSQL connected"

    def execute_query(self, query):
        return f"PostgreSQL: {query}"

class UserService:
    """抽象に依存 - 依存性注入"""
    def __init__(self, db: Database):
        self.db = db  # 疎結合

    def get_user(self, user_id):
        return self.db.execute_query(f"SELECT * FROM users WHERE id={user_id}")

# 使用例
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# データベースを簡単に切り替え可能
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)
```

### 依存性注入（Dependency Injection）の方法

```python
# 1. コンストラクタインジェクション（推奨）
class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

# 2. セッターインジェクション
class Service:
    def set_repository(self, repository: Repository):
        self.repository = repository

# 3. インターフェースインジェクション
class Injectable(ABC):
    @abstractmethod
    def inject(self, dependency):
        pass
```

---

## SOLID原則の相互関係

### 関係図
```
SRP ─────┐
         ├──→ クラス設計の基盤
OCP ─────┘

LSP ─────┐
         ├──→ 継承の正しい使い方
ISP ─────┤
         ├──→ 抽象化の方法
DIP ─────┘
```

### 相乗効果
- **SRP + OCP**: 責任が単一なら拡張しやすい
- **LSP + DIP**: 置換可能な抽象に依存する
- **ISP + DIP**: 小さなインターフェースに依存する

---

## 実務での適用

### 原則適用の判断基準

| 状況 | 適用すべきか |
|------|------------|
| プロトタイプ開発 | 後回し（動くものを優先） |
| 変更頻度が低いコード | 不要（過剰設計を避ける） |
| 共有ライブラリ | 必須（多くの利用者） |
| ビジネスロジック | 推奨（変更に強い） |

### アンチパターン
1. **過剰な抽象化**: すべてをインターフェース化
2. **早すぎる一般化**: 1回の使用で抽象化
3. **原則の盲目的適用**: コンテキストを無視

### リファクタリングの順序
1. まず動くコードを書く
2. テストを書く
3. 重複や変更の兆候を発見
4. SOLID原則を適用してリファクタリング
5. テストで動作を確認

---

## トラブルシューティング

### よくある質問

**Q: すべてのクラスでSOLIDを守るべき？**
A: いいえ。変更頻度が高い、複雑、または再利用される部分で優先的に適用。

**Q: SRPでクラスが増えすぎる問題は？**
A: 適切な名前空間/モジュール設計で解決。クラス数より責任の明確さが重要。

**Q: パフォーマンスへの影響は？**
A: 抽象化によるオーバーヘッドは現代の環境では通常無視できる。測定してから最適化。

**Q: 既存コードへの適用方法は？**
A: 修正が必要になった部分から段階的にリファクタリング。一度にすべては変えない。

---

## 学習ロードマップ

### Week 1: 理解と識別
- [ ] 各原則の定義を理解
- [ ] 違反例を識別できるようになる
- [ ] 自分のコードでの違反箇所を発見

### Week 2: 小規模リファクタリング
- [ ] 1つのクラスでSRP適用
- [ ] 既存の継承でLSP確認
- [ ] 小さなインターフェースを設計（ISP）

### Week 3: 設計への適用
- [ ] 新機能でOCPを意識
- [ ] DIコンテナの使用（DIP）
- [ ] コードレビューでSOLIDを指摘

### Week 4: 総合演習
- [ ] 既存の小さなモジュールを完全リファクタリング
- [ ] すべての原則を適用
- [ ] テストで品質を担保

---

## 参考資料

### 書籍
- "Clean Architecture" - Robert C. Martin
- "Agile Software Development, Principles, Patterns, and Practices" - Robert C. Martin
- "リファクタリング 既存のコードを安全に改善する" - Martin Fowler

### オンラインリソース
- [SOLID Principles of Object Oriented Design](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Uncle Bob's Blog - Clean Coder](https://blog.cleancoder.com/)
