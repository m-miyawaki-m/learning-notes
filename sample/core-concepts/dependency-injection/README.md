# 依存性注入（Dependency Injection）学習計画

## 学習目標
- DIの本質的な概念と「なぜ必要か」を理解する
- Spring FrameworkでのDI実装パターンを習得する
- テスタビリティと保守性向上の観点からDIを実務で適切に使えるようになる

## 前提知識
- Javaの基本文法（クラス、インターフェース、継承）
- オブジェクト指向の基礎（カプセル化、多態性）
- Spring Frameworkの基本的な使い方

## 学習ロードマップ

### Week 1: 概念理解
- [ ] DIとは何か、なぜ必要なのか（密結合vs疎結合）
- [ ] IoC（制御の反転）との関係性
- [ ] 3種類の注入方法（コンストラクタ、セッター、フィールド）
- [ ] DIを使わない場合の問題点を実感する
- [ ] テスタビリティとの関係

### Week 2: Spring DI実装基礎
- [ ] @Autowiredの使い方
- [ ] @Component, @Service, @Repositoryの違い
- [ ] コンストラクタ注入 vs フィールド注入（なぜコンストラクタ注入が推奨されるか）
- [ ] DIコンテナのライフサイクル
- [ ] スコープ（Singleton, Prototype, Request等）の理解

### Week 3: Spring DI実装応用
- [ ] @Qualifier による複数Bean管理
- [ ] @Primary の使い方
- [ ] Java Config（@Configuration, @Bean）
- [ ] @ConditionalOn* による条件付きBean登録
- [ ] 循環依存の問題と回避方法

### Week 4: 実践・振り返り
- [ ] 実プロジェクトの既存コードでDIパターンを分析
- [ ] 密結合なコードをDIでリファクタリング
- [ ] 単体テストでのモック注入を実践
- [ ] 学んだ内容を同僚に説明できるレベルまで整理

## 参考資料
- [Spring公式ドキュメント - Core Technologies: IoC Container](https://docs.spring.io/spring-framework/reference/core.html)
- 書籍『Spring徹底入門 第2版』（翔泳社）
- 書籍『Java言語で学ぶデザインパターン入門』（結城浩）- Dependency Injection章
- Baeldung: [Intro to Inversion of Control and Dependency Injection with Spring](https://www.baeldung.com/inversion-control-and-dependency-injection-in-spring)

## 学習ログ

### 2024-12-07
- 学習計画作成
- 次回: DIの基本概念から学習開始
