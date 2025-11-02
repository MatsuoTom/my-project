# 📋 Phase 2 実装計画書

**フェーズ:** Phase 2 - コア計算ロジックの統合  
**目標期間:** 2-3週間  
**優先度:** 🟠 高  
**作成日:** 2025年10月29日

---

## 🎯 Phase 2の目標

### 主要目標
- **コード削減:** -800行
- **重複削減:** 保険価値計算 30箇所以上 → 1箇所（統合エンジン）
- **テスト追加:** 50件以上
- **カバレッジ:** 47% → 60%

### 技術目標
1. 保険計算エンジンの統合
2. データクラスの導入
3. 重複関数の統合
4. 包括的テストスイート構築

---

## 📊 現状分析

### 発見された重複パターン

#### 1. **保険価値計算の重複**（14箇所）

**streamlit_app.py:**
- `calculate_final_benefit()` (行1061) - 感度分析内の計算
- `_calculate_switching_value()` (行5363) - 乗り換え戦略
- `_calculate_partial_withdrawal_value()` (行5766) - 部分解約戦略
- `_calculate_simple_insurance_value()` (行5847) - 単純継続
- `_calculate_partial_withdrawal_value_enhanced()` (行5875) - 強化版部分解約

**withdrawal_optimizer.py:**
- `calculate_policy_value()` (行25) - 解約返戻金計算
- `calculate_total_benefit()` (行70) - 総合利益計算
- `_calculate_partial_withdrawal_benefit()` (行312) - 部分解約利益
- `_calculate_switch_benefit()` (行369) - 乗り換え利益

**comparison_app.py:**
- `calculate_insurance_investment_scenario()` (行210) - シナリオ計算
- `calculate_breakeven_year()` (行311) - 損益分岐点

#### 2. **共通する計算ロジック**

**基本的な保険価値計算:**
```python
# パターン1: 複利計算（月次積立）
net_premium = monthly_premium * (1 - fee_rate)
monthly_rate = annual_rate / 12
if monthly_rate > 0:
    value = net_premium * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
else:
    value = net_premium * total_months
```

**手数料計算:**
```python
# パターン2: 積立手数料 + 残高手数料
setup_fee = monthly_premium * fee_rate * total_months
balance_fee = insurance_value * balance_fee_rate * total_months
```

**節税効果:**
```python
# パターン3: 税金ヘルパー利用（Phase 1で統一済み）
tax_helper = get_tax_helper()
tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, income)
total_tax_savings = tax_result['total_savings'] * period
```

#### 3. **重複の規模**

| ファイル | 重複箇所 | 平均行数 | 合計行数（推定） |
|---------|---------|---------|-----------------|
| streamlit_app.py | 5箇所 | 80行 | 400行 |
| withdrawal_optimizer.py | 4箇所 | 60行 | 240行 |
| comparison_app.py | 2箇所 | 50行 | 100行 |
| **合計** | **11箇所** | **-** | **740行** |

**削減可能行数:** 約700行（統合エンジン200行 + テスト300行 = 削減実質500行）

---

## 🏗️ アーキテクチャ設計

### 1. データクラス設計

#### InsurancePlan（保険プラン）
```python
@dataclass
class InsurancePlan:
    """生命保険プラン"""
    monthly_premium: float          # 月額保険料
    annual_rate: float              # 年利率（%）
    investment_period: int          # 投資期間（年）
    fee_rate: float = 0.013        # 積立手数料率
    balance_fee_rate: float = 0.00008  # 残高手数料率（月次）
    
    @property
    def annual_premium(self) -> float:
        """年間保険料"""
        return self.monthly_premium * 12
    
    @property
    def monthly_rate(self) -> float:
        """月次運用利回り"""
        return self.annual_rate / 100 / 12
```

#### FundPlan（投資信託プラン）
```python
@dataclass
class FundPlan:
    """投資信託プラン"""
    annual_return: float           # 年間期待リターン（%）
    annual_fee: float              # 実質コスト（%）
    
    @property
    def net_return(self) -> float:
        """手数料控除後リターン"""
        return self.annual_return - self.annual_fee
    
    @property
    def monthly_return(self) -> float:
        """月次リターン"""
        return self.net_return / 12
```

#### InsuranceResult（計算結果）
```python
@dataclass
class InsuranceResult:
    """保険価値計算結果"""
    insurance_value: float          # 保険価値
    total_paid: float               # 総払込額
    total_fees: float               # 総手数料
    tax_savings: float              # 節税額
    net_value: float                # 正味価値
    return_rate: float              # 実質利回り
    
    # 詳細情報（オプション）
    timeline: Optional[List[dict]] = None  # 年次推移
    breakdown: Optional[dict] = None       # 内訳
```

### 2. InsuranceCalculator（統合エンジン）

#### 基本構造
```python
class InsuranceCalculator:
    """
    生命保険価値計算の統合エンジン
    
    Phase 1で作成したtax_helperと連携して、
    保険価値計算を一元化する。
    """
    
    def __init__(self):
        """初期化"""
        self.tax_helper = get_tax_helper()
    
    # コア計算メソッド
    def calculate_simple_value(
        self, 
        plan: InsurancePlan, 
        taxable_income: float = 5000000
    ) -> InsuranceResult:
        """単純継続の価値計算"""
        pass
    
    def calculate_partial_withdrawal_value(
        self,
        plan: InsurancePlan,
        interval: int,
        withdrawal_ratio: float,
        reinvestment_option: str,
        taxable_income: float
    ) -> InsuranceResult:
        """部分解約戦略の価値計算"""
        pass
    
    def calculate_switching_value(
        self,
        plan: InsurancePlan,
        fund: FundPlan,
        switch_year: int,
        taxable_income: float
    ) -> InsuranceResult:
        """乗り換え戦略の価値計算"""
        pass
    
    def calculate_comparison(
        self,
        plan: InsurancePlan,
        fund: FundPlan,
        taxable_income: float
    ) -> dict:
        """投資信託との比較"""
        pass
    
    # ヘルパーメソッド
    def _calculate_compound_interest(
        self,
        monthly_payment: float,
        monthly_rate: float,
        total_months: int
    ) -> float:
        """複利計算（月次積立）"""
        pass
    
    def _calculate_fees(
        self,
        plan: InsurancePlan,
        insurance_value: float,
        total_months: int
    ) -> Tuple[float, float]:
        """手数料計算（積立手数料、残高手数料）"""
        pass
    
    def _calculate_tax_benefit(
        self,
        annual_premium: float,
        period: int,
        taxable_income: float
    ) -> float:
        """税制優遇効果計算"""
        pass
```

### 3. ディレクトリ構造

```
life_insurance/
├── analysis/
│   ├── __init__.py
│   ├── insurance_calculator.py    # ✨ 新規: 統合エンジン
│   ├── withdrawal_optimizer.py    # 🔄 リファクタ: エンジン利用に変更
│   └── scenario_analyzer.py       # 🔄 リファクタ: エンジン利用に変更
├── models/                        # ✨ 新規: データクラス
│   ├── __init__.py
│   ├── insurance_plan.py          # InsurancePlan, FundPlan
│   └── calculation_result.py      # InsuranceResult
├── tests/
│   ├── test_insurance_calculator.py  # ✨ 新規: 50件以上のテスト
│   ├── test_models.py                # ✨ 新規: データクラステスト
│   └── ...
└── ...
```

---

## 📅 実装スケジュール

### Week 1: データクラス + エンジン設計

#### Task 2.1: 重複箇所の詳細分析（1日）
- [x] grep検索で計算関数をリストアップ（完了）
- [ ] 各関数のシグネチャと計算ロジックを文書化
- [ ] 共通パターンの抽出
- [ ] 統合可能な箇所の特定

#### Task 2.2: データクラス設計・実装（2日）
- [ ] `models/` ディレクトリ作成
- [ ] `InsurancePlan` 実装
- [ ] `FundPlan` 実装
- [ ] `InsuranceResult` 実装
- [ ] データクラスのテスト作成（20件）

#### Task 2.3: エンジンの基本設計（2日）
- [ ] `InsuranceCalculator` クラス設計
- [ ] コアメソッドのシグネチャ定義
- [ ] ヘルパーメソッドの設計
- [ ] 設計レビュー

### Week 2: エンジン実装 + テスト

#### Task 2.4: コアメソッド実装（3日）
- [ ] `calculate_simple_value()` 実装
- [ ] `calculate_partial_withdrawal_value()` 実装
- [ ] `calculate_switching_value()` 実装
- [ ] `calculate_comparison()` 実装
- [ ] 各メソッドの単体テスト作成

#### Task 2.5: ヘルパーメソッド実装（2日）
- [ ] `_calculate_compound_interest()` 実装
- [ ] `_calculate_fees()` 実装
- [ ] `_calculate_tax_benefit()` 実装
- [ ] ヘルパーメソッドのテスト作成

#### Task 2.6: 統合テスト（2日）
- [ ] エンドツーエンドテスト作成
- [ ] 既存コードとの計算結果比較
- [ ] パフォーマンステスト
- [ ] テストカバレッジ60%達成確認

### Week 3: 既存コード置換 + 完了

#### Task 2.7: streamlit_app.py リファクタ（3日）
- [ ] 5箇所の計算関数をエンジン利用に置換
- [ ] 各置換後に動作確認
- [ ] UIテスト

#### Task 2.8: withdrawal_optimizer.py リファクタ（2日）
- [ ] 4箇所の計算メソッドをエンジン利用に変更
- [ ] 既存テストの修正
- [ ] 新規テスト追加

#### Task 2.9: comparison_app.py リファクタ（1日）
- [ ] 2箇所の計算関数をエンジン利用に変更
- [ ] 動作確認

#### Task 2.10: Phase 2完了作業（1日）
- [ ] 全テスト実行（60件以上）
- [ ] Streamlitアプリ統合テスト
- [ ] PROGRESS.md更新
- [ ] COMPLETION_REPORT.md作成
- [ ] Gitコミット・タグ（v0.4.0-phase2-complete）

---

## 🧪 テスト戦略

### テストスイート構成

#### 1. データクラステスト（20件）
- `test_models.py`
- InsurancePlanの検証テスト
- FundPlanの検証テスト
- InsuranceResultの検証テスト
- プロパティの計算テスト

#### 2. InsuranceCalculatorテスト（40件）
- `test_insurance_calculator.py`
- 基本計算テスト（10件）
  - 単純継続計算
  - 部分解約計算
  - 乗り換え計算
  - 比較計算
- ヘルパーメソッドテスト（10件）
  - 複利計算
  - 手数料計算
  - 税制優遇計算
- エッジケーステスト（10件）
  - ゼロ値
  - 負の値
  - 境界値
- 統合テスト（10件）
  - エンドツーエンド
  - 既存コードとの結果比較

#### 3. リファクタ後のテスト（10件）
- withdrawal_optimizer統合テスト
- scenario_analyzer統合テスト
- UI統合テスト

**合計:** 70件以上のテスト

---

## 📈 期待される効果

### コードメトリクス

| 指標 | Before | After | 改善率 |
|------|--------|-------|--------|
| 総コード行数 | 8,461行 | 7,661行 | -800行（-9.5%） |
| 保険計算重複 | 11箇所 | 1箇所 | **-91%** |
| 平均関数長 | 85行 | 60行 | -29% |
| テストカバレッジ | 47% | 60% | +13% |
| テスト件数 | 60件 | 130件 | +117% |

### ビジネスインパクト

**保守性:**
- 保険計算ロジックが1箇所に集約
- バグ修正時の変更箇所: 11箇所 → 1箇所
- 修正工数: **-90%削減**

**開発効率:**
- 新戦略追加時のコード量: 80行 → 20行
- 開発時間: **-75%削減**
- テスト工数: **-60%削減**（共通テストで対応）

**計算精度:**
- データクラスによる型安全性向上
- 統一された計算ロジックでバグ減少
- テストカバレッジ60%で品質保証

---

## ⚠️ リスクと対策

### リスク 1: 大規模リファクタリングによるバグ混入

**対策:**
- 段階的な実装（Week 1-3に分割）
- 各ステップでのテスト実行
- 既存コードとの計算結果比較テスト

### リスク 2: 既存コードとの互換性

**対策:**
- データクラスに変換用メソッド追加
- 既存のdict形式もサポート
- 段階的な移行戦略

### リスク 3: スケジュール遅延

**対策:**
- 2-3週間の余裕を持ったスケジュール
- 週次レビューで進捗確認
- クリティカルパスの優先実装

---

## 🎯 成功基準

### 必須要件
- ✅ 保険計算11箇所を1箇所に統合
- ✅ テスト70件以上作成・全通過
- ✅ コード800行削減
- ✅ カバレッジ60%達成
- ✅ 既存機能の動作確認（バグゼロ）

### 推奨要件
- ⭐ ドキュメント完備（docstring、README）
- ⭐ パフォーマンス維持（計算時間±10%以内）
- ⭐ 型ヒント100%
- ⭐ Gitタグ・コミットメッセージの適切性

---

## 📚 参考資料

### Phase 1の成果物
- `life_insurance/utils/tax_helpers.py`
- `life_insurance/tests/test_tax_helpers.py`
- `REFACTORING/PHASE_1/COMPLETION_REPORT.md`

### 既存コード
- `life_insurance/ui/streamlit_app.py`
- `life_insurance/analysis/withdrawal_optimizer.py`
- `life_insurance/analysis/scenario_analyzer.py`

### 設計パターン
- データクラス（@dataclass）
- ファクトリーパターン
- ストラテジーパターン（戦略計算）

---

## 🚀 次のアクション

### 今すぐ開始
1. Task 2.1: 重複箇所の詳細分析
2. 各計算関数のシグネチャと計算ロジックを文書化
3. 共通パターンの抽出

### 準備作業
1. `REFACTORING/PHASE_2/ANALYSIS.md` 作成
2. 計算関数の詳細リスト作成
3. データクラスの詳細設計

---

**計画書バージョン:** 1.0  
**作成日:** 2025年10月29日  
**次回更新:** Task 2.1完了後
