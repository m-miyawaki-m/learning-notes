# jQuery 実践ガイド

> 対象: jQuery 3.x
> 環境: 実務でのjQuery使用、バニラJSへの移行

このドキュメントは、jQueryの実践的な使用方法と、バニラJavaScriptへの移行パターンを記載しています。

---

## 目次

1. [導入とセットアップ](#導入とセットアップ)
2. [よくある実装パターン](#よくある実装パターン)
3. [バニラJSへの移行](#バニラjsへの移行)
4. [レガシーコードのリファクタリング](#レガシーコードのリファクタリング)
5. [トラブルシューティング](#トラブルシューティング)

---

## 導入とセットアップ

### CDN経由（開発・検証用）

```html
<!DOCTYPE html>
<html>
<head>
    <title>jQuery Example</title>
</head>
<body>
    <h1>Hello jQuery</h1>

    <!-- jQuery CDN -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

    <script>
    $(document).ready(function() {
        console.log('jQuery loaded!');
        console.log('jQuery version:', $.fn.jquery);
    });
    </script>
</body>
</html>
```

### npmでインストール（本番環境）

```bash
npm install jquery
```

```javascript
// ES6モジュール
import $ from 'jquery';

$(document).ready(function() {
    console.log('jQuery loaded via npm!');
});
```

### バージョン確認

```javascript
console.log($.fn.jquery); // "3.7.1"
```

---

## よくある実装パターン

### 1. フォームバリデーション

```javascript
$(document).ready(function() {
    $('#myForm').on('submit', function(e) {
        e.preventDefault();

        const name = $('#name').val().trim();
        const email = $('#email').val().trim();

        // バリデーション
        if (name === '') {
            alert('名前を入力してください');
            $('#name').focus();
            return false;
        }

        if (!isValidEmail(email)) {
            alert('有効なメールアドレスを入力してください');
            $('#email').focus();
            return false;
        }

        // 送信
        this.submit();
    });

    function isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
});
```

### 2. 動的テーブルの行追加・削除

```html
<table id="userTable">
    <thead>
        <tr>
            <th>名前</th>
            <th>メール</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        <!-- 行が追加される -->
    </tbody>
</table>
<button id="addRow">行追加</button>
```

```javascript
$(document).ready(function() {
    // 行追加
    $('#addRow').on('click', function() {
        const $row = $('<tr>')
            .append($('<td>').html('<input type="text" name="name[]">'))
            .append($('<td>').html('<input type="email" name="email[]">'))
            .append($('<td>').html('<button class="delete-btn">削除</button>'));

        $('#userTable tbody').append($row);
    });

    // 行削除（イベントデリゲーション）
    $('#userTable').on('click', '.delete-btn', function() {
        $(this).closest('tr').remove();
    });
});
```

### 3. Ajaxでデータ取得・表示

```javascript
$(document).ready(function() {
    $('#loadUsers').on('click', function() {
        $.ajax({
            url: '/api/users',
            method: 'GET',
            dataType: 'json',
            beforeSend: function() {
                $('#loading').show();
            },
            success: function(users) {
                displayUsers(users);
            },
            error: function(xhr, status, error) {
                alert('エラーが発生しました: ' + error);
            },
            complete: function() {
                $('#loading').hide();
            }
        });
    });

    function displayUsers(users) {
        const $tbody = $('#userTable tbody').empty();

        users.forEach(function(user) {
            const $row = $('<tr>')
                .append($('<td>').text(user.id))
                .append($('<td>').text(user.name))
                .append($('<td>').text(user.email));

            $tbody.append($row);
        });
    }
});
```

### 4. モーダルウィンドウ

```html
<button id="openModal">モーダルを開く</button>

<div id="modal" class="modal" style="display: none;">
    <div class="modal-content">
        <span class="close">&times;</span>
        <h2>モーダルタイトル</h2>
        <p>モーダルの内容</p>
    </div>
</div>
```

```css
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: white;
    margin: 15% auto;
    padding: 20px;
    width: 50%;
    border-radius: 8px;
}

.close {
    float: right;
    font-size: 28px;
    cursor: pointer;
}
```

```javascript
$(document).ready(function() {
    // モーダルを開く
    $('#openModal').on('click', function() {
        $('#modal').fadeIn(300);
    });

    // 閉じるボタン
    $('.close').on('click', function() {
        $('#modal').fadeOut(300);
    });

    // 背景クリックで閉じる
    $('#modal').on('click', function(e) {
        if (e.target.id === 'modal') {
            $(this).fadeOut(300);
        }
    });

    // Escキーで閉じる
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('#modal').fadeOut(300);
        }
    });
});
```

### 5. タブ切り替え

```html
<div class="tabs">
    <button class="tab-btn active" data-tab="tab1">タブ1</button>
    <button class="tab-btn" data-tab="tab2">タブ2</button>
    <button class="tab-btn" data-tab="tab3">タブ3</button>
</div>

<div id="tab1" class="tab-content active">タブ1の内容</div>
<div id="tab2" class="tab-content">タブ2の内容</div>
<div id="tab3" class="tab-content">タブ3の内容</div>
```

```javascript
$(document).ready(function() {
    $('.tab-btn').on('click', function() {
        const tabId = $(this).data('tab');

        // 全タブボタンの active を削除
        $('.tab-btn').removeClass('active');
        // クリックされたボタンに active を追加
        $(this).addClass('active');

        // 全タブコンテンツを非表示
        $('.tab-content').removeClass('active').hide();
        // 選択されたタブコンテンツを表示
        $('#' + tabId).addClass('active').fadeIn(300);
    });
});
```

### 6. オートコンプリート（簡易版）

```html
<input type="text" id="searchInput" placeholder="検索...">
<ul id="suggestions" style="display: none;"></ul>
```

```javascript
$(document).ready(function() {
    const users = ['Alice', 'Bob', 'Charlie', 'David', 'Eve'];

    $('#searchInput').on('input', function() {
        const query = $(this).val().toLowerCase();

        if (query.length === 0) {
            $('#suggestions').hide().empty();
            return;
        }

        const filtered = users.filter(user =>
            user.toLowerCase().includes(query)
        );

        if (filtered.length === 0) {
            $('#suggestions').hide().empty();
            return;
        }

        const $list = $('#suggestions').empty();

        filtered.forEach(function(user) {
            $list.append(
                $('<li>')
                    .text(user)
                    .on('click', function() {
                        $('#searchInput').val(user);
                        $('#suggestions').hide();
                    })
            );
        });

        $list.show();
    });

    // 外側クリックで閉じる
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#searchInput, #suggestions').length) {
            $('#suggestions').hide();
        }
    });
});
```

---

## バニラJSへの移行

### セレクタの置き換え

```javascript
// jQuery
const $element = $('#myId');
const $elements = $('.myClass');

// バニラJS
const element = document.getElementById('myId');
const elements = document.querySelectorAll('.myClass');
```

### DOM操作の置き換え

```javascript
// jQuery
$('#myElement').text('Hello');
$('#myElement').html('<strong>Bold</strong>');
$('#myElement').addClass('active');

// バニラJS
document.getElementById('myElement').textContent = 'Hello';
document.getElementById('myElement').innerHTML = '<strong>Bold</strong>';
document.getElementById('myElement').classList.add('active');
```

### イベントの置き換え

```javascript
// jQuery
$('#button').on('click', function() {
    console.log('Clicked');
});

// バニラJS
document.getElementById('button').addEventListener('click', function() {
    console.log('Clicked');
});
```

### Ajaxの置き換え

```javascript
// jQuery
$.ajax({
    url: '/api/users',
    method: 'GET',
    success: function(data) {
        console.log(data);
    },
    error: function(error) {
        console.error(error);
    }
});

// バニラJS（Fetch API）
fetch('/api/users')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
```

### アニメーションの置き換え

```javascript
// jQuery
$('#element').fadeIn(300);

// バニラJS（CSS Transition）
const element = document.getElementById('element');
element.style.opacity = '0';
element.style.display = 'block';

setTimeout(() => {
    element.style.transition = 'opacity 0.3s';
    element.style.opacity = '1';
}, 10);

// または Web Animations API
element.animate([
    { opacity: 0 },
    { opacity: 1 }
], {
    duration: 300,
    fill: 'forwards'
});
```

---

## レガシーコードのリファクタリング

### Before: jQuery依存コード

```javascript
// レガシーコード（jQuery）
$(document).ready(function() {
    $('#submitBtn').on('click', function() {
        const name = $('#name').val();
        const email = $('#email').val();

        $.ajax({
            url: '/api/users',
            method: 'POST',
            data: { name: name, email: email },
            success: function(response) {
                $('#message').text('保存しました').fadeIn();
            }
        });
    });
});
```

### After: バニラJS

```javascript
// モダンなバニラJS
document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submitBtn');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const message = document.getElementById('message');

    submitBtn.addEventListener('click', async () => {
        const userData = {
            name: nameInput.value,
            email: emailInput.value
        };

        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                message.textContent = '保存しました';
                message.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
```

### 段階的な移行戦略

#### Step 1: 新規コードはバニラJSで書く

```javascript
// 新機能はバニラJSで実装
document.getElementById('newFeature').addEventListener('click', () => {
    // 新しいコード
});

// 既存のjQueryコードはそのまま
$('#oldFeature').on('click', function() {
    // 既存コード（後で移行）
});
```

#### Step 2: ユーティリティ関数を作成

```javascript
// utils.js - jQueryライクなヘルパー
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

function addClass(el, className) {
    el.classList.add(className);
}

function removeClass(el, className) {
    el.classList.remove(className);
}

// 使用例
const element = $('#myElement');
addClass(element, 'active');
```

#### Step 3: 機能単位で移行

```javascript
// モジュール化して段階的に移行
// form-handler.js (バニラJS)
export function initFormHandler() {
    const form = document.getElementById('myForm');
    form.addEventListener('submit', handleSubmit);
}

// main.js
import { initFormHandler } from './form-handler.js';

$(document).ready(function() {
    // 新規機能（バニラJS）
    initFormHandler();

    // 既存機能（jQuery - 後で移行）
    $('#legacyFeature').on('click', function() {
        // ...
    });
});
```

---

## トラブルシューティング

### $ is not defined

```javascript
// 原因: jQueryが読み込まれていない

// 解決1: CDNを確認
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

// 解決2: jQuery.noConflict()
var $j = jQuery.noConflict();
$j(document).ready(function() {
    $j('#myElement').text('Hello');
});
```

### DOM要素が見つからない

```javascript
// ❌ 問題: DOMが読み込まれる前に実行
$('#myElement').text('Hello'); // 要素が存在しない

// ✅ 解決: $(document).ready()を使用
$(document).ready(function() {
    $('#myElement').text('Hello');
});
```

### イベントハンドラーが動作しない

```javascript
// ❌ 問題: 動的に追加された要素にイベントが効かない
$('.button').on('click', function() {
    console.log('Clicked');
});

// 後から追加（イベントが効かない）
$('body').append('<button class="button">Click me</button>');

// ✅ 解決: イベントデリゲーション
$(document).on('click', '.button', function() {
    console.log('Clicked');
});
```

### Ajaxリクエストが失敗

```javascript
$.ajax({
    url: '/api/users',
    method: 'POST',
    data: JSON.stringify({ name: 'John' }), // ❌ 文字列化は不要
    contentType: 'application/json', // ✅ これを追加
    success: function(data) {
        console.log(data);
    }
});

// または
$.ajax({
    url: '/api/users',
    method: 'POST',
    data: { name: 'John' }, // オブジェクトのまま渡す
    success: function(data) {
        console.log(data);
    }
});
```

---

## ベストプラクティス

### 1. $(document).ready()は1回だけ

```javascript
// ❌ 避ける
$(document).ready(function() { /* ... */ });
$(document).ready(function() { /* ... */ });
$(document).ready(function() { /* ... */ });

// ✅ 推奨
$(document).ready(function() {
    init();
});

function init() {
    initEventHandlers();
    loadData();
    // ...
}
```

### 2. jQueryオブジェクトをキャッシュ

```javascript
// ❌ 非効率（毎回DOM検索）
$('#myElement').addClass('active');
$('#myElement').css('color', 'red');
$('#myElement').text('Hello');

// ✅ 効率的（1回の検索）
const $element = $('#myElement');
$element.addClass('active');
$element.css('color', 'red');
$element.text('Hello');

// または
$('#myElement')
    .addClass('active')
    .css('color', 'red')
    .text('Hello');
```

### 3. イベントデリゲーションを活用

```javascript
// ❌ 各要素にリスナー
$('.button').each(function() {
    $(this).on('click', function() { /* ... */ });
});

// ✅ 親要素に1つだけ
$(document).on('click', '.button', function() { /* ... */ });
```

---

## 参考資料

- [jQuery API Documentation](https://api.jquery.com/)
- [You Might Not Need jQuery](https://youmightnotneedjquery.com/)
- [jQuery to JavaScript](https://tobiasahlin.com/blog/move-from-jquery-to-vanilla-javascript/)

---

## チートシート

### jQuery → バニラJS クイックリファレンス

```javascript
// セレクタ
$('#id')              → document.getElementById('id')
$('.class')           → document.querySelectorAll('.class')

// テキスト
$(el).text()          → el.textContent
$(el).text('text')    → el.textContent = 'text'

// HTML
$(el).html()          → el.innerHTML
$(el).html('<b>html</b>') → el.innerHTML = '<b>html</b>'

// クラス
$(el).addClass('active')    → el.classList.add('active')
$(el).removeClass('active') → el.classList.remove('active')
$(el).toggleClass('active') → el.classList.toggle('active')

// イベント
$(el).on('click', fn)  → el.addEventListener('click', fn)
$(el).off('click', fn) → el.removeEventListener('click', fn)

// Ajax
$.get(url, callback)   → fetch(url).then(r => r.json()).then(callback)
```
