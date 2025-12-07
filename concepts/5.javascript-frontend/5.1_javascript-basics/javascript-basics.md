# JavaScript言語基礎 学習ノート

> 対象: JavaScript ES6+
> 環境: ブラウザ（Chrome, Edge）, Node.js

## 学習目標

- プロトタイプベースOOPの仕組みを理解する
- クロージャとスコープの概念を理解し、実務で活用できる
- 非同期処理の各手法を使い分けられる
- イベントループの動作原理を理解する
- thisの挙動を予測し、適切に扱える

---

## 5.1.1 プロトタイプベースOOP

### 概要

JavaScriptは**クラスベース**ではなく**プロトタイプベース**のオブジェクト指向言語です。

### プロトタイプチェーン

```javascript
// コンストラクタ関数
function Person(name) {
    this.name = name;
}

// プロトタイプにメソッド追加
Person.prototype.greet = function() {
    console.log(`Hello, I'm ${this.name}`);
};

const alice = new Person('Alice');
alice.greet(); // "Hello, I'm Alice"

// プロトタイプチェーンの確認
console.log(alice.__proto__ === Person.prototype); // true
console.log(Person.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__); // null
```

#### プロトタイプチェーンの仕組み

```
alice オブジェクト
  ↓ __proto__
Person.prototype { greet: function }
  ↓ __proto__
Object.prototype { toString, valueOf, ... }
  ↓ __proto__
null
```

### ES6 クラス構文（シンタックスシュガー）

```javascript
class Person {
    constructor(name) {
        this.name = name;
    }

    greet() {
        console.log(`Hello, I'm ${this.name}`);
    }
}

// 内部的にはプロトタイプベース
const bob = new Person('Bob');
console.log(bob.__proto__ === Person.prototype); // true
```

### 継承

```javascript
class Employee extends Person {
    constructor(name, company) {
        super(name); // 親クラスのコンストラクタ呼び出し
        this.company = company;
    }

    work() {
        console.log(`${this.name} is working at ${this.company}`);
    }
}

const charlie = new Employee('Charlie', 'Acme Corp');
charlie.greet(); // "Hello, I'm Charlie"
charlie.work();  // "Charlie is working at Acme Corp"

// プロトタイプチェーン
console.log(charlie.__proto__ === Employee.prototype); // true
console.log(Employee.prototype.__proto__ === Person.prototype); // true
```

### プロトタイプ vs クラス（Java等）の違い

| 項目 | プロトタイプ（JavaScript） | クラス（Java） |
|------|---------------------------|---------------|
| **設計** | オブジェクトからオブジェクトを複製 | クラスから設計図を作成 |
| **継承** | プロトタイプチェーン | クラス階層 |
| **動的変更** | 実行時にプロトタイプ変更可能 | コンパイル時に固定 |
| **メソッド共有** | プロトタイプで共有 | クラスで定義 |

---

## 5.1.2 クロージャとスコープ

### スコープの種類

#### 1. グローバルスコープ

```javascript
var globalVar = 'global';

function test() {
    console.log(globalVar); // アクセス可能
}
```

#### 2. 関数スコープ（var）

```javascript
function outer() {
    var functionScoped = 'function scope';

    if (true) {
        var innerVar = 'still function scope';
    }

    console.log(innerVar); // アクセス可能（varは関数スコープ）
}

// console.log(functionScoped); // ReferenceError
```

#### 3. ブロックスコープ（let, const）

```javascript
function blockScopeTest() {
    if (true) {
        let blockScoped = 'block scope';
        const constant = 'constant';
    }

    // console.log(blockScoped); // ReferenceError
}

for (let i = 0; i < 3; i++) {
    // i はブロックスコープ
}
// console.log(i); // ReferenceError
```

### クロージャ

**クロージャ**は、関数とその関数が宣言された環境（レキシカルスコープ）の組み合わせです。

#### 基本例

```javascript
function createCounter() {
    let count = 0; // 外部からアクセス不可

    return function() {
        count++;
        return count;
    };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3

// count変数は外部からアクセスできない（カプセル化）
```

#### 実用例：プライベート変数

```javascript
function BankAccount(initialBalance) {
    let balance = initialBalance; // プライベート変数

    return {
        deposit(amount) {
            balance += amount;
            return balance;
        },
        withdraw(amount) {
            if (balance >= amount) {
                balance -= amount;
                return balance;
            } else {
                throw new Error('Insufficient funds');
            }
        },
        getBalance() {
            return balance;
        }
    };
}

const account = new BankAccount(100);
account.deposit(50);  // 150
account.withdraw(30); // 120
console.log(account.getBalance()); // 120

// balance に直接アクセスできない
// console.log(account.balance); // undefined
```

#### よくある落とし穴：ループ内のクロージャ

```javascript
// ❌ 間違い（var使用）
for (var i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i); // 3, 3, 3 （期待: 0, 1, 2）
    }, 100);
}

// ✅ 正しい（let使用）
for (let i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i); // 0, 1, 2
    }, 100);
}

// ✅ 正しい（クロージャで即座に実行）
for (var i = 0; i < 3; i++) {
    (function(j) {
        setTimeout(function() {
            console.log(j); // 0, 1, 2
        }, 100);
    })(i);
}
```

---

## 5.1.3 非同期処理（コールバック、Promise、async/await）

### 1. コールバック

#### 基本例

```javascript
function fetchData(callback) {
    setTimeout(() => {
        const data = { id: 1, name: 'Alice' };
        callback(data);
    }, 1000);
}

fetchData(function(data) {
    console.log(data);
});
```

#### コールバック地獄（Callback Hell）

```javascript
// ❌ 読みにくい
fetchUser(userId, function(user) {
    fetchPosts(user.id, function(posts) {
        fetchComments(posts[0].id, function(comments) {
            console.log(comments);
        });
    });
});
```

### 2. Promise

#### 基本例

```javascript
function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            const data = { id: 1, name: 'Alice' };
            resolve(data); // 成功
            // reject(new Error('Failed')); // 失敗
        }, 1000);
    });
}

fetchData()
    .then(data => {
        console.log(data);
        return data.id;
    })
    .then(id => {
        console.log('ID:', id);
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        console.log('Done');
    });
```

#### Promise チェーン

```javascript
fetchUser(userId)
    .then(user => fetchPosts(user.id))
    .then(posts => fetchComments(posts[0].id))
    .then(comments => console.log(comments))
    .catch(error => console.error(error));
```

#### Promise.all（並列実行）

```javascript
const promise1 = fetch('/api/users/1');
const promise2 = fetch('/api/users/2');
const promise3 = fetch('/api/users/3');

Promise.all([promise1, promise2, promise3])
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(users => {
        console.log(users); // 全て完了後に実行
    })
    .catch(error => {
        console.error('いずれかが失敗:', error);
    });
```

### 3. async/await

#### 基本例

```javascript
async function getUserData() {
    try {
        const user = await fetchUser(userId);
        const posts = await fetchPosts(user.id);
        const comments = await fetchComments(posts[0].id);
        console.log(comments);
    } catch (error) {
        console.error('Error:', error);
    }
}

getUserData();
```

#### 並列実行

```javascript
async function fetchMultipleUsers() {
    // ❌ 逐次実行（遅い）
    const user1 = await fetch('/api/users/1').then(r => r.json());
    const user2 = await fetch('/api/users/2').then(r => r.json());
    const user3 = await fetch('/api/users/3').then(r => r.json());

    // ✅ 並列実行（速い）
    const [user1, user2, user3] = await Promise.all([
        fetch('/api/users/1').then(r => r.json()),
        fetch('/api/users/2').then(r => r.json()),
        fetch('/api/users/3').then(r => r.json())
    ]);

    return [user1, user2, user3];
}
```

### 比較表

| 手法 | 読みやすさ | エラーハンドリング | 使い分け |
|------|----------|------------------|---------|
| **コールバック** | ❌ 低い | 困難 | レガシーコード、単純な非同期 |
| **Promise** | ○ 中程度 | .catch() | ライブラリAPI |
| **async/await** | ✅ 高い | try/catch | モダンなコード、推奨 |

---

## 5.1.4 イベントループ

### JavaScriptの実行モデル

JavaScriptは**シングルスレッド**ですが、**イベントループ**により非同期処理を実現しています。

### イベントループの仕組み

```
┌───────────────────────────┐
│   Call Stack（実行中）     │
└───────────────────────────┘
           ↑
           │
┌───────────────────────────┐
│   Event Loop              │ ← 常に監視
└───────────────────────────┘
           ↓
┌───────────────────────────┐
│   Task Queue              │ ← setTimeout, setInterval
└───────────────────────────┘
           ↓
┌───────────────────────────┐
│   Microtask Queue         │ ← Promise, queueMicrotask
└───────────────────────────┘
```

### 実行順序

```javascript
console.log('1');

setTimeout(() => {
    console.log('2 (Task Queue)');
}, 0);

Promise.resolve().then(() => {
    console.log('3 (Microtask Queue)');
});

console.log('4');

// 出力順序:
// 1
// 4
// 3 (Microtask Queue)
// 2 (Task Queue)
```

**実行順序:**
1. 同期コード（Call Stack）
2. Microtask Queue（Promise）
3. Task Queue（setTimeout）

### 詳細例

```javascript
console.log('Start');

setTimeout(() => console.log('Timeout 1'), 0);

Promise.resolve()
    .then(() => console.log('Promise 1'))
    .then(() => console.log('Promise 2'));

setTimeout(() => console.log('Timeout 2'), 0);

Promise.resolve().then(() => console.log('Promise 3'));

console.log('End');

// 出力:
// Start
// End
// Promise 1
// Promise 3
// Promise 2
// Timeout 1
// Timeout 2
```

---

## 5.1.5 this の挙動

### thisの決定ルール

JavaScriptの`this`は**呼び出し方**で決まります。

### 1. 通常の関数呼び出し

```javascript
function showThis() {
    console.log(this);
}

showThis(); // グローバルオブジェクト（window or undefined in strict mode）
```

### 2. メソッド呼び出し

```javascript
const person = {
    name: 'Alice',
    greet: function() {
        console.log(this.name);
    }
};

person.greet(); // "Alice" （this = person）

const greet = person.greet;
greet(); // undefined （this = グローバル）
```

### 3. コンストラクタ呼び出し

```javascript
function Person(name) {
    this.name = name;
}

const alice = new Person('Alice');
console.log(alice.name); // "Alice"
```

### 4. アロー関数

アロー関数は**thisをバインドしない**（レキシカルスコープのthisを使用）。

```javascript
const person = {
    name: 'Alice',
    greet: function() {
        setTimeout(function() {
            console.log(this.name); // undefined （thisはグローバル）
        }, 100);
    }
};

person.greet();
```

```javascript
const person = {
    name: 'Alice',
    greet: function() {
        setTimeout(() => {
            console.log(this.name); // "Alice" （thisは外側のスコープ）
        }, 100);
    }
};

person.greet();
```

### 5. call / apply / bind

```javascript
function greet(greeting) {
    console.log(`${greeting}, ${this.name}`);
}

const person = { name: 'Alice' };

// call: 即座に実行
greet.call(person, 'Hello'); // "Hello, Alice"

// apply: 引数を配列で渡す
greet.apply(person, ['Hi']); // "Hi, Alice"

// bind: 新しい関数を返す
const boundGreet = greet.bind(person);
boundGreet('Hey'); // "Hey, Alice"
```

### よくある問題と解決策

#### 問題: イベントハンドラーでのthis

```javascript
class Button {
    constructor() {
        this.count = 0;
        const btn = document.querySelector('#myButton');

        // ❌ thisがButtonインスタンスではなくbtn要素になる
        btn.addEventListener('click', this.handleClick);
    }

    handleClick() {
        this.count++; // エラー: thisはbutton要素
        console.log(this.count);
    }
}
```

#### 解決策1: bind

```javascript
class Button {
    constructor() {
        this.count = 0;
        const btn = document.querySelector('#myButton');
        btn.addEventListener('click', this.handleClick.bind(this));
    }

    handleClick() {
        this.count++;
        console.log(this.count);
    }
}
```

#### 解決策2: アロー関数

```javascript
class Button {
    constructor() {
        this.count = 0;
        const btn = document.querySelector('#myButton');
        btn.addEventListener('click', () => this.handleClick());
    }

    handleClick() {
        this.count++;
        console.log(this.count);
    }
}
```

---

## 学習ロードマップ

### Week 1: プロトタイプとスコープ
- [ ] プロトタイプチェーンの仕組み理解
- [ ] クロージャの実装練習
- [ ] var/let/constの違いを実践

### Week 2: 非同期処理
- [ ] Promiseの基本理解
- [ ] async/awaitの実践
- [ ] エラーハンドリングパターン習得

### Week 3: イベントループとthis
- [ ] イベントループの動作確認
- [ ] thisの挙動パターン習得
- [ ] アロー関数の適切な使い分け

### Week 4: 実践
- [ ] 実プロジェクトでの非同期処理実装
- [ ] コールバック地獄のリファクタリング
- [ ] パフォーマンス最適化

---

## 参考資料

- [MDN Web Docs - JavaScript](https://developer.mozilla.org/ja/docs/Web/JavaScript)
- 書籍『JavaScript本格入門』
- 書籍『改訂新版JavaScript本格入門』
- [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS)
- [JavaScript.info](https://javascript.info/)

---

## チートシート

### 非同期処理の選択

```javascript
// シンプルな非同期
setTimeout(() => { /* ... */ }, 1000);

// チェーン処理
fetchData()
    .then(process)
    .then(save)
    .catch(handleError);

// 読みやすい非同期（推奨）
async function main() {
    try {
        const data = await fetchData();
        const result = await process(data);
        await save(result);
    } catch (error) {
        handleError(error);
    }
}
```

### thisの確認

```javascript
console.log(this); // 現在のthisを確認
console.dir(functionName); // 関数の詳細を確認
```
