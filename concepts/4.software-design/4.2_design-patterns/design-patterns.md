# デザインパターン

> GoFの23パターンを中心とした再利用可能な設計パターン

## 学習目標
- 主要なデザインパターンの意図と構造を理解する
- 各パターンの適用場面を判断できるようになる
- パターンを組み合わせた設計ができるようになる
- アンチパターンを回避できるようになる

---

## デザインパターンとは

### 定義
**繰り返し現れる設計問題に対する、実証済みの解決策**

- 設計の共通言語
- 車輪の再発明を避ける
- コミュニケーションツール

### パターンの構成要素
1. **名前**: パターンを識別する用語
2. **問題**: どんな状況で使うか
3. **解決策**: 設計の構造
4. **結果**: トレードオフと結果

---

## 生成パターン（Creational Patterns）

オブジェクトの生成に関するパターン

### 1. Factory Pattern（ファクトリパターン）

**目的**: オブジェクト生成のロジックをカプセル化

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    """生成ロジックを集約"""
    @staticmethod
    def create_animal(animal_type: str) -> Animal:
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# 使用例
factory = AnimalFactory()
animal = factory.create_animal("dog")
print(animal.speak())  # "Woof!"
```

**メリット**:
- 生成ロジックの集約
- クライアントコードと具象クラスの分離

**適用場面**:
- 生成するオブジェクトの型が実行時に決まる
- 生成ロジックが複雑

---

### 2. Abstract Factory Pattern（抽象ファクトリパターン）

**目的**: 関連するオブジェクト群を一貫して生成

```python
from abc import ABC, abstractmethod

# 抽象製品
class Button(ABC):
    @abstractmethod
    def render(self):
        pass

class Checkbox(ABC):
    @abstractmethod
    def render(self):
        pass

# 具象製品 - Windows
class WindowsButton(Button):
    def render(self):
        return "Rendering Windows Button"

class WindowsCheckbox(Checkbox):
    def render(self):
        return "Rendering Windows Checkbox"

# 具象製品 - macOS
class MacButton(Button):
    def render(self):
        return "Rendering Mac Button"

class MacCheckbox(Checkbox):
    def render(self):
        return "Rendering Mac Checkbox"

# 抽象ファクトリ
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass

# 具象ファクトリ
class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()

    def create_checkbox(self):
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self):
        return MacButton()

    def create_checkbox(self):
        return MacCheckbox()

# 使用例
def render_ui(factory: GUIFactory):
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    print(button.render())
    print(checkbox.render())

# OSに応じてファクトリを切り替え
factory = WindowsFactory()
render_ui(factory)
```

**適用場面**:
- 関連するオブジェクト群を一貫して生成したい
- プラットフォーム固有のコンポーネント

---

### 3. Singleton Pattern（シングルトンパターン）

**目的**: クラスのインスタンスが1つだけであることを保証

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# 使用例
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True

# スレッドセーフなシングルトン
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**注意点**:
- グローバル状態を作るため、テストが難しくなる
- マルチスレッド環境では注意が必要
- 依存性注入で代替可能な場合が多い

**適用場面**:
- ログ、設定、キャッシュなど
- リソースの共有が必要な場合

---

### 4. Builder Pattern（ビルダーパターン）

**目的**: 複雑なオブジェクトの構築プロセスを分離

```python
class Pizza:
    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.mushrooms = False

    def __str__(self):
        return f"Pizza(size={self.size}, cheese={self.cheese}, " \
               f"pepperoni={self.pepperoni}, mushrooms={self.mushrooms})"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()

    def set_size(self, size):
        self.pizza.size = size
        return self  # メソッドチェーン

    def add_cheese(self):
        self.pizza.cheese = True
        return self

    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self

    def add_mushrooms(self):
        self.pizza.mushrooms = True
        return self

    def build(self):
        return self.pizza

# 使用例
pizza = (PizzaBuilder()
         .set_size("Large")
         .add_cheese()
         .add_pepperoni()
         .build())

print(pizza)
```

**適用場面**:
- コンストラクタの引数が多い
- オプショナルなパラメータが多い
- 構築プロセスが複雑

---

### 5. Prototype Pattern（プロトタイプパターン）

**目的**: 既存オブジェクトのクローンで新しいオブジェクトを作成

```python
import copy

class Prototype:
    def clone(self):
        return copy.deepcopy(self)

class Document(Prototype):
    def __init__(self, title, content, formatting):
        self.title = title
        self.content = content
        self.formatting = formatting

# 使用例
original = Document("Original", "Content", {"font": "Arial", "size": 12})
cloned = original.clone()
cloned.title = "Copy"

print(original.title)  # "Original"
print(cloned.title)    # "Copy"
```

**適用場面**:
- オブジェクトの生成コストが高い
- 似たオブジェクトを大量に作成

---

## 構造パターン（Structural Patterns）

クラスやオブジェクトの構造に関するパターン

### 6. Adapter Pattern（アダプタパターン）

**目的**: 互換性のないインターフェースを変換

```python
# 既存のクラス（変更できない）
class LegacyPrinter:
    def print_old(self, text):
        return f"[OLD] {text}"

# 新しいインターフェース
class Printer:
    def print(self, text):
        pass

# アダプタ
class PrinterAdapter(Printer):
    def __init__(self, legacy_printer):
        self.legacy_printer = legacy_printer

    def print(self, text):
        return self.legacy_printer.print_old(text)

# 使用例
legacy = LegacyPrinter()
adapter = PrinterAdapter(legacy)
print(adapter.print("Hello"))  # "[OLD] Hello"
```

**適用場面**:
- 既存のクラスを変更できない
- サードパーティライブラリの統合

---

### 7. Decorator Pattern（デコレータパターン）

**目的**: オブジェクトに動的に機能を追加

```python
from abc import ABC, abstractmethod

class Coffee(ABC):
    @abstractmethod
    def cost(self):
        pass

    @abstractmethod
    def description(self):
        pass

class SimpleCoffee(Coffee):
    def cost(self):
        return 5

    def description(self):
        return "Simple Coffee"

# デコレータ基底クラス
class CoffeeDecorator(Coffee):
    def __init__(self, coffee):
        self._coffee = coffee

class MilkDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 2

    def description(self):
        return self._coffee.description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 1

    def description(self):
        return self._coffee.description() + ", Sugar"

# 使用例
coffee = SimpleCoffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)

print(coffee.description())  # "Simple Coffee, Milk, Sugar"
print(coffee.cost())  # 8
```

**Pythonのデコレータ構文**:
```python
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_decorator
def say_hello():
    print("Hello!")

say_hello()
```

**適用場面**:
- 機能の動的な追加・削除
- 継承より柔軟な拡張

---

### 8. Facade Pattern（ファサードパターン）

**目的**: 複雑なサブシステムへの統一インターフェース

```python
# 複雑なサブシステム
class CPU:
    def freeze(self):
        print("CPU: Freezing")

    def execute(self):
        print("CPU: Executing")

class Memory:
    def load(self, address, data):
        print(f"Memory: Loading {data} at {address}")

class HardDrive:
    def read(self, sector, size):
        return f"Data from sector {sector}"

# ファサード
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()

    def start(self):
        """複雑な起動処理を隠蔽"""
        self.cpu.freeze()
        data = self.hard_drive.read(0, 1024)
        self.memory.load(0, data)
        self.cpu.execute()

# 使用例
computer = ComputerFacade()
computer.start()  # 簡単！
```

**適用場面**:
- 複雑なライブラリの簡略化
- レイヤー間のインターフェース

---

### 9. Proxy Pattern（プロキシパターン）

**目的**: 別オブジェクトへのアクセスを制御

```python
from abc import ABC, abstractmethod

class Image(ABC):
    @abstractmethod
    def display(self):
        pass

class RealImage(Image):
    def __init__(self, filename):
        self.filename = filename
        self._load_from_disk()

    def _load_from_disk(self):
        print(f"Loading {self.filename}")

    def display(self):
        print(f"Displaying {self.filename}")

class ProxyImage(Image):
    """遅延読み込みプロキシ"""
    def __init__(self, filename):
        self.filename = filename
        self._real_image = None

    def display(self):
        if self._real_image is None:
            self._real_image = RealImage(self.filename)
        self._real_image.display()

# 使用例
image = ProxyImage("large_image.jpg")
# ここではまだ読み込まれない
image.display()  # ここで初めて読み込まれる
```

**プロキシの種類**:
- **仮想プロキシ**: 遅延初期化
- **保護プロキシ**: アクセス制御
- **リモートプロキシ**: 遠隔オブジェクトの代理

---

## 振る舞いパターン（Behavioral Patterns）

オブジェクト間の責任分担と協調に関するパターン

### 10. Strategy Pattern（ストラテジパターン）

**目的**: アルゴリズムのファミリーを定義し、交換可能にする

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number):
        self.card_number = card_number

    def pay(self, amount):
        return f"Paid {amount} using Credit Card {self.card_number}"

class PayPalPayment(PaymentStrategy):
    def __init__(self, email):
        self.email = email

    def pay(self, amount):
        return f"Paid {amount} using PayPal {self.email}"

class BitcoinPayment(PaymentStrategy):
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address

    def pay(self, amount):
        return f"Paid {amount} using Bitcoin {self.wallet_address}"

class ShoppingCart:
    def __init__(self, payment_strategy: PaymentStrategy):
        self.payment_strategy = payment_strategy

    def checkout(self, amount):
        return self.payment_strategy.pay(amount)

# 使用例
cart = ShoppingCart(CreditCardPayment("1234-5678"))
print(cart.checkout(100))

# 支払い方法を変更
cart.payment_strategy = PayPalPayment("user@example.com")
print(cart.checkout(200))
```

**適用場面**:
- 複数のアルゴリズムから選択
- if-elseの羅列を排除

---

### 11. Observer Pattern（オブザーバパターン）

**目的**: 1対多の依存関係で、状態変化を自動通知

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self._observers = []
        self._state = None

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def set_state(self, state):
        self._state = state
        self.notify()

    def get_state(self):
        return self._state

class ConcreteObserver(Observer):
    def __init__(self, name):
        self.name = name

    def update(self, subject):
        print(f"{self.name} received update: {subject.get_state()}")

# 使用例
subject = Subject()
observer1 = ConcreteObserver("Observer 1")
observer2 = ConcreteObserver("Observer 2")

subject.attach(observer1)
subject.attach(observer2)

subject.set_state("New State")
# Output:
# Observer 1 received update: New State
# Observer 2 received update: New State
```

**適用場面**:
- イベント駆動システム
- UI更新（MVCのモデル-ビュー）

---

### 12. Command Pattern（コマンドパターン）

**目的**: リクエストをオブジェクトとしてカプセル化

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class Light:
    def on(self):
        print("Light is ON")

    def off(self):
        print("Light is OFF")

class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.on()

    def undo(self):
        self.light.off()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.off()

    def undo(self):
        self.light.on()

class RemoteControl:
    def __init__(self):
        self.history = []

    def execute_command(self, command: Command):
        command.execute()
        self.history.append(command)

    def undo_last(self):
        if self.history:
            command = self.history.pop()
            command.undo()

# 使用例
light = Light()
on_command = LightOnCommand(light)
off_command = LightOffCommand(light)

remote = RemoteControl()
remote.execute_command(on_command)   # Light is ON
remote.execute_command(off_command)  # Light is OFF
remote.undo_last()                   # Light is ON (undo)
```

**適用場面**:
- undo/redo機能
- トランザクション
- マクロコマンド

---

### 13. Template Method Pattern（テンプレートメソッドパターン）

**目的**: アルゴリズムの骨格を定義し、ステップをサブクラスで実装

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self):
        """テンプレートメソッド"""
        self.read_data()
        self.process_data()
        self.save_data()

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

class CSVProcessor(DataProcessor):
    def read_data(self):
        print("Reading CSV file")

    def process_data(self):
        print("Processing CSV data")

    def save_data(self):
        print("Saving to database")

class JSONProcessor(DataProcessor):
    def read_data(self):
        print("Reading JSON file")

    def process_data(self):
        print("Processing JSON data")

    def save_data(self):
        print("Saving to cache")

# 使用例
csv_processor = CSVProcessor()
csv_processor.process()
```

**適用場面**:
- 共通のアルゴリズム構造
- フレームワークのフック

---

## パターンの組み合わせ

### 実践例: Webアプリケーション

```python
# Singleton + Factory
class DatabaseConnectionPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self, db_type):
        # Factory Pattern
        if db_type == "mysql":
            return MySQLConnection()
        elif db_type == "postgres":
            return PostgresConnection()

# Strategy + Decorator
class AuthenticationService:
    def __init__(self, strategy: AuthStrategy):
        self.strategy = strategy  # Strategy

    @rate_limit_decorator  # Decorator
    @log_decorator
    def authenticate(self, credentials):
        return self.strategy.authenticate(credentials)
```

---

## アンチパターン

避けるべき悪い設計パターン

### 1. God Object（神オブジェクト）
**問題**: 1つのクラスが多すぎる責任を持つ
**解決**: SRPに従って分割

### 2. Lava Flow（溶岩流）
**問題**: 理由不明のコードが残り続ける
**解決**: 定期的なリファクタリング

### 3. Golden Hammer（黄金のハンマー）
**問題**: 特定のパターンを過剰に適用
**解決**: 問題に応じたパターン選択

---

## 学習ロードマップ

### Week 1-2: 生成パターン
- [ ] Factory, Singleton, Builderを実装
- [ ] 各パターンの使い分けを理解

### Week 3-4: 構造パターン
- [ ] Adapter, Decorator, Facadeを実装
- [ ] 既存コードへの適用を検討

### Week 5-6: 振る舞いパターン
- [ ] Strategy, Observer, Commandを実装
- [ ] イベント駆動システムを構築

### Week 7-8: 統合と実践
- [ ] 複数パターンの組み合わせ
- [ ] 実プロジェクトへの適用
- [ ] コードレビューでパターンを識別

---

## 参考資料

### 書籍
- "Design Patterns: Elements of Reusable Object-Oriented Software" - GoF
- "Head First Design Patterns" - Freeman & Freeman
- "リファクタリング" - Martin Fowler

### オンラインリソース
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [SourceMaking - Design Patterns](https://sourcemaking.com/design_patterns)
