# 📚 リファクタリングプロジェクト - ドキュメント索引

このディレクトリには、my-projectの大規模リファクタリングに関する
すべてのドキュメントと管理ファイルが含まれています。

---

## 🎯 プロジェクト概要

**目的:** コードの冗長性を削減し、保守性・拡張性を向上させる  
**期間:** 8-12週間  
**削減目標:** ~1,500行（約29%削減）

---

## 📖 主要ドキュメント

### 🌟 すぐに読むべきドキュメント

1. **[QUICKSTART.md](./QUICKSTART.md)** ⭐ **ここから始める**
   - 今すぐPhase 1を開始する手順
   - 最初の1箇所の置換方法
   - トラブルシューティング

2. **[README.md](./README.md)**
   - プロジェクト全体の概要
   - 4つのPhaseの説明
   - 目標と期待効果

3. **[MASTER_PLAN.md](./MASTER_PLAN.md)**
   - 詳細な実装計画
   - 各Phaseのタスク一覧
   - メトリクス測定方法

4. **[PROGRESS.md](./PROGRESS.md)**
   - 進捗トラッキング
   - 週次・月次レビュー
   - 課題管理

---

## 📁 ディレクトリ構造

```
REFACTORING/
├── README.md                    # プロジェクト概要
├── MASTER_PLAN.md               # 詳細実装計画
├── PROGRESS.md                  # 進捗トラッキング
├── QUICKSTART.md                # クイックスタートガイド
├── INDEX.md                     # このファイル
│
├── PHASE_1/                     # Phase 1: 税金ヘルパー
│   ├── TASKS.md                 # 詳細タスクリスト
│   └── templates/
│       ├── tax_helpers.py       # 実装テンプレート
│       └── test_tax_helpers.py  # テストテンプレート
│
├── PHASE_2/                     # Phase 2: コア計算統合
│   └── README.md                # Phase 2概要（準備中）
│
├── PHASE_3/                     # Phase 3: 共通基盤
│   └── README.md                # Phase 3概要（準備中）
│
└── PHASE_4/                     # Phase 4: UI最適化
    └── README.md                # Phase 4概要（準備中）
```

---

## 🚀 開始方法

### 初めての場合

1. **[QUICKSTART.md](./QUICKSTART.md)** を読む（5分）
2. Phase 1のセットアップを実施（10分）
3. 最初の1箇所を置換（5分）
4. テスト実行と動作確認（5分）
5. コミット

**合計所要時間:** 約25分で最初の成果が得られます

### すでに開始している場合

1. **[PROGRESS.md](./PROGRESS.md)** で現在の進捗を確認
2. 該当Phaseの `TASKS.md` を開く
3. 次のチェックボックスのタスクを実施
4. 完了後、進捗を更新

---

## 📊 Phase別ガイド

### Phase 1: 税金ヘルパー実装（1-2週間）

**状態:** 🟡 準備完了  
**優先度:** 🔴 最高

**ドキュメント:**
- [PHASE_1/TASKS.md](./PHASE_1/TASKS.md) - 詳細タスク
- [PHASE_1/templates/](./PHASE_1/templates/) - 実装テンプレート

**開始条件:** すぐに開始可能

**目標:**
- 税金計算の重複コード削減（30箇所）
- ~500行のコード削減
- テストカバレッジ55%達成

---

### Phase 2: コア計算ロジック統合（2-3週間）

**状態:** ⚪ 準備中  
**優先度:** 🟠 高

**開始条件:** Phase 1完了後

**目標:**
- 保険計算エンジンの統合
- ~800行のコード削減
- 計算精度の一元管理

---

### Phase 3: 共通基盤構築（3-4週間）

**状態:** ⚪ 準備中  
**優先度:** 🟡 中

**開始条件:** Phase 2完了後

**目標:**
- common/ディレクトリ構築
- 両モジュールでの共通コード利用
- プロジェクト全体の一貫性向上

---

### Phase 4: UI層最適化（1-2週間）

**状態:** ⚪ 準備中  
**優先度:** 🟢 低

**開始条件:** Phase 3完了後

**目標:**
- UI共通コンポーネント
- 可視化ヘルパー
- ~300行のコード削減

---

## 🛠️ よく使うコマンド

### テスト実行
```bash
# 特定のテストファイル
pytest life_insurance/tests/test_tax_helpers.py -v

# すべてのテスト
pytest life_insurance/tests/ -v

# カバレッジ付き
pytest --cov=life_insurance --cov-report=term-missing
```

### コード品質チェック
```bash
# フォーマット
black life_insurance/

# インポート整理
isort life_insurance/

# 型チェック
mypy life_insurance/

# 重複コード検出
pylint --disable=all --enable=duplicate-code life_insurance/
```

### 行数カウント
```bash
# Pythonファイルの総行数
(Get-ChildItem -Recurse -Include *.py -Exclude tests | Measure-Object -Property Length -Sum).Sum
```

### アプリ起動
```bash
# 生命保険アプリ
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501

# 比較アプリ
streamlit run life_insurance/ui/comparison_app.py --server.port=8502

# 年金計算アプリ
streamlit run pension_calc/ui/streamlit_app.py --server.port=8503
```

---

## 📝 進捗報告の方法

### 週次レビュー（毎週金曜日推奨）

1. `PROGRESS.md` を開く
2. 該当週のセクションを更新
   - 完了タスクにチェック
   - 進行中タスクを記入
   - ブロッカーがあれば記録
3. メトリクスを測定して記録
4. 次週の計画を記入

### Phase完了時

1. `PROGRESS.md` の該当Phaseを「完了」にマーク
2. メトリクスの最終値を記録
3. 次のPhaseの `TASKS.md` を作成
4. コミット: `git commit -m "docs: Phase X完了"`

---

## 🆘 ヘルプ・サポート

### トラブルシューティング

各Phaseの `TASKS.md` にトラブルシューティングセクションがあります。

### よくある質問

**Q: Phase 1の途中で他の作業が必要になった場合は？**  
A: 現在の進捗を `PROGRESS.md` に記録し、ブランチを切り替えてください。
   再開時は記録を見て続きから開始できます。

**Q: テストが失敗する場合は？**  
A: まず元のコードに戻して既存テストがパスするか確認してください。
   その後、変更箇所を小さく分割して段階的に実施します。

**Q: 計算結果が元と異なる場合は？**  
A: 辞書のキー名、関数の引数順序、デフォルト値を確認してください。

---

## 📞 連絡・報告

### 定期レビュー

- **週次:** 金曜日に `PROGRESS.md` を更新
- **Phase完了時:** 完了報告とメトリクス記録

### 緊急時

- 重大なバグを発見した場合は即座に `PROGRESS.md` の課題管理に記録
- 既存機能が壊れた場合は変更を戻してから調査

---

## 🎉 マイルストーン

- [ ] Phase 1完了（目標: 2週間以内）
- [ ] Phase 2完了（目標: 5週間以内）
- [ ] Phase 3完了（目標: 9週間以内）
- [ ] Phase 4完了（目標: 11週間以内）
- [ ] 総合テスト・ドキュメント更新（目標: 12週間以内）

---

**最終更新:** 2025年10月25日  
**次のアクション:** [QUICKSTART.md](./QUICKSTART.md) からPhase 1を開始
