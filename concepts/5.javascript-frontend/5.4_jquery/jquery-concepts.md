# jQuery 学習ノート（概念編）

> 対象: jQuery 3.x
> 環境: モダンブラウザ、レガシーコードのメンテナンス

## 学習目標

- jQueryの役割と必要性を理解する
- jQueryとバニラJavaScriptの違いを理解する
- レガシーコードの読解・メンテナンスができる
- 適切にバニラJSへ移行できる

---

## jQueryとは

**jQuery**は、DOM操作、イベント処理、Ajax通信を簡潔に記述できるJavaScriptライブラリです。

### 登場背景（2006年）

当時のブラウザ間の互換性問題を解決するために作られました。

```javascript
// Internet Explorer 6/7/8時代の問題
// ブラウザごとに異なるAPIを吸収

// jQueryなら統一されたAPI
$('#myElement').addClass('active');
```

### 現在の位置づけ

- **モダン開発**: React/Vue.js等が主流
- **レガシーコード**: 多くの既存システムで稼働中
- **学習価値**: DOM操作の理解、既存コードのメンテナンス

---

## jQueryの特徴

### 1. セレクタによる要素取得

```javascript
// バニラJS
const element = document.querySelector('#myId');
const elements = document.querySelectorAll('.myClass');

// jQuery
const $element = $('#myId');
const $elements = $('.myClass');
```

### 2. チェーンメソッド

```javascript
// バニラJS
const element = document.querySelector('.box');
element.classList.add('active');
element.style.color = 'red';
element.textContent = 'Hello';

// jQuery
$('.box')
    .addClass('active')
    .css('color', 'red')
    .text('Hello');
```

### 3. 暗黙のループ

```javascript
// バニラJS
const elements = document.querySelectorAll('.item');
elements.forEach(element => {
    element.classList.add('active');
});

// jQuery（暗黙的にループ）
$('.item').addClass('active');
```

### 4. クロスブラウザ対応

```javascript
// バニラJS（古いブラウザでは動かない可能性）
element.addEventListener('click', handler);

// jQuery（全ブラウザで動作）
$(element).on('click', handler);
```

---

## jQueryの基本構文

### $(document).ready()

```javascript
// DOM読み込み完了後に実行
$(document).ready(function() {
    console.log('DOM ready');
});

// 短縮形
$(function() {
    console.log('DOM ready');
});

// バニラJS equivalent
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready');
});
```

### セレクタ

```javascript
// ID
$('#myId')

// クラス
$('.myClass')

// タグ
$('p')

// 属性
$('[data-id="123"]')

// 複合
$('div.container > p.text')

// 疑似クラス
$('li:first')
$('li:last')
$('li:eq(2)')  // 3番目
$('li:even')   // 偶数番目
$('li:odd')    // 奇数番目
```

### メソッドチェーン

```javascript
$('#myElement')
    .addClass('active')
    .css('color', 'red')
    .fadeIn(300)
    .text('Updated');
```

---

## DOM操作

### 要素の取得・操作

```javascript
// テキスト取得・設定
$('#myElement').text();           // 取得
$('#myElement').text('New text'); // 設定

// HTML取得・設定
$('#myElement').html();
$('#myElement').html('<strong>Bold</strong>');

// 属性
$('#myElement').attr('data-id');
$('#myElement').attr('data-id', '123');
$('#myElement').removeAttr('data-id');

// クラス
$('#myElement').addClass('active');
$('#myElement').removeClass('active');
$('#myElement').toggleClass('active');
$('#myElement').hasClass('active');

// スタイル
$('#myElement').css('color', 'red');
$('#myElement').css({
    'color': 'red',
    'font-size': '16px'
});
```

### 要素の作成・追加・削除

```javascript
// 作成
const $newDiv = $('<div>').text('Hello');

// 追加
$('#parent').append($newDiv);        // 末尾に追加
$('#parent').prepend($newDiv);       // 先頭に追加
$('#element').after($newDiv);        // 後ろに追加
$('#element').before($newDiv);       // 前に追加

// 削除
$('#myElement').remove();            // 要素を削除
$('#myElement').empty();             // 子要素を全削除
```

### 要素の走査

```javascript
$('#myElement').parent();            // 親
$('#myElement').parents('.container'); // 先祖（フィルタ可）
$('#myElement').children();          // 子
$('#myElement').find('.item');       // 子孫
$('#myElement').siblings();          // 兄弟
$('#myElement').next();              // 次の兄弟
$('#myElement').prev();              // 前の兄弟
```

---

## イベント処理

### イベントリスナー

```javascript
// クリックイベント
$('#button').on('click', function() {
    console.log('Clicked!');
});

// 短縮形
$('#button').click(function() {
    console.log('Clicked!');
});

// 複数イベント
$('#input').on('focus blur', function() {
    $(this).toggleClass('active');
});

// イベント削除
$('#button').off('click');
```

### イベントデリゲーション

```javascript
// 親要素にリスナーを設置
$('#list').on('click', '.item', function() {
    console.log('Item clicked:', $(this).text());
});

// 後から追加される要素にも自動適用
$('#list').append('<li class="item">New Item</li>');
```

### thisの扱い

```javascript
$('.item').on('click', function() {
    // this = DOMエレメント
    console.log(this.textContent);

    // $(this) = jQueryオブジェクト
    $(this).addClass('active');
});
```

---

## Ajax

### $.ajax()

```javascript
$.ajax({
    url: '/api/users',
    method: 'GET',
    dataType: 'json',
    success: function(data) {
        console.log(data);
    },
    error: function(xhr, status, error) {
        console.error(error);
    }
});
```

### 短縮形

```javascript
// GET
$.get('/api/users', function(data) {
    console.log(data);
});

// POST
$.post('/api/users', { name: 'John' }, function(response) {
    console.log(response);
});

// JSON取得
$.getJSON('/api/users', function(data) {
    console.log(data);
});
```

---

## アニメーション

### 基本アニメーション

```javascript
// フェード
$('#element').fadeIn(300);
$('#element').fadeOut(300);
$('#element').fadeToggle(300);
$('#element').fadeTo(300, 0.5); // 透明度指定

// スライド
$('#element').slideDown(300);
$('#element').slideUp(300);
$('#element').slideToggle(300);

// 表示/非表示
$('#element').show(300);
$('#element').hide(300);
$('#element').toggle(300);
```

### カスタムアニメーション

```javascript
$('#element').animate({
    left: '250px',
    opacity: 0.5,
    height: '150px',
    width: '150px'
}, 1000);
```

---

## jQueryとバニラJSの対応表

### セレクタ

| jQuery | バニラJS |
|--------|---------|
| `$('#id')` | `document.getElementById('id')` |
| `$('.class')` | `document.querySelectorAll('.class')` |
| `$('div')` | `document.querySelectorAll('div')` |

### DOM操作

| jQuery | バニラJS |
|--------|---------|
| `$(el).text('text')` | `el.textContent = 'text'` |
| `$(el).html('<b>html</b>')` | `el.innerHTML = '<b>html</b>'` |
| `$(el).addClass('active')` | `el.classList.add('active')` |
| `$(el).removeClass('active')` | `el.classList.remove('active')` |
| `$(el).attr('data-id', '1')` | `el.setAttribute('data-id', '1')` |

### イベント

| jQuery | バニラJS |
|--------|---------|
| `$(el).on('click', fn)` | `el.addEventListener('click', fn)` |
| `$(el).off('click', fn)` | `el.removeEventListener('click', fn)` |
| `$(el).trigger('click')` | `el.click()` |

### Ajax

| jQuery | バニラJS |
|--------|---------|
| `$.ajax({url, success})` | `fetch(url).then(r => r.json())` |
| `$.get(url, callback)` | `fetch(url).then(r => r.json())` |
| `$.post(url, data, callback)` | `fetch(url, {method: 'POST', body})` |

---

## jQueryを使うべきか？

### jQueryが適している場面

- ✅ 既存のjQueryプロジェクトのメンテナンス
- ✅ 古いブラウザ（IE11以下）対応が必要
- ✅ 簡単なDOM操作のみのシンプルなページ

### バニラJSが適している場面

- ✅ 新規プロジェクト
- ✅ モダンブラウザのみ対応
- ✅ パフォーマンス重視
- ✅ React/Vue.js等のフレームワーク使用

### パフォーマンス比較

```javascript
// バニラJS: 速い
document.querySelectorAll('.item').forEach(el => {
    el.classList.add('active');
});

// jQuery: やや遅い（オーバーヘッドあり）
$('.item').addClass('active');
```

---

## 学習ロードマップ

### Week 1: jQuery基礎
- [ ] セレクタとDOM操作
- [ ] イベント処理
- [ ] 既存jQueryコードの読解

### Week 2: 実践
- [ ] jQueryを使ったUI実装
- [ ] Ajax通信
- [ ] アニメーション

### Week 3: バニラJSへの移行
- [ ] jQueryコードをバニラJSに書き換え
- [ ] パフォーマンス比較
- [ ] モダンなアプローチの理解

### Week 4: 応用
- [ ] レガシーコードのリファクタリング
- [ ] 段階的なjQuery削減
- [ ] フレームワークへの移行検討

---

## 参考資料

- [jQuery API Documentation](https://api.jquery.com/)
- [You Might Not Need jQuery](https://youmightnotneedjquery.com/)
- [jQuery → バニラJS 移行ガイド](https://github.com/cferdinandi/smooth-scroll)

---

## 次のステップ

- [jQuery実践ガイド](../../../practices/javascript/jquery-practices.md) - 実装例とパターン集
- バニラJavaScript基礎に戻る
- React/Vue.jsなどのモダンフレームワークへ
