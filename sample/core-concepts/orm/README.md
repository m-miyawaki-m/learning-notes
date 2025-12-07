# ORM（Object-Relational Mapping）学習計画

## 学習目標
- ORMの概念と「なぜ必要か」を理解する
- MyBatisの特性（SQLマッパー）とJPA/Hibernateとの違いを理解する
- N+1問題などの典型的な問題とその対策を習得する

## 前提知識
- SQL基礎（SELECT, JOIN, トランザクション）
- Javaの基本文法
- リレーショナルデータベースの基礎知識

## 学習ロードマップ

### Week 1: ORM概念理解
- [ ] ORMとは何か、なぜ必要なのか
- [ ] インピーダンスミスマッチの問題
- [ ] ORMのメリット・デメリット
- [ ] ORM vs SQLマッパーの違い

### Week 2: MyBatis基礎
- [ ] MyBatisの基本構成（Mapper XML, Mapper Interface）
- [ ] 基本的なCRUD操作
- [ ] 動的SQL（if, choose, foreach）
- [ ] ResultMapとマッピング戦略

### Week 3: MyBatis応用
- [ ] 1対多、多対多のマッピング
- [ ] ネストされたResultMap
- [ ] キャッシュ（1次、2次）
- [ ] トランザクション管理

### Week 4: パフォーマンスと問題対策
- [ ] N+1問題の理解と対策
- [ ] Lazy Loading vs Eager Loading
- [ ] バッチ処理の最適化
- [ ] 実行計画の読み方

## 参考資料
- [MyBatis公式ドキュメント](https://mybatis.org/mybatis-3/ja/)
- Oracle SQL Developer で実行計画確認
- 社内プロジェクトの既存MyBatis実装を分析

## 学習ログ

### 2024-12-07
- 学習計画作成
- 次回: ORMの概念から学習開始
