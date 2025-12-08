# テスト戦略

> テストピラミッドとテスト駆動開発の理論と実践

## 学習目標
- テストピラミッドの概念と各層の役割を理解する
- 単体テスト、統合テスト、E2Eテストの違いと使い分けを習得する
- TDD/BDDの手法を実践できるようになる
- 効果的なテスト戦略を設計できるようになる

---

## 1. テストピラミッド

### 概念

```
        /\
       /  \      E2E Tests (UI Tests)
      /____\     少数・遅い・高コスト
     /      \
    /        \   Integration Tests
   /__________\  中程度・中速・中コスト
  /            \
 /   Unit Tests \
/________________\ 多数・高速・低コスト
```

### 各層の役割

| テスト種別 | 範囲 | 速度 | コスト | 割合の目安 |
|----------|------|------|--------|-----------|
| Unit (単体) | 1つの関数/クラス | 高速 (ms) | 低 | 70% |
| Integration (統合) | 複数コンポーネント | 中速 (s) | 中 | 20% |
| E2E (エンドツーエンド) | システム全体 | 低速 (m) | 高 | 10% |

### なぜピラミッド型か

1. **高速フィードバック**: 単体テストが多いほど、早く問題を発見
2. **メンテナンス性**: 単体テストは変更に強い
3. **コストバランス**: E2Eは重要な機能に限定
4. **デバッグ容易性**: 小さいテストほど原因特定が簡単

### アンチパターン: アイスクリームコーン

```
      ____
     /    \
    /      \    E2E Tests が多すぎる
   /        \   → 遅い、脆い、高コスト
  /          \
 /            \
/______________\  Unit Tests が少ない
```

---

## 2. 単体テスト（Unit Test）

### 定義と特徴

**定義**: 1つの関数やクラスを独立してテストする

**特徴**:
- 外部依存（DB、API、ファイル）なし
- 高速実行（数ミリ秒）
- 独立性（他のテストに影響されない）

### 例: Python (pytest)

```python
# 対象コード: calculator.py
class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# テストコード: test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    def setup_method(self):
        """各テストの前に実行"""
        self.calc = Calculator()

    def test_add_positive_numbers(self):
        result = self.calc.add(2, 3)
        assert result == 5

    def test_add_negative_numbers(self):
        result = self.calc.add(-2, -3)
        assert result == -5

    def test_divide_normal(self):
        result = self.calc.divide(10, 2)
        assert result == 5.0

    def test_divide_by_zero_raises_error(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
```

### 例: JavaScript (Jest)

```javascript
// 対象コード: user.js
class User {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    isAdult() {
        return this.age >= 18;
    }

    greet() {
        return `Hello, I'm ${this.name}`;
    }
}

// テストコード: user.test.js
describe('User', () => {
    let user;

    beforeEach(() => {
        user = new User('Alice', 25);
    });

    test('should return correct greeting', () => {
        expect(user.greet()).toBe("Hello, I'm Alice");
    });

    test('should identify adult correctly', () => {
        expect(user.isAdult()).toBe(true);
    });

    test('should identify minor correctly', () => {
        const minor = new User('Bob', 15);
        expect(minor.isAdult()).toBe(false);
    });
});
```

### 良い単体テストの条件（F.I.R.S.T原則）

- **Fast**: 高速（数ミリ秒）
- **Independent**: 独立（他のテストに依存しない）
- **Repeatable**: 再現可能（常に同じ結果）
- **Self-Validating**: 自己検証（合否が明確）
- **Timely**: タイムリー（実装と同時に書く）

---

## 3. 統合テスト（Integration Test）

### 定義と特徴

**定義**: 複数のコンポーネントが連携して正しく動作するかをテスト

**テスト対象**:
- データベース接続
- 外部API呼び出し
- ファイルI/O
- モジュール間の連携

### 例: データベース統合テスト

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base
from repository import UserRepository

class TestUserRepository:
    @pytest.fixture(scope='function')
    def db_session(self):
        """テスト用DBセッション"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_create_and_retrieve_user(self, db_session):
        repo = UserRepository(db_session)

        # ユーザー作成
        user = repo.create_user(name='Alice', email='alice@example.com')
        assert user.id is not None

        # ユーザー取得
        retrieved = repo.get_user_by_id(user.id)
        assert retrieved.name == 'Alice'
        assert retrieved.email == 'alice@example.com'

    def test_update_user(self, db_session):
        repo = UserRepository(db_session)
        user = repo.create_user(name='Bob', email='bob@example.com')

        # ユーザー更新
        repo.update_user(user.id, name='Robert')

        # 確認
        updated = repo.get_user_by_id(user.id)
        assert updated.name == 'Robert'
        assert updated.email == 'bob@example.com'
```

### 例: API統合テスト

```python
import pytest
from flask import Flask
from api import create_app

class TestUserAPI:
    @pytest.fixture
    def client(self):
        app = create_app('testing')
        with app.test_client() as client:
            yield client

    def test_create_user_endpoint(self, client):
        response = client.post('/api/users', json={
            'name': 'Alice',
            'email': 'alice@example.com'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Alice'
        assert 'id' in data

    def test_get_user_endpoint(self, client):
        # ユーザー作成
        create_response = client.post('/api/users', json={
            'name': 'Bob',
            'email': 'bob@example.com'
        })
        user_id = create_response.get_json()['id']

        # ユーザー取得
        get_response = client.get(f'/api/users/{user_id}')
        assert get_response.status_code == 200
        data = get_response.get_json()
        assert data['name'] == 'Bob'
```

### 統合テストのベストプラクティス

1. **テストデータの分離**: 本番データに影響させない
2. **クリーンアップ**: テスト後の状態をリセット
3. **トランザクション管理**: ロールバックで元の状態に戻す
4. **モックの最小化**: 実際の統合をテストする

---

## 4. E2Eテスト（End-to-End Test）

### 定義と特徴

**定義**: ユーザー視点でシステム全体の動作をテスト

**特徴**:
- ブラウザ操作を自動化
- 実際の環境に近い状態でテスト
- 最も遅く、最も脆い

### 例: Selenium (Python)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

class TestLoginFlow:
    @pytest.fixture
    def browser(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_successful_login(self, browser):
        # ログインページにアクセス
        browser.get('http://localhost:5000/login')

        # フォーム入力
        email_input = browser.find_element(By.ID, 'email')
        password_input = browser.find_element(By.ID, 'password')

        email_input.send_keys('user@example.com')
        password_input.send_keys('password123')

        # ログインボタンクリック
        login_button = browser.find_element(By.ID, 'login-button')
        login_button.click()

        # ダッシュボードにリダイレクトされることを確認
        WebDriverWait(browser, 10).until(
            EC.url_contains('/dashboard')
        )

        # ウェルカムメッセージを確認
        welcome_msg = browser.find_element(By.CLASS_NAME, 'welcome-message')
        assert 'Welcome' in welcome_msg.text

    def test_login_with_invalid_credentials(self, browser):
        browser.get('http://localhost:5000/login')

        email_input = browser.find_element(By.ID, 'email')
        password_input = browser.find_element(By.ID, 'password')

        email_input.send_keys('invalid@example.com')
        password_input.send_keys('wrongpassword')

        login_button = browser.find_element(By.ID, 'login-button')
        login_button.click()

        # エラーメッセージを確認
        error_msg = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        assert 'Invalid credentials' in error_msg.text
```

### 例: Playwright (JavaScript)

```javascript
const { test, expect } = require('@playwright/test');

test.describe('Shopping Cart', () => {
    test('should add item to cart and checkout', async ({ page }) => {
        // 商品ページにアクセス
        await page.goto('http://localhost:3000/products');

        // 商品を選択
        await page.click('button[data-product-id="123"]');

        // カートに追加確認
        await expect(page.locator('.cart-count')).toHaveText('1');

        // カートページに移動
        await page.click('a[href="/cart"]');

        // 商品がカートにあることを確認
        await expect(page.locator('.cart-item')).toBeVisible();

        // チェックアウト
        await page.click('button:has-text("Checkout")');

        // 配送情報入力
        await page.fill('#shipping-name', 'John Doe');
        await page.fill('#shipping-address', '123 Main St');

        // 注文確定
        await page.click('button:has-text("Place Order")');

        // 成功メッセージ確認
        await expect(page.locator('.success-message')).toContainText('Order placed successfully');
    });
});
```

### E2Eテストのベストプラクティス

1. **クリティカルパスに集中**: 重要なユーザーフローのみ
2. **ページオブジェクトパターン**: UI要素をカプセル化
3. **待機戦略**: 明示的な待機を使用
4. **スクリーンショット**: 失敗時のデバッグ用
5. **並列実行**: テスト時間の短縮

---

## 5. テスト駆動開発（TDD）

### Red-Green-Refactor サイクル

```
1. Red: 失敗するテストを書く
   ↓
2. Green: テストを通す最小限のコード
   ↓
3. Refactor: コードを改善
   ↓
   繰り返し
```

### 実践例

```python
# Step 1: Red - 失敗するテストを書く
def test_fizzbuzz_returns_fizz_for_3():
    assert fizzbuzz(3) == "Fizz"

# 実行 → エラー（fizzbuzz関数が存在しない）

# Step 2: Green - 最小限の実装
def fizzbuzz(n):
    if n == 3:
        return "Fizz"

# 実行 → パス

# Step 1: Red - 次のテストを追加
def test_fizzbuzz_returns_buzz_for_5():
    assert fizzbuzz(5) == "Buzz"

# 実行 → 失敗

# Step 2: Green - 実装を拡張
def fizzbuzz(n):
    if n == 3:
        return "Fizz"
    if n == 5:
        return "Buzz"

# Step 1: Red - さらにテスト追加
def test_fizzbuzz_returns_fizz_for_multiples_of_3():
    assert fizzbuzz(6) == "Fizz"
    assert fizzbuzz(9) == "Fizz"

# Step 2: Green - 一般化
def fizzbuzz(n):
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"

# Step 3: Refactor - リファクタリング
def fizzbuzz(n):
    result = ""
    if n % 3 == 0:
        result += "Fizz"
    if n % 5 == 0:
        result += "Buzz"
    return result or str(n)
```

### TDDのメリット

1. **設計の改善**: テスタブルなコードは良い設計
2. **リグレッション防止**: テストが保護層になる
3. **ドキュメント**: テストが仕様書
4. **自信**: リファクタリングしやすい

### TDDのデメリット

1. **学習曲線**: 慣れるまで時間がかかる
2. **初期コスト**: 開発時間が増える
3. **過剰テスト**: 実装詳細をテストしがち

---

## 6. 振る舞い駆動開発（BDD）

### 概念

**BDD = TDD + ユビキタス言語**

ビジネス要件をテストとして記述

### Given-When-Then 構文

```gherkin
Feature: ユーザーログイン

  Scenario: 正しい認証情報でログイン
    Given ユーザー "alice@example.com" が登録されている
    And パスワードは "password123"
    When ログインページにアクセスする
    And メールアドレス "alice@example.com" を入力
    And パスワード "password123" を入力
    And "ログイン" ボタンをクリック
    Then ダッシュボードにリダイレクトされる
    And "Welcome, Alice" というメッセージが表示される
```

### 実装例: Python (behave)

```python
# features/login.feature
Feature: User Login

  Scenario: Successful login with valid credentials
    Given a user with email "alice@example.com" exists
    When I visit the login page
    And I fill in "email" with "alice@example.com"
    And I fill in "password" with "password123"
    And I click "Login"
    Then I should be on the dashboard page
    And I should see "Welcome, Alice"

# features/steps/login_steps.py
from behave import given, when, then

@given('a user with email "{email}" exists')
def step_user_exists(context, email):
    context.user = create_user(email=email, password='password123')

@when('I visit the login page')
def step_visit_login(context):
    context.browser.get('http://localhost:5000/login')

@when('I fill in "{field}" with "{value}"')
def step_fill_in(context, field, value):
    input_field = context.browser.find_element_by_id(field)
    input_field.send_keys(value)

@when('I click "{button_text}"')
def step_click_button(context, button_text):
    button = context.browser.find_element_by_xpath(f"//button[text()='{button_text}']")
    button.click()

@then('I should be on the dashboard page')
def step_check_url(context):
    assert 'dashboard' in context.browser.current_url

@then('I should see "{text}"')
def step_see_text(context, text):
    assert text in context.browser.page_source
```

### BDDのメリット

1. **共通言語**: 技術者と非技術者の橋渡し
2. **要件の明確化**: 曖昧さを減らす
3. **Living Documentation**: 常に最新の仕様書

---

## 7. テスト戦略の設計

### テスト計画のチェックリスト

```markdown
## テスト対象
- [ ] ビジネスロジック（Unit）
- [ ] データ永続化（Integration）
- [ ] API エンドポイント（Integration）
- [ ] ユーザーフロー（E2E）
- [ ] エラーハンドリング（Unit/Integration）
- [ ] セキュリティ（Integration/E2E）
- [ ] パフォーマンス（専用テスト）

## カバレッジ目標
- [ ] Unit: 80%以上
- [ ] Integration: 主要機能 100%
- [ ] E2E: クリティカルパス 100%

## CI/CD 統合
- [ ] コミット時に Unit テスト実行
- [ ] PR 時に全テスト実行
- [ ] デプロイ前に E2E テスト実行
```

### テストの優先順位付け

```python
# 優先度マトリクス
priority_matrix = {
    "high_risk_high_frequency": "最優先でテスト",  # ログイン、決済
    "high_risk_low_frequency": "重点的にテスト",   # 年次処理
    "low_risk_high_frequency": "基本的なテスト",   # 一覧表示
    "low_risk_low_frequency": "最小限のテスト"    # 設定画面
}
```

---

## トラブルシューティング

### よくある問題

**Q: テストが遅すぎる**
A:
- 単体テストでモックを使用
- 統合テストの並列実行
- E2Eテストの削減

**Q: テストが脆い（よく壊れる）**
A:
- 実装詳細ではなく振る舞いをテスト
- 明示的な待機を使用（E2E）
- テストデータの独立性を確保

**Q: カバレッジ100%を目指すべき？**
A: いいえ。80-90%を目標に、クリティカルな部分を確実にカバー。

---

## 学習ロードマップ

### Week 1: 単体テスト
- [ ] テストフレームワークのセットアップ
- [ ] 10個以上の単体テストを書く
- [ ] カバレッジ測定

### Week 2: 統合テスト
- [ ] DBテストのセットアップ
- [ ] API統合テストの実装
- [ ] テストデータ管理

### Week 3: E2Eテスト
- [ ] Selenium/Playwright のセットアップ
- [ ] 主要なユーザーフローをテスト
- [ ] ページオブジェクトパターン適用

### Week 4: TDD実践
- [ ] TDDで新機能を実装
- [ ] Red-Green-Refactor を体験
- [ ] テスト戦略を文書化

---

## 参考資料

### 書籍
- "Test Driven Development: By Example" - Kent Beck
- "Growing Object-Oriented Software, Guided by Tests" - Steve Freeman
- "xUnit Test Patterns" - Gerard Meszaros

### ツール
- pytest (Python)
- Jest (JavaScript)
- Selenium / Playwright (E2E)
- Coverage.py / Istanbul (カバレッジ)
