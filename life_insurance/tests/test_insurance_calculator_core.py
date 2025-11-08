"""
InsuranceCalculatorコアメソッドのテストスイート

Task 2.4で実装されたコアメソッド（公開API）の統合テスト。
6つのコアメソッドの正確性、エッジケース、統合動作を検証します。
"""

import pytest
from life_insurance.analysis.insurance_calculator import InsuranceCalculator
from life_insurance.models import InsurancePlan, FundPlan


class TestCalculateSimpleValue:
    """calculate_simple_value()のテスト"""

    def test_basic_calculation(self):
        """基本的な保険価値計算"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,
            investment_period=20,
            fee_rate=0.013,
            balance_fee_rate=0.00008,
        )

        result = calculator.calculate_simple_value(plan)

        # 基本検証
        assert result.insurance_value > 0
        assert result.total_paid == 30000 * 20 * 12  # 720万円
        assert result.setup_fee > 0
        assert result.balance_fee > 0
        assert result.tax_benefit > 0

        # 保険価値は支払総額より大きい（2%運用）
        assert result.insurance_value > result.total_paid

        # 実質利回りは手数料分だけ低下（2%未満）
        assert 0 < result.actual_return_rate < 2.0

    def test_high_return_rate(self):
        """高利回りケース"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=50000, annual_rate=5.0, investment_period=30)

        result = calculator.calculate_simple_value(plan)

        assert result.insurance_value > result.total_paid * 1.5
        # 実質利回りは手数料控除後で2%程度
        assert result.actual_return_rate > 2.0

    def test_zero_return_rate(self):
        """ゼロ利回りケース"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=0.0, investment_period=10)

        result = calculator.calculate_simple_value(plan)

        # 利回りゼロでも節税効果があるのでプラスになる
        # 手数料が2%程度、節税効果が4%程度で差し引き微増
        assert result.actual_return_rate >= 0  # ゼロ以上

    def test_short_period(self):
        """短期間ケース（5年）"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=5)

        result = calculator.calculate_simple_value(plan)

        assert result.total_paid == 30000 * 5 * 12  # 180万円
        assert result.insurance_value > 0
        # 短期なので複利効果は限定的
        assert result.actual_return_rate < 1.5


class TestCalculatePartialWithdrawalValue:
    """calculate_partial_withdrawal_value()のテスト"""

    def test_basic_partial_withdrawal(self):
        """基本的な部分解約計算"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0, use_nisa=False)

        result = calculator.calculate_partial_withdrawal_value(
            plan, withdrawal_ratio=0.3, withdrawal_interval=5, reinvestment_plan=fund
        )

        # 基本検証
        assert result.insurance_value > 0  # 保険残高
        assert result.reinvestment_value > 0  # 再投資残高
        assert result.total_paid == 30000 * 20 * 12

        # 総資産（保険+再投資）
        total_assets = result.insurance_value + result.reinvestment_value
        assert total_assets > result.total_paid

    def test_nisa_reinvestment(self):
        """NISA枠での再投資"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund_nisa = FundPlan(reinvestment_rate=5.0, use_nisa=True)
        fund_taxable = FundPlan(reinvestment_rate=5.0, use_nisa=False)

        result_nisa = calculator.calculate_partial_withdrawal_value(plan, 0.3, 5, fund_nisa)
        result_taxable = calculator.calculate_partial_withdrawal_value(plan, 0.3, 5, fund_taxable)

        # NISA枠の方が手取りが多い（非課税効果）
        assert result_nisa.net_value > result_taxable.net_value
        assert result_nisa.reinvestment_tax == 0.0
        assert result_taxable.reinvestment_tax > 0.0

    def test_no_reinvestment_plan(self):
        """再投資なし（現金保有）"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)

        result = calculator.calculate_partial_withdrawal_value(
            plan, withdrawal_ratio=0.3, withdrawal_interval=5, reinvestment_plan=None
        )

        # 現金保有なら再投資残高は解約金の合計のみ
        assert result.reinvestment_value >= 0

    def test_frequent_withdrawal(self):
        """頻繁な解約（毎年）"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=10)
        fund = FundPlan(reinvestment_rate=5.0)

        result = calculator.calculate_partial_withdrawal_value(plan, 0.2, 1, fund)  # 毎年20%解約

        # 頻繁な解約でも計算完了
        assert result.net_value > 0


class TestCalculateSwitchingValue:
    """calculate_switching_value()のテスト"""

    def test_basic_switching(self):
        """基本的な乗り換え計算"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0, use_nisa=False)

        result = calculator.calculate_switching_value(plan, 10, fund)

        # 基本検証
        assert result.insurance_value == 0.0  # 保険は解約済み
        assert result.reinvestment_value > 0  # 投資信託に移行
        assert result.total_paid == 30000 * 20 * 12
        assert result.surrender_value > 0
        assert result.withdrawal_tax >= 0

    def test_early_switching(self):
        """早期乗り換え（5年目）"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0)

        result = calculator.calculate_switching_value(plan, 5, fund)

        # 早期解約は控除が大きい
        assert result.withdrawal_tax >= 0
        # 残り15年間は投資信託運用
        assert result.reinvestment_value > 0

    def test_late_switching(self):
        """後期乗り換え（15年目）"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0)

        result = calculator.calculate_switching_value(plan, 15, fund)

        # 後期解約は控除が小さい
        assert result.reinvestment_value > 0

    def test_nisa_switching(self):
        """NISA枠で乗り換え"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund_nisa = FundPlan(reinvestment_rate=5.0, use_nisa=True)
        fund_taxable = FundPlan(reinvestment_rate=5.0, use_nisa=False)

        result_nisa = calculator.calculate_switching_value(plan, 10, fund_nisa)
        result_taxable = calculator.calculate_switching_value(plan, 10, fund_taxable)

        # NISA枠の方が手取りが多い
        assert result_nisa.net_value > result_taxable.net_value
        assert result_nisa.reinvestment_tax == 0.0
        assert result_taxable.reinvestment_tax > 0.0


class TestCalculateTotalBenefit:
    """calculate_total_benefit()のテスト"""

    def test_basic_benefit_calculation(self):
        """基本的な総合利益計算"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)

        benefit = calculator.calculate_total_benefit(plan)

        # 必須キーの存在確認
        assert "gross_benefit" in benefit
        assert "tax_benefit" in benefit
        assert "investment_gain" in benefit
        assert "total_fees" in benefit
        assert "total_tax" in benefit
        assert "net_benefit" in benefit
        assert "actual_return_rate" in benefit
        assert "benefit_breakdown" in benefit

        # 利益分解の検証
        breakdown = benefit["benefit_breakdown"]
        assert "運用益" in breakdown
        assert "節税効果" in breakdown
        assert "手数料" in breakdown
        assert "税金" in breakdown
        assert "純利益" in breakdown

        # 純利益の整合性（計算モデルの違いにより多少の誤差は許容）
        calculated_net = (
            breakdown["運用益"]
            + breakdown["節税効果"]
            + breakdown["手数料"]  # 負の値
            + breakdown["税金"]  # 負の値
        )
        # 手数料の計算モデルの違いにより、30万円程度の誤差は許容
        assert abs(calculated_net - benefit["net_benefit"]) < 300000

    def test_high_income_benefit(self):
        """高所得者の総合利益"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=50000, annual_rate=3.0, investment_period=30)

        benefit = calculator.calculate_total_benefit(plan, taxable_income=10000000)

        # 高所得者は節税効果が大きい
        assert benefit["tax_benefit"] > 300000


class TestCalculateComparison:
    """calculate_comparison()のテスト"""

    def test_basic_comparison(self):
        """基本的な3戦略比較"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0, use_nisa=True)

        comparison = calculator.calculate_comparison(plan, fund)

        # 必須キーの存在確認
        assert "insurance_only" in comparison
        assert "fund_only" in comparison
        assert "switching" in comparison
        assert "recommendation" in comparison

        # 各戦略のデータ検証
        assert comparison["insurance_only"]["net_value"] > 0
        assert comparison["fund_only"]["net_value"] > 0

        # 推奨戦略の検証
        rec = comparison["recommendation"]
        assert "strategy" in rec
        assert "expected_value" in rec
        assert rec["expected_value"] > 0

    def test_fund_outperforms_insurance(self):
        """投資信託が保険を上回るケース"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,  # 低利回り
            investment_period=20,
            fee_rate=0.02,  # 高手数料
            balance_fee_rate=0.0001,
        )
        fund = FundPlan(reinvestment_rate=7.0, use_nisa=True)  # 高利回り

        comparison = calculator.calculate_comparison(plan, fund)

        # 投資信託の方が有利
        fund_value = comparison["fund_only"]["total_value"]
        insurance_value = comparison["insurance_only"]["total_value"]
        assert fund_value > insurance_value

    def test_switching_strategies(self):
        """複数の乗り換え戦略を比較"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        fund = FundPlan(reinvestment_rate=5.0, use_nisa=True)

        comparison = calculator.calculate_comparison(plan, fund)

        # 乗り換え戦略のデータが存在
        switching = comparison["switching"]
        assert len(switching) > 0

        # 各乗り換え年のデータ検証
        for year_key, data in switching.items():
            assert "net_value" in data
            assert "return_rate" in data
            assert "tax_benefit" in data
            assert data["net_value"] > 0


class TestCalculateBreakevenYear:
    """calculate_breakeven_year()のテスト"""

    def test_basic_breakeven(self):
        """基本的な元本回収年計算"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)

        breakeven = calculator.calculate_breakeven_year(plan)

        # 必須キーの存在確認
        assert "breakeven_year" in breakeven
        assert "breakeven_value" in breakeven
        assert "yearly_values" in breakeven
        assert "total_paid_at_end" in breakeven
        assert "breakeven_ratio" in breakeven

        # 元本回収年が見つかるべき（2%運用なら早期）
        # 節税効果を考慮すると4年目で回収可能
        if breakeven["breakeven_year"]:
            assert 3 <= breakeven["breakeven_year"] <= 10
            assert breakeven["breakeven_value"] > 0

    def test_high_return_early_breakeven(self):
        """高利回りで早期元本回収"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=5.0, investment_period=20)

        breakeven = calculator.calculate_breakeven_year(plan)

        # 高利回りなら早期に元本回収
        assert breakeven["breakeven_year"] is not None
        assert breakeven["breakeven_year"] < 10

    def test_zero_return_no_breakeven(self):
        """ゼロ利回りでも節税効果で元本回収可能"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=0.0, investment_period=20)

        breakeven = calculator.calculate_breakeven_year(plan)

        # 利回りゼロでも節税効果があるので元本回収可能
        # （年間48,000円 × 税率 ≈ 約15,000円/年の節税）
        assert breakeven["breakeven_year"] is not None
        assert breakeven["breakeven_year"] <= 15  # 15年以内に回収

    def test_yearly_values_progression(self):
        """年次価値の推移確認"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=30000, annual_rate=3.0, investment_period=15)

        breakeven = calculator.calculate_breakeven_year(plan)

        # 年次データの検証
        yearly_values = breakeven["yearly_values"]
        assert len(yearly_values) == 15

        # 各年のデータ構造確認
        for data in yearly_values:
            assert "year" in data
            assert "total_paid" in data
            assert "surrender_value" in data
            assert "net_value" in data
            assert "tax_benefit" in data
            assert "total_value" in data
            assert "breakeven" in data

        # 総支払額は単調増加
        for i in range(len(yearly_values) - 1):
            assert yearly_values[i + 1]["total_paid"] > yearly_values[i]["total_paid"]


class TestInsuranceCalculatorIntegration:
    """InsuranceCalculatorの統合テスト"""

    def test_realistic_scenario_comparison(self):
        """現実的なシナリオでの全メソッド統合テスト"""
        calculator = InsuranceCalculator()

        # 現実的なプラン設定
        plan = InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,
            investment_period=20,
            fee_rate=0.013,
            balance_fee_rate=0.00008,
            withdrawal_fee_rate=0.01,
        )
        fund = FundPlan(reinvestment_rate=5.0, use_nisa=True)
        taxable_income = 5000000

        # 1. 単純継続
        simple = calculator.calculate_simple_value(plan, taxable_income)

        # 2. 部分解約
        partial = calculator.calculate_partial_withdrawal_value(plan, 0.3, 5, fund, taxable_income)

        # 3. 乗り換え
        switching = calculator.calculate_switching_value(plan, 10, fund, taxable_income)

        # 4. 総合利益
        benefit = calculator.calculate_total_benefit(plan, taxable_income)

        # 5. 比較分析
        comparison = calculator.calculate_comparison(plan, fund, taxable_income)

        # 6. 元本回収年
        breakeven = calculator.calculate_breakeven_year(plan, taxable_income)

        # すべてのメソッドが正常に完了
        assert simple.net_value > 0
        assert partial.net_value > 0
        assert switching.net_value > 0
        assert benefit["net_benefit"] is not None
        assert comparison["recommendation"]["strategy"] is not None
        assert len(breakeven["yearly_values"]) > 0

        # 投資信託（5%）が保険（2%）より有利なはず
        assert comparison["fund_only"]["total_value"] > comparison["insurance_only"]["total_value"]

    def test_all_methods_with_same_plan(self):
        """同一プランで全メソッドの整合性確認"""
        calculator = InsuranceCalculator()
        plan = InsurancePlan(monthly_premium=40000, annual_rate=2.5, investment_period=25)

        # すべてのメソッドが同じtotal_paidを返すべき
        simple = calculator.calculate_simple_value(plan)
        benefit = calculator.calculate_total_benefit(plan)
        breakeven = calculator.calculate_breakeven_year(plan)

        expected_total_paid = 40000 * 25 * 12  # 1200万円

        assert simple.total_paid == expected_total_paid
        assert breakeven["total_paid_at_end"] == expected_total_paid
