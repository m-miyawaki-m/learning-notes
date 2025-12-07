# DOM操作 学習ノート

> 対象: DOM API, JavaScript ES6+
> 環境: モダンブラウザ（Chrome, Edge, Firefox）

## 学習目標

- DOMツリー構造を理解する
- 効率的なDOM操作ができる
- イベント伝播の仕組みを理解する
- イベントデリゲーションを実装できる

---

## 5.2.1 DOMツリー構造

### DOMとは

**DOM (Document Object Model)** は、HTMLドキュメントをツリー構造として表現したAPIです。

### DOM ツリーの構造

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My Page</title>
  </head>
  <body>
    <h1>Hello</h1>
    <p>World</p>
  </body>
</html>
```

```
Document
  └─ html (Element)
      ├─ head (Element)
      │   └─ title (Element)
      │       └─ "My Page" (Text)
      └─ body (Element)
          ├─ h1 (Element)
          │   └─ "Hello" (Text)
          └─ p (Element)
              └─ "World" (Text)
```

### ノードの種類

| ノードタイプ | nodeType | 例 |
|------------|----------|-----|
| **Element** | 1 | `<div>`, `<p>` |
| **Attr** | 2 | `class="container"` |
| **Text** | 3 | テキストコンテンツ |
| **Comment** | 8 | `<!-- コメント -->` |
| **Document** | 9 | `document` |

### 要素の取得

#### 1. IDで取得

```javascript
const element = document.getElementById('myId');
```

#### 2. クラス名で取得

```javascript
const elements = document.getElementsByClassName('myClass');
// HTMLCollection（配列ライク、ライブ）

// 配列に変換
const array = Array.from(elements);
```

#### 3. タグ名で取得

```javascript
const paragraphs = document.getElementsByTagName('p');
```

#### 4. CSSセレクタで取得（推奨）

```javascript
// 最初の1つ
const element = document.querySelector('.myClass');
const element = document.querySelector('#myId');
const element = document.querySelector('div.container > p');

// 全て
const elements = document.querySelectorAll('.myClass');
// NodeList（配列ライク、静的スナップショット）

// forEach使用可能
elements.forEach(el => {
    console.log(el);
});
```

### 要素の作成・追加・削除

#### 作成

```javascript
const div = document.createElement('div');
const text = document.createTextNode('Hello');

div.textContent = 'Hello World';
div.innerHTML = '<strong>Bold</strong> text';

// 属性設定
div.id = 'myDiv';
div.className = 'container';
div.setAttribute('data-id', '123');
```

#### 追加

```javascript
const parent = document.querySelector('#parent');
const child = document.createElement('div');

// 末尾に追加
parent.appendChild(child);

// 先頭に追加
parent.insertBefore(child, parent.firstChild);

// より柔軟な挿入
parent.insertAdjacentHTML('beforeend', '<p>Text</p>');
// 'beforebegin': 要素の前
// 'afterbegin': 最初の子の前
// 'beforeend': 最後の子の後
// 'afterend': 要素の後
```

#### 削除

```javascript
const element = document.querySelector('#myElement');

// 自分自身を削除
element.remove();

// 親から削除
element.parentNode.removeChild(element);
```

### DOM 走査

```javascript
const element = document.querySelector('#myElement');

// 親
element.parentNode;
element.parentElement;

// 子
element.children;        // HTMLCollection（要素のみ）
element.childNodes;      // NodeList（テキストノード含む）
element.firstElementChild;
element.lastElementChild;

// 兄弟
element.nextElementSibling;
element.previousElementSibling;
```

### 属性操作

```javascript
const element = document.querySelector('#myElement');

// 取得
element.getAttribute('data-id');
element.dataset.id; // data-* 属性専用

// 設定
element.setAttribute('data-id', '123');
element.dataset.id = '123';

// 削除
element.removeAttribute('data-id');

// 存在確認
element.hasAttribute('data-id');
```

### クラス操作

```javascript
const element = document.querySelector('#myElement');

// クラス追加
element.classList.add('active');
element.classList.add('active', 'highlight');

// クラス削除
element.classList.remove('active');

// トグル
element.classList.toggle('active');

// 存在確認
element.classList.contains('active');

// 置換
element.classList.replace('old', 'new');
```

### スタイル操作

```javascript
const element = document.querySelector('#myElement');

// インラインスタイル設定
element.style.color = 'red';
element.style.backgroundColor = 'blue';
element.style.fontSize = '16px';

// 複数設定
Object.assign(element.style, {
    color: 'red',
    backgroundColor: 'blue',
    fontSize: '16px'
});

// 計算済みスタイル取得
const computed = window.getComputedStyle(element);
console.log(computed.color);
console.log(computed.fontSize);
```

---

## 5.2.2 イベント伝播（キャプチャ、バブリング）

### イベント伝播の3フェーズ

```html
<div id="outer">
  <div id="middle">
    <button id="inner">Click me</button>
  </div>
</div>
```

```
1. キャプチャフェーズ（上から下へ）
   window → document → html → body → #outer → #middle → #inner

2. ターゲットフェーズ
   #inner （イベント発生元）

3. バブリングフェーズ（下から上へ）
   #inner → #middle → #outer → body → html → document → window
```

### イベントリスナーの登録

```javascript
const button = document.querySelector('#inner');

// バブリングフェーズで捕捉（デフォルト）
button.addEventListener('click', function(event) {
    console.log('Button clicked!');
});

// キャプチャフェーズで捕捉
button.addEventListener('click', function(event) {
    console.log('Capture phase');
}, true); // 第3引数: true = キャプチャ

// オプション指定
button.addEventListener('click', function(event) {
    console.log('Click');
}, {
    capture: false,  // キャプチャフェーズで捕捉
    once: true,      // 一度だけ実行
    passive: true    // preventDefault() 呼ばない（スクロール最適化）
});
```

### イベント伝播の確認

```javascript
const outer = document.querySelector('#outer');
const middle = document.querySelector('#middle');
const inner = document.querySelector('#inner');

// バブリングの確認
outer.addEventListener('click', () => console.log('Outer'));
middle.addEventListener('click', () => console.log('Middle'));
inner.addEventListener('click', () => console.log('Inner'));

// innerをクリックすると:
// "Inner" → "Middle" → "Outer"
```

### イベント伝播の制御

#### stopPropagation()

```javascript
middle.addEventListener('click', function(event) {
    console.log('Middle');
    event.stopPropagation(); // これ以上伝播しない
});

// innerをクリックすると:
// "Inner" → "Middle" （Outerには伝播しない）
```

#### stopImmediatePropagation()

```javascript
middle.addEventListener('click', function(event) {
    console.log('Middle 1');
    event.stopImmediatePropagation(); // 同じ要素の他のリスナーも停止
});

middle.addEventListener('click', function(event) {
    console.log('Middle 2'); // 実行されない
});
```

#### preventDefault()

```javascript
const link = document.querySelector('a');

link.addEventListener('click', function(event) {
    event.preventDefault(); // デフォルト動作（ページ遷移）をキャンセル
    console.log('Link clicked but not navigating');
});
```

---

## 5.2.3 イベントデリゲーション

### 問題: 大量の要素にイベントリスナー

```javascript
// ❌ 非効率（メモリ消費大）
const buttons = document.querySelectorAll('.button');
buttons.forEach(button => {
    button.addEventListener('click', function() {
        console.log('Clicked:', this.textContent);
    });
});
```

### 解決策: イベントデリゲーション

親要素にイベントリスナーを1つだけ設置し、`event.target`で判定します。

```javascript
// ✅ 効率的
const container = document.querySelector('#container');

container.addEventListener('click', function(event) {
    // クリックされた要素がボタンかチェック
    if (event.target.matches('.button')) {
        console.log('Clicked:', event.target.textContent);
    }
});
```

### 実用例: 動的に追加される要素

```javascript
const list = document.querySelector('#list');

// イベントデリゲーション
list.addEventListener('click', function(event) {
    if (event.target.matches('.delete-btn')) {
        const item = event.target.closest('.list-item');
        item.remove();
    }
});

// 後から追加される要素にも自動で適用される
const newItem = document.createElement('li');
newItem.className = 'list-item';
newItem.innerHTML = 'New Item <button class="delete-btn">Delete</button>';
list.appendChild(newItem);
```

### イベントデリゲーションのメリット

1. **メモリ効率**: リスナー1つだけ
2. **動的要素対応**: 後から追加される要素にも適用
3. **パフォーマンス**: イベントリスナーの数が少ない

### 実装パターン

```javascript
// パターン1: matches() を使用
container.addEventListener('click', function(event) {
    if (event.target.matches('.button')) {
        handleButtonClick(event.target);
    }
});

// パターン2: closest() を使用（子要素がクリックされる場合）
container.addEventListener('click', function(event) {
    const button = event.target.closest('.button');
    if (button) {
        handleButtonClick(button);
    }
});

// パターン3: 複数の条件
container.addEventListener('click', function(event) {
    const target = event.target;

    if (target.matches('.edit-btn')) {
        handleEdit(target);
    } else if (target.matches('.delete-btn')) {
        handleDelete(target);
    } else if (target.matches('.save-btn')) {
        handleSave(target);
    }
});
```

---

## パフォーマンス最適化

### 1. DOM操作のバッチ処理

```javascript
// ❌ 非効率（リフローが3回発生）
const container = document.querySelector('#container');
container.appendChild(document.createElement('div'));
container.appendChild(document.createElement('div'));
container.appendChild(document.createElement('div'));

// ✅ 効率的（リフローが1回）
const fragment = document.createDocumentFragment();
fragment.appendChild(document.createElement('div'));
fragment.appendChild(document.createElement('div'));
fragment.appendChild(document.createElement('div'));
container.appendChild(fragment);
```

### 2. innerHTML vs createElement

```javascript
// innerHTML: シンプルだが遅い（パース処理）
container.innerHTML = '<div>Item 1</div><div>Item 2</div>';

// createElement: 速い
const div1 = document.createElement('div');
div1.textContent = 'Item 1';
const div2 = document.createElement('div');
div2.textContent = 'Item 2';
container.appendChild(div1);
container.appendChild(div2);
```

### 3. クラス変更によるスタイル変更

```javascript
// ❌ 複数回リフロー
element.style.width = '100px';
element.style.height = '100px';
element.style.backgroundColor = 'red';

// ✅ 1回のリフロー
element.className = 'box-style'; // CSSで定義
```

---

## 学習ロードマップ

### Week 1: DOM基礎
- [ ] DOMツリー構造の理解
- [ ] 要素の取得・作成・削除
- [ ] 属性・クラス操作

### Week 2: イベント処理
- [ ] イベントリスナーの登録
- [ ] イベント伝播の理解
- [ ] preventDefault / stopPropagation

### Week 3: 実践
- [ ] イベントデリゲーション実装
- [ ] 動的なUI構築
- [ ] パフォーマンス最適化

### Week 4: 応用
- [ ] 実プロジェクトでのDOM操作
- [ ] jQueryからバニラJSへの移行
- [ ] フレームワーク（React等）との比較

---

## 参考資料

- [MDN - Document Object Model](https://developer.mozilla.org/ja/docs/Web/API/Document_Object_Model)
- [MDN - イベントリファレンス](https://developer.mozilla.org/ja/docs/Web/Events)
- [JavaScript.info - DOM](https://javascript.info/document)

---

## チートシート

### 要素取得

```javascript
document.getElementById('id')
document.querySelector('.class')
document.querySelectorAll('div.class')
```

### 要素操作

```javascript
element.textContent = 'text'
element.innerHTML = '<strong>html</strong>'
element.classList.add('active')
element.setAttribute('data-id', '1')
```

### イベント

```javascript
element.addEventListener('click', handler)
event.preventDefault()
event.stopPropagation()
event.target // クリックされた要素
event.currentTarget // リスナーが登録された要素
```
