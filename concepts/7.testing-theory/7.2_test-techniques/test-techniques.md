# テスト技法

> ホワイトボックス/ブラックボックステスト、境界値分析、モック/スタブの実践技法

## 学習目標
- ホワイトボックス/ブラックボックステストの違いと使い分けを理解する
- 境界値分析と等価分割を使ったテストケース設計ができるようになる
- モックとスタブを適切に使い分けられるようになる
- テストカバレッジの意味と限界を理解する

---

## 1. ホワイトボックステスト

### 定義

**ホワイトボックステスト**: 内部構造（コード）を見てテストを設計する

**目的**: コードの全パスを網羅的にテスト

### カバレッジの種類

#### 1.1 ステートメントカバレッジ（行カバレッジ）

すべての行が実行されたか

```python
def is_positive(n):
    if n > 0:
        return True  # Line 3
    return False      # Line 4

# テストケース1: n=5
# → Line 3 実行、Line 4 未実行（50% カバレッジ）

# テストケース2: n=-1
# → Line 4 実行（合計100% カバレッジ）
```

#### 1.2 ブランチカバレッジ（分岐カバレッジ）

すべての条件分岐（True/False）が実行されたか

```python
def calculate_discount(price, is_member, is_holiday):
    discount = 0
    if is_member:           # Branch 1
        discount += 10
    if is_holiday:          # Branch 2
        discount += 5
    return price * (1 - discount / 100)

# 必要なテストケース（2^2 = 4パターン）
# 1. is_member=True, is_holiday=True
# 2. is_member=True, is_holiday=False
# 3. is_member=False, is_holiday=True
# 4. is_member=False, is_holiday=False
```

#### 1.3 条件カバレッジ

各条件式の True/False が実行されたか

```python
def can_access(user, resource):
    # 複合条件
    if user.is_admin or (user.is_member and resource.is_public):
        return True
    return False

# テストケース
# 1. is_admin=True → 最初の条件でTrue
# 2. is_admin=False, is_member=True, is_public=True → 2つ目の条件でTrue
# 3. is_admin=False, is_member=False → False
# 4. is_admin=False, is_member=True, is_public=False → False
```

#### 1.4 パスカバレッジ

すべての実行可能なパスが実行されたか

```python
def process(a, b, c):
    if a > 0:           # Branch A
        do_something()
    if b > 0:           # Branch B
        do_other()
    if c > 0:           # Branch C
        do_more()

# パス数 = 2^3 = 8通り
# 1. a>0, b>0, c>0
# 2. a>0, b>0, c<=0
# 3. a>0, b<=0, c>0
# ... (全8パターン)
```

### カバレッジ測定例

```python
# coverage.py を使用
# pip install coverage

# テスト実行とカバレッジ測定
# coverage run -m pytest test_calculator.py
# coverage report

# 結果例
# Name                 Stmts   Miss  Cover
# ----------------------------------------
# calculator.py           20      2    90%
# test_calculator.py      30      0   100%
# ----------------------------------------
# TOTAL                   50      2    96%

# HTML レポート生成
# coverage html
```

### ホワイトボックステストの実践例

```python
def calculate_grade(score):
    """点数から成績を計算"""
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100")

    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

# ホワイトボックステスト（全パスをカバー）
class TestCalculateGrade:
    def test_invalid_negative_score(self):
        with pytest.raises(ValueError):
            calculate_grade(-1)

    def test_invalid_over_100_score(self):
        with pytest.raises(ValueError):
            calculate_grade(101)

    def test_grade_a(self):
        assert calculate_grade(90) == 'A'
        assert calculate_grade(100) == 'A'

    def test_grade_b(self):
        assert calculate_grade(80) == 'B'
        assert calculate_grade(89) == 'B'

    def test_grade_c(self):
        assert calculate_grade(70) == 'C'

    def test_grade_d(self):
        assert calculate_grade(60) == 'D'

    def test_grade_f(self):
        assert calculate_grade(0) == 'F'
        assert calculate_grade(59) == 'F'
```

---

## 2. ブラックボックステスト

### 定義

**ブラックボックステスト**: 内部実装を見ずに、仕様のみに基づいてテストを設計する

**目的**: 要件が満たされているかを確認

### テスト設計技法

#### 2.1 等価分割（Equivalence Partitioning）

**概念**: 入力を同じ振る舞いをするグループに分割

```python
def validate_age(age):
    """年齢検証: 0-17は未成年、18-64は成人、65+は高齢者"""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age < 18:
        return "minor"
    elif age < 65:
        return "adult"
    else:
        return "senior"

# 等価クラス
# 1. 無効クラス: age < 0
# 2. 未成年: 0 <= age < 18
# 3. 成人: 18 <= age < 65
# 4. 高齢者: age >= 65

class TestValidateAge:
    def test_negative_age(self):
        """無効クラス"""
        with pytest.raises(ValueError):
            validate_age(-1)

    def test_minor(self):
        """未成年クラス - 代表値を選択"""
        assert validate_age(10) == "minor"

    def test_adult(self):
        """成人クラス"""
        assert validate_age(30) == "adult"

    def test_senior(self):
        """高齢者クラス"""
        assert validate_age(70) == "senior"
```

#### 2.2 境界値分析（Boundary Value Analysis）

**概念**: 境界付近でバグが発生しやすい

**テスト値の選択**:
- 境界値
- 境界値 - 1
- 境界値 + 1

```python
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age < 18:
        return "minor"
    elif age < 65:
        return "adult"
    else:
        return "senior"

# 境界値
# - 0 (最小値)
# - 18 (未成年/成人の境界)
# - 65 (成人/高齢者の境界)

class TestValidateAgeBoundary:
    # 最小値の境界
    def test_age_negative_boundary(self):
        with pytest.raises(ValueError):
            validate_age(-1)

    def test_age_zero(self):
        assert validate_age(0) == "minor"

    def test_age_one(self):
        assert validate_age(1) == "minor"

    # 18歳の境界
    def test_age_17(self):
        assert validate_age(17) == "minor"

    def test_age_18(self):
        assert validate_age(18) == "adult"

    def test_age_19(self):
        assert validate_age(19) == "adult"

    # 65歳の境界
    def test_age_64(self):
        assert validate_age(64) == "adult"

    def test_age_65(self):
        assert validate_age(65) == "senior"

    def test_age_66(self):
        assert validate_age(66) == "senior"
```

#### 2.3 デシジョンテーブル（決定表）

**概念**: 複数の条件の組み合わせを表形式で整理

```python
def calculate_shipping(weight, is_member, destination):
    """
    配送料計算
    - weight < 5kg: 500円
    - weight >= 5kg: 1000円
    - 会員: 200円割引
    - 国内: 追加料金なし
    - 海外: 追加2000円
    """
    if weight < 5:
        cost = 500
    else:
        cost = 1000

    if is_member:
        cost -= 200

    if destination == 'overseas':
        cost += 2000

    return max(cost, 0)  # 負の値を防ぐ

# デシジョンテーブル
# | weight<5 | is_member | overseas | Expected |
# |----------|-----------|----------|----------|
# | T        | T         | F        | 300      |
# | T        | T         | T        | 2300     |
# | T        | F         | F        | 500      |
# | T        | F         | T        | 2500     |
# | F        | T         | F        | 800      |
# | F        | T         | T        | 2800     |
# | F        | F         | F        | 1000     |
# | F        | F         | T        | 3000     |

import pytest

@pytest.mark.parametrize("weight,is_member,destination,expected", [
    (3, True, 'domestic', 300),
    (3, True, 'overseas', 2300),
    (3, False, 'domestic', 500),
    (3, False, 'overseas', 2500),
    (7, True, 'domestic', 800),
    (7, True, 'overseas', 2800),
    (7, False, 'domestic', 1000),
    (7, False, 'overseas', 3000),
])
def test_calculate_shipping(weight, is_member, destination, expected):
    assert calculate_shipping(weight, is_member, destination) == expected
```

#### 2.4 状態遷移テスト

**概念**: システムの状態遷移をテスト

```python
class VendingMachine:
    def __init__(self):
        self.state = 'idle'
        self.balance = 0

    def insert_coin(self, amount):
        if self.state == 'idle':
            self.balance += amount
            self.state = 'has_money'
        elif self.state == 'has_money':
            self.balance += amount

    def select_product(self, price):
        if self.state == 'has_money':
            if self.balance >= price:
                self.balance -= price
                self.state = 'dispensing'
                return True
            else:
                return False
        return False

    def dispense(self):
        if self.state == 'dispensing':
            self.state = 'idle' if self.balance == 0 else 'has_money'
            return True
        return False

    def return_coins(self):
        if self.state in ['has_money', 'dispensing']:
            returned = self.balance
            self.balance = 0
            self.state = 'idle'
            return returned
        return 0

# 状態遷移テスト
class TestVendingMachine:
    def test_initial_state(self):
        vm = VendingMachine()
        assert vm.state == 'idle'
        assert vm.balance == 0

    def test_idle_to_has_money(self):
        vm = VendingMachine()
        vm.insert_coin(100)
        assert vm.state == 'has_money'
        assert vm.balance == 100

    def test_has_money_to_dispensing(self):
        vm = VendingMachine()
        vm.insert_coin(100)
        success = vm.select_product(80)
        assert success
        assert vm.state == 'dispensing'
        assert vm.balance == 20

    def test_dispensing_to_idle(self):
        vm = VendingMachine()
        vm.insert_coin(100)
        vm.select_product(100)
        vm.dispense()
        assert vm.state == 'idle'
        assert vm.balance == 0

    def test_return_coins(self):
        vm = VendingMachine()
        vm.insert_coin(100)
        returned = vm.return_coins()
        assert returned == 100
        assert vm.state == 'idle'
        assert vm.balance == 0
```

---

## 3. モックとスタブ

### 定義

- **スタブ（Stub）**: 決まった値を返すダミーオブジェクト
- **モック（Mock）**: 呼び出しを検証できるテストダブル
- **フェイク（Fake）**: 簡易的な動作実装
- **スパイ（Spy）**: 実オブジェクトの呼び出しを記録

### モックの使い分け

```python
from unittest.mock import Mock, MagicMock, patch
import requests

# 対象コード
class WeatherService:
    def get_temperature(self, city):
        response = requests.get(f'https://api.weather.com/{city}')
        return response.json()['temperature']

class WeatherApp:
    def __init__(self, weather_service):
        self.weather_service = weather_service

    def display_temperature(self, city):
        temp = self.weather_service.get_temperature(city)
        return f"The temperature in {city} is {temp}°C"
```

### 3.1 スタブ（Stub）

決まった値を返すだけ

```python
class TestWeatherAppWithStub:
    def test_display_temperature(self):
        # スタブを作成
        stub_service = Mock()
        stub_service.get_temperature.return_value = 25

        app = WeatherApp(stub_service)
        result = app.display_temperature('Tokyo')

        assert result == "The temperature in Tokyo is 25°C"
        # 呼び出しは検証しない（スタブの特徴）
```

### 3.2 モック（Mock）

呼び出しを検証する

```python
class TestWeatherAppWithMock:
    def test_display_temperature(self):
        # モックを作成
        mock_service = Mock()
        mock_service.get_temperature.return_value = 25

        app = WeatherApp(mock_service)
        result = app.display_temperature('Tokyo')

        # 戻り値の確認
        assert result == "The temperature in Tokyo is 25°C"

        # 呼び出しの検証（モックの特徴）
        mock_service.get_temperature.assert_called_once_with('Tokyo')
```

### 3.3 パッチ（Patch）

既存のオブジェクトを置き換える

```python
class TestWeatherServiceWithPatch:
    @patch('requests.get')
    def test_get_temperature(self, mock_get):
        # requests.get をモック化
        mock_response = Mock()
        mock_response.json.return_value = {'temperature': 30}
        mock_get.return_value = mock_response

        service = WeatherService()
        temp = service.get_temperature('Osaka')

        assert temp == 30
        mock_get.assert_called_once_with('https://api.weather.com/Osaka')
```

### 3.4 スパイ（Spy）

実オブジェクトの呼び出しを記録

```python
from unittest.mock import spy

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        result = 0
        for _ in range(b):
            result = self.add(result, a)  # add を内部で呼び出し
        return result

class TestCalculatorWithSpy:
    def test_multiply_calls_add(self):
        calc = Calculator()

        # add メソッドをスパイ化
        with patch.object(calc, 'add', wraps=calc.add) as spy_add:
            result = calc.multiply(3, 4)

            # 結果の確認
            assert result == 12

            # add が4回呼ばれたことを確認
            assert spy_add.call_count == 4
```

### 3.5 フェイク（Fake）

簡易的な実装

```python
# 実際のデータベース
class Database:
    def save(self, key, value):
        # 実際のDB操作
        pass

    def get(self, key):
        # 実際のDB操作
        pass

# フェイク（インメモリDB）
class FakeDatabase:
    def __init__(self):
        self.storage = {}

    def save(self, key, value):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key)

# テストで使用
class TestUserRepository:
    def test_save_and_retrieve_user(self):
        fake_db = FakeDatabase()
        repo = UserRepository(fake_db)

        user = User(name='Alice')
        repo.save(user)

        retrieved = repo.get(user.id)
        assert retrieved.name == 'Alice'
```

### モックのベストプラクティス

```python
# ❌ 悪い例：内部実装の詳細をモック
def test_bad_mock():
    mock_list = Mock()
    mock_list.append.return_value = None

    # 内部実装に依存しすぎ
    some_function(mock_list)

    mock_list.append.assert_called_with(42)
    # リファクタリングでappendを使わなくなったら壊れる

# ✅ 良い例：振る舞いをテスト
def test_good():
    result = some_function([])
    assert 42 in result  # 結果を検証
```

---

## 4. テストカバレッジの意味と限界

### カバレッジの測定

```python
# coverage.py の使い方
# pip install coverage pytest-cov

# 実行
# pytest --cov=myapp --cov-report=html

# .coveragerc 設定ファイル
# [run]
# source = myapp
# omit =
#     */tests/*
#     */migrations/*
#     */venv/*
#
# [report]
# exclude_lines =
#     pragma: no cover
#     def __repr__
#     raise AssertionError
#     raise NotImplementedError
#     if __name__ == .__main__.:
```

### カバレッジ100%でも見逃すバグ

```python
def divide(a, b):
    return a / b

# テスト（100% カバレッジ）
def test_divide():
    assert divide(10, 2) == 5

# しかし、ゼロ除算は見逃している！
# divide(10, 0)  # ZeroDivisionError
```

### 意味のあるカバレッジ

```python
def calculate_discount(price, is_member):
    # カバレッジは100%でも...
    discount = 0.1 if is_member else 0.0
    return price * (1 - discount)

# テスト1（カバレッジ100%だが不十分）
def test_calculate_discount_member():
    result = calculate_discount(100, True)
    assert result == 90

# テスト2（境界値も確認）
def test_calculate_discount_non_member():
    result = calculate_discount(100, False)
    assert result == 100

# テスト3（さらに境界値）
def test_calculate_discount_zero_price():
    assert calculate_discount(0, True) == 0
    assert calculate_discount(0, False) == 0
```

### カバレッジの目標値

| プロジェクトタイプ | 推奨カバレッジ |
|-------------------|---------------|
| ライブラリ | 90-100% |
| ビジネスロジック | 80-90% |
| UI/フロントエンド | 60-80% |
| プロトタイプ | 50-60% |

### カバレッジより重要なこと

1. **重要な機能を確実にテスト**
2. **境界値・エラーケースを網羅**
3. **テストの意図が明確**
4. **リファクタリングしやすいテスト**

---

## 5. テストケース設計の実践

### 包括的なテストケース設計

```python
def process_order(order_items, coupon_code=None, user=None):
    """
    注文処理
    - order_items: 注文アイテムリスト
    - coupon_code: クーポンコード（オプション）
    - user: ユーザー（会員の場合）
    """
    if not order_items:
        raise ValueError("Order must contain at least one item")

    # 小計計算
    subtotal = sum(item.price * item.quantity for item in order_items)

    # クーポン適用
    discount = 0
    if coupon_code:
        coupon = get_coupon(coupon_code)
        if coupon and coupon.is_valid():
            discount = subtotal * coupon.discount_rate

    # 会員割引
    if user and user.is_member:
        discount += subtotal * 0.05

    total = subtotal - discount

    return {
        'subtotal': subtotal,
        'discount': discount,
        'total': total
    }

# 包括的なテストケース
class TestProcessOrder:
    # 正常系 - 等価分割
    def test_order_without_coupon_or_membership(self):
        """通常の注文"""
        items = [OrderItem(price=100, quantity=2)]
        result = process_order(items)
        assert result['total'] == 200

    def test_order_with_valid_coupon(self):
        """有効なクーポン付き注文"""
        items = [OrderItem(price=100, quantity=2)]
        result = process_order(items, coupon_code='SAVE10')
        assert result['discount'] == 20
        assert result['total'] == 180

    def test_order_with_membership(self):
        """会員の注文"""
        items = [OrderItem(price=100, quantity=2)]
        user = User(is_member=True)
        result = process_order(items, user=user)
        assert result['discount'] == 10
        assert result['total'] == 190

    def test_order_with_coupon_and_membership(self):
        """クーポン + 会員割引"""
        items = [OrderItem(price=100, quantity=2)]
        user = User(is_member=True)
        result = process_order(items, coupon_code='SAVE10', user=user)
        assert result['discount'] == 30  # 20 + 10
        assert result['total'] == 170

    # 境界値
    def test_order_with_one_item(self):
        """最小数のアイテム"""
        items = [OrderItem(price=100, quantity=1)]
        result = process_order(items)
        assert result['total'] == 100

    def test_order_with_zero_quantity(self):
        """数量0のアイテム"""
        items = [OrderItem(price=100, quantity=0)]
        result = process_order(items)
        assert result['total'] == 0

    # 異常系
    def test_order_with_empty_items(self):
        """空の注文"""
        with pytest.raises(ValueError, match="at least one item"):
            process_order([])

    def test_order_with_invalid_coupon(self):
        """無効なクーポン"""
        items = [OrderItem(price=100, quantity=2)]
        result = process_order(items, coupon_code='INVALID')
        assert result['discount'] == 0

    def test_order_with_expired_coupon(self):
        """期限切れクーポン"""
        items = [OrderItem(price=100, quantity=2)]
        # モックで期限切れクーポンを返す
        with patch('get_coupon') as mock_get_coupon:
            mock_coupon = Mock()
            mock_coupon.is_valid.return_value = False
            mock_get_coupon.return_value = mock_coupon

            result = process_order(items, coupon_code='EXPIRED')
            assert result['discount'] == 0
```

---

## トラブルシューティング

### よくある質問

**Q: どこまでテストを書けばいい？**
A: クリティカルなパス + 境界値 + エラーケース。100%を目指さない。

**Q: モックを使いすぎると脆くなる？**
A: はい。外部依存のみモック化し、内部実装はモックしない。

**Q: プライベートメソッドはテストすべき？**
A: 通常は不要。パブリックメソッド経由で間接的にテスト。

---

## 学習ロードマップ

### Week 1: テスト設計技法
- [ ] 等価分割と境界値分析を学習
- [ ] 既存機能のテストケース設計
- [ ] デシジョンテーブル作成

### Week 2: カバレッジ
- [ ] カバレッジツールのセットアップ
- [ ] 現状のカバレッジ測定
- [ ] 未カバー部分の特定とテスト追加

### Week 3: モックとスタブ
- [ ] モックライブラリの学習
- [ ] 外部依存のモック化
- [ ] スタブとモックの使い分け

### Week 4: 総合演習
- [ ] 複雑な機能の包括的テスト設計
- [ ] カバレッジ80%以上達成
- [ ] テストレビュー実施

---

## 参考資料

### 書籍
- "ソフトウェアテスト技法" - Boris Beizer
- "テスト駆動開発" - Kent Beck
- "xUnit Test Patterns" - Gerard Meszaros

### ツール
- Coverage.py (Python カバレッジ)
- Istanbul (JavaScript カバレッジ)
- pytest-mock (Python モック)
- Jest (JavaScript テスト+モック)

### 標準
- ISO/IEC/IEEE 29119 (ソフトウェアテスト標準)
- ISTQB (テスト技術者資格)
