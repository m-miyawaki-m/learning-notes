# Ajax と Promise 実践ガイド

> 対象: 現代のJavaScript（ES6+）
> 環境: モダンブラウザ

このドキュメントは、Ajax と Promise を使った実践的な実装パターンとベストプラクティスを記載しています。

---

## 目次

1. [APIクライアントの実装](#apiクライアントの実装)
2. [よくある実装パターン](#よくある実装パターン)
3. [エラーハンドリング戦略](#エラーハンドリング戦略)
4. [パフォーマンス最適化](#パフォーマンス最適化)
5. [実践的な例](#実践的な例)

---

## APIクライアントの実装

### 基本的なAPIクライアント

```javascript
// api-client.js
class APIClient {
    constructor(baseURL, options = {}) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        this.timeout = options.timeout || 30000;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new APIError(
                    `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    await response.text()
                );
            }

            return await response.json();

        } catch (error) {
            if (error.name === 'AbortError') {
                throw new APIError('Request timeout', 408);
            }
            throw error;
        }
    }

    get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// カスタムエラークラス
class APIError extends Error {
    constructor(message, status, body) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.body = body;
    }
}

// 使用例
const api = new APIClient('https://api.example.com', {
    headers: { 'Authorization': 'Bearer token123' },
    timeout: 10000
});

// GET
const users = await api.get('/users', { page: 1, limit: 10 });

// POST
const newUser = await api.post('/users', {
    name: 'Alice',
    email: 'alice@example.com'
});

// PUT
const updated = await api.put('/users/1', { name: 'Alice Smith' });

// DELETE
await api.delete('/users/1');
```

### 認証付きAPIクライアント

```javascript
class AuthenticatedAPIClient extends APIClient {
    constructor(baseURL, options = {}) {
        super(baseURL, options);
        this.token = null;
    }

    setToken(token) {
        this.token = token;
        this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    async login(username, password) {
        const response = await this.post('/auth/login', {
            username,
            password
        });

        this.setToken(response.token);
        return response;
    }

    logout() {
        this.token = null;
        delete this.defaultHeaders['Authorization'];
    }

    async refreshToken() {
        if (!this.token) {
            throw new Error('No token to refresh');
        }

        const response = await this.post('/auth/refresh', {
            token: this.token
        });

        this.setToken(response.token);
        return response;
    }

    async request(endpoint, options = {}) {
        try {
            return await super.request(endpoint, options);
        } catch (error) {
            // 401エラーの場合、トークンリフレッシュを試みる
            if (error.status === 401 && this.token) {
                await this.refreshToken();
                return await super.request(endpoint, options);
            }
            throw error;
        }
    }
}

// 使用例
const authAPI = new AuthenticatedAPIClient('https://api.example.com');

// ログイン
await authAPI.login('alice', 'password123');

// 認証が必要なリクエスト
const profile = await authAPI.get('/users/me');
```

---

## よくある実装パターン

### 1. データフェッチとローディング表示

```javascript
// data-loader.js
class DataLoader {
    constructor(apiClient) {
        this.api = apiClient;
        this.loadingElement = document.getElementById('loading');
        this.errorElement = document.getElementById('error');
        this.contentElement = document.getElementById('content');
    }

    showLoading() {
        this.loadingElement.style.display = 'block';
        this.errorElement.style.display = 'none';
        this.contentElement.style.display = 'none';
    }

    showError(message) {
        this.loadingElement.style.display = 'none';
        this.errorElement.style.display = 'block';
        this.errorElement.textContent = message;
        this.contentElement.style.display = 'none';
    }

    showContent() {
        this.loadingElement.style.display = 'none';
        this.errorElement.style.display = 'none';
        this.contentElement.style.display = 'block';
    }

    async loadData(endpoint, renderFunction) {
        this.showLoading();

        try {
            const data = await this.api.get(endpoint);
            renderFunction(data);
            this.showContent();
        } catch (error) {
            this.showError(`データの読み込みに失敗しました: ${error.message}`);
        }
    }
}

// 使用例
const loader = new DataLoader(api);

function renderUsers(users) {
    const html = users.map(user => `
        <div class="user">
            <h3>${user.name}</h3>
            <p>${user.email}</p>
        </div>
    `).join('');

    document.getElementById('content').innerHTML = html;
}

loader.loadData('/users', renderUsers);
```

### 2. フォーム送信

```javascript
// form-handler.js
class FormHandler {
    constructor(formElement, apiClient) {
        this.form = formElement;
        this.api = apiClient;
        this.submitButton = formElement.querySelector('[type="submit"]');

        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(event) {
        event.preventDefault();

        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());

        this.setLoading(true);
        this.clearErrors();

        try {
            const response = await this.api.post('/users', data);
            this.onSuccess(response);
        } catch (error) {
            this.onError(error);
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(isLoading) {
        this.submitButton.disabled = isLoading;
        this.submitButton.textContent = isLoading ? '送信中...' : '送信';
    }

    clearErrors() {
        const errorElements = this.form.querySelectorAll('.error-message');
        errorElements.forEach(el => el.remove());
    }

    showFieldError(fieldName, message) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        field.parentNode.appendChild(errorElement);
    }

    onSuccess(response) {
        alert('送信成功！');
        this.form.reset();
    }

    onError(error) {
        if (error.status === 422 && error.body) {
            // バリデーションエラー
            const errors = JSON.parse(error.body);
            for (const [field, message] of Object.entries(errors)) {
                this.showFieldError(field, message);
            }
        } else {
            alert(`エラー: ${error.message}`);
        }
    }
}

// 使用例
const form = document.getElementById('userForm');
const formHandler = new FormHandler(form, api);
```

### 3. リアルタイムサーチ（デバウンス）

```javascript
// search-handler.js
class SearchHandler {
    constructor(inputElement, apiClient, options = {}) {
        this.input = inputElement;
        this.api = apiClient;
        this.resultsElement = options.resultsElement;
        this.debounceTime = options.debounceTime || 300;
        this.minLength = options.minLength || 2;

        this.debounceTimer = null;

        this.input.addEventListener('input', (e) => this.handleInput(e));
    }

    handleInput(event) {
        const query = event.target.value.trim();

        // デバウンス処理
        clearTimeout(this.debounceTimer);

        if (query.length < this.minLength) {
            this.clearResults();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, this.debounceTime);
    }

    async search(query) {
        try {
            this.showLoading();

            const results = await this.api.get('/search', { q: query });

            this.displayResults(results);

        } catch (error) {
            this.showError(error.message);
        }
    }

    showLoading() {
        this.resultsElement.innerHTML = '<div class="loading">検索中...</div>';
    }

    displayResults(results) {
        if (results.length === 0) {
            this.resultsElement.innerHTML = '<div>結果がありません</div>';
            return;
        }

        const html = results.map(item => `
            <div class="search-result" data-id="${item.id}">
                <h4>${item.title}</h4>
                <p>${item.description}</p>
            </div>
        `).join('');

        this.resultsElement.innerHTML = html;
    }

    clearResults() {
        this.resultsElement.innerHTML = '';
    }

    showError(message) {
        this.resultsElement.innerHTML = `<div class="error">${message}</div>`;
    }
}

// 使用例
const searchInput = document.getElementById('search');
const searchResults = document.getElementById('results');

const searchHandler = new SearchHandler(searchInput, api, {
    resultsElement: searchResults,
    debounceTime: 500,
    minLength: 3
});
```

### 4. 無限スクロール

```javascript
// infinite-scroll.js
class InfiniteScroll {
    constructor(containerElement, apiClient, options = {}) {
        this.container = containerElement;
        this.api = apiClient;
        this.endpoint = options.endpoint || '/items';
        this.renderItem = options.renderItem;

        this.page = 1;
        this.hasMore = true;
        this.loading = false;

        this.setupObserver();
        this.loadMore();
    }

    setupObserver() {
        // Intersection Observer でスクロール監視
        const sentinel = document.createElement('div');
        sentinel.className = 'scroll-sentinel';
        this.container.appendChild(sentinel);

        this.observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && this.hasMore && !this.loading) {
                this.loadMore();
            }
        }, { threshold: 0.5 });

        this.observer.observe(sentinel);
    }

    async loadMore() {
        if (this.loading || !this.hasMore) return;

        this.loading = true;
        this.showLoading();

        try {
            const response = await this.api.get(this.endpoint, {
                page: this.page,
                limit: 20
            });

            this.appendItems(response.items);

            this.hasMore = response.hasNext;
            this.page++;

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    }

    appendItems(items) {
        const fragment = document.createDocumentFragment();

        items.forEach(item => {
            const element = this.renderItem(item);
            fragment.appendChild(element);
        });

        // センチネル要素の前に挿入
        const sentinel = this.container.querySelector('.scroll-sentinel');
        this.container.insertBefore(fragment, sentinel);
    }

    showLoading() {
        const loader = document.createElement('div');
        loader.className = 'infinite-loader';
        loader.textContent = '読み込み中...';
        this.container.appendChild(loader);
    }

    hideLoading() {
        const loader = this.container.querySelector('.infinite-loader');
        if (loader) loader.remove();
    }

    showError(message) {
        const error = document.createElement('div');
        error.className = 'error';
        error.textContent = `エラー: ${message}`;
        this.container.appendChild(error);
    }
}

// 使用例
const container = document.getElementById('item-list');

function renderItem(item) {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
        <h3>${item.title}</h3>
        <p>${item.description}</p>
    `;
    return div;
}

const scroll = new InfiniteScroll(container, api, {
    endpoint: '/posts',
    renderItem: renderItem
});
```

---

## エラーハンドリング戦略

### グローバルエラーハンドラ

```javascript
// error-handler.js
class GlobalErrorHandler {
    constructor() {
        this.handlers = new Map();
        this.defaultHandler = this.defaultErrorHandler;
    }

    register(errorType, handler) {
        this.handlers.set(errorType, handler);
    }

    handle(error) {
        // ステータスコードに応じたハンドラ
        if (error.status && this.handlers.has(error.status)) {
            return this.handlers.get(error.status)(error);
        }

        // エラータイプに応じたハンドラ
        if (error.name && this.handlers.has(error.name)) {
            return this.handlers.get(error.name)(error);
        }

        // デフォルトハンドラ
        return this.defaultHandler(error);
    }

    defaultErrorHandler(error) {
        console.error('Unhandled error:', error);
        alert(`エラーが発生しました: ${error.message}`);
    }
}

const errorHandler = new GlobalErrorHandler();

// ステータスコード別のハンドラ登録
errorHandler.register(401, (error) => {
    console.log('認証エラー、ログイン画面へリダイレクト');
    window.location.href = '/login';
});

errorHandler.register(403, (error) => {
    alert('アクセス権限がありません');
});

errorHandler.register(404, (error) => {
    alert('リソースが見つかりません');
});

errorHandler.register(500, (error) => {
    alert('サーバーエラーが発生しました。しばらく待ってから再試行してください。');
});

// ネットワークエラー
errorHandler.register('TypeError', (error) => {
    alert('ネットワークエラー。インターネット接続を確認してください。');
});

// 使用例
try {
    const data = await api.get('/users');
} catch (error) {
    errorHandler.handle(error);
}
```

---

## パフォーマンス最適化

### 1. リクエストのキャッシュ

```javascript
// cache-manager.js
class CacheManager {
    constructor(ttl = 60000) { // デフォルト1分
        this.cache = new Map();
        this.ttl = ttl;
    }

    set(key, value) {
        this.cache.set(key, {
            value,
            timestamp: Date.now()
        });
    }

    get(key) {
        const item = this.cache.get(key);

        if (!item) return null;

        // TTL確認
        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }

        return item.value;
    }

    clear() {
        this.cache.clear();
    }
}

// APIクライアントにキャッシュ機能を追加
class CachedAPIClient extends APIClient {
    constructor(baseURL, options = {}) {
        super(baseURL, options);
        this.cache = new CacheManager(options.cacheTTL);
    }

    async get(endpoint, params = {}) {
        const cacheKey = `${endpoint}?${JSON.stringify(params)}`;
        const cached = this.cache.get(cacheKey);

        if (cached) {
            console.log('Cache hit:', cacheKey);
            return cached;
        }

        const data = await super.get(endpoint, params);
        this.cache.set(cacheKey, data);

        return data;
    }

    clearCache() {
        this.cache.clear();
    }
}

// 使用例
const cachedAPI = new CachedAPIClient('https://api.example.com', {
    cacheTTL: 300000 // 5分
});

// 初回はAPIリクエスト
const users1 = await cachedAPI.get('/users');

// 2回目はキャッシュから取得（5分以内）
const users2 = await cachedAPI.get('/users');
```

### 2. リクエストの並列化

```javascript
// 複数のAPIを並列実行
async function loadDashboardData() {
    const [users, posts, comments, stats] = await Promise.all([
        api.get('/users'),
        api.get('/posts'),
        api.get('/comments'),
        api.get('/stats')
    ]);

    return { users, posts, comments, stats };
}

// 使用例
try {
    const dashboardData = await loadDashboardData();
    renderDashboard(dashboardData);
} catch (error) {
    console.error('ダッシュボードデータの読み込みに失敗:', error);
}
```

### 3. リクエストのバッチ処理

```javascript
// request-batcher.js
class RequestBatcher {
    constructor(apiClient, options = {}) {
        this.api = apiClient;
        this.batchSize = options.batchSize || 10;
        this.delay = options.delay || 100;
        this.queue = [];
        this.processing = false;
    }

    add(request) {
        return new Promise((resolve, reject) => {
            this.queue.push({ request, resolve, reject });
            this.process();
        });
    }

    async process() {
        if (this.processing || this.queue.length === 0) return;

        this.processing = true;

        while (this.queue.length > 0) {
            const batch = this.queue.splice(0, this.batchSize);

            try {
                const results = await Promise.allSettled(
                    batch.map(item => item.request())
                );

                results.forEach((result, index) => {
                    if (result.status === 'fulfilled') {
                        batch[index].resolve(result.value);
                    } else {
                        batch[index].reject(result.reason);
                    }
                });

            } catch (error) {
                batch.forEach(item => item.reject(error));
            }

            if (this.queue.length > 0) {
                await new Promise(resolve => setTimeout(resolve, this.delay));
            }
        }

        this.processing = false;
    }
}

// 使用例
const batcher = new RequestBatcher(api, { batchSize: 5, delay: 200 });

// 大量のリクエストを効率的に処理
const userIds = Array.from({ length: 100 }, (_, i) => i + 1);

const users = await Promise.all(
    userIds.map(id =>
        batcher.add(() => api.get(`/users/${id}`))
    )
);
```

---

## 実践的な例

### フルスタックのユーザー管理画面

```javascript
// user-manager.js
class UserManager {
    constructor() {
        this.api = new AuthenticatedAPIClient('https://api.example.com');
        this.loader = new DataLoader(this.api);
        this.currentPage = 1;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUsers();
    }

    setupEventListeners() {
        // 検索
        const searchInput = document.getElementById('search');
        let debounceTimer;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.searchUsers(e.target.value);
            }, 300);
        });

        // 新規作成ボタン
        document.getElementById('createUser').addEventListener('click', () => {
            this.showCreateModal();
        });

        // ページネーション
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadUsers();
            }
        });

        document.getElementById('nextPage').addEventListener('click', () => {
            this.currentPage++;
            this.loadUsers();
        });
    }

    async loadUsers() {
        try {
            this.loader.showLoading();

            const response = await this.api.get('/users', {
                page: this.currentPage,
                limit: 10
            });

            this.renderUsers(response.users);
            this.updatePagination(response.totalPages);

            this.loader.showContent();

        } catch (error) {
            this.loader.showError(error.message);
        }
    }

    async searchUsers(query) {
        if (query.length < 2) {
            this.loadUsers();
            return;
        }

        try {
            const users = await this.api.get('/users/search', { q: query });
            this.renderUsers(users);
        } catch (error) {
            alert(`検索エラー: ${error.message}`);
        }
    }

    renderUsers(users) {
        const tbody = document.getElementById('userTableBody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>
                    <button onclick="userManager.editUser(${user.id})">編集</button>
                    <button onclick="userManager.deleteUser(${user.id})">削除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePagination(totalPages) {
        document.getElementById('currentPage').textContent = this.currentPage;
        document.getElementById('totalPages').textContent = totalPages;

        document.getElementById('prevPage').disabled = this.currentPage === 1;
        document.getElementById('nextPage').disabled = this.currentPage === totalPages;
    }

    async editUser(userId) {
        try {
            const user = await this.api.get(`/users/${userId}`);
            this.showEditModal(user);
        } catch (error) {
            alert(`ユーザー取得エラー: ${error.message}`);
        }
    }

    async deleteUser(userId) {
        if (!confirm('本当に削除しますか？')) return;

        try {
            await this.api.delete(`/users/${userId}`);
            alert('削除しました');
            this.loadUsers();
        } catch (error) {
            alert(`削除エラー: ${error.message}`);
        }
    }

    showCreateModal() {
        // モーダル表示処理
        const modal = document.getElementById('userModal');
        modal.style.display = 'block';

        const form = document.getElementById('userForm');
        form.reset();

        form.onsubmit = async (e) => {
            e.preventDefault();
            await this.createUser(new FormData(form));
        };
    }

    showEditModal(user) {
        // モーダル表示処理
        const modal = document.getElementById('userModal');
        modal.style.display = 'block';

        const form = document.getElementById('userForm');
        form.elements['name'].value = user.name;
        form.elements['email'].value = user.email;

        form.onsubmit = async (e) => {
            e.preventDefault();
            await this.updateUser(user.id, new FormData(form));
        };
    }

    async createUser(formData) {
        const data = Object.fromEntries(formData.entries());

        try {
            await this.api.post('/users', data);
            alert('作成しました');
            document.getElementById('userModal').style.display = 'none';
            this.loadUsers();
        } catch (error) {
            alert(`作成エラー: ${error.message}`);
        }
    }

    async updateUser(userId, formData) {
        const data = Object.fromEntries(formData.entries());

        try {
            await this.api.put(`/users/${userId}`, data);
            alert('更新しました');
            document.getElementById('userModal').style.display = 'none';
            this.loadUsers();
        } catch (error) {
            alert(`更新エラー: ${error.message}`);
        }
    }
}

// 初期化
const userManager = new UserManager();
```

---

## 参考資料

- [MDN - Fetch API](https://developer.mozilla.org/ja/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN - Promise](https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Using_promises)
- [JavaScript.info - Network requests](https://javascript.info/network)

---

## まとめ

### ベストプラクティス

1. **APIクライアントクラスを作成**: 共通処理を集約
2. **エラーハンドリングを統一**: グローバルエラーハンドラ
3. **キャッシュを活用**: 不要なリクエストを削減
4. **並列実行**: Promise.all で効率化
5. **ローディング表示**: UX向上
6. **タイムアウト設定**: ハングを防ぐ
7. **リトライ処理**: 一時的なエラーに対応
