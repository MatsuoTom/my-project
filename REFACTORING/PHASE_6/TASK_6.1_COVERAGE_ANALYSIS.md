# Task 6.1: テストカバレッジ向上 - 詳細分析レポート

**作成日**: 2025年11月8日  
**Phase**: 6  
**Task**: 6.1  
**目標**: テストカバレッジ 65.16% → 70%以上

---

## 📊 現状サマリー

### 全体カバレッジ
- **テスト実行**: 296件（合格286件、失敗10件）
- **成功率**: 96.6%
- **プロジェクト全体カバレッジ**: 31.04%（未テストファイル含む）
- **テスト対象モジュールカバレッジ**: **約65%**（Phase 5測定時と整合）

### テスト失敗（10件）
**対象ファイル**: `life_insurance/tests/test_optimizer.py`  
**原因**:
1. **API不整合**: `result.net_value` → `result['net_value']`（dict vs オブジェクト）
2. **引数エラー**: `FundPlan.__init__()` に `capital_gains_tax_rate` 引数が存在しない

---

## 🎯 優先度別カバレッジ分析

### 【最優先】テスト失敗の修正

#### 1. `life_insurance/analysis/withdrawal_optimizer.py` (39.86%)

**失敗テスト**:
- `test_calculate_total_benefit`
- `test_optimize_withdrawal_timing`
- `test_analyze_income_scenarios`
- `test_analyze_all_strategies`
- `test_partial_withdrawal_benefit`
- `test_partial_withdrawal_with_zero_reinvest`
- `test_partial_withdrawal_with_high_reinvest`
- `test_full_withdrawal_early`
- `test_full_withdrawal_late`
- `test_switch_benefit`

**問題箇所**:
```python
# Line 124: AttributeError
surrender_value = result.net_value  # ❌ result は dict
# 正しくは:
surrender_value = result['net_value']  # ✅

# Line 407, 459: TypeError
fund_plan = FundPlan(
    capital_gains_tax_rate=...  # ❌ この引数は存在しない
)
# 正しくは:
fund_plan = FundPlan(
    monthly_investment=...,
    annual_rate=...,
    investment_period=...,
    fee_rate=...
)
```

**未カバー行（127-143, 192-200, 235-248, 301-367, 416-429, 468-480, 505-568, 581-626）**:
- `calculate_total_benefit`: 解約所得税計算（127-143行）
- `optimize_withdrawal_timing`: 最適タイミング探索（192-200行）
- `analyze_income_scenarios`: 所得シナリオ分析（235-248行）
- `analyze_all_strategies`: 全戦略分析（301-367行）
- `_calculate_partial_withdrawal_benefit`: 部分引き出し計算（416-429行）
- `_calculate_switch_benefit`: 切り替え戦略計算（468-480行）
- プライベートヘルパーメソッド（505-568, 581-626行）

**修正アクション**:
1. **即座修正**: Line 124の`result.net_value` → `result['net_value']`
2. **FundPlan修正**: Line 407, 459の引数を正しいシグネチャに変更
3. **テスト追加**: 未カバー行のテストケース10-15件追加

---

### 【優先度高】低カバレッジモジュール

#### 2. `pension_calc/core/pension_utils.py` (48.44%)

**未カバー行**:
- **170行**: `os.makedirs(DATA_DIR, exist_ok=True)` - ディレクトリ作成
- **174-189行**: `_coerce_dtypes()` - DataFrame型強制変換
  - 数値列変換（Int64）
  - 文字列列変換（string）
  - 欠損値処理（fillna）
- **209-238行**: `get_career_model()` - キャリアモデル取得
  - `default`モデル（30-60歳）
  - `expanded`モデル（25-60歳）
  - `to_yen`オプション
- **243-247行**: 未使用コード（削除候補）
- **254-272行**: `estimate_income_by_company_growth()` - 年収推定
  - 企業成長モデル（段階的昇給）
  - 役職別年収推定

**追加すべきテストケース（推定15-20件）**:
1. `_coerce_dtypes()`のテスト（5件）
   - 正常系: 正しいDataFrame変換
   - 異常系: 欠損値含むDataFrame
   - 異常系: 不正な列名
   - 境界値: 空DataFrame
   - 境界値: 数値文字列混在

2. `get_career_model()`のテスト（6件）
   - 正常系: `default`モデル
   - 正常系: `expanded`モデル
   - 正常系: `to_yen=True`
   - 異常系: 不正なモデル名
   - 検証: 年齢昇順
   - 検証: 年収範囲

3. `estimate_income_by_company_growth()`のテスト（4件）
   - 正常系: 基本パターン
   - 境界値: 最小年齢
   - 境界値: 最大年齢
   - 異常系: 範囲外年齢

4. ディレクトリ作成テスト（2件）
   - 正常系: ディレクトリ作成
   - 正常系: 既存ディレクトリ

**修正アクション**:
1. `tests/test_pension_utils.py`に15-20テストケース追加
2. カバレッジ測定: 48% → 70%目標

---

#### 3. `life_insurance/analysis/scenario_analyzer.py` (12.50%)

**未カバー箇所（ほぼ全体）**:
- **45-73行**: `compare_scenarios()` - シナリオ比較
- **85-100行**: `analyze_tax_impact()` - 税効果分析
- **135-155行**: `generate_report()` - レポート生成
- **174-222行**: `calculate_scenario_metrics()` - メトリクス計算
- **243-272行**: `compare_with_alternatives()` - 代替案比較
- **288-316行**: `analyze_sensitivity()` - 感度分析
- **334-367行**: `generate_visualization_data()` - 可視化データ生成
- **372-422行**: プライベートメソッド群

**追加すべきテストケース（推定30-40件）**:
1. `compare_scenarios()`テスト（8件）
   - 正常系: 2シナリオ比較
   - 正常系: 複数シナリオ比較
   - 異常系: 空シナリオリスト
   - 異常系: 不正なシナリオ形式
   - 境界値: 1シナリオのみ
   - 検証: 最適シナリオ選択
   - 検証: メトリクス計算
   - 検証: ソート順

2. `analyze_tax_impact()`テスト（6件）
   - 正常系: 標準所得
   - 正常系: 高所得
   - 正常系: 低所得
   - 境界値: 所得0円
   - 検証: 税率計算
   - 検証: 節税効果計算

3. `generate_report()`テスト（6件）
   - 正常系: 完全レポート
   - 正常系: サマリーのみ
   - 正常系: 詳細レポート
   - 検証: レポート形式
   - 検証: データ整合性
   - 検証: 出力形式

4. その他メソッドテスト（10-20件）
   - `calculate_scenario_metrics()`
   - `compare_with_alternatives()`
   - `analyze_sensitivity()`
   - `generate_visualization_data()`

**修正アクション**:
1. `life_insurance/tests/test_scenario_analyzer.py`作成
2. 30-40テストケース追加
3. カバレッジ測定: 12.5% → 50%目標

---

#### 4. `life_insurance/analysis/withdrawal_optimizer.py` (39.86%)

**テスト失敗修正後の追加テストケース（10-15件）**:
1. `calculate_policy_value()`追加テスト（3件）
   - 境界値: 初期保険料0円
   - 境界値: 非常に長い期間（50年）
   - 異常系: 負の利回り

2. `calculate_total_benefit()`追加テスト（3件）
   - 境界値: 解約利益が50万円以下（非課税）
   - 境界値: 解約利益が50万円超（課税）
   - 異常系: 将来年が開始年より前

3. `optimize_withdrawal_timing()`追加テスト（2件）
   - 境界値: max_years=1
   - 検証: 最適年が正しい

4. `analyze_income_scenarios()`追加テスト（2件）
   - 正常系: 複数シナリオ
   - 境界値: 1シナリオのみ

5. `analyze_all_strategies()`追加テスト（2件）
   - 正常系: 全戦略実行
   - 検証: 最適戦略選択

**修正アクション**:
1. テスト失敗修正（優先度最高）
2. 10-15テストケース追加
3. カバレッジ測定: 40% → 60%目標

---

### 【優先度中】細かいギャップ

#### 5. `common/utils/math_utils.py` (93.94%)

**未カバー行**:
- **287行**: `calculate_monthly_payment()` の異常系
- **293-295行**: エラーハンドリング

**追加テストケース（2件）**:
1. `calculate_monthly_payment()`異常系
   - 境界値: 金利0%、期間0年
   - 異常系: 元金0円

**修正アクション**:
1. `common/tests/test_math_utils.py`に2テストケース追加
2. カバレッジ測定: 93.94% → 100%目標

---

#### 6. `life_insurance/core/tax_calculator.py` (75.31%)

**未カバー行**:
- **47行**: `get_income_tax_rate()` の異常系
- **196行**: `calculate_tax_savings()` の境界値
- **218-250行**: `simulate_income_changes()` の詳細ケース

**追加テストケース（3件）**:
1. `get_income_tax_rate()`異常系（1件）
2. `calculate_tax_savings()`境界値（1件）
3. `simulate_income_changes()`詳細ケース（1件）

**修正アクション**:
1. `life_insurance/tests/test_tax.py`に3テストケース追加
2. カバレッジ測定: 75% → 85%目標

---

#### 7. `life_insurance/core/deduction_calculator.py` (68.49%)

**未カバー行**:
- **46行**: `calculate_old_deduction()` の境界値
- **121行**: `get_deduction_breakdown()` の詳細ケース
- **172-205行**: `optimize_premium_distribution()` の複雑ケース

**追加テストケース（3件）**:
1. `calculate_old_deduction()`境界値（1件）
2. `get_deduction_breakdown()`詳細ケース（1件）
3. `optimize_premium_distribution()`複雑ケース（1件）

**修正アクション**:
1. `life_insurance/tests/test_deduction.py`に3テストケース追加
2. カバレッジ測定: 68% → 80%目標

---

## 📝 実装スケジュール

### ステップ1: テスト失敗の修正（即座実行）
**推定時間**: 1-2時間

1. ✅ カバレッジ詳細分析（完了）
2. ⏳ `withdrawal_optimizer.py` Line 124修正
3. ⏳ `withdrawal_optimizer.py` Line 407, 459のFundPlan修正
4. ⏳ テスト再実行・検証

**成功基準**: 296件すべてのテスト合格

---

### ステップ2: 低カバレッジモジュールのテスト追加（優先度高）
**推定時間**: 4-6時間

1. ⏳ `pension_utils.py`テスト追加（15-20件）
2. ⏳ `scenario_analyzer.py`テスト追加（30-40件）
3. ⏳ `withdrawal_optimizer.py`追加テスト（10-15件）

**成功基準**: 
- `pension_utils.py`: 48% → 70%
- `scenario_analyzer.py`: 12.5% → 50%
- `withdrawal_optimizer.py`: 40% → 60%

---

### ステップ3: 細かいギャップの修正（優先度中）
**推定時間**: 1-2時間

1. ⏳ `math_utils.py`テスト追加（2件）
2. ⏳ `tax_calculator.py`テスト追加（3件）
3. ⏳ `deduction_calculator.py`テスト追加（3件）

**成功基準**: 
- `math_utils.py`: 93.94% → 100%
- `tax_calculator.py`: 75% → 85%
- `deduction_calculator.py`: 68% → 80%

---

### ステップ4: カバレッジ再測定・目標達成確認
**推定時間**: 0.5-1時間

1. ⏳ 全テスト実行（pytest --cov）
2. ⏳ カバレッジレポート確認
3. ⏳ CI/CDでの検証

**成功基準**: 全体カバレッジ 70%以上達成

---

### ステップ5: Task 6.1完了レポート作成
**推定時間**: 0.5-1時間

1. ⏳ 追加テスト数サマリー
2. ⏳ カバレッジ改善率レポート
3. ⏳ 残課題リスト

**成功基準**: レポート完成、Git commit

---

## 🎯 目標達成予測

### 現状カバレッジ（テスト対象モジュール）
- **common/**: 70-100%（良好）
- **life_insurance/**: 約70%（良好だが改善可能）
- **pension_calc/**: 48%（要改善）

### 目標カバレッジ（Phase 6）
- **全体**: 65% → **70%以上**
- **pension_calc/**: 48% → **70%**
- **life_insurance/analysis/**: 40% → **60%**

### 推定追加テスト数
- **最小**: 50-60件
- **最大**: 70-80件

### 推定作業時間
- **最小**: 7-11時間
- **最大**: 10-15時間

---

## 📈 HTMLカバレッジレポートの使い方

### ローカルでの確認方法
```powershell
# カバレッジ測定実行
pytest --cov=. --cov-report=term-missing --cov-report=html:htmlcov

# ブラウザでレポートを開く
# htmlcov/index.html をブラウザで開く
# Windows: start htmlcov/index.html
```

### レポートの見方
- **緑行（class="run"）**: カバー済み ✅
- **赤行（class="mis show_mis"）**: 未カバー ❌
- **黄行（class="par"）**: 部分カバー ⚠️

### 未カバー箇所の特定
1. `htmlcov/index.html`でファイル一覧確認
2. 低カバレッジファイルをクリック
3. 赤行を確認してテストケース追加
4. 再測定で緑行に変わることを確認

---

## 🚀 次のアクション

### 即座実行（優先度: 最高）
```powershell
# 1. テスト失敗の修正開始
# life_insurance/analysis/withdrawal_optimizer.py を編集
```

**担当**: AI Agent  
**期限**: 即座（30分以内）  
**検証**: `pytest life_insurance/tests/test_optimizer.py -v`

---

## 📌 関連ドキュメント

- [Phase 6実装計画](./IMPLEMENTATION_PLAN.md)
- [Phase 5完了レポート](../PHASE_5/COMPLETION_REPORT.md)
- [セキュリティレポート](../PHASE_5/SECURITY_REPORT.md)

---

**レポート作成者**: GitHub Copilot  
**最終更新**: 2025年11月8日 16:30 JST
