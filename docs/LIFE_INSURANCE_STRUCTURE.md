# 💰 生命保険料控除分析システム - 詳細構成ドキュメント

最終更新: 2025年10月18日  
バージョン: 2.0.0

## 📊 システム概要

旧生命保険料控除制度（平成23年12月31日以前の契約）の節税効果と最適な引き出しタイミングを分析する包括的なWebアプリケーションシステム。

## 🏗️ アーキテクチャ

```
life_insurance/
├── __init__.py         # 📦 パッケージエントリポイント
├── config.py           # ⚙️ システム設定ファイル（NEW）
├── core/               # 🔧 コア計算エンジン（税額・控除計算）
│   ├── __init__.py
│   ├── deduction_calculator.py
│   └── tax_calculator.py
├── analysis/           # 📊 高度分析機能（最適化・シナリオ分析）
│   ├── __init__.py
│   ├── withdrawal_optimizer.py
│   └── scenario_analyzer.py
├── ui/                 # 🖥️ ユーザーインターフェース（Streamlit Web UI）
│   ├── __init__.py
│   ├── streamlit_app.py        # メインアプリ
│   └── comparison_app.py       # 投資信託比較アプリ
└── tests/              # ✅ テストスイート（NEW）
    ├── __init__.py
    ├── test_deduction.py
    ├── test_tax.py
    └── test_optimizer.py
```

---

## 📁 詳細構成

### � **パッケージ構造（改善済み）**

#### 📄 `life_insurance/__init__.py`
**パッケージのエントリポイント**

すべての主要クラスをインポートし、外部から簡単にアクセス可能にします。

```python
from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer
from life_insurance.analysis.scenario_analyzer import ScenarioAnalyzer

__all__ = [
    "LifeInsuranceDeductionCalculator",
    "TaxCalculator",
    "WithdrawalOptimizer",
    "ScenarioAnalyzer",
]
```

**使用例**:
```python
# パッケージから直接インポート可能
from life_insurance import WithdrawalOptimizer

optimizer = WithdrawalOptimizer()
```

---

### ⚙️ **config.py - システム設定ファイル（NEW）**

システム全体で使用する定数、税率テーブル、デフォルト値を一元管理。

**主要設定**:

1. **税率設定（2024年度）**
   - `TAX_BRACKETS`: 所得税率テーブル
   - `RESIDENT_TAX_RATE`: 住民税率（10%）
   - `RECONSTRUCTION_TAX_RATE`: 復興特別所得税率（2.1%）

2. **生命保険料控除設定**
   - `OLD_INSURANCE_DEDUCTION_MAX`: 旧制度の上限（50,000円）
   - `OLD_DEDUCTION_BRACKETS`: 控除額計算区分

3. **保険運用設定**
   - `DEFAULT_RETURN_RATE`: デフォルト運用利回り（1.25%）
   - `CANCELLATION_PENALTY_RATES`: 解約控除率

4. **再投資オプション設定**
   - `REINVESTMENT_OPTIONS`: 部分解約後の資金運用オプション
   - `DEFAULT_REINVEST_RATE`: デフォルト再投資利回り（1%）

5. **UI設定**
   - `PAGE_TITLE`: ページタイトル
   - `NUMBER_FORMAT`: 数値フォーマット
   - `COLOR_PALETTE`: カラーパレット

**使用例**:
```python
from life_insurance.config import TAX_BRACKETS, DEFAULT_RETURN_RATE

# 設定値を参照
rate = DEFAULT_RETURN_RATE  # 0.0125
```

---

### �🔧 **core/ - コア計算エンジン**

基本的な控除額計算と税額計算を提供する基盤モジュール。

#### 📄 `deduction_calculator.py`
**旧生命保険料控除額の計算エンジン**

**クラス**: `LifeInsuranceDeductionCalculator`

**主要メソッド**:

1. **`calculate_old_deduction(annual_premium: float) -> float`**
   - 旧制度の控除額を計算
   - 入力: 年間保険料
   - 出力: 控除額（最大50,000円）
   - 計算式:
     ```
     25,000円以下: 全額
     25,001～50,000円: 保険料 × 50% + 12,500円
     50,001～100,000円: 保険料 × 25% + 25,000円
     100,001円以上: 50,000円（上限）
     ```

2. **`get_deduction_breakdown(annual_premium: float) -> Dict`**
   - 控除額の詳細内訳を返す
   - 段階ごとの計算過程を可視化

3. **`calculate_multiple_contracts(contracts: List[float]) -> Dict`**
   - 複数契約の合算控除額を計算
   - 合計保険料から控除額を算出

4. **`optimize_premium_distribution(total_budget: float, num_contracts: int) -> Dict`**
   - 複数契約への保険料配分を最適化
   - 控除額を最大化する配分を提案

**使用例**:
```python
calculator = LifeInsuranceDeductionCalculator()
deduction = calculator.calculate_old_deduction(100000)  # 50,000円
```

---

#### 📄 `tax_calculator.py`
**税額計算と節税効果分析エンジン**

**クラス**: `TaxCalculator`

**主要メソッド**:

1. **`get_income_tax_rate(taxable_income: float) -> float`**
   - 課税所得に応じた所得税率を返す
   - 累進課税の税率表に基づく

2. **`calculate_income_tax(taxable_income: float) -> Dict`**
   - 所得税・復興特別所得税の詳細計算
   - 出力: 各種税額の内訳

3. **`calculate_tax_savings(deduction_amount: float, taxable_income: float) -> Dict`**
   - 控除による節税効果を計算
   - 所得税・住民税の節税額を算出
   - 出力例:
     ```python
     {
         "所得税節税額": 10500,
         "住民税節税額": 5000,
         "合計節税額": 15500,
         "節税率": 0.155
     }
     ```

4. **`get_tax_bracket_info(taxable_income: float) -> Dict`**
   - 現在の税率区分情報を取得
   - 次の税率区分までの余裕額も算出

5. **`simulate_income_changes(base_income: float, scenarios: List) -> pd.DataFrame`**
   - 所得変動シナリオでの税額シミュレーション
   - 複数の所得水準での比較分析

**税率表（2024年度）**:
```
課税所得         所得税率   控除額
195万円以下      5%        0円
195万～330万円   10%       97,500円
330万～695万円   20%       427,500円
695万～900万円   23%       636,000円
900万～1800万円  33%       1,536,000円
1800万～4000万円 40%       2,796,000円
4000万円超       45%       4,796,000円
```

**使用例**:
```python
tax_calc = TaxCalculator()
savings = tax_calc.calculate_tax_savings(50000, 5000000)
# 課税所得500万円で控除額5万円の節税効果を計算
```

---

### 📊 **analysis/** - 高度分析機能

最適化アルゴリズムとシナリオ分析を提供するモジュール。

#### 📄 `withdrawal_optimizer.py`
**引き出しタイミング最適化エンジン**

**クラス**: `WithdrawalOptimizer`

**主要メソッド**:

1. **`calculate_policy_value(initial_premium, annual_premium, years, return_rate) -> Dict`**
   - 保険の解約返戻金を計算
   - 複利計算による運用益を考慮
   - 解約控除率も反映（経過年数により減少）

2. **`calculate_total_benefit(annual_premium, taxable_income, withdrawal_year, ...) -> Dict`**
   - 総合的な利益を計算
   - 節税効果 + 解約返戻金 - 解約所得税 - 払込保険料
   - 一時所得の計算（50万円控除、1/2課税）を考慮

3. **`optimize_withdrawal_timing(annual_premium, taxable_income, ...) -> Tuple`**
   - 最適な引き出しタイミングを分析
   - 1年～最大年数までの全パターンをシミュレーション
   - 最も純利益が高いタイミングを特定

4. **`analyze_income_scenarios(annual_premium, base_income, scenarios, ...) -> pd.DataFrame`**
   - 異なる所得シナリオでの比較分析
   - 低所得・基準・高所得での効果を比較

5. **`analyze_all_strategies(...) -> pd.DataFrame`** ⭐ **NEW**
   - **複数戦略の一括分析・ランキング化**
   - 部分解約戦略（50パターン）
   - 全解約戦略（11パターン）
   - 乗り換え戦略（55パターン）
   - 合計116戦略を自動比較
   - 純利益順にランキング表示

6. **`_calculate_partial_withdrawal_benefit(...) -> float`** ⭐ **NEW**
   - 部分解約戦略の純利益計算
   - 定期的に一部を解約し、解約資金は再投資
   - **再投資利回りオプション**: 0%（現金）～5%（投資信託）
   - 保険残高と再投資資金の両方を運用

7. **`_calculate_switch_benefit(...) -> float`** ⭐ **NEW**
   - 乗り換え戦略の純利益計算
   - 既存保険を解約→新商品へ乗り換え
   - 乗り換え手数料を考慮

8. **`analyze_tax_reform_impact(...) -> Dict`**
   - 税制改正の影響を分析
   - 改正前後の節税効果を比較

**使用例**:
```python
optimizer = WithdrawalOptimizer()

# 最適タイミング分析
best, all_results = optimizer.optimize_withdrawal_timing(
    annual_premium=100000,
    taxable_income=5000000,
    policy_start_year=2020,
    max_years=15
)

# 複数戦略ランキング
df_ranking = optimizer.analyze_all_strategies(
    annual_premium=108000,
    taxable_income=6000000,
    policy_start_year=2010,
    interval_range=[1,2,3,4,5],
    rate_range=[0.21, 0.51, 0.81],
    full_withdrawal_years=[10,15,20],
    switch_years=[10,15],
    switch_rates=[0.01, 0.03, 0.05],
    max_years=20,
    return_rate=0.0125,
    withdrawal_reinvest_rate=0.01  # 預金1%で再投資
)
```

---

#### 📄 `scenario_analyzer.py`
**シナリオ・感度・リスク分析エンジン**

**クラス**: `ScenarioAnalyzer`

**主要メソッド**:

1. **`create_comprehensive_scenario(...) -> pd.DataFrame`**
   - 包括的なシナリオ分析
   - 複数の保険料・所得・運用利回りの組み合わせを評価

2. **`analyze_sensitivity(base_params, variable, range_values) -> Dict`**
   - 感度分析（パラメータ変動の影響評価）
   - 保険料・所得・利回り等の変化による純利益への影響を可視化

3. **`create_monte_carlo_simulation(...) -> Dict`**
   - モンテカルロシミュレーション
   - 運用利回りの不確実性を考慮
   - 信頼区間の算出

4. **`plot_scenario_comparison(scenario_results) -> Figure`**
   - シナリオ比較グラフの作成
   - Plotlyによるインタラクティブな可視化

5. **`generate_recommendation_report(scenario_results) -> str`**
   - 分析結果に基づく推奨レポート生成
   - リスク評価と具体的な提案を含む

**使用例**:
```python
analyzer = ScenarioAnalyzer()

# 感度分析
sensitivity = analyzer.analyze_sensitivity(
    base_params={
        'annual_premium': 100000,
        'taxable_income': 5000000,
        'return_rate': 0.02
    },
    variable='return_rate',
    range_values=[0.01, 0.015, 0.02, 0.025, 0.03]
)
```

---

### 🖥️ **ui/** - ユーザーインターフェース

Streamlitベースの対話的Webアプリケーション。

#### 📄 `streamlit_app.py`
**メインWebアプリケーション**

**主要ページ**:

1. **🏠 ホーム**
   - システム概要とナビゲーション
   - 主要機能の紹介

2. **💰 生命保険控除について**
   - 基本控除計算
   - 引き出しタイミング最適化
   - 所得シナリオ比較

3. **📊 投資信託との比較**
   - 生命保険vs投資信託の資産形成効果比較
   - 手数料・税制の違いを考慮

4. **🏆 詳細分析（戦略ランキング）** ⭐ **NEW**
   - **複数戦略の同時比較・ランキング表示**
   - **部分解約後の資金運用オプション選択**
   - パラメータ自動生成（±5年±50%範囲）
   - インタラクティブなデータテーブル

**主要機能関数**:

- **`_show_detailed_plan_analysis()`** ⭐ **UPDATED**
  - 詳細プラン分析のUI
  - プラン設定（月払保険料、年利、契約期間、課税所得）
  - **再投資オプション選択UI**（預金・投資信託・カスタム）
  - 「📊 詳細分析を実行」ボタン
  - 戦略ランキング表の表示

- `show_home_page()`
  - ホーム画面

- `show_life_insurance_analysis()`
  - 生命保険控除の基本分析

- `show_mutual_fund_comparison()`
  - 投資信託との比較分析

- `show_deduction_calculator()`
  - 基本控除計算機能

**UIコンポーネント**:
- サイドバーナビゲーション
- タブ式レイアウト
- Plotlyインタラクティブグラフ
- データフレーム表示
- メトリクスカード
- 入力フォーム

**起動方法**:
```bash
streamlit run life_insurance/ui/streamlit_app.py
```

---

#### 📄 `comparison_app.py`
**投資信託比較専用アプリ**

生命保険料控除と投資信託（つみたてNISA等）の詳細比較に特化したアプリ。

---

#### 📄 `streamlit_app_fixed.py`
**バックアップファイル**

開発中の安定版バックアップ。

---

### ✅ **tests/ - テストスイート（NEW）**

pytest を使用した包括的なテストスイート。

#### 📄 `test_deduction.py`
**控除額計算のテスト**

**テストクラス**:
- `TestDeductionCalculator`: 基本的な控除額計算
- `TestEdgeCases`: エッジケース（境界値、異常値）

**主要テストケース**:
```python
def test_calculate_old_deduction_below_25000(self, calculator):
    """保険料が25,000円以下の場合のテスト（全額控除）"""
    assert calculator.calculate_old_deduction(10000) == 10000
    assert calculator.calculate_old_deduction(25000) == 25000

def test_calculate_old_deduction_above_100000(self, calculator):
    """保険料が100,001円以上の場合のテスト（上限50,000円）"""
    assert calculator.calculate_old_deduction(120000) == 50000
```

**実行方法**:
```bash
pytest life_insurance/tests/test_deduction.py -v
```

---

#### 📄 `test_tax.py`
**税額計算のテスト**

**テストクラス**:
- `TestTaxCalculator`: 基本的な税額計算
- `TestTaxBrackets`: 税率区分の境界値
- `TestReconstructionTax`: 復興特別所得税

**主要テストケース**:
```python
def test_calculate_income_tax(self, calculator):
    """所得税計算のテスト"""
    result = calculator.calculate_income_tax(5000000)
    expected_income_tax = 5000000 * 0.20 - 427500
    assert abs(result["所得税"] - expected_income_tax) < 1

def test_calculate_tax_savings(self, calculator):
    """節税効果計算のテスト"""
    result = calculator.calculate_tax_savings(
        deduction_amount=50000,
        taxable_income=5000000
    )
    assert result["所得税節税額"] > 10000
    assert result["住民税節税額"] == 5000
```

**実行方法**:
```bash
pytest life_insurance/tests/test_tax.py -v
```

---

#### 📄 `test_optimizer.py`
**引き出しタイミング最適化のテスト**

**テストクラス**:
- `TestWithdrawalOptimizer`: 基本的な最適化機能
- `TestPartialWithdrawal`: 部分解約戦略
- `TestFullWithdrawal`: 全解約戦略
- `TestSwitchStrategy`: 乗り換え戦略
- `TestEdgeCases`: エッジケース

**主要テストケース**:
```python
def test_analyze_all_strategies(self, optimizer):
    """全戦略分析のテスト"""
    result = optimizer.analyze_all_strategies(
        annual_premium=100000,
        taxable_income=5000000,
        policy_start_year=2020,
        interval_range=[1, 2],
        rate_range=[0.5],
        full_withdrawal_years=[10],
        switch_years=[10],
        switch_rates=[0.03],
        max_years=15,
        return_rate=0.02,
        withdrawal_reinvest_rate=0.01
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
```

**全テスト実行**:
```bash
# すべてのテストを実行
pytest life_insurance/tests/ -v

# カバレッジレポート付きで実行
pytest life_insurance/tests/ --cov=life_insurance --cov-report=html
```

---

## 🔗 モジュール間の依存関係（改善済み）

```
ui/streamlit_app.py
ui/comparison_app.py
    ↓
analysis/withdrawal_optimizer.py
analysis/scenario_analyzer.py
    ↓
core/deduction_calculator.py
core/tax_calculator.py
    ↓
config.py (設定ファイル)
```

**依存関係の説明**:
1. UI層は分析層のクラスを利用
2. 分析層はコア層の計算エンジンを利用
3. すべての層が config.py の設定値を参照可能
4. 各層は独立してテスト・メンテナンス可能

**インポート規約（統一済み）**:
```python
# ✅ 正しいインポート（絶対パス）
from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer

# ❌ 避けるべきインポート（sys.path 操作）
import sys
sys.path.append(os.path.dirname(__file__))
from core.deduction_calculator import LifeInsuranceDeductionCalculator
```

---

## 📊 主要データフロー

### 戦略ランキング分析のフロー

```
1. ユーザー入力（UI）
   ├─ 月払保険料
   ├─ 年利
   ├─ 契約期間
   ├─ 課税所得
   └─ 再投資オプション ⭐ NEW
       ↓
2. パラメータ自動生成
   ├─ 年数範囲: ±5年
   ├─ 解約割合: ±50%
   ├─ 間隔: 1～5年
   └─ 手数料率: 1～5%
       ↓
3. 戦略シミュレーション
   ├─ 部分解約戦略（50パターン）
   │   └─ 再投資利回りで運用 ⭐ NEW
   ├─ 全解約戦略（11パターン）
   └─ 乗り換え戦略（55パターン）
       ↓
4. ランキング化・表示
   └─ 純利益順にソート
```

---

## 🎯 主要機能とユースケース

### 1. 基本控除計算
**ユーザー**: 保険契約を検討中の個人
**目的**: 年間保険料に応じた控除額と節税効果を確認
**使用モジュール**: `deduction_calculator.py`, `tax_calculator.py`

### 2. 引き出しタイミング最適化
**ユーザー**: 既存保険契約者
**目的**: 最も利益が高い解約タイミングを特定
**使用モジュール**: `withdrawal_optimizer.py`

### 3. 戦略ランキング比較 ⭐ NEW
**ユーザー**: 資産運用を最適化したい個人
**目的**: 部分解約・全解約・乗り換えの116戦略を比較
**使用モジュール**: `withdrawal_optimizer.py`, `streamlit_app.py`
**特徴**:
- 部分解約後の資金運用を考慮
- 預金・投資信託など再投資先を選択可能
- 現実的な比較で最適戦略を発見

### 4. シナリオ分析
**ユーザー**: リスクを考慮した計画を立てたい個人
**目的**: 複数の将来シナリオでの効果を比較
**使用モジュール**: `scenario_analyzer.py`

### 5. 感度分析
**ユーザー**: パラメータの影響を理解したい個人
**目的**: 運用利回り・所得等の変動による影響度を評価
**使用モジュール**: `scenario_analyzer.py`

---

## 🚀 起動方法

### メインアプリ起動（推奨）

**方法1: 専用スクリプトを使用**
```bash
# 仮想環境有効化
.\.venv\Scripts\Activate.ps1

# 専用スクリプトで起動
python scripts/run_life_insurance_app.py
```

**方法2: Streamlit 直接起動**
```bash
streamlit run life_insurance/ui/streamlit_app.py
```

### 投資信託比較アプリ起動

```bash
# 専用スクリプトで起動（ポート8502）
python scripts/run_comparison_app.py

# または直接起動
streamlit run life_insurance/ui/comparison_app.py
```

### 起動時のポート設定

| アプリ | デフォルトポート | 用途 |
|--------|-----------------|------|
| メインアプリ (streamlit_app.py) | 8507 | 引き出しタイミング最適化 |
| 比較アプリ (comparison_app.py) | 8502 | 投資信託との比較 |
| 年金計算アプリ (pension) | 8511 | 年金シミュレーション |
| NISA投資アプリ (investment) | 8512 | NISA投資分析 |

---

## 🔧 技術スタック

### コア技術
- **Python**: 3.12+
- **パッケージ管理**: uv / pip
- **Streamlit**: Webアプリフレームワーク
- **pandas**: データ処理・分析
- **numpy**: 数値計算

### 可視化
- **plotly**: インタラクティブグラフ
- **matplotlib**: 静的グラフ
- **seaborn**: 統計的可視化

### テスト
- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ測定

### その他
- **typing**: 型ヒント
- **datetime**: 日付処理

### 開発ツール
- **VS Code**: 推奨IDE
- **Git**: バージョン管理

---

## 📈 最新の改善内容（2025年10月18日）

### ✅ パッケージ構造の正規化

**改善内容**:
1. **`__init__.py` の整備**
   - すべての主要クラスを適切にエクスポート
   - パッケージとしての一貫性を確保

2. **インポート文の統一**
   - `sys.path` の手動操作を削除
   - 絶対インポート（`life_insurance.core.xxx`）に統一
   - 環境依存の脆弱なコードを排除

3. **設定ファイルの分離**
   - `config.py` を新規作成
   - 税率テーブル、デフォルト値を一元管理
   - マジックナンバーを削減

4. **テストスイートの追加**
   - `test_deduction.py`: 控除額計算のテスト
   - `test_tax.py`: 税額計算のテスト
   - `test_optimizer.py`: 最適化機能のテスト
   - pytest による包括的なテストカバレッジ

5. **不要ファイルの整理**
   - `streamlit_app_fixed.py` を削除
   - `comparison_app.py` の用途を明確化
   - 起動スクリプトを改善

**効果**:
- ✅ **保守性の向上**: パッケージとして一貫性のある構造
- ✅ **テスタビリティ**: 単体テストが容易
- ✅ **可読性**: インポート文が明確
- ✅ **拡張性**: 新機能追加が容易
- ✅ **品質保証**: テストによる継続的な検証

---

### ⭐ 部分解約後の資金運用機能（前回実装）

**背景**: 
従来の実装では、部分解約した資金が「どこに行くか」が不明確でした。

**改善内容**:
1. **再投資利回りオプションの追加**
   - 預金（年利1%）【デフォルト】
   - 運用なし（現金保有、年利0%）
   - 投資信託（年利3%）
   - 投資信託（年利5%）
   - カスタム（任意の年利）

2. **計算ロジックの改善**
   - 部分解約した資金を複利で運用
   - 毎年、既に解約した資金に利息を付与
   - 最終的な資産価値 = 保険残高 + 再投資資金（運用後）

3. **UIの拡張**
   - 「💰 部分解約後の資金運用」セクション追加
   - ドロップダウンで運用先を選択
   - 選択した利回りがリアルタイムで反映

**効果**:
```
再投資利回り0%:  純利益 597万円（全解約より+544万円）
再投資利回り1%:  純利益 637万円（全解約より+584万円）
再投資利回り3%:  純利益 729万円（全解約より+676万円）
再投資利回り5%:  純利益 838万円（全解約より+785万円）
```

---

## 📝 開発・メンテナンス

### コーディング規約
- **型ヒント**: すべての関数に引数・戻り値の型を明記
- **Docstring**: Google形式で記述
- **命名**: snake_case（関数・変数）、PascalCase（クラス）
- **インポート**: 絶対パス（`life_insurance.xxx`）を使用

### テスト実行

**すべてのテストを実行**:
```bash
pytest life_insurance/tests/ -v
```

**特定のテストファイルを実行**:
```bash
pytest life_insurance/tests/test_deduction.py -v
```

**カバレッジレポート付き**:
```bash
pytest life_insurance/tests/ --cov=life_insurance --cov-report=html
```

**テスト結果の確認**:
```bash
# HTMLレポートを開く
start htmlcov/index.html  # Windows
```

### 新機能追加の流れ

1. **コア層**: 計算ロジックを実装
   ```python
   # life_insurance/core/new_calculator.py
   class NewCalculator:
       def calculate(self):
           pass
   ```

2. **テスト追加**: pytest でテストを作成
   ```python
   # life_insurance/tests/test_new_calculator.py
   def test_calculate():
       calc = NewCalculator()
       assert calc.calculate() == expected_value
   ```

3. **分析層**: 高度な分析アルゴリズムを追加
   ```python
   # life_insurance/analysis/new_analyzer.py
   from life_insurance.core.new_calculator import NewCalculator
   ```

4. **UI層**: Streamlitで対話的UIを構築
   ```python
   # life_insurance/ui/streamlit_app.py
   from life_insurance.analysis.new_analyzer import NewAnalyzer
   ```

5. **設定追加**: 必要に応じて config.py に定数を追加
   ```python
   # life_insurance/config.py
   NEW_FEATURE_CONSTANT = 0.05
   ```

### デバッグ

**Pythonデバッグ**:
```bash
# 特定のモジュールを直接実行
python -m life_insurance.core.deduction_calculator
```

**Streamlitデバッグモード**:
```bash
streamlit run life_insurance/ui/streamlit_app.py --logger.level=debug
```

---

## 📚 ドキュメント一覧

1. **`README_old.md`**: プロジェクト全体の概要
2. **`LIFE_INSURANCE_STRUCTURE.md`**: 本ドキュメント（詳細構成）
3. **`VERIFICATION_GUIDE.md`**: 動作確認ガイド
4. **`WITHDRAWAL_REINVESTMENT_GUIDE.md`**: 部分解約後の資金運用ガイド

---

## 🎓 学習リソース

### システム理解のための推奨学習順序

1. **基本**: `core/deduction_calculator.py`
   - 控除額計算の基礎を理解

2. **税務**: `core/tax_calculator.py`
   - 日本の税制（累進課税）を学習

3. **最適化**: `analysis/withdrawal_optimizer.py`
   - 最適化アルゴリズムの実装を学習

4. **分析**: `analysis/scenario_analyzer.py`
   - シナリオ分析・感度分析の手法を学習

5. **UI**: `ui/streamlit_app.py`
   - Streamlitの使い方を習得

---

## 🔮 今後の開発予定

### 短期（1～2ヶ月）
- [x] `tests/` ディレクトリの充実 ✅
- [x] パッケージ構造の正規化 ✅
- [x] 設定ファイルの分離 ✅
- [ ] エラーハンドリングの強化
- [ ] パフォーマンス最適化（大規模データ対応）
- [ ] ロギング機能の追加

### 中期（3～6ヶ月）
- [ ] 新生命保険料控除（平成24年以降）対応
- [ ] データベース連携（過去の分析結果保存）
- [ ] PDFレポート自動生成
- [ ] CI/CD パイプラインの構築
- [ ] Docker コンテナ化

### 長期（6ヶ月～1年）
- [ ] 機械学習による最適戦略予測
- [ ] マルチユーザー対応
- [ ] クラウドデプロイ（AWS/Azure）
- [ ] REST API の提供
- [ ] モバイルアプリ対応

---

## 📞 サポート・問い合わせ

### 技術的な質問
- コア計算: `core/` 関連
- 分析機能: `analysis/` 関連
- UI/UX: `ui/` 関連

### バグ報告
- 計算結果の誤り
- UI表示の不具合
- パフォーマンス問題

---

## ⚠️ 注意事項

このツールは**分析・参考用**です。

- 実際の税額は個々の状況により異なります
- 保険商品の選択は専門家にご相談ください
- 運用利回りは保証されるものではありません
- 税制は変更される可能性があります

---

**最終更新**: 2025年10月18日  
**バージョン**: 2.0  
**メンテナー**: プロジェクト開発チーム
---

##  関連ドキュメント

1. **README.md**: プロジェクト全体の概要
2. **LIFE_INSURANCE_STRUCTURE.md**: 本ドキュメント（詳細構成）
3. **VERIFICATION_GUIDE.md**: 動作確認ガイド
4. **WITHDRAWAL_REINVESTMENT_GUIDE.md**: 部分解約後の資金運用ガイド
5. **.github/copilot-instructions.md**: AI エージェント向けプロジェクト指示

---

##  クイックスタートガイド

### 初回セットアップ

```bash
# 1. リポジトリをクローン
cd my-project

# 2. 仮想環境を有効化
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. テストを実行（動作確認）
pytest life_insurance/tests/ -v

# 4. アプリを起動
python scripts/run_life_insurance_app.py
```

### 基本的な使い方

```python
# パッケージから直接インポート
from life_insurance import (
    LifeInsuranceDeductionCalculator,
    TaxCalculator,
    WithdrawalOptimizer,
)

# 控除額を計算
calc = LifeInsuranceDeductionCalculator()
deduction = calc.calculate_old_deduction(annual_premium=100000)
print(f\"控除額: {deduction:,}円\")  # 控除額: 50,000円

# 節税効果を計算
tax_calc = TaxCalculator()
savings = tax_calc.calculate_tax_savings(
    deduction_amount=50000,
    taxable_income=5000000
)
print(f\"合計節税額: {savings['合計節税額']:,}円\")

# 引き出しタイミングを最適化
optimizer = WithdrawalOptimizer()
best, all_results = optimizer.optimize_withdrawal_timing(
    annual_premium=100000,
    taxable_income=5000000,
    policy_start_year=2020,
    max_years=15
)
print(f\"最適な引き出し年: {best['引き出し年']}年\")
print(f\"純利益: {best['純利益']:,}円\")
```
