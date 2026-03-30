# 📋 リファクタリング マスタープラン

> このファイルの目的: リファクタリングで何を進めるか、Phaseごとの計画と成功基準を定義する。

**バージョン:** 1.0  
**作成日:** 2025年10月25日

> 補足（2026-03-30）: 本ファイルの Phase 1-4 は 2025 年時点の大規模リファクタリング計画です。  
> 現行運用に合わせた構成整備は、以下の「構成整備トラック」として別管理します。

---
## 🧭 構成整備トラック（2026-03-30）
**目的:** 現在の運用実態に合わせて、構成・ドキュメント・Git 管理ルールを整理する

### 旧計画との対応関係

#### 旧計画に含まれていた要素

- `common/` を中心とした共通基盤整備
- `life_insurance` / `pension_calc` の責務整理
- UI 共通化、可視化ヘルパー化

#### 旧計画に明示的には含まれていなかった要素

- README / `pyproject.toml` の現構成との整合
- ローカル生成データの Git 管理ルール
- `docs/` を正本、`REFACTORING/` を履歴とする文書運用ルール
- ドキュメント入口の一本化（`docs/INDEX.md`）
- 保存データ・アーカイブの運用ポリシー明確化

### 完了項目

- [x] Phase 1: README / pyproject の整合化
- [x] Phase 2: ローカル生成データの非追跡化（saved_plans）
- [x] Phase 3: docs 正本化と REFACTORING 履歴化、導線整備

### 成果物

- `docs/DOCUMENTATION_STRUCTURE.md`
- `docs/INDEX.md`
- `docs/DOCS_INVENTORY.md`
- `REFACTORING/INDEX.md`（docs への逆リンク追記）
- `REFACTORING/README.md`（履歴アーカイブ明記）

### 補完計画（未織り込み要素を含む）

#### Track A: 実構成整合
- [x] `README.md` の構成図と起動手順を現状へ合わせる
- [x] `pyproject.toml` の `testpaths` / coverage 対象を現状へ合わせる

#### Track B: ローカルデータ管理
- [x] `vehicle_finance/data/saved_plans/` を非追跡化する
- [x] `.gitignore` にローカル生成物ルールを追加する
- [x] `archive/` の保存方針を明文化する

#### Track C: ドキュメント運用
- [x] `docs/` を正本とするルールを定義する
- [x] `docs/INDEX.md` を追加して入口を一本化する
- [x] `REFACTORING/` 側から `docs/` への逆リンクを追加する
- [x] `docs/` 側の既存文書を「現行仕様 / 履歴参照」で初回棚卸しする
- [x] `docs/DOCS_INVENTORY.md` を追加して分類結果を記録する

#### Track D: 運用導線の統一
- [x] `main.py` と `scripts/` の役割分担を明文化する
- [x] 実行コマンドの正本を `README.md` / `docs/` に統一する
- [x] テスト / 検証 / 起動コマンドの重複記載を整理する

#### Track E: 維持管理
- [x] 新規ドキュメント追加時の配置ルールを `docs/CONTRIBUTING.md` に追記する
- [x] `docs/` 直下の主要文書を棚卸しし、要更新候補を更新する
- [x] `archive/` と `docs/` の境界を見直し、入口と分類ルールを明文化する

### 補完計画の成功基準

- 現行運用の正本が `docs/` に統一されている
- ローカル生成データが Git 差分を汚さない
- README / pyproject / 実ディレクトリ構成の間に大きなズレがない
- 新規参加者が `docs/INDEX.md` から必要情報へ到達できる

## 🎯 旧計画 Phase 1: 即効性の高いリファクタリング

**期間:** 1-2週間  
**優先度:** 🔴 最高  
**期待削減行数:** ~500行

### 旧計画タスク一覧（2025年時点）

#### 1.1 税金ヘルパーモジュール作成
- [ ] `life_insurance/utils/__init__.py` 作成
- [ ] `life_insurance/utils/tax_helpers.py` 作成
  - [ ] `TaxDeductionHelper` クラス実装
  - [ ] `calculate_annual_tax_savings()` メソッド
  - [ ] `calculate_total_tax_savings_over_years()` メソッド
  - [ ] `get_tax_helper()` シングルトン関数
- [ ] `life_insurance/tests/test_tax_helpers.py` 作成
  - [ ] 基本計算テスト（10ケース以上）
  - [ ] エッジケーステスト
  - [ ] 境界値テスト

**成功基準:**
- ✓ すべてのテストがパス
- ✓ 型ヒント完備
- ✓ docstring充実

#### 1.2 既存コードの置換
- [ ] `streamlit_app.py` の重複コード特定（完了済み: 30箇所）
- [ ] 段階的置換（10箇所ずつ推奨）
  - [ ] 1-10箇所目の置換
  - [ ] 11-20箇所目の置換
  - [ ] 21-30箇所目の置換
- [ ] 各置換後にテスト実行
- [ ] UI動作確認

**成功基準:**
- ✓ 全置換完了
- ✓ 既存テスト全パス
- ✓ Streamlitアプリが正常起動
- ✓ 計算結果が変更前と一致

#### 1.3 comparison_app.pyの更新
- [ ] `comparison_app.py` でもtax_helpersを利用
- [ ] 重複コード削除
- [ ] テスト確認

**成功基準:**
- ✓ 比較アプリが正常動作

---

## 🎯 旧計画 Phase 2: コア計算ロジックの統合

**期間:** 2-3週間  
**優先度:** 🟠 高  
**期待削減行数:** ~800行

### 旧計画タスク一覧（2025年時点）

#### 2.1 データクラス設計
- [ ] `life_insurance/models/__init__.py` 作成
- [ ] `life_insurance/models/plans.py` 作成
  - [ ] `InsurancePlan` データクラス
  - [ ] `FundPlan` データクラス
  - [ ] バリデーション追加

#### 2.2 統合計算エンジン実装
- [ ] `life_insurance/analysis/insurance_calculator.py` 作成
  - [ ] `InsuranceValueCalculator` クラス
  - [ ] `calculate_simple_accumulation()` メソッド
  - [ ] `calculate_partial_withdrawal()` メソッド
  - [ ] `optimize_partial_withdrawal_strategy()` メソッド
  - [ ] `calculate_switching_value()` メソッド

#### 2.3 既存関数の統合
- [ ] `_calculate_partial_withdrawal_value()` → 削除
- [ ] `_calculate_partial_withdrawal_value_enhanced()` → 削除
- [ ] `_calculate_simple_insurance_value()` → 削除
- [ ] `_calculate_switching_value()` → 統合
- [ ] `calculate_partial_withdrawal_strategy()` → リダイレクト
- [ ] `optimize_partial_withdrawal_strategy()` → リダイレクト

#### 2.4 テスト追加
- [ ] `life_insurance/tests/test_insurance_calculator.py` 作成
  - [ ] 単純積立計算テスト
  - [ ] 部分解約計算テスト
  - [ ] 最適化テスト
  - [ ] エッジケース網羅

**成功基準:**
- ✓ 計算精度が元の実装と一致
- ✓ パフォーマンス劣化なし
- ✓ テストカバレッジ80%以上

---

## 🎯 旧計画 Phase 3: 共通基盤構築

**期間:** 3-4週間  
**優先度:** 🟡 中  
**期待削減行数:** ~200行

### 旧計画タスク一覧（2025年時点）

#### 3.1 共通ディレクトリ構造作成
- [ ] `common/__init__.py` 作成
- [ ] `common/calculators/__init__.py` 作成
- [ ] `common/models/__init__.py` 作成
- [ ] `common/utils/__init__.py` 作成

#### 3.2 基底クラス実装
- [ ] `common/calculators/base_calculator.py`
  - [ ] `BaseFinancialCalculator` 抽象クラス
  - [ ] `CompoundInterestMixin`
- [ ] `common/models/financial_plan.py`
  - [ ] `FinancialPlan` 基底クラス

#### 3.3 数学ユーティリティ
- [ ] `common/utils/math_utils.py`
  - [ ] 複利計算関数
  - [ ] 年金現価計算
  - [ ] IRR計算

#### 3.4 日付ユーティリティ
- [ ] `common/utils/date_utils.py`
  - [ ] 年齢計算
  - [ ] 期間計算
  - [ ] 和暦変換

#### 3.5 既存モジュールの移行
- [ ] `life_insurance` での共通基盤利用
- [ ] `pension_calc` での共通基盤利用

**成功基準:**
- ✓ 両モジュールで共通コード利用
- ✓ インポートエラーなし
- ✓ すべてのテストパス

---

## 🎯 旧計画 Phase 4: UI層の最適化

**期間:** 1-2週間  
**優先度:** 🟢 低  
**期待削減行数:** ~300行

### 旧計画タスク一覧（2025年時点）

#### 4.1 UI共通コンポーネント
- [ ] `common/ui/__init__.py` 作成
- [ ] `common/ui/input_components.py`
  - [ ] `FinancialInputs` クラス
  - [ ] 年収入力
  - [ ] 保険料入力
  - [ ] 利率スライダー
  - [ ] 年齢範囲入力

#### 4.2 可視化ヘルパー
- [ ] `life_insurance/utils/visualization.py`
  - [ ] `FinancialChartBuilder` クラス
  - [ ] タイムライン比較チャート
  - [ ] バーチャート
  - [ ] ヒートマップ

#### 4.3 UI関数のリファクタリング
- [ ] `streamlit_app.py` の入力部分を共通コンポーネント化
- [ ] プロット生成を可視化ヘルパー利用に変更
- [ ] `pension_calc/ui/streamlit_app.py` も同様に更新

**成功基準:**
- ✓ UI一貫性向上
- ✓ コード削減
- ✓ 動作確認完了

---

## 📊 進捗メトリクス

各Phaseで以下を測定:

- **コード削減率:** (削減行数 / 元の行数) × 100
- **テストカバレッジ:** pytest-cov で測定
- **関数の平均行数:** 自動スクリプトで測定
- **重複コード検出:** pylint --disable=all --enable=duplicate-code

### 測定コマンド
```bash
# 行数カウント
find . -name "*.py" -not -path "*/tests/*" -not -path "*/.venv/*" | xargs wc -l

# テストカバレッジ
pytest --cov=life_insurance --cov=pension_calc --cov-report=term-missing

# 重複コード検出
pylint --disable=all --enable=duplicate-code life_insurance/ pension_calc/
```

---

## 🔄 継続的改善プロセス

### 週次レビュー（金曜日推奨）
1. 今週の完了タスク確認
2. 次週のタスク優先順位設定
3. ブロッカーの特定と解決策検討
4. メトリクス測定と記録

### 月次振り返り
1. Phase進捗の確認
2. 目標達成度評価
3. 必要に応じた計画調整
4. ドキュメント更新

---

## ⚙️ 開発環境セットアップ

### 推奨ツール
```bash
# コード品質チェック
pip install pylint flake8 mypy black isort

# テストツール
pip install pytest pytest-cov

# 実行
black life_insurance/ pension_calc/ common/
isort life_insurance/ pension_calc/ common/
mypy life_insurance/ pension_calc/ common/
```

### pre-commitフック（オプション）
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

---

## 📚 参考資料

- [Pythonコーディング規約 PEP 8](https://peps.python.org/pep-0008/)
- [Google Pythonスタイルガイド](https://google.github.io/styleguide/pyguide.html)
- [リファクタリング: 既存のコードを安全に改善する](https://martinfowler.com/books/refactoring.html)

---

**次のアクション:** Phase 1のタスクから開始してください  
詳細は `REFACTORING/PHASE_1/` を参照
