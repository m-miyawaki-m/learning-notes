# Struts2 実装ガイド

> 対象: Struts 2.5.x
> 環境: Tomcat 9.x, Maven/Gradle

このドキュメントは、Struts2を使った実践的な実装方法とパターンを記載しています。

---

## 目次

1. [プロジェクトセットアップ](#プロジェクトセットアップ)
2. [基本的なCRUD実装](#基本的なcrud実装)
3. [よくある実装パターン](#よくある実装パターン)
4. [ファイルアップロード](#ファイルアップロード)
5. [Ajax連携](#ajax連携)
6. [Spring連携](#spring連携)
7. [トラブルシューティング](#トラブルシューティング)

---

## プロジェクトセットアップ

### Maven依存関係

```xml
<!-- pom.xml -->
<properties>
    <struts2.version>2.5.30</struts2.version>
</properties>

<dependencies>
    <!-- Struts2 Core -->
    <dependency>
        <groupId>org.apache.struts</groupId>
        <artifactId>struts2-core</artifactId>
        <version>${struts2.version}</version>
    </dependency>

    <!-- Convention Plugin（アノテーションベース設定） -->
    <dependency>
        <groupId>org.apache.struts</groupId>
        <artifactId>struts2-convention-plugin</artifactId>
        <version>${struts2.version}</version>
    </dependency>

    <!-- JSON Plugin（Ajax用） -->
    <dependency>
        <groupId>org.apache.struts</groupId>
        <artifactId>struts2-json-plugin</artifactId>
        <version>${struts2.version}</version>
    </dependency>

    <!-- Spring Plugin -->
    <dependency>
        <groupId>org.apache.struts</groupId>
        <artifactId>struts2-spring-plugin</artifactId>
        <version>${struts2.version}</version>
    </dependency>

    <!-- サーブレットAPI -->
    <dependency>
        <groupId>javax.servlet</groupId>
        <artifactId>javax.servlet-api</artifactId>
        <version>4.0.1</version>
        <scope>provided</scope>
    </dependency>

    <!-- JSP/JSTL -->
    <dependency>
        <groupId>javax.servlet.jsp</groupId>
        <artifactId>javax.servlet.jsp-api</artifactId>
        <version>2.3.3</version>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

### Gradle依存関係

```gradle
// build.gradle
ext {
    struts2Version = '2.5.30'
}

dependencies {
    implementation "org.apache.struts:struts2-core:${struts2Version}"
    implementation "org.apache.struts:struts2-convention-plugin:${struts2Version}"
    implementation "org.apache.struts:struts2-json-plugin:${struts2Version}"
    implementation "org.apache.struts:struts2-spring-plugin:${struts2Version}"

    providedCompile 'javax.servlet:javax.servlet-api:4.0.1'
    providedCompile 'javax.servlet.jsp:javax.servlet.jsp-api:2.3.3'
}
```

### プロジェクト構成

```
src/
├── main/
│   ├── java/
│   │   └── com/example/
│   │       ├── action/
│   │       │   ├── UserAction.java
│   │       │   └── LoginAction.java
│   │       ├── model/
│   │       │   └── User.java
│   │       ├── service/
│   │       │   └── UserService.java
│   │       └── interceptor/
│   │           └── AuthInterceptor.java
│   ├── resources/
│   │   ├── struts.xml
│   │   ├── messages.properties
│   │   └── log4j2.xml
│   └── webapp/
│       ├── WEB-INF/
│       │   └── web.xml
│       ├── jsp/
│       │   ├── login.jsp
│       │   ├── userList.jsp
│       │   └── userForm.jsp
│       ├── css/
│       ├── js/
│       └── index.jsp
└── test/
    └── java/
        └── com/example/action/
            └── UserActionTest.java
```

---

## 基本的なCRUD実装

### Model

```java
// User.java
package com.example.model;

public class User {
    private Long id;
    private String username;
    private String email;
    private int age;

    // コンストラクタ
    public User() {}

    public User(Long id, String username, String email, int age) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.age = age;
    }

    // getter/setter
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}
```

### Service

```java
// UserService.java
package com.example.service;

import com.example.model.User;
import java.util.*;

public class UserService {
    private Map<Long, User> users = new HashMap<>();
    private Long nextId = 1L;

    public UserService() {
        // ダミーデータ
        users.put(1L, new User(1L, "alice", "alice@example.com", 30));
        users.put(2L, new User(2L, "bob", "bob@example.com", 25));
        nextId = 3L;
    }

    public List<User> findAll() {
        return new ArrayList<>(users.values());
    }

    public User findById(Long id) {
        return users.get(id);
    }

    public void save(User user) {
        if (user.getId() == null) {
            user.setId(nextId++);
        }
        users.put(user.getId(), user);
    }

    public void delete(Long id) {
        users.remove(id);
    }
}
```

### Action（CRUD）

```java
// UserAction.java
package com.example.action;

import com.example.model.User;
import com.example.service.UserService;
import com.opensymphony.xwork2.ActionSupport;
import com.opensymphony.xwork2.ModelDriven;
import com.opensymphony.xwork2.Preparable;

import java.util.List;

public class UserAction extends ActionSupport implements ModelDriven<User>, Preparable {

    private UserService userService = new UserService();
    private User user = new User();
    private List<User> users;
    private Long id;

    // ModelDrivenの実装
    @Override
    public User getModel() {
        return user;
    }

    // Preparableの実装（各メソッド実行前に呼ばれる）
    @Override
    public void prepare() throws Exception {
        if (id != null) {
            user = userService.findById(id);
            if (user == null) {
                user = new User();
            }
        }
    }

    // 一覧表示
    public String list() {
        users = userService.findAll();
        return SUCCESS;
    }

    // 新規作成フォーム表示
    public String create() {
        return INPUT;
    }

    // 編集フォーム表示
    public String edit() {
        if (user == null || user.getId() == null) {
            addActionError("ユーザーが見つかりません");
            return ERROR;
        }
        return INPUT;
    }

    // 保存（新規作成・更新共通）
    public String save() {
        // バリデーション
        if (user.getUsername() == null || user.getUsername().trim().isEmpty()) {
            addFieldError("username", "ユーザー名は必須です");
            return INPUT;
        }

        try {
            userService.save(user);
            addActionMessage("ユーザーを保存しました");
            return SUCCESS;
        } catch (Exception e) {
            addActionError("保存に失敗しました: " + e.getMessage());
            return ERROR;
        }
    }

    // 削除
    public String delete() {
        if (id == null) {
            addActionError("IDが指定されていません");
            return ERROR;
        }

        try {
            userService.delete(id);
            addActionMessage("ユーザーを削除しました");
            return SUCCESS;
        } catch (Exception e) {
            addActionError("削除に失敗しました: " + e.getMessage());
            return ERROR;
        }
    }

    // getter/setter
    public List<User> getUsers() { return users; }
    public void setUsers(List<User> users) { this.users = users; }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
}
```

### struts.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE struts PUBLIC
    "-//Apache Software Foundation//DTD Struts Configuration 2.5//EN"
    "http://struts.apache.org/dtds/struts-2.5.dtd">

<struts>
    <constant name="struts.devMode" value="true"/>
    <constant name="struts.i18n.encoding" value="UTF-8"/>
    <constant name="struts.ui.theme" value="simple"/>

    <package name="default" extends="struts-default">
        <!-- ユーザー一覧 -->
        <action name="userList" class="com.example.action.UserAction" method="list">
            <result>/jsp/userList.jsp</result>
        </action>

        <!-- 新規作成フォーム -->
        <action name="userCreate" class="com.example.action.UserAction" method="create">
            <result name="input">/jsp/userForm.jsp</result>
        </action>

        <!-- 編集フォーム -->
        <action name="userEdit" class="com.example.action.UserAction" method="edit">
            <result name="input">/jsp/userForm.jsp</result>
            <result name="error" type="redirectAction">userList</result>
        </action>

        <!-- 保存 -->
        <action name="userSave" class="com.example.action.UserAction" method="save">
            <result type="redirectAction">userList</result>
            <result name="input">/jsp/userForm.jsp</result>
            <result name="error">/jsp/userForm.jsp</result>
        </action>

        <!-- 削除 -->
        <action name="userDelete" class="com.example.action.UserAction" method="delete">
            <result type="redirectAction">userList</result>
            <result name="error" type="redirectAction">userList</result>
        </action>
    </package>
</struts>
```

### JSP（一覧画面）

```jsp
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<html>
<head>
    <title>ユーザー一覧</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>ユーザー一覧</h1>

    <!-- メッセージ表示 -->
    <s:if test="hasActionMessages()">
        <div style="color: green;">
            <s:actionmessage/>
        </div>
    </s:if>
    <s:if test="hasActionErrors()">
        <div style="color: red;">
            <s:actionerror/>
        </div>
    </s:if>

    <!-- 新規作成ボタン -->
    <p>
        <s:a action="userCreate">新規作成</s:a>
    </p>

    <!-- ユーザー一覧テーブル -->
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>ユーザー名</th>
                <th>メール</th>
                <th>年齢</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <s:iterator value="users" var="user">
                <tr>
                    <td><s:property value="#user.id"/></td>
                    <td><s:property value="#user.username"/></td>
                    <td><s:property value="#user.email"/></td>
                    <td><s:property value="#user.age"/></td>
                    <td>
                        <s:url action="userEdit" var="editUrl">
                            <s:param name="id" value="#user.id"/>
                        </s:url>
                        <s:a href="%{editUrl}">編集</s:a> |

                        <s:url action="userDelete" var="deleteUrl">
                            <s:param name="id" value="#user.id"/>
                        </s:url>
                        <s:a href="%{deleteUrl}"
                             onclick="return confirm('本当に削除しますか？')">削除</s:a>
                    </td>
                </tr>
            </s:iterator>
        </tbody>
    </table>
</body>
</html>
```

### JSP（フォーム画面）

```jsp
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<html>
<head>
    <title>ユーザー登録・編集</title>
    <style>
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 120px; }
        input[type="text"], input[type="email"], input[type="number"] {
            width: 300px; padding: 5px;
        }
        .error { color: red; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1><s:if test="id == null">新規作成</s:if><s:else>編集</s:else></h1>

    <!-- エラーメッセージ -->
    <s:if test="hasFieldErrors()">
        <div style="color: red;">
            <s:fielderror/>
        </div>
    </s:if>

    <!-- フォーム -->
    <s:form action="userSave" method="post">
        <s:hidden name="id"/>

        <div class="form-group">
            <s:textfield name="username"
                         label="ユーザー名"
                         required="true"/>
        </div>

        <div class="form-group">
            <s:textfield name="email"
                         label="メールアドレス"
                         type="email"/>
        </div>

        <div class="form-group">
            <s:textfield name="age"
                         label="年齢"
                         type="number"/>
        </div>

        <div class="form-group">
            <s:submit value="保存"/>
            <s:a action="userList">キャンセル</s:a>
        </div>
    </s:form>
</body>
</html>
```

---

## よくある実装パターン

### 1. ログイン認証

```java
// LoginAction.java
public class LoginAction extends ActionSupport {
    private String username;
    private String password;

    @Override
    public String execute() {
        // 認証ロジック（実際はDBチェック）
        if ("admin".equals(username) && "password".equals(password)) {
            Map<String, Object> session = ActionContext.getContext().getSession();
            session.put("username", username);
            session.put("loggedIn", true);

            return SUCCESS;
        } else {
            addActionError("ユーザー名またはパスワードが間違っています");
            return INPUT;
        }
    }

    // getter/setter
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

### 2. ログアウト

```java
// LogoutAction.java
public class LogoutAction extends ActionSupport {
    @Override
    public String execute() {
        Map<String, Object> session = ActionContext.getContext().getSession();
        session.clear();
        return SUCCESS;
    }
}
```

### 3. 認証インターセプター

```java
// AuthInterceptor.java
package com.example.interceptor;

import com.opensymphony.xwork2.ActionInvocation;
import com.opensymphony.xwork2.interceptor.AbstractInterceptor;

import java.util.Map;

public class AuthInterceptor extends AbstractInterceptor {

    @Override
    public String intercept(ActionInvocation invocation) throws Exception {
        Map<String, Object> session = invocation.getInvocationContext().getSession();
        Boolean loggedIn = (Boolean) session.get("loggedIn");

        if (loggedIn == null || !loggedIn) {
            return "login";
        }

        return invocation.invoke();
    }
}
```

```xml
<!-- struts.xml -->
<package name="secure" extends="struts-default">
    <interceptors>
        <interceptor name="auth" class="com.example.interceptor.AuthInterceptor"/>

        <interceptor-stack name="secureStack">
            <interceptor-ref name="auth"/>
            <interceptor-ref name="defaultStack"/>
        </interceptor-stack>
    </interceptors>

    <default-interceptor-ref name="secureStack"/>

    <global-results>
        <result name="login" type="redirect">/login.jsp</result>
    </global-results>

    <!-- 認証が必要なアクション -->
    <action name="dashboard" class="com.example.action.DashboardAction">
        <result>/jsp/dashboard.jsp</result>
    </action>
</package>

<!-- ログインは認証不要 -->
<package name="public" extends="struts-default">
    <action name="login" class="com.example.action.LoginAction">
        <result name="success" type="redirectAction">
            <param name="actionName">dashboard</param>
            <param name="namespace">/</param>
        </result>
        <result name="input">/login.jsp</result>
    </action>
</package>
```

---

## ファイルアップロード

### Action

```java
// FileUploadAction.java
public class FileUploadAction extends ActionSupport {
    private File upload;              // アップロードされたファイル
    private String uploadContentType; // MIMEタイプ
    private String uploadFileName;    // ファイル名

    @Override
    public String execute() {
        try {
            // 保存先ディレクトリ
            String uploadPath = ServletActionContext.getServletContext()
                .getRealPath("/uploads");
            File uploadDir = new File(uploadPath);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            // ファイル保存
            File destFile = new File(uploadDir, uploadFileName);
            FileUtils.copyFile(upload, destFile);

            addActionMessage("ファイルをアップロードしました: " + uploadFileName);
            return SUCCESS;

        } catch (Exception e) {
            addActionError("アップロードに失敗しました: " + e.getMessage());
            return ERROR;
        }
    }

    // getter/setter
    public File getUpload() { return upload; }
    public void setUpload(File upload) { this.upload = upload; }

    public String getUploadContentType() { return uploadContentType; }
    public void setUploadContentType(String uploadContentType) {
        this.uploadContentType = uploadContentType;
    }

    public String getUploadFileName() { return uploadFileName; }
    public void setUploadFileName(String uploadFileName) {
        this.uploadFileName = uploadFileName;
    }
}
```

### struts.xml

```xml
<action name="fileUpload" class="com.example.action.FileUploadAction">
    <interceptor-ref name="fileUpload">
        <param name="maximumSize">10485760</param> <!-- 10MB -->
        <param name="allowedTypes">
            image/png,image/jpeg,image/gif,application/pdf
        </param>
    </interceptor-ref>
    <interceptor-ref name="defaultStack"/>

    <result>/jsp/uploadSuccess.jsp</result>
    <result name="input">/jsp/uploadForm.jsp</result>
</action>
```

### JSP

```jsp
<%@ taglib prefix="s" uri="/struts-tags" %>
<s:form action="fileUpload" method="post" enctype="multipart/form-data">
    <s:file name="upload" label="ファイル選択"/>
    <s:submit value="アップロード"/>
</s:form>
```

---

## Ajax連携

### JSON Plugin使用

#### Action

```java
// AjaxUserAction.java
public class AjaxUserAction extends ActionSupport {
    private List<User> users;
    private User user;
    private String result;

    public String getUsers() {
        UserService service = new UserService();
        users = service.findAll();
        return SUCCESS;
    }

    public String saveUser() {
        UserService service = new UserService();
        try {
            service.save(user);
            result = "success";
        } catch (Exception e) {
            result = "error";
        }
        return SUCCESS;
    }

    // getter/setter
    public List<User> getUsers() { return users; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    public String getResult() { return result; }
}
```

#### struts.xml

```xml
<package name="ajax" extends="json-default">
    <action name="getUsers" class="com.example.action.AjaxUserAction" method="getUsers">
        <result type="json">
            <param name="root">users</param>
        </result>
    </action>

    <action name="saveUser" class="com.example.action.AjaxUserAction" method="saveUser">
        <result type="json">
            <param name="root">result</param>
        </result>
    </action>
</package>
```

#### JavaScript

```javascript
// ユーザー一覧取得
fetch('/getUsers.action')
    .then(response => response.json())
    .then(users => {
        console.log(users);
        // テーブル更新など
    });

// ユーザー保存
fetch('/saveUser.action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user: { username: 'Alice', email: 'alice@example.com', age: 30 }
    })
})
.then(response => response.json())
.then(result => {
    console.log(result); // "success" or "error"
});
```

---

## Spring連携

### applicationContext.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="
           http://www.springframework.org/schema/beans
           http://www.springframework.org/schema/beans/spring-beans.xsd
           http://www.springframework.org/schema/context
           http://www.springframework.org/schema/context/spring-context.xsd">

    <!-- コンポーネントスキャン -->
    <context:component-scan base-package="com.example"/>

    <!-- UserService Bean -->
    <bean id="userService" class="com.example.service.UserService"/>

    <!-- UserAction Bean -->
    <bean id="userAction" class="com.example.action.UserAction" scope="prototype">
        <property name="userService" ref="userService"/>
    </bean>
</beans>
```

### Action（DI対応）

```java
// UserAction.java
public class UserAction extends ActionSupport {
    private UserService userService;  // Springから注入

    // Setter Injection
    public void setUserService(UserService userService) {
        this.userService = userService;
    }

    public String list() {
        users = userService.findAll();
        return SUCCESS;
    }
}
```

### struts.xml

```xml
<!-- Spring管理のActionを参照 -->
<action name="userList" class="userAction" method="list">
    <result>/jsp/userList.jsp</result>
</action>
```

---

## トラブルシューティング

### よくあるエラーと解決策

#### 1. No result defined for action

```
No result defined for action com.example.action.UserAction and result input
```

**解決**: struts.xmlにresultを追加

```xml
<action name="user" class="com.example.action.UserAction">
    <result name="input">/jsp/userForm.jsp</result>
</action>
```

#### 2. Cannot find class

```
Could not load class: com.example.action.UserAction
```

**解決**: クラスパスやパッケージ名を確認

#### 3. パラメータがnull

**原因**: getter/setterの未定義

**解決**: プロパティに対応するgetter/setterを定義

#### 4. ファイルアップロード失敗

```
File upload exceeded maximum size
```

**解決**: struts.xmlで最大サイズを設定

```xml
<constant name="struts.multipart.maxSize" value="10485760"/>
```

---

## 参考資料

- [Struts 2 Documentation](https://struts.apache.org/documentation.html)
- [Struts 2 Tutorials](https://www.journaldev.com/2263/struts-2-tutorial)
- [Spring Struts Integration](https://www.baeldung.com/spring-mvc-struts-2)
