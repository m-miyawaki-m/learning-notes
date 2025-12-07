# Struts2 フレームワーク概念

> 対象: Struts 2.5.x
> 前提: Java, サーブレット/JSP基礎

## 学習目標

- Struts2のアーキテクチャと動作原理を理解する
- MVCパターンにおけるStruts2の役割を理解する
- Action、Interceptor、Result の概念を理解する
- OGNLとValueStackの仕組みを理解する

---

## Struts2とは

### 概要

**Apache Struts2** は、Java EE Webアプリケーション開発のためのMVCフレームワークです。

### 歴史

- **Struts 1.x**: 2000年代初頭に登場
- **Struts 2.x**: WebWork2と統合して2006年リリース
- **現在**: レガシーシステムで広く使用されているが、新規開発ではSpring MVCが主流

### Struts1 vs Struts2

| 項目 | Struts 1 | Struts 2 |
|------|----------|----------|
| **基盤** | サーブレットAPI依存 | POJO ベース |
| **アクション** | ActionクラスはSingleton | アクションはリクエストごとに生成 |
| **バリデーション** | ActionFormで実装 | アノテーション/XMLで宣言的 |
| **テスト容易性** | 低い | 高い（POJO） |
| **式言語** | JSTL | OGNL |

---

## アーキテクチャ

### MVCパターンにおける役割

```
┌─────────────────────────────────────┐
│          ブラウザ（View）            │
└─────────────────────────────────────┘
                 ↓ リクエスト
┌─────────────────────────────────────┐
│         FilterDispatcher            │ ← フロントコントローラー
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Interceptor Stack              │ ← 横断的処理
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│          Action（Controller）       │ ← ビジネスロジック
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│          Model（Service/DAO）       │ ← データ処理
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│          Result（View）             │ ← JSP表示
└─────────────────────────────────────┘
```

### リクエストライフサイクル

```
1. ブラウザからリクエスト
   ↓
2. FilterDispatcher がリクエストを受け取る
   ↓
3. ActionMapper がアクションを特定
   ↓
4. Interceptor Stack を実行（前処理）
   ↓
5. Action を実行
   ↓
6. Interceptor Stack を実行（後処理）
   ↓
7. Result を実行（JSPレンダリング）
   ↓
8. レスポンスをブラウザに返す
```

---

## 主要コンポーネント

### 1. Action

#### 概念

**Action**は、ユーザーのリクエストを処理するコントローラーです。

#### 特徴

- POJOクラス（特定のクラスを継承する必要なし）
- リクエストごとに新しいインスタンスが生成される
- スレッドセーフ

#### Actionの実装パターン

```java
// パターン1: POJOアクション
public class LoginAction {
    private String username;
    private String password;

    public String execute() {
        // ビジネスロジック
        if ("admin".equals(username) && "password".equals(password)) {
            return "success";
        }
        return "error";
    }

    // getter/setter
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

#### 戻り値の標準定数

```java
// com.opensymphony.xwork2.Action インターフェース
public interface Action {
    String SUCCESS = "success";  // 成功
    String ERROR = "error";      // エラー
    String INPUT = "input";      // 入力画面に戻る
    String LOGIN = "login";      // ログイン画面
    String NONE = "none";        // Resultなし

    String execute() throws Exception;
}
```

### 2. Interceptor（インターセプター）

#### 概念

**Interceptor**は、Actionの実行前後に共通処理を挟み込む仕組みです。

#### 用途

- リクエストパラメータの自動設定
- バリデーション
- ロギング
- セッション管理
- 例外処理
- ファイルアップロード

#### 標準インターセプター

```xml
<!-- struts.xml -->
<action name="login" class="com.example.LoginAction">
    <interceptor-ref name="defaultStack"/>
    <result name="success">/welcome.jsp</result>
    <result name="error">/login.jsp</result>
</action>
```

#### defaultStack の構成

```
defaultStack:
  - exception (例外処理)
  - alias (エイリアス変換)
  - servletConfig (サーブレット情報設定)
  - prepare (準備処理)
  - i18n (国際化)
  - chain (アクションチェーン)
  - modelDriven (モデル駆動)
  - fileUpload (ファイルアップロード)
  - params (パラメータ設定)
  - conversionError (変換エラー)
  - validation (バリデーション)
  - workflow (ワークフロー)
```

#### カスタムインターセプター

```java
public class LoggingInterceptor extends AbstractInterceptor {
    @Override
    public String intercept(ActionInvocation invocation) throws Exception {
        String actionName = invocation.getProxy().getActionName();
        System.out.println("Before Action: " + actionName);

        // Actionを実行
        String result = invocation.invoke();

        System.out.println("After Action: " + actionName + " -> " + result);
        return result;
    }
}
```

### 3. Result（結果）

#### 概念

**Result**は、Actionの実行結果に基づいて表示する画面を決定します。

#### Resultタイプ

| タイプ | 説明 | 用途 |
|--------|------|------|
| **dispatcher** | JSPにフォワード（デフォルト） | 画面表示 |
| **redirect** | リダイレクト | PRGパターン |
| **redirectAction** | 別のアクションにリダイレクト | アクション間遷移 |
| **stream** | バイナリストリーム | ファイルダウンロード |
| **json** | JSON形式 | Ajax |
| **chain** | 別のアクションにチェーン | アクション連携 |

#### Result設定例

```xml
<action name="login" class="com.example.LoginAction">
    <!-- JSPにフォワード -->
    <result name="success">/welcome.jsp</result>

    <!-- リダイレクト -->
    <result name="error" type="redirect">/login.jsp</result>

    <!-- 別のアクションにリダイレクト -->
    <result name="success" type="redirectAction">
        <param name="actionName">dashboard</param>
    </result>
</action>
```

---

## OGNL（Object-Graph Navigation Language）

### 概念

**OGNL**は、Struts2で使用される式言語で、オブジェクトグラフを操作します。

### ValueStack

Struts2の中心的なデータ構造で、リクエストスコープのデータを管理します。

```
ValueStack (LIFO - スタック構造)
┌─────────────────────┐
│  Temporary Objects  │ ← 一時オブジェクト
├─────────────────────┤
│  Action             │ ← 現在のアクション
├─────────────────────┤
│  Model (if exists)  │ ← ModelDrivenの場合
└─────────────────────┘
```

### OGNL式の使用例

#### JSPでの使用

```jsp
<!-- プロパティアクセス -->
<s:property value="username"/>

<!-- ネストしたプロパティ -->
<s:property value="user.address.city"/>

<!-- リストアクセス -->
<s:property value="users[0].name"/>

<!-- Mapアクセス -->
<s:property value="userMap['admin'].name"/>

<!-- メソッド呼び出し -->
<s:property value="user.getName()"/>

<!-- 静的メソッド -->
<s:property value="@com.example.Util@formatDate(date)"/>
```

#### 条件式

```jsp
<s:if test="age >= 18">
    成人です
</s:if>
<s:elseif test="age >= 13">
    未成年です
</s:elseif>
<s:else>
    子供です
</s:else>
```

### ActionContextとValueStack

```java
public class MyAction {
    private String message;

    public String execute() {
        // ValueStackにデータを追加
        ActionContext context = ActionContext.getContext();
        ValueStack stack = context.getValueStack();

        // プッシュ
        stack.push(new User("Alice"));

        // セット
        stack.set("message", "Hello, World!");

        return SUCCESS;
    }
}
```

---

## 設定ファイル

### struts.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE struts PUBLIC
    "-//Apache Software Foundation//DTD Struts Configuration 2.5//EN"
    "http://struts.apache.org/dtds/struts-2.5.dtd">

<struts>
    <!-- 定数設定 -->
    <constant name="struts.devMode" value="true"/>
    <constant name="struts.i18n.encoding" value="UTF-8"/>

    <!-- パッケージ定義 -->
    <package name="default" extends="struts-default">
        <!-- グローバルResult -->
        <global-results>
            <result name="error">/error.jsp</result>
        </global-results>

        <!-- グローバル例外マッピング -->
        <global-exception-mappings>
            <exception-mapping exception="java.lang.Exception"
                             result="error"/>
        </global-exception-mappings>

        <!-- アクション定義 -->
        <action name="login" class="com.example.LoginAction">
            <result name="success">/welcome.jsp</result>
            <result name="input">/login.jsp</result>
        </action>

        <!-- ワイルドカード -->
        <action name="*User" class="com.example.{1}UserAction" method="{1}">
            <result>/{1}User.jsp</result>
        </action>
    </package>
</struts>
```

### web.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         version="3.1">

    <!-- Struts2フィルター -->
    <filter>
        <filter-name>struts2</filter-name>
        <filter-class>
            org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter
        </filter-class>
    </filter>

    <filter-mapping>
        <filter-name>struts2</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

    <!-- ウェルカムファイル -->
    <welcome-file-list>
        <welcome-file>index.jsp</welcome-file>
    </welcome-file-list>
</web-app>
```

---

## バリデーション

### XMLベースのバリデーション

```xml
<!-- LoginAction-validation.xml -->
<!DOCTYPE validators PUBLIC
    "-//Apache Struts//XWork Validator 1.0.3//EN"
    "http://struts.apache.org/dtds/xwork-validator-1.0.3.dtd">

<validators>
    <field name="username">
        <field-validator type="requiredstring">
            <message>ユーザー名は必須です</message>
        </field-validator>
        <field-validator type="stringlength">
            <param name="minLength">4</param>
            <param name="maxLength">20</param>
            <message>ユーザー名は4〜20文字で入力してください</message>
        </field-validator>
    </field>

    <field name="email">
        <field-validator type="requiredstring">
            <message>メールアドレスは必須です</message>
        </field-validator>
        <field-validator type="email">
            <message>正しいメールアドレスを入力してください</message>
        </field-validator>
    </field>
</validators>
```

### アノテーションベースのバリデーション

```java
public class RegisterAction extends ActionSupport {

    @RequiredStringValidator(message = "ユーザー名は必須です")
    @StringLengthFieldValidator(minLength = "4", maxLength = "20",
        message = "ユーザー名は4〜20文字で入力してください")
    private String username;

    @RequiredStringValidator(message = "メールアドレスは必須です")
    @EmailValidator(message = "正しいメールアドレスを入力してください")
    private String email;

    @IntRangeFieldValidator(min = "18", max = "100",
        message = "年齢は18〜100の範囲で入力してください")
    private int age;

    // getter/setter
}
```

---

## 国際化（i18n）

### リソースバンドル

```properties
# messages_ja.properties
login.username=ユーザー名
login.password=パスワード
login.submit=ログイン
error.login.failed=ログインに失敗しました

# messages_en.properties
login.username=Username
login.password=Password
login.submit=Login
error.login.failed=Login failed
```

### JSPでの使用

```jsp
<%@ taglib prefix="s" uri="/struts-tags" %>

<s:form action="login">
    <s:textfield name="username" key="login.username"/>
    <s:password name="password" key="login.password"/>
    <s:submit key="login.submit"/>
</s:form>

<!-- または -->
<s:text name="login.username"/>
```

### Actionでの使用

```java
public class LoginAction extends ActionSupport {
    @Override
    public String execute() {
        if (loginFailed) {
            addActionError(getText("error.login.failed"));
            return INPUT;
        }
        return SUCCESS;
    }
}
```

---

## タグライブラリ

### 主要タグ

#### フォームタグ

```jsp
<!-- テキストフィールド -->
<s:textfield name="username" label="ユーザー名"/>

<!-- パスワード -->
<s:password name="password" label="パスワード"/>

<!-- セレクトボックス -->
<s:select name="country"
          label="国"
          list="countries"
          listKey="code"
          listValue="name"/>

<!-- ラジオボタン -->
<s:radio name="gender"
         label="性別"
         list="{'男性','女性'}"/>

<!-- チェックボックス -->
<s:checkboxlist name="hobbies"
                label="趣味"
                list="hobbies"/>

<!-- 送信ボタン -->
<s:submit value="送信"/>
```

#### 制御タグ

```jsp
<!-- 繰り返し -->
<s:iterator value="users" var="user">
    <s:property value="#user.name"/>
</s:iterator>

<!-- 条件分岐 -->
<s:if test="age >= 18">
    成人
</s:if>
<s:else>
    未成年
</s:else>
```

#### データタグ

```jsp
<!-- プロパティ表示 -->
<s:property value="username"/>

<!-- デフォルト値 -->
<s:property value="description" default="説明なし"/>

<!-- エスケープなし -->
<s:property value="htmlContent" escapeHtml="false"/>
```

---

## セキュリティ

### 脆弱性への対策

#### 1. OGNL インジェクション対策

```xml
<!-- struts.xml -->
<constant name="struts.ognl.allowStaticMethodAccess" value="false"/>
<constant name="struts.enable.DynamicMethodInvocation" value="false"/>
```

#### 2. XSS対策

```jsp
<!-- デフォルトでエスケープされる -->
<s:property value="userInput"/>

<!-- エスケープを無効化する場合（注意）-->
<s:property value="htmlContent" escapeHtml="false"/>
```

#### 3. CSRF対策

```xml
<!-- struts.xml -->
<interceptor-ref name="token"/>

<result name="invalid.token">/error.jsp</result>
```

```jsp
<!-- JSP -->
<s:form action="submitForm">
    <s:token/>
    <!-- フォームフィールド -->
</s:form>
```

---

## 学習ロードマップ

### Week 1: 基礎
- [ ] Struts2のアーキテクチャ理解
- [ ] Actionの作成と設定
- [ ] struts.xml の基本設定
- [ ] JSPでのStruts2タグ使用

### Week 2: 中級
- [ ] Interceptorの理解と活用
- [ ] バリデーションの実装
- [ ] 国際化対応
- [ ] OGNL式の理解

### Week 3: 実践
- [ ] ファイルアップロード
- [ ] Ajax連携
- [ ] セキュリティ対策
- [ ] 実際のアプリケーション開発

### Week 4: 応用
- [ ] カスタムインターセプター作成
- [ ] プラグイン開発
- [ ] 既存システムのメンテナンス
- [ ] Spring連携

---

## 参考資料

- [Apache Struts 2 Documentation](https://struts.apache.org/documentation.html)
- [Struts 2 Core Developers Guide](https://struts.apache.org/core-developers/)
- 書籍『Struts 2 in Action』
- [Struts 2 Security Bulletins](https://struts.apache.org/security/)

---

## よくある問題

### 1. Action が見つからない

```
There is no Action mapped for namespace [/] and action name [login]
```

**原因**: struts.xml の設定ミス

**解決**:
- actionのnameとURLが一致しているか確認
- packageのnamespaceを確認

### 2. Result が見つからない

```
No result defined for action and result input
```

**原因**: Resultの定義漏れ

**解決**:
```xml
<action name="login" class="com.example.LoginAction">
    <result name="input">/login.jsp</result>
</action>
```

### 3. パラメータが設定されない

**原因**: getter/setterの未定義

**解決**: プロパティに対応するgetter/setterを定義

---

## まとめ

### Struts2の主要概念

- **Action**: リクエスト処理（Controller）
- **Interceptor**: 横断的処理
- **Result**: 画面遷移（View）
- **OGNL**: 式言語とValueStack
- **バリデーション**: 入力検証
- **国際化**: 多言語対応

### 現在の位置づけ

- レガシーシステムで広く使用
- 新規開発ではSpring MVCが主流
- セキュリティ脆弱性に注意が必要
- 既存システムのメンテナンススキルとして重要
