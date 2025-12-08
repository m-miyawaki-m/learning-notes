# AST（抽象構文木）によるプログラム解析の概念

> プログラムを構造的に理解し、解析・変換するための基礎理論

## 学習目標
- [ ] ASTの概念と重要性を理解する
- [ ] コンパイラの処理フローを理解する
- [ ] 静的解析と動的解析の違いを理解する
- [ ] ASTを使った実用的な解析手法を学ぶ
- [ ] メタプログラミングの基礎を理解する

---

## 1. ASTとは何か

### 1.1 定義

**AST (Abstract Syntax Tree, 抽象構文木)**: プログラムの構造を階層的な木構造で表現したもの

```
ソースコード: x = 1 + 2 * 3

構文木:
    Assignment (代入)
    ├── Left: x (変数)
    └── Right: BinOp (二項演算)
        ├── Left: 1
        ├── Op: Add (+)
        └── Right: BinOp (二項演算)
            ├── Left: 2
            ├── Op: Multiply (*)
            └── Right: 3
```

### 1.2 「抽象」の意味

**抽象構文木** vs **具象構文木 (CST: Concrete Syntax Tree)**

```python
# ソースコード
if x > 0:
    print(x)

# 具象構文木（CST）: すべてのトークンを保持
├── IF_KEYWORD: "if"
├── WHITESPACE: " "
├── IDENTIFIER: "x"
├── WHITESPACE: " "
├── GREATER: ">"
├── WHITESPACE: " "
├── NUMBER: "0"
├── COLON: ":"
├── NEWLINE
├── INDENT
├── ...

# 抽象構文木（AST）: 意味のある構造のみ
├── If
│   ├── test: Compare
│   │   ├── left: Name(x)
│   │   ├── ops: [Gt]
│   │   └── comparators: [Constant(0)]
│   └── body:
│       └── Expr
│           └── Call
│               └── func: Name(print)
│               └── args: [Name(x)]
```

**抽象化のメリット**:
- 空白、コメント、括弧などの構文的詳細を削除
- プログラムの「意味」に集中できる
- 言語間で共通の構造を扱いやすい

---

## 2. コンパイラとASTの関係

### 2.1 コンパイラの処理フロー

```
ソースコード
    ↓
[1] 字句解析 (Lexical Analysis / Tokenization)
    ↓
トークン列
    ↓
[2] 構文解析 (Syntax Analysis / Parsing)
    ↓
AST (抽象構文木)
    ↓
[3] 意味解析 (Semantic Analysis)
    ↓
注釈付きAST
    ↓
[4] 最適化 (Optimization)
    ↓
最適化済みAST
    ↓
[5] コード生成 (Code Generation)
    ↓
機械語 / バイトコード
```

### 2.2 各段階の詳細

#### [1] 字句解析（Lexical Analysis）

**目的**: ソースコードを意味のある単位（トークン）に分割

```python
# 入力
"x = 1 + 2"

# 出力（トークン列）
[
    Token(IDENTIFIER, "x"),
    Token(ASSIGN, "="),
    Token(NUMBER, "1"),
    Token(PLUS, "+"),
    Token(NUMBER, "2")
]
```

**字句解析器（Lexer）の役割**:
- 空白、改行、コメントの除去
- キーワード、識別子、リテラル、演算子の識別
- 字句エラーの検出（不正な文字など）

#### [2] 構文解析（Syntax Analysis）

**目的**: トークン列を構文規則に従ってASTに変換

```
文法規則（BNF記法）:
expression := term (('+' | '-') term)*
term       := factor (('*' | '/') factor)*
factor     := NUMBER | IDENTIFIER | '(' expression ')'

入力: 1 + 2 * 3

構文木:
    expression
    ├── term: 1
    ├── +
    └── term
        ├── factor: 2
        ├── *
        └── factor: 3
```

**構文解析器（Parser）の役割**:
- 文法規則に従ってASTを構築
- 構文エラーの検出（括弧の不一致など）
- 演算子の優先順位と結合規則の適用

**パーサーの種類**:
- **再帰下降パーサー**: 文法規則を再帰関数として実装
- **LR パーサー**: 左から右へ、右端導出（効率的）
- **PEG パーサー**: 解析表現文法（バックトラック可能）

#### [3] 意味解析（Semantic Analysis）

**目的**: プログラムが「意味的に」正しいか検証

```python
# 構文的には正しいが意味的に間違い
x = "hello"
y = x + 5  # 型エラー: str + int

# 意味解析でチェック:
# - 型の整合性
# - 変数の宣言（未定義変数の使用）
# - スコープの妥当性
# - 関数呼び出しの引数の数と型
```

**意味解析器の役割**:
- 型チェック
- スコープ解決（変数がどのスコープで定義されているか）
- シンボルテーブルの構築
- 意味エラーの検出

---

## 3. ASTの構造と設計パターン

### 3.1 ノードの種類

典型的なASTノードの分類:

```
1. 式 (Expression)
   - リテラル: 数値、文字列、真偽値
   - 変数参照: 識別子
   - 二項演算: +, -, *, /, %, ==, !=, <, >, ...
   - 単項演算: -, !, not
   - 関数呼び出し: func(args)
   - 配列アクセス: arr[index]

2. 文 (Statement)
   - 代入文: x = value
   - 条件文: if-else
   - ループ文: for, while
   - return文
   - 関数定義
   - クラス定義

3. 宣言 (Declaration)
   - 変数宣言
   - 関数宣言
   - クラス宣言
   - インポート文
```

### 3.2 Visitor パターン

**目的**: ASTを走査して情報を収集・変換する

```python
# Visitorパターンの概念

class ASTNode:
    def accept(self, visitor):
        """Visitorを受け入れる"""
        pass

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binop(self)

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_number(self)

class ASTVisitor:
    """訪問者の基底クラス"""

    def visit_binop(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        # 処理...

    def visit_number(self, node):
        # 処理...
        pass

# 具体的な訪問者
class Evaluator(ASTVisitor):
    """ASTを評価して計算結果を返す"""

    def visit_binop(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.op == '+':
            return left + right
        elif node.op == '*':
            return left * right
        # ...

    def visit_number(self, node):
        return node.value

# 使用例
# AST: 1 + 2 * 3
ast = BinOp(
    Number(1),
    '+',
    BinOp(Number(2), '*', Number(3))
)

evaluator = Evaluator()
result = ast.accept(evaluator)  # 7
```

**Visitorパターンのメリット**:
- ノードのクラスを変更せずに新しい操作を追加できる
- 関連する操作を1つのVisitorクラスにまとめられる
- 複数のVisitorで異なる処理を実行できる

### 3.3 Transformer パターン

**目的**: ASTを別のASTに変換する

```python
class ASTTransformer:
    """ASTを変換する"""

    def transform(self, node):
        method_name = f'transform_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_transform)
        return method(node)

    def generic_transform(self, node):
        """デフォルトの変換（変更なし）"""
        return node

# 具体的な変換器
class ConstantFolder(ASTTransformer):
    """定数畳み込み最適化"""

    def transform_BinOp(self, node):
        # 子ノードを先に変換
        left = self.transform(node.left)
        right = self.transform(node.right)

        # 両方が定数なら計算
        if isinstance(left, Number) and isinstance(right, Number):
            if node.op == '+':
                return Number(left.value + right.value)
            elif node.op == '*':
                return Number(left.value * right.value)

        # そうでなければ元のまま
        return BinOp(left, node.op, right)

# 例: 1 + 2 を 3 に最適化
ast = BinOp(Number(1), '+', Number(2))
optimizer = ConstantFolder()
optimized = optimizer.transform(ast)  # Number(3)
```

---

## 4. 静的解析の概念

### 4.1 静的解析とは

**静的解析（Static Analysis）**: プログラムを**実行せずに**コードを解析する手法

```
動的解析（実行が必要）      静的解析（実行不要）
├── テスト                 ├── 構文チェック
├── プロファイリング         ├── 型チェック
├── デバッグ               ├── リンター
└── ログ分析               ├── セキュリティスキャン
                          └── 複雑度計算
```

### 4.2 静的解析でできること

#### 1. 構文チェック（Syntax Check）

```python
# 構文エラーを検出
def hello(
    print("missing closing parenthesis")
```

#### 2. 型チェック（Type Check）

```python
# 型の不一致を検出
def add(a: int, b: int) -> int:
    return a + b

result = add("1", "2")  # 型エラー: str を int に渡している
```

#### 3. 未使用変数・コードの検出

```python
def calculate(x, y):
    result = x + y
    unused = x * y  # 警告: 未使用変数
    return result

def never_called():  # 警告: 未使用関数
    pass
```

#### 4. スタイル違反の検出

```python
# PEP 8 違反
def BadFunctionName( x,y ):  # 関数名、空白の問題
    z=x+y  # 演算子の周りに空白がない
    return z
```

#### 5. 潜在的なバグの検出

```python
# NULL参照の可能性
def process(data):
    result = data.get('value')  # Noneかもしれない
    return result.upper()  # AttributeError の可能性

# 無限ループ
while True:
    process_data()
    # break がない

# リソースリーク
file = open('data.txt')
data = file.read()
# file.close() がない
```

#### 6. セキュリティ脆弱性の検出

```python
# SQLインジェクションの危険性
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"  # 危険
    return db.execute(query)

# パストラバーサルの危険性
def read_file(filename):
    return open(f"/data/{filename}").read()  # ../etc/passwd など
```

### 4.3 制約と限界

**ハルティング問題**: すべてのプログラムについて、停止するかどうかを判定することは不可能

```python
# このコードは停止する？（一般には決定不能）
def unknown_halting(n):
    while True:
        if is_prime(n):
            break
        n += 1
    return n
```

**静的解析の限界**:
- 実行時にしか決まらない値は解析できない
- 完全な解析は不可能（過検出 or 検出漏れ）
- トレードオフ: 精度 vs 実行時間

---

## 5. ASTを使った解析の実践パターン

### 5.1 パターン1: 情報収集

**目的**: コードベースの統計情報を収集

```
例:
- 関数の数
- クラスの数
- 平均関数長
- コメント率
- import されているモジュール一覧
```

**アプローチ**:
1. ASTを走査
2. 対象ノード（FunctionDef, ClassDef など）をカウント
3. 統計情報を集計

### 5.2 パターン2: パターンマッチング

**目的**: 特定のコードパターンを検出

```python
# 検出したいパターン
# 1. print文のデバッグコードが残っている
# 2. assert False が残っている
# 3. TODO コメントが残っている

# アンチパターン:
if condition == True:  # == True は不要
    pass

# 非推奨API:
os.popen()  # subprocess.run() を使うべき
```

**アプローチ**:
1. 検出したいパターンをASTのノード構造として定義
2. ASTを走査してパターンに一致するノードを検索
3. 一致した箇所を報告

### 5.3 パターン3: データフロー解析

**目的**: 変数の値がどう流れるか追跡

```python
# 変数の流れを追跡
x = get_user_input()  # 汚染された入力
y = x + "_suffix"     # y も汚染
z = sanitize(y)       # z は安全
execute_sql(z)        # OK: z は安全

# x を直接 execute_sql に渡すと危険
execute_sql(x)  # 警告: 汚染されたデータ
```

**アプローチ**:
1. 各変数の「汚染状態」を追跡
2. 代入や関数呼び出しで状態を伝播
3. 危険な操作に汚染されたデータが渡されていないかチェック

### 5.4 パターン4: 制御フロー解析

**目的**: プログラムの実行経路を分析

```python
def example(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    # x == 0 の場合、return がない → None が返る
```

**制御フローグラフ (CFG)**:
```
        [Start]
           ↓
      [x > 0?]
       ↙    ↘
   [True]  [False]
      ↓        ↓
  [return] [x < 0?]
            ↙    ↘
        [True]  [False]
           ↓        ↓
      [return]  [end]
                   ↓
              [return None]
```

**アプローチ**:
1. ASTから制御フローグラフを構築
2. すべての経路を列挙
3. 問題のある経路（return なし、到達不能コードなど）を検出

### 5.5 パターン5: 複雑度計算

**目的**: コードの複雑さを定量化

**循環的複雑度（Cyclomatic Complexity）**:
```
M = E - N + 2P

E: エッジ数（制御フローの矢印）
N: ノード数（基本ブロック）
P: 連結成分数（通常1）
```

**計算の簡易版**:
```
複雑度 = 1 + 判定ポイントの数

判定ポイント:
- if, elif
- while, for
- and, or
- except
- case (switch)
```

```python
def example(x, y):  # 複雑度 = 1
    if x > 0:       # +1 = 2
        if y > 0:   # +1 = 3
            return "both positive"
        elif y < 0: # +1 = 4
            return "x positive, y negative"
    elif x < 0:     # +1 = 5
        return "x negative"
    return "x zero"

# 循環的複雑度 = 5
```

**複雑度の目安**:
- 1-10: シンプル（良好）
- 11-20: やや複雑（要注意）
- 21-50: 複雑（リファクタリング推奨）
- 51+: 非常に複雑（テスト困難）

---

## 6. メタプログラミングとコード生成

### 6.1 メタプログラミングとは

**メタプログラミング**: プログラムを操作するプログラム

```
レベル0: データを操作するプログラム
    例: calculator.py が数値を計算

レベル1: プログラムを操作するプログラム
    例: linter.py が calculator.py を解析

レベル2: プログラムを操作するプログラムを操作...
    例: linter を自動生成するツール
```

### 6.2 コード生成の用途

#### 1. ボイラープレートの自動生成

```python
# 手動で書くと冗長
class User:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"User(name={self.name}, age={self.age}, email={self.email})"

    def __eq__(self, other):
        return self.name == other.name and ...

# データクラスで自動生成
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
    # __init__, __repr__, __eq__ が自動生成される
```

#### 2. ORMのクエリビルダー

```python
# SQLを直接書く代わりに
query = "SELECT * FROM users WHERE age > 20"

# Pythonコードから生成
query = User.select().where(User.age > 20)
# → ASTを使ってSQLに変換
```

#### 3. テンプレートエンジン

```python
# テンプレート
template = "Hello, {{ name }}!"

# ASTに変換して実行
ast = parse_template(template)
result = ast.render(name="Alice")  # "Hello, Alice!"
```

### 6.3 トランスパイラ

**トランスパイラ**: ある言語から別の言語へ変換

```
例:
- TypeScript → JavaScript
- CoffeeScript → JavaScript
- Sass → CSS
- Python 3.10+ → Python 3.8 (async/await の展開)
```

**処理フロー**:
```
ソース言語コード
    ↓
[パース] → AST（ソース言語）
    ↓
[変換] → AST（ターゲット言語）
    ↓
[生成] → ターゲット言語コード
```

---

## 7. 実用ツールとライブラリ

### 7.1 言語別のASTライブラリ

| 言語 | ライブラリ | 特徴 |
|------|-----------|------|
| Python | ast (標準) | Python組み込み |
| JavaScript | Acorn | 高速、軽量 |
| JavaScript | Babel Parser | 最新構文対応 |
| JavaScript | Esprima | 標準準拠 |
| TypeScript | TypeScript Compiler API | 型情報も含む |
| Java | JavaParser | Java専用 |
| Java | Eclipse JDT | IDE用 |
| C/C++ | Clang | LLVMベース |
| Go | go/ast | Go標準 |
| Rust | syn | マクロ用 |

### 7.2 静的解析ツール

| ツール | 言語 | 用途 |
|--------|------|------|
| pylint | Python | 総合的な静的解析 |
| mypy | Python | 型チェック |
| flake8 | Python | スタイルチェック |
| ESLint | JavaScript | 総合的な静的解析 |
| TSLint | TypeScript | TypeScript専用 |
| SonarQube | 多言語 | 品質管理 |
| Checkmarx | 多言語 | セキュリティ |

---

## 8. 学習ロードマップ

### Phase 1: 基礎理解（1-2週間）
- [ ] コンパイラの基本概念を学ぶ
- [ ] ASTの構造を理解する
- [ ] 簡単な式のASTを手で書いてみる

### Phase 2: 実装（2-3週間）
- [ ] 標準ライブラリでASTを生成
- [ ] Visitorパターンを実装
- [ ] 簡単な解析ツールを作成

### Phase 3: 応用（3-4週間）
- [ ] リンターを作成
- [ ] コード変換ツールを作成
- [ ] 複雑度計算ツールを作成

### Phase 4: 実践（継続）
- [ ] 実際のプロジェクトに適用
- [ ] カスタム解析ルールを追加
- [ ] CI/CDに統合

---

## 9. よくある質問

### Q1: ASTと正規表現の違いは？

**正規表現**: テキストのパターンマッチング
- 構造を理解しない
- コメント内のコードも誤検出
- 入れ子構造の処理が困難

**AST**: プログラムの構造を理解
- 文法的に正しく解析
- コメントは除外される
- 複雑な構造も正確に扱える

```python
# 正規表現で "def " を検索すると誤検出
# comment: "def should be defined"
text = "def is a keyword"

# ASTなら関数定義のみ検出
def actual_function():  # ✓ 検出
    pass
```

### Q2: すべての問題を静的解析で検出できる？

**No.** 完全な解析は理論的に不可能（ハルティング問題）

検出できること:
- 構文エラー
- 型エラー
- スタイル違反
- 一部の論理エラー

検出できないこと:
- 実行時エラーの一部
- ビジネスロジックの誤り
- パフォーマンス問題の多く

### Q3: ASTと字句解析の違いは？

| | 字句解析 | 構文解析（AST） |
|--|---------|----------------|
| 入力 | 文字列 | トークン列 |
| 出力 | トークン列 | AST |
| 理解 | 単語レベル | 文構造レベル |
| 例 | "x", "=", "1" | Assignment(x, 1) |

---

## 10. 参考リソース

### 書籍
- "Compilers: Principles, Techniques, and Tools" (ドラゴンブック)
- "Modern Compiler Implementation" シリーズ
- "Crafting Interpreters" - Bob Nystrom

### オンラインリソース
- [AST Explorer](https://astexplorer.net/) - ASTの可視化
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Green Tree Snakes](https://greentreesnakes.readthedocs.io/) - Python AST Tutorial

### ツール
- [pylint](https://pylint.org/)
- [ESLint](https://eslint.org/)
- [SonarQube](https://www.sonarqube.org/)

---

## まとめ

### ASTの本質
1. **構造の理解**: プログラムを木構造として表現
2. **意味の抽出**: 構文的詳細を排除し、意味に集中
3. **変換の基盤**: コード解析・変換のための標準的な中間表現

### なぜ重要か
- **コード品質**: 静的解析で問題を早期発見
- **開発効率**: 自動リファクタリング、コード生成
- **理解促進**: プログラムの構造を可視化

### 次のステップ
1. 実際に手を動かしてASTを生成してみる
2. 簡単な解析ツールを作成してみる
3. 既存の静的解析ツールのソースコードを読む
