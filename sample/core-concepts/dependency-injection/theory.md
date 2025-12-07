# 依存性注入（Dependency Injection）- 理論

Tags: #design-pattern #dependency-injection #ioc #solid #testability

## 概要
依存性注入（DI）は、オブジェクトが必要とする依存関係を外部から注入する設計パターンです。これにより、クラス間の結合度を下げ、テスタビリティと保守性を向上させます。

## 解決する問題

### 問題: 密結合なコード
```java
public class UserService {
    private UserRepository repository = new UserRepositoryImpl(); // ❌ 密結合
    
    public User findUser(Long id) {
        return repository.findById(id);
    }
}
```

**問題点:**
- `UserService`が`UserRepositoryImpl`の具象クラスに直接依存
- テスト時にモックに差し替えられない
- 実装を変更する際に`UserService`も修正が必要

## 核心的な考え方

### 1. 依存性の外部化
オブジェクトが自分で依存オブジェクトを生成するのではなく、外部から受け取る。

### 2. インターフェースへの依存
具象クラスではなく、インターフェース（抽象）に依存する（依存性逆転の原則）。

### 3. 制御の反転（IoC）
オブジェクトの生成と管理の制御を、アプリケーションコードからフレームワーク（DIコンテナ）に移譲する。

## 詳細説明

### 注入方法の3パターン

#### 1. コンストラクタ注入（推奨）
```java
public class UserService {
    private final UserRepository repository;
    
    // 依存性をコンストラクタで受け取る
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

**メリット:**
- 依存関係が明示的
- 不変（final）にできる
- nullチェック不要（必須依存）

#### 2. セッター注入
```java
public class UserService {
    private UserRepository repository;
    
    public void setRepository(UserRepository repository) {
        this.repository = repository;
    }
}
```

**メリット:**
- オプショナルな依存に適している
- 後から依存を変更可能

**デメリット:**
- 不変にできない
- 依存が必須かオプションか不明確

#### 3. フィールド注入（非推奨）
```java
public class UserService {
    @Autowired
    private UserRepository repository; // ❌ 推奨されない
}
```

**デメリット:**
- テストが困難（Springコンテナなしでインスタンス化できない）
- 依存関係が隠蔽される
- 循環依存に気づきにくい

## メリット

### 1. テスタビリティの向上
```java
@Test
void testFindUser() {
    // モックを簡単に注入できる
    UserRepository mockRepo = mock(UserRepository.class);
    UserService service = new UserService(mockRepo);
    
    when(mockRepo.findById(1L)).thenReturn(new User());
    // テスト実行...
}
```

### 2. 疎結合・高凝集
- クラスが「何をするか」に集中できる
- 「どう作るか」はDIコンテナに任せる

### 3. 保守性の向上
- 実装の差し替えが容易
- 設定ファイルやアノテーションで切り替え可能

## よくある誤解・落とし穴

### 誤解1: DIは常に良い
- シンプルなユーティリティクラスには不要
- 過度な抽象化は逆に複雑性を増す

### 誤解2: DIコンテナ = DI
- DIはパターン、DIコンテナはその実現手段の一つ
- 手動でコンストラクタ注入することもDI

### 落とし穴: 循環依存
```java
class A {
    A(B b) { ... }
}
class B {
    B(A a) { ... } // ❌ 循環依存
}
```
設計を見直すサイン。

## ベストプラクティス

1. **コンストラクタ注入を優先する**
2. **インターフェースに依存する**（具象クラスではなく）
3. **必須依存はコンストラクタ、オプション依存はセッターで**
4. **フィールド注入は避ける**
5. **循環依存が発生したら設計を見直す**

## 関連概念
- [IoC（制御の反転）](../ioc/README.md)
- [SOLID原則 - 依存性逆転の原則](../../design/solid/dip.md)
- [Factory Pattern](../../design/design-patterns/factory.md)

## 参考資料
- Martin Fowler: [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html)
- 『Clean Architecture』Robert C. Martin
- Spring公式ドキュメント
