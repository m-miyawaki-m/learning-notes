# Spring Framework での依存性注入実装

Tags: #spring #java #dependency-injection #autowired

## 概要
Spring FrameworkはDIコンテナを提供し、Bean（Springが管理するオブジェクト）の生成・注入・ライフサイクル管理を自動化します。

## 基本実装

### 1. アノテーションベースのBean定義

```java
@Service
public class UserService {
    private final UserRepository repository;
    
    // コンストラクタが1つの場合、@Autowiredは省略可能（Spring 4.3+）
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
    
    public User findUser(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
}
```

```java
@Repository
public class UserRepositoryImpl implements UserRepository {
    @Override
    public Optional<User> findById(Long id) {
        // DB アクセス処理
    }
}
```

### 2. ステレオタイプアノテーション

| アノテーション | 用途 | 層 |
|------------|------|-----|
| `@Component` | 汎用的なBean | - |
| `@Service` | ビジネスロジック | サービス層 |
| `@Repository` | データアクセス | 永続化層 |
| `@Controller` | Webリクエスト処理 | プレゼンテーション層 |

## 注入パターン

### コンストラクタ注入（推奨）

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    
    // 複数の依存がある場合も明示的
    public OrderService(
        OrderRepository orderRepository,
        PaymentService paymentService
    ) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
    }
}
```

**Lombok使用時:**
```java
@Service
@RequiredArgsConstructor  // finalフィールドのコンストラクタを自動生成
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
}
```

### セッター注入

```java
@Service
public class NotificationService {
    private EmailService emailService;
    
    @Autowired(required = false)  // オプショナルな依存
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

## スコープ管理

### Singleton（デフォルト）
```java
@Service
@Scope("singleton")  // 省略可能
public class UserService {
    // アプリケーション全体で1つのインスタンス
}
```

### Prototype
```java
@Service
@Scope("prototype")
public class ReportGenerator {
    // 要求ごとに新しいインスタンス生成
}
```

### Web関連スコープ
```java
@Service
@Scope(value = WebApplicationContext.SCOPE_REQUEST)
public class RequestScopedService {
    // HTTPリクエストごとに新インスタンス
}
```

## 複数Bean管理

### @Qualifier
```java
public interface NotificationSender {
    void send(String message);
}

@Component("emailSender")
public class EmailNotificationSender implements NotificationSender { }

@Component("smsSender")
public class SmsNotificationSender implements NotificationSender { }

@Service
public class NotificationService {
    private final NotificationSender sender;
    
    public NotificationService(
        @Qualifier("emailSender") NotificationSender sender
    ) {
        this.sender = sender;
    }
}
```

### @Primary
```java
@Component
@Primary  // 複数候補がある場合、これを優先
public class EmailNotificationSender implements NotificationSender { }

@Component
public class SmsNotificationSender implements NotificationSender { }

@Service
public class NotificationService {
    // @Primary が付いた EmailNotificationSender が注入される
    public NotificationService(NotificationSender sender) { }
}
```

## Java Configuration

```java
@Configuration
public class AppConfig {
    
    @Bean
    public UserService userService(UserRepository repository) {
        return new UserService(repository);
    }
    
    @Bean
    @Profile("dev")  // 開発環境でのみ有効
    public DataSource devDataSource() {
        // H2などの開発用DB設定
    }
    
    @Bean
    @Profile("prod")  // 本番環境でのみ有効
    public DataSource prodDataSource() {
        // 本番DB設定
    }
}
```

## 条件付きBean登録

```java
@Configuration
public class CacheConfig {
    
    @Bean
    @ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("users");
    }
}
```

## 循環依存の解決

### 問題のあるコード
```java
@Service
public class ServiceA {
    public ServiceA(ServiceB b) { }  // ❌
}

@Service
public class ServiceB {
    public ServiceB(ServiceA a) { }  // ❌ 循環依存
}
```

### 解決策1: セッター注入に変更
```java
@Service
public class ServiceA {
    private ServiceB serviceB;
    
    @Autowired
    public void setServiceB(ServiceB serviceB) {
        this.serviceB = serviceB;
    }
}
```

### 解決策2: @Lazy
```java
@Service
public class ServiceA {
    public ServiceA(@Lazy ServiceB b) { }  // 遅延初期化
}
```

### 解決策3: 設計を見直す（推奨）
循環依存は設計の問題を示すサイン。責務の分離を再検討する。

## テストでのDI

### 単体テスト（Spring不要）
```java
class UserServiceTest {
    @Test
    void testFindUser() {
        // モックを直接注入
        UserRepository mockRepo = mock(UserRepository.class);
        UserService service = new UserService(mockRepo);
        
        when(mockRepo.findById(1L)).thenReturn(Optional.of(new User()));
        
        User result = service.findUser(1L);
        assertNotNull(result);
    }
}
```

### 統合テスト（Springコンテナ使用）
```java
@SpringBootTest
class UserServiceIntegrationTest {
    @Autowired
    private UserService userService;
    
    @MockBean  // Springコンテキスト内でモック化
    private UserRepository repository;
    
    @Test
    void testFindUser() {
        when(repository.findById(1L)).thenReturn(Optional.of(new User()));
        
        User result = userService.findUser(1L);
        assertNotNull(result);
    }
}
```

## よくあるトラブルシューティング

### NoSuchBeanDefinitionException
```
No qualifying bean of type 'UserRepository' available
```
**原因**: Beanがコンテナに登録されていない
**解決**: `@Component`系アノテーションの付け忘れ、ComponentScan範囲外

### NoUniqueBeanDefinitionException
```
expected single matching bean but found 2
```
**原因**: 同じ型のBeanが複数存在
**解決**: `@Qualifier`または`@Primary`を使用

### BeanCurrentlyInCreationException
```
Requested bean is currently in creation: Is there an unresolvable circular reference?
```
**原因**: 循環依存
**解決**: 設計見直し、または`@Lazy`使用

## ベストプラクティス

1. **コンストラクタ注入を優先**（不変性、必須依存の明示化）
2. **Lombokの`@RequiredArgsConstructor`で簡潔に**
3. **フィールド注入は避ける**（テスタビリティ低下）
4. **適切なステレオタイプアノテーションを使う**（可読性）
5. **循環依存は設計を見直すサイン**

## 関連ファイル
- [依存性注入の理論](./theory.md)
- [学習計画](./README.md)

## 参考資料
- [Spring Framework Reference - The IoC Container](https://docs.spring.io/spring-framework/reference/core/beans.html)
- [Baeldung - Spring Dependency Injection](https://www.baeldung.com/spring-dependency-injection)
