# 🚀 Phase 1: 税金ヘルパー実装

**期間:** 1-2週間  
**優先度:** 🔴 最高  
**期待削減:** ~500行

---

## 📋 タスクチェックリスト

### Task 1.1: 税金ヘルパーモジュール作成

#### ステップ 1: ディレクトリ作成
```bash
mkdir -p life_insurance/utils
touch life_insurance/utils/__init__.py
```

- [x] `life_insurance/utils/` ディレクトリ作成 ✅
- [x] `life_insurance/utils/__init__.py` 作成 ✅

#### ステップ 2: tax_helpers.py 実装

- [x] ファイル作成: `life_insurance/utils/tax_helpers.py` ✅
- [x] `TaxDeductionHelper` クラス実装 ✅
  - [x] `__init__()` メソッド ✅
  - [x] `calculate_annual_tax_savings()` メソッド ✅
  - [x] `calculate_total_tax_savings_over_years()` メソッド ✅
- [x] `get_tax_helper()` シングルトン関数実装 ✅
- [x] 型ヒント完備 ✅
- [x] docstring充実 ✅

**参考コード:** `REFACTORING/PHASE_1/templates/tax_helpers.py` 参照

#### ステップ 3: テスト作成

- [x] ファイル作成: `life_insurance/tests/test_tax_helpers.py` ✅
- [x] 基本計算テスト ✅
  - [x] 正常系テスト（複数パターン） ✅
  - [x] 課税所得別テスト ✅
  - [x] 年間保険料別テスト ✅
- [x] エッジケーステスト ✅
  - [x] 0円のケース ✅
  - [x] 上限値のケース ✅
- [x] 境界値テスト ✅

**実行コマンド:**
```bash
pytest life_insurance/tests/test_tax_helpers.py -v
```

- [x] すべてのテストがパス ✅ (25/25件)

---

### Task 1.2: 既存コードの置換

#### ステップ 1: 重複箇所の特定（完了済み）

以下の30箇所で同じパターンが繰り返されています:

```python
calculator = LifeInsuranceDeductionCalculator()
deduction = calculator.calculate_old_deduction(annual_premium)
tax_calc = TaxCalculator()
tax_savings_result = tax_calc.calculate_tax_savings(deduction, taxable_income)
annual_tax_savings = tax_savings_result["合計節税額"]
```

**対象ファイル:**
- `life_insurance/ui/streamlit_app.py` (28箇所)
- `life_insurance/ui/comparison_app.py` (2箇所)

#### ステップ 2: インポート追加

各ファイルの先頭に追加:
```python
from life_insurance.utils.tax_helpers import get_tax_helper
```

- [x] `streamlit_app.py` にインポート追加 ✅
- [ ] `comparison_app.py` にインポート追加

#### ステップ 3: 段階的置換（10箇所ずつ）

**置換前:**
```python
calculator = LifeInsuranceDeductionCalculator()
deduction = calculator.calculate_old_deduction(annual_premium)
tax_calc = TaxCalculator()
tax_savings_result = tax_calc.calculate_tax_savings(deduction, taxable_income)
annual_tax_savings = tax_savings_result["合計節税額"]
```

**置換後:**
```python
tax_helper = get_tax_helper()
tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, taxable_income)
annual_tax_savings = tax_result['total_savings']
```

**streamlit_app.py の置換進捗:**
- [x] 1箇所目（224-230行目）✅ 2025-10-25 完了
- [ ] 2-10箇所目
- [ ] 11-20箇所目
- [ ] 21-28箇所目

**対象箇所リスト:**

**streamlit_app.py:**
1. [ ] 行102: `show_home_page()` 内
2. [ ] 行221: `_show_basic_deduction_calculator()` 内
3. [ ] 行420: `show_deduction_calculator()` 内
4. [ ] 行516: `show_withdrawal_optimizer()` 内
5. [ ] 行816: `show_scenario_analysis()` 内
6. [ ] 行1083: `calculate_final_benefit()` 内
7. [ ] 行1520: `show_report_generator()` 内
8. [ ] 行1713: `show_report_generator()` 内（2回目）
9. [ ] 行2316: `show_investment_comparison()` 内
10. [ ] 行4155: `_show_deduction_from_income()` 内

**第1バッチ完了後:**
- [ ] テスト実行: `pytest life_insurance/tests/`
- [ ] アプリ起動確認: `streamlit run life_insurance/ui/streamlit_app.py`
- [ ] 計算結果の一致確認

11. [ ] 行4297: `_show_insurance_settings()` 内
12. [ ] 行4861: `_show_insurance_comparison()` 内
13. [ ] 行5270: `_show_no_switching_analysis()` 内
14. [ ] 行5418: `_calculate_switching_value()` 内
15. [ ] 行5867: `_calculate_partial_withdrawal_value()` 内
16. [ ] 行5907: `_calculate_simple_insurance_value()` 内
17. [ ] 行6033: `_calculate_partial_withdrawal_value_enhanced()` 内
18. [ ] 行6131: `_calculate_partial_withdrawal_value_enhanced()` 内（2回目）
19-28. [ ] その他の重複箇所

**第2バッチ完了後:**
- [ ] テスト実行
- [ ] アプリ起動確認

**comparison_app.py:**
29. [ ] 行230: `calculate_insurance_investment_scenario()` 内
30. [ ] その他の重複箇所

**第3バッチ完了後:**
- [ ] 全テスト実行
- [ ] 両アプリの起動確認

---

### Task 1.3: 最終確認

- [ ] すべてのテストがパス
- [ ] Streamlitアプリが正常起動
- [ ] 比較アプリが正常起動
- [ ] 計算結果が元の実装と一致
- [ ] コミット: `git commit -m "refactor: Phase 1 - 税金ヘルパー実装完了"`

---

## 📊 Phase 1 メトリクス

### 開始時（ベースライン）
- 総行数: 8,500行
- `streamlit_app.py`: ~6,500行
- テストカバレッジ: 45%

### 完了時（目標）
- 削減行数: ~500行
- `streamlit_app.py`: ~6,000行
- テストカバレッジ: 55%
- 新規追加: `tax_helpers.py` (~150行), `test_tax_helpers.py` (~200行)

### 実績
（完了後に記入）

---

## 🐛 トラブルシューティング

### よくある問題

#### 問題 1: インポートエラー
```
ModuleNotFoundError: No module named 'life_insurance.utils'
```

**解決策:**
- `life_insurance/utils/__init__.py` が存在するか確認
- プロジェクトルートから実行しているか確認

#### 問題 2: 計算結果の不一致
```
AssertionError: 12500.0 != 12345.6
```

**解決策:**
- `tax_result['total_savings']` のキー名を確認
- 元のコードで`["合計節税額"]`を使っていた箇所を`['total_savings']`に変更

#### 問題 3: Streamlit起動エラー
```
AttributeError: 'dict' object has no attribute 'get'
```

**解決策:**
- 戻り値の辞書構造を確認
- `tax_result['total_savings']` ではなく `tax_result.get('total_savings', 0)` を使用

---

## 📝 コミットメッセージ例

```bash
# タスク1.1完了時
git add life_insurance/utils/
git commit -m "feat: 税金ヘルパーモジュール追加 (Phase 1-1.1)

- TaxDeductionHelper クラス実装
- calculate_annual_tax_savings() メソッド追加
- シングルトンパターンで get_tax_helper() 実装
- 包括的なテストスイート追加"

# タスク1.2完了時（バッチごと）
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor: streamlit_app.py 税金計算を共通化 (1-10箇所) (Phase 1-1.2)

- 重複していた税金計算コードを get_tax_helper() に置換
- 約100行のコード削減
- 既存テスト全パス確認済み"

# Phase 1完了時
git commit -m "refactor: Phase 1完了 - 税金ヘルパー実装

- 税金計算ロジックを30箇所以上で共通化
- 約500行のコード削減
- テストカバレッジ55%に向上
- 既存機能の動作確認済み"
```

---

**次のアクション:** タスク1.1から開始してください  
テンプレートコードは `templates/` ディレクトリを参照
