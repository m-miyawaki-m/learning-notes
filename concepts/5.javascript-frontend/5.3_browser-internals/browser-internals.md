# ブラウザ動作原理 学習ノート

> 対象: モダンブラウザ（Chrome, Edge, Firefox）
> 関連: パフォーマンス最適化、セキュリティ

## 学習目標

- ブラウザのレンダリングプロセスを理解する
- リフローとリペイントの違いを理解し、最適化できる
- ブラウザストレージの使い分けができる
- Same-Origin Policyとその回避方法を理解する

---

## 5.3.1 レンダリングプロセス

### ブラウザのレンダリングパイプライン

```
HTML → DOM構築
CSS  → CSSOM構築
        ↓
    Render Tree構築
        ↓
      Layout（Reflow）
        ↓
      Paint
        ↓
      Composite
```

### 1. HTML パース → DOM 構築

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Page</title>
  </head>
  <body>
    <h1>Hello</h1>
  </body>
</html>
```

↓ パース ↓

```
Document
  └─ html
      ├─ head
      │   └─ title
      └─ body
          └─ h1
```

### 2. CSS パース → CSSOM 構築

```css
body { font-size: 16px; }
h1 { color: blue; }
```

↓ パース ↓

```
CSSOM Tree
  └─ body: { font-size: 16px }
      └─ h1: { font-size: 16px, color: blue } (継承)
```

### 3. Render Tree 構築

DOM + CSSOM = Render Tree

- `display: none` の要素は含まれない
- `<script>`, `<meta>` などは含まれない

### 4. Layout（Reflow）

各要素の**位置**と**サイズ**を計算します。

```
Viewport: 1024px × 768px
  └─ body: 1024px × 768px
      └─ h1: 1024px × 32px (0, 0)
```

### 5. Paint

ピクセル単位で描画します（色、テキスト、影など）。

### 6. Composite

レイヤーを合成して最終的な画面を生成します。

---

## 5.3.2 リフロー vs リペイント

### リフロー（Reflow / Layout）

要素の**位置**や**サイズ**が変更される場合に発生。**重い処理**です。

#### リフローをトリガーする操作

```javascript
// ❌ リフロー発生
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';

element.classList.add('large'); // widthやheightが変わる場合

// 要素の追加・削除
parent.appendChild(newElement);
element.remove();

// スクロール
window.scrollTo(0, 100);

// サイズ取得（強制的にリフロー）
const height = element.offsetHeight;
const width = element.clientWidth;
```

### リペイント（Repaint）

要素の**見た目**のみ変更される場合に発生。リフローより軽い。

#### リペイントのみ発生する操作

```javascript
// リフローなし、リペイントのみ
element.style.color = 'red';
element.style.backgroundColor = 'blue';
element.style.visibility = 'hidden';
```

### コンポジット（Composite）のみ

最も軽い処理。GPUアクセラレーションが可能です。

#### コンポジットのみ発生する操作

```javascript
// リフロー・リペイントなし、コンポジットのみ
element.style.transform = 'translateX(100px)';
element.style.opacity = 0.5';
```

### パフォーマンス比較

| 操作 | リフロー | リペイント | コンポジット | コスト |
|------|---------|----------|------------|--------|
| `width` 変更 | ✅ | ✅ | ✅ | 高 |
| `color` 変更 | ❌ | ✅ | ✅ | 中 |
| `transform` 変更 | ❌ | ❌ | ✅ | 低 |

### 最適化テクニック

#### 1. バッチ処理

```javascript
// ❌ リフローが3回
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';

// ✅ リフローが1回
element.style.cssText = 'width: 100px; height: 100px; margin: 10px;';

// または
element.className = 'box-large'; // CSSクラスで一括変更
```

#### 2. DocumentFragment 使用

```javascript
// ❌ 要素ごとにリフロー
for (let i = 0; i < 100; i++) {
    const div = document.createElement('div');
    container.appendChild(div); // 100回リフロー
}

// ✅ 1回のリフロー
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
    const div = document.createElement('div');
    fragment.appendChild(div);
}
container.appendChild(fragment); // 1回だけリフロー
```

#### 3. オフスクリーン操作

```javascript
// 要素を一時的にDOMから外して操作
const parent = element.parentNode;
parent.removeChild(element);

// 大量の変更を実行
element.style.width = '100px';
element.style.height = '100px';
// ...

parent.appendChild(element); // 1回だけリフロー
```

#### 4. transform / opacity を使う

```javascript
// ❌ リフロー発生
element.style.left = '100px';

// ✅ コンポジットのみ
element.style.transform = 'translateX(100px)';
```

#### 5. will-change ヒント

```css
.element {
    will-change: transform; /* ブラウザに変更予告 */
}
```

```javascript
// JavaScriptから
element.style.willChange = 'transform';

// アニメーション後は削除
element.addEventListener('animationend', () => {
    element.style.willChange = 'auto';
});
```

---

## 5.3.3 ブラウザストレージ

### 種類と比較

| 種類 | 容量 | 永続性 | スコープ | 用途 |
|------|------|--------|---------|------|
| **Cookie** | 4KB | 期限設定可 | ドメイン | 認証トークン |
| **LocalStorage** | 5~10MB | 永続 | オリジン | ユーザー設定 |
| **SessionStorage** | 5~10MB | タブ閉じるまで | タブ | 一時データ |
| **IndexedDB** | 数百MB~ | 永続 | オリジン | 大量データ |

### 1. Cookie

```javascript
// 設定
document.cookie = "username=John; expires=Fri, 31 Dec 2024 23:59:59 GMT; path=/";

// 読み取り
console.log(document.cookie); // "username=John; session=abc123"

// ヘルパー関数
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/`;
}

function getCookie(name) {
    const cookies = document.cookie.split('; ');
    for (let cookie of cookies) {
        const [key, value] = cookie.split('=');
        if (key === name) return value;
    }
    return null;
}
```

### 2. LocalStorage

```javascript
// 保存
localStorage.setItem('username', 'John');
localStorage.setItem('settings', JSON.stringify({ theme: 'dark' }));

// 取得
const username = localStorage.getItem('username');
const settings = JSON.parse(localStorage.getItem('settings'));

// 削除
localStorage.removeItem('username');

// 全削除
localStorage.clear();

// キー一覧
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    console.log(key, localStorage.getItem(key));
}
```

### 3. SessionStorage

```javascript
// LocalStorageと同じAPI
sessionStorage.setItem('tempData', 'value');
const data = sessionStorage.getItem('tempData');
```

### 4. IndexedDB

```javascript
// データベース開く
const request = indexedDB.open('MyDatabase', 1);

request.onupgradeneeded = function(event) {
    const db = event.target.result;

    // オブジェクトストア作成
    const objectStore = db.createObjectStore('users', { keyPath: 'id' });
    objectStore.createIndex('email', 'email', { unique: true });
};

request.onsuccess = function(event) {
    const db = event.target.result;

    // データ追加
    const transaction = db.transaction(['users'], 'readwrite');
    const objectStore = transaction.objectStore('users');

    objectStore.add({ id: 1, name: 'John', email: 'john@example.com' });

    // データ取得
    const getRequest = objectStore.get(1);
    getRequest.onsuccess = function() {
        console.log(getRequest.result);
    };
};
```

### 使い分け

```javascript
// 認証トークン（サーバーに送信する必要がある）
document.cookie = "token=abc123; Secure; HttpOnly; SameSite=Strict";

// ユーザー設定（永続化）
localStorage.setItem('theme', 'dark');

// フォーム入力の一時保存（タブ閉じたら削除）
sessionStorage.setItem('draftPost', JSON.stringify(formData));

// 大量のオフラインデータ
// IndexedDBを使用
```

---

## 5.3.4 Same-Origin Policy

### オリジンとは

オリジン = **スキーム** + **ホスト** + **ポート**

```
https://example.com:443/path?query=value

スキーム: https
ホスト: example.com
ポート: 443
```

### 同一オリジンの判定

| URL | 結果 | 理由 |
|-----|------|------|
| `https://example.com/page` | ✅ 同一 | 完全一致 |
| `https://example.com:443/page` | ✅ 同一 | HTTPSのデフォルトポート |
| `http://example.com/page` | ❌ 異なる | スキーム違い |
| `https://sub.example.com/page` | ❌ 異なる | ホスト違い |
| `https://example.com:8080/page` | ❌ 異なる | ポート違い |

### Same-Origin Policy による制限

```javascript
// ❌ 異なるオリジンからのXHR/Fetchは失敗
fetch('https://api.otherdomain.com/data')
    .then(response => response.json())
    .catch(error => {
        // Error: Cross-Origin Request Blocked
    });

// ❌ 異なるオリジンのiframeへのアクセス不可
const iframe = document.querySelector('iframe');
iframe.contentWindow.document; // SecurityError
```

### CORS（Cross-Origin Resource Sharing）

サーバー側で許可を設定します。

#### サーバー設定例（Node.js/Express）

```javascript
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', 'https://example.com');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.header('Access-Control-Allow-Credentials', 'true');
    next();
});
```

#### Spring Boot設定例

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(true);
    }
}
```

### CORS リクエストの種類

#### 1. シンプルリクエスト

```javascript
// GET, POST（Content-Type: application/x-www-form-urlencoded等）
fetch('https://api.example.com/data', {
    method: 'GET'
});
```

#### 2. プリフライトリクエスト

```javascript
// カスタムヘッダーやJSONを送信する場合
// ブラウザが自動的にOPTIONSリクエストを送信

fetch('https://api.example.com/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token'
    },
    body: JSON.stringify({ name: 'John' })
});

// 1. OPTIONS https://api.example.com/data （プリフライト）
//    サーバーが許可を返す
// 2. POST https://api.example.com/data （実際のリクエスト）
```

### CORS の回避方法

#### 1. プロキシサーバー

```javascript
// フロントエンド（同一オリジン）
fetch('/api/proxy?url=https://external-api.com/data')
    .then(response => response.json());

// バックエンド（Node.js）
app.get('/api/proxy', async (req, res) => {
    const url = req.query.url;
    const response = await fetch(url);
    const data = await response.json();
    res.json(data);
});
```

#### 2. JSONP（レガシー、非推奨）

```javascript
function handleResponse(data) {
    console.log(data);
}

const script = document.createElement('script');
script.src = 'https://api.example.com/data?callback=handleResponse';
document.body.appendChild(script);
```

#### 3. postMessage（iframe間通信）

```javascript
// 親ページ
const iframe = document.querySelector('iframe');
iframe.contentWindow.postMessage('Hello', 'https://otherdomain.com');

// iframe内
window.addEventListener('message', (event) => {
    if (event.origin === 'https://example.com') {
        console.log(event.data); // "Hello"
    }
});
```

---

## セキュリティ

### XSS（Cross-Site Scripting）対策

```javascript
// ❌ 危険
element.innerHTML = userInput;

// ✅ 安全
element.textContent = userInput;

// ✅ サニタイズ
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
```

### CSP（Content Security Policy）

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self' https://trusted.com;">
```

---

## 学習ロードマップ

### Week 1: レンダリング基礎
- [ ] レンダリングパイプラインの理解
- [ ] リフロー・リペイントの発生条件
- [ ] Chrome DevToolsでのパフォーマンス分析

### Week 2: ストレージ
- [ ] LocalStorage / SessionStorage 実装
- [ ] Cookie の適切な使用
- [ ] IndexedDB の基本操作

### Week 3: セキュリティ
- [ ] Same-Origin Policy の理解
- [ ] CORS 設定
- [ ] XSS対策

### Week 4: 最適化
- [ ] レンダリング最適化実践
- [ ] 実プロジェクトのパフォーマンス改善

---

## 参考資料

- [Chrome Developers - Rendering Performance](https://web.dev/rendering-performance/)
- [MDN - Same-origin policy](https://developer.mozilla.org/ja/docs/Web/Security/Same-origin_policy)
- [MDN - Web Storage API](https://developer.mozilla.org/ja/docs/Web/API/Web_Storage_API)
- 書籍『ハイパフォーマンス ブラウザネットワーキング』

---

## チートシート

### パフォーマンス最適化

```javascript
// ❌ 避ける
element.style.width = '100px';  // リフロー

// ✅ 推奨
element.style.transform = 'scaleX(2)';  // コンポジットのみ
```

### ストレージ選択

```javascript
// 永続的なユーザー設定
localStorage.setItem('theme', 'dark');

// タブ限定の一時データ
sessionStorage.setItem('form', data);

// サーバーに送る認証情報
document.cookie = "token=xxx; Secure; HttpOnly";
```
