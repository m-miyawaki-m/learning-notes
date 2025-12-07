# Ajax と Promise 概念ノート

> 対象: 現代のJavaScript（ES6+）
> 環境: モダンブラウザ、Node.js

## 学習目標

- Ajaxの概念と仕組みを理解する
- XMLHttpRequest と Fetch API の違いを理解する
- Promiseの概念と状態遷移を理解する
- async/await の仕組みを理解する
- 非同期処理のエラーハンドリングができる

---

## Ajax（Asynchronous JavaScript and XML）

### 概念

**Ajax**は、ページ全体をリロードせずにサーバーと非同期通信を行う技術です。

### 従来のWebアプリケーション vs Ajax

#### 従来の方式（同期通信）

```
ユーザー操作
  ↓
フォーム送信（ページ全体リロード）
  ↓
サーバー処理
  ↓
新しいHTMLページ全体を返す
  ↓
画面が真っ白になる（待機時間）
  ↓
新しいページ表示
```

#### Ajax方式（非同期通信）

```
ユーザー操作
  ↓
JavaScriptでサーバーにリクエスト（非同期）
  ↓
ユーザーは画面を操作可能（待機中も操作できる）
  ↓
サーバーからデータ（JSON等）を受信
  ↓
JavaScriptで画面の一部のみ更新
```

### Ajaxのメリット

1. **ユーザー体験の向上**: ページリロードなし
2. **帯域幅の削減**: 必要なデータのみ送受信
3. **レスポンスの高速化**: 画面の一部のみ更新
4. **非同期処理**: ユーザーは待機中も操作可能

### Ajaxのデメリット

1. **SEO対策が困難**: 検索エンジンがJavaScriptを解析できない場合がある
2. **ブラウザの戻るボタン問題**: 履歴管理が必要
3. **JavaScript無効環境では動作しない**
4. **複雑性の増加**: 非同期処理のデバッグが困難

---

## XMLHttpRequest（XHR）

### 概念

**XMLHttpRequest**は、Ajaxの基盤となるブラウザAPI（レガシー）です。

### 基本的な使い方

```javascript
// XHRオブジェクト作成
const xhr = new XMLHttpRequest();

// リクエスト初期化
xhr.open('GET', 'https://api.example.com/users', true);

// レスポンスタイプ設定
xhr.responseType = 'json';

// イベントハンドラ設定
xhr.onload = function() {
    if (xhr.status === 200) {
        console.log('成功:', xhr.response);
    } else {
        console.error('エラー:', xhr.status);
    }
};

xhr.onerror = function() {
    console.error('ネットワークエラー');
};

// リクエスト送信
xhr.send();
```

### XHRのライフサイクル

```
UNSENT (0)
  ↓ open()
OPENED (1)
  ↓ send()
HEADERS_RECEIVED (2)
  ↓
LOADING (3)
  ↓
DONE (4)
```

### readyState の値

```javascript
xhr.onreadystatechange = function() {
    console.log('readyState:', xhr.readyState);

    // 0: UNSENT - openが呼ばれていない
    // 1: OPENED - openが呼ばれた
    // 2: HEADERS_RECEIVED - レスポンスヘッダー受信
    // 3: LOADING - レスポンスボディ受信中
    // 4: DONE - 完了

    if (xhr.readyState === 4 && xhr.status === 200) {
        console.log(xhr.responseText);
    }
};
```

### POSTリクエスト

```javascript
const xhr = new XMLHttpRequest();
xhr.open('POST', 'https://api.example.com/users');

// ヘッダー設定
xhr.setRequestHeader('Content-Type', 'application/json');

xhr.onload = function() {
    if (xhr.status === 201) {
        console.log('作成成功:', xhr.response);
    }
};

// データ送信
const data = { name: 'Alice', email: 'alice@example.com' };
xhr.send(JSON.stringify(data));
```

### XHRの問題点

```javascript
// ❌ コールバック地獄
xhr1.onload = function() {
    xhr2.onload = function() {
        xhr3.onload = function() {
            // ネストが深くなる
        };
        xhr3.send();
    };
    xhr2.send();
};
xhr1.send();

// ❌ エラーハンドリングが煩雑
// ❌ API設計が古い
```

---

## Fetch API

### 概念

**Fetch API**は、XMLHttpRequestの現代的な代替APIです。Promiseベースで、よりシンプルです。

### 基本的な使い方

```javascript
// GETリクエスト
fetch('https://api.example.com/users')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('データ:', data);
    })
    .catch(error => {
        console.error('エラー:', error);
    });
```

### async/await を使った記述

```javascript
async function fetchUsers() {
    try {
        const response = await fetch('https://api.example.com/users');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('データ:', data);
        return data;

    } catch (error) {
        console.error('エラー:', error);
    }
}

fetchUsers();
```

### POSTリクエスト

```javascript
async function createUser(userData) {
    const response = await fetch('https://api.example.com/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

// 使用例
createUser({ name: 'Alice', email: 'alice@example.com' })
    .then(data => console.log('作成成功:', data))
    .catch(error => console.error('エラー:', error));
```

### リクエストオプション

```javascript
fetch('https://api.example.com/users', {
    method: 'POST',           // GET, POST, PUT, DELETE等
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token123'
    },
    body: JSON.stringify(data),  // リクエストボディ
    mode: 'cors',             // cors, no-cors, same-origin
    credentials: 'include',   // include, same-origin, omit
    cache: 'no-cache',        // キャッシュモード
    redirect: 'follow',       // follow, error, manual
    referrerPolicy: 'no-referrer'
});
```

### レスポンスの処理

```javascript
const response = await fetch('https://api.example.com/data');

// レスポンスの種類に応じて処理
const json = await response.json();        // JSON
const text = await response.text();        // テキスト
const blob = await response.blob();        // バイナリ（画像等）
const formData = await response.formData(); // FormData
const arrayBuffer = await response.arrayBuffer(); // ArrayBuffer

// レスポンス情報
console.log(response.status);      // 200
console.log(response.statusText);  // "OK"
console.log(response.headers.get('Content-Type'));
console.log(response.ok);          // status が 200-299 なら true
```

### Fetch API の注意点

```javascript
// ❌ ネットワークエラー以外はrejectしない
fetch('https://api.example.com/404')
    .then(response => {
        // ステータス404でもここに来る！
        console.log(response.ok);  // false
        console.log(response.status); // 404
    });

// ✅ 正しいエラーハンドリング
fetch('https://api.example.com/404')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error('エラー:', error);
    });
```

---

## Promise（約束）

### 概念

**Promise**は、非同期処理の結果を表すオブジェクトです。「将来値が確定する約束」を表現します。

### Promiseの3つの状態

```
Pending（保留中）
  ↓
Fulfilled（成功）または Rejected（失敗）
  ↓
Settled（決着済み）
```

```javascript
// 状態遷移の例
const promise = new Promise((resolve, reject) => {
    // Pending状態

    setTimeout(() => {
        const success = Math.random() > 0.5;

        if (success) {
            resolve('成功！');  // Fulfilled状態へ
        } else {
            reject('失敗！');   // Rejected状態へ
        }
    }, 1000);
});

console.log(promise); // Promise { <pending> }

// 1秒後
// Promise { <fulfilled>: '成功！' }
// または
// Promise { <rejected>: '失敗！' }
```

### Promiseの作成

```javascript
// 基本的な作成
const promise = new Promise((resolve, reject) => {
    // 非同期処理
    setTimeout(() => {
        resolve('成功のデータ');
        // または
        // reject(new Error('失敗の理由'));
    }, 1000);
});
```

### then() と catch()

```javascript
promise
    .then(result => {
        // 成功時の処理
        console.log('成功:', result);
        return result + ' (処理済み)';
    })
    .then(result => {
        // 前のthenの戻り値を受け取る
        console.log('次の処理:', result);
    })
    .catch(error => {
        // 失敗時の処理
        console.error('エラー:', error);
    })
    .finally(() => {
        // 成功・失敗に関わらず実行
        console.log('完了');
    });
```

### Promiseチェーン

```javascript
// ユーザー取得 → 投稿取得 → コメント取得
fetchUser(userId)
    .then(user => {
        console.log('ユーザー:', user);
        return fetchPosts(user.id);
    })
    .then(posts => {
        console.log('投稿:', posts);
        return fetchComments(posts[0].id);
    })
    .then(comments => {
        console.log('コメント:', comments);
    })
    .catch(error => {
        console.error('エラー発生:', error);
    });
```

### Promise.all()（並列実行）

```javascript
// 複数のPromiseを並列実行し、全て完了するまで待つ
const promise1 = fetch('https://api.example.com/users/1').then(r => r.json());
const promise2 = fetch('https://api.example.com/users/2').then(r => r.json());
const promise3 = fetch('https://api.example.com/users/3').then(r => r.json());

Promise.all([promise1, promise2, promise3])
    .then(([user1, user2, user3]) => {
        console.log('全ユーザー取得完了');
        console.log(user1, user2, user3);
    })
    .catch(error => {
        // いずれか1つでも失敗したら即座にreject
        console.error('エラー:', error);
    });
```

### Promise.allSettled()

```javascript
// 全てのPromiseが完了するまで待つ（成功・失敗問わず）
Promise.allSettled([promise1, promise2, promise3])
    .then(results => {
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                console.log(`Promise ${index} 成功:`, result.value);
            } else {
                console.log(`Promise ${index} 失敗:`, result.reason);
            }
        });
    });
```

### Promise.race()

```javascript
// 最初に完了したPromiseの結果を返す
const timeout = new Promise((resolve, reject) => {
    setTimeout(() => reject(new Error('タイムアウト')), 5000);
});

const fetchData = fetch('https://api.example.com/data').then(r => r.json());

Promise.race([fetchData, timeout])
    .then(data => console.log('データ取得成功:', data))
    .catch(error => console.error('エラー:', error));
```

### Promise.any()

```javascript
// 最初に成功したPromiseの結果を返す
Promise.any([promise1, promise2, promise3])
    .then(result => {
        console.log('最初の成功:', result);
    })
    .catch(error => {
        // 全て失敗した場合のみ
        console.error('全て失敗:', error);
    });
```

---

## async / await

### 概念

**async/await**は、Promiseをより読みやすく書くための構文糖衣（シンタックスシュガー）です。

### 基本的な使い方

```javascript
// Promiseベース（then/catch）
function fetchUserPromise(userId) {
    return fetch(`https://api.example.com/users/${userId}`)
        .then(response => response.json())
        .then(user => {
            console.log(user);
            return user;
        })
        .catch(error => {
            console.error(error);
        });
}

// async/awaitベース
async function fetchUserAsync(userId) {
    try {
        const response = await fetch(`https://api.example.com/users/${userId}`);
        const user = await response.json();
        console.log(user);
        return user;
    } catch (error) {
        console.error(error);
    }
}
```

### asyncの性質

```javascript
// async関数は必ずPromiseを返す
async function example() {
    return 'Hello';
}

// 以下と同等
function example() {
    return Promise.resolve('Hello');
}

example().then(value => console.log(value)); // "Hello"
```

### awaitの性質

```javascript
// awaitはasync関数内でのみ使用可能
async function example() {
    // ✅ OK
    const result = await somePromise;

    // ❌ トップレベルでは使えない（例外: ESモジュール）
    // const result = await somePromise;
}

// トップレベル await（ESモジュール）
// top-level-await.mjs
const data = await fetch('https://api.example.com/data').then(r => r.json());
console.log(data);
```

### 逐次実行 vs 並列実行

```javascript
// ❌ 遅い: 逐次実行（6秒かかる）
async function sequentialFetch() {
    const user1 = await fetch('/api/users/1').then(r => r.json()); // 2秒
    const user2 = await fetch('/api/users/2').then(r => r.json()); // 2秒
    const user3 = await fetch('/api/users/3').then(r => r.json()); // 2秒

    return [user1, user2, user3];
}

// ✅ 速い: 並列実行（2秒で完了）
async function parallelFetch() {
    const [user1, user2, user3] = await Promise.all([
        fetch('/api/users/1').then(r => r.json()),
        fetch('/api/users/2').then(r => r.json()),
        fetch('/api/users/3').then(r => r.json())
    ]);

    return [user1, user2, user3];
}
```

### エラーハンドリング

```javascript
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('エラー発生:', error);
        throw error; // 再スロー
    } finally {
        console.log('処理完了');
    }
}

// 使用側でもエラーハンドリング
fetchData()
    .then(data => console.log(data))
    .catch(error => console.error('外側でキャッチ:', error));
```

---

## 実践的なパターン

### 1. リトライ処理

```javascript
async function fetchWithRetry(url, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            console.log(`Retry ${i + 1}/${maxRetries}`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}
```

### 2. タイムアウト処理

```javascript
function timeout(ms) {
    return new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), ms)
    );
}

async function fetchWithTimeout(url, ms = 5000) {
    try {
        const response = await Promise.race([
            fetch(url),
            timeout(ms)
        ]);
        return await response.json();
    } catch (error) {
        console.error('タイムアウトまたはエラー:', error);
        throw error;
    }
}
```

### 3. キャンセル可能なリクエスト

```javascript
const controller = new AbortController();
const signal = controller.signal;

// リクエスト開始
fetch('https://api.example.com/data', { signal })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => {
        if (error.name === 'AbortError') {
            console.log('リクエストがキャンセルされました');
        } else {
            console.error('エラー:', error);
        }
    });

// 3秒後にキャンセル
setTimeout(() => controller.abort(), 3000);
```

### 4. ページネーション

```javascript
async function fetchAllPages(baseUrl) {
    let allData = [];
    let page = 1;
    let hasMore = true;

    while (hasMore) {
        const response = await fetch(`${baseUrl}?page=${page}`);
        const data = await response.json();

        allData = [...allData, ...data.items];

        hasMore = data.hasNext;
        page++;
    }

    return allData;
}
```

---

## XHR vs Fetch 比較表

| 項目 | XMLHttpRequest | Fetch API |
|------|---------------|-----------|
| **API設計** | イベントベース | Promiseベース |
| **読みやすさ** | ❌ 低い | ✅ 高い |
| **エラーハンドリング** | 複雑 | シンプル（try/catch） |
| **進捗イベント** | ✅ あり | ❌ なし |
| **リクエストキャンセル** | abort() | AbortController |
| **ブラウザ対応** | 全ブラウザ | IE非対応 |
| **HTTPエラー** | エラーイベント発火 | rejectされない |

---

## 学習ロードマップ

### Week 1: Ajax基礎
- [ ] Ajaxの概念理解
- [ ] XMLHttpRequestの基本
- [ ] Fetch APIの基本
- [ ] JSONの送受信

### Week 2: Promise
- [ ] Promiseの概念と状態遷移
- [ ] then/catch/finally
- [ ] Promiseチェーン
- [ ] Promise.all/race/allSettled

### Week 3: async/await
- [ ] async/awaitの基本
- [ ] エラーハンドリング
- [ ] 逐次実行と並列実行の使い分け
- [ ] 実践的なパターン

### Week 4: 実践
- [ ] リトライ処理の実装
- [ ] タイムアウト処理
- [ ] リクエストキャンセル
- [ ] 実際のAPI連携

---

## 参考資料

- [MDN - Ajax](https://developer.mozilla.org/ja/docs/Web/Guide/AJAX)
- [MDN - Fetch API](https://developer.mozilla.org/ja/docs/Web/API/Fetch_API)
- [MDN - Promise](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [MDN - async/await](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Statements/async_function)
- [JavaScript.info - Promises](https://javascript.info/promise-basics)

---

## チートシート

### Fetch API（GET）

```javascript
const response = await fetch('https://api.example.com/data');
const data = await response.json();
```

### Fetch API（POST）

```javascript
const response = await fetch('https://api.example.com/data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: 'value' })
});
```

### Promise.all（並列）

```javascript
const [result1, result2] = await Promise.all([promise1, promise2]);
```

### エラーハンドリング

```javascript
try {
    const data = await fetchData();
} catch (error) {
    console.error(error);
} finally {
    console.log('完了');
}
```
