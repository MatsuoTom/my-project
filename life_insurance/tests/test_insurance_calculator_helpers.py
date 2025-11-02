"""
InsuranceCalculatorのヘルパーメソッドテスト

このモジュールはInsuranceCalculatorの5つのヘルパーメソッドをテストします：
1. _calculate_compound_interest - 年金終価計算
2. _calculate_fees - 手数料計算
3. _calculate_tax_benefit - 節税効果計算
4. _calculate_surrender_deduction - 解約控除計算
5. _calculate_withdrawal_tax - 一時所得課税計算
"""

import pytest
from life_insurance.analysis import InsuranceCalculator
from life_insurance.models import InsurancePlan, FundPlan


class TestCalculateCompoundInterest:
    """年金終価計算のテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    def test_basic_calculation(self, calculator):
        """基本的な複利計算"""
        monthly_payment = 30000 * (1 - 0.013)  # 手数料控除後
        monthly_rate = 0.02 / 12  # 年利2%
        total_months = 240  # 20年
        
        result = calculator._calculate_compound_interest(monthly_payment, monthly_rate, total_months)
        
        # 期待値: 約873万円
        assert 8700000 < result < 8750000
    
    def test_zero_rate(self, calculator):
        """利回りゼロの場合"""
        monthly_payment = 30000
        monthly_rate = 0.0
        total_months = 240
        
        result = calculator._calculate_compound_interest(monthly_payment, monthly_rate, total_months)
        
        # 単純な積立合計
        expected = monthly_payment * total_months
        assert result == expected
    
    def test_high_rate(self, calculator):
        """高利回りの場合"""
        monthly_payment = 30000
        monthly_rate = 0.05 / 12  # 年利5%
        total_months = 240
        
        result = calculator._calculate_compound_interest(monthly_payment, monthly_rate, total_months)
        
        # 期待値: 約1230万円
        assert 12200000 < result < 12400000
    
    def test_short_period(self, calculator):
        """短期間の計算"""
        monthly_payment = 30000
        monthly_rate = 0.02 / 12
        total_months = 12  # 1年
        
        result = calculator._calculate_compound_interest(monthly_payment, monthly_rate, total_months)
        
        # 期待値: 約36.3万円
        assert 363000 < result < 364000
    
    def test_long_period(self, calculator):
        """長期間の計算"""
        monthly_payment = 30000
        monthly_rate = 0.02 / 12
        total_months = 480  # 40年
        
        result = calculator._calculate_compound_interest(monthly_payment, monthly_rate, total_months)
        
        # 期待値: 約2200万円
        assert 21000000 < result < 23000000


class TestCalculateFees:
    """手数料計算のテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    @pytest.fixture
    def plan(self):
        """テスト用の保険プラン"""
        return InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,
            investment_period=20,
            fee_rate=0.013,
            balance_fee_rate=0.00008
        )
    
    def test_basic_fees(self, calculator, plan):
        """基本的な手数料計算"""
        insurance_value = 8000000
        total_months = 240
        
        setup_fee, balance_fee = calculator._calculate_fees(plan, insurance_value, total_months)
        
        # 積立手数料: 30,000 × 0.013 × 240 = 93,600円
        assert abs(setup_fee - 93600) < 1
        
        # 残高手数料: 8,000,000 × 0.00008 × 240 = 153,600円
        assert abs(balance_fee - 153600) < 1
    
    def test_zero_insurance_value(self, calculator, plan):
        """保険価値ゼロの場合"""
        insurance_value = 0
        total_months = 240
        
        setup_fee, balance_fee = calculator._calculate_fees(plan, insurance_value, total_months)
        
        # 積立手数料のみ
        assert setup_fee > 0
        assert balance_fee == 0
    
    def test_short_period(self, calculator, plan):
        """短期間の手数料"""
        insurance_value = 1000000
        total_months = 12
        
        setup_fee, balance_fee = calculator._calculate_fees(plan, insurance_value, total_months)
        
        # 積立手数料: 30,000 × 0.013 × 12 = 4,680円
        assert abs(setup_fee - 4680) < 1
        
        # 残高手数料: 1,000,000 × 0.00008 × 12 = 960円
        assert abs(balance_fee - 960) < 1
    
    def test_different_fee_rates(self, calculator):
        """異なる手数料率"""
        plan = InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,
            investment_period=20,
            fee_rate=0.02,  # 2%
            balance_fee_rate=0.0001  # 0.01%
        )
        insurance_value = 8000000
        total_months = 240
        
        setup_fee, balance_fee = calculator._calculate_fees(plan, insurance_value, total_months)
        
        # 積立手数料: 30,000 × 0.02 × 240 = 144,000円
        assert abs(setup_fee - 144000) < 1
        
        # 残高手数料: 8,000,000 × 0.0001 × 240 = 192,000円
        assert abs(balance_fee - 192000) < 1


class TestCalculateTaxBenefit:
    """節税効果計算のテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    def test_basic_tax_benefit(self, calculator):
        """基本的な節税効果"""
        annual_premium = 360000  # 月3万円 × 12
        period = 20
        taxable_income = 5000000
        
        tax_savings = calculator._calculate_tax_benefit(annual_premium, period, taxable_income)
        
        # 期待値: 年間約15,210円 × 20年 = 304,200円
        assert 300000 < tax_savings < 310000
    
    def test_high_premium(self, calculator):
        """高額保険料の場合"""
        annual_premium = 1200000  # 月10万円 × 12
        period = 20
        taxable_income = 5000000
        
        tax_savings = calculator._calculate_tax_benefit(annual_premium, period, taxable_income)
        
        # 控除上限があるため、3万円の場合と同程度
        assert 300000 < tax_savings < 310000
    
    def test_short_period(self, calculator):
        """短期間の節税効果"""
        annual_premium = 360000
        period = 5
        taxable_income = 5000000
        
        tax_savings = calculator._calculate_tax_benefit(annual_premium, period, taxable_income)
        
        # 期待値: 年間約15,210円 × 5年 = 76,050円
        assert 75000 < tax_savings < 78000
    
    def test_different_income(self, calculator):
        """異なる所得での節税効果"""
        annual_premium = 360000
        period = 20
        
        # 高所得（所得税率が高い）
        high_income = 10000000
        high_tax_savings = calculator._calculate_tax_benefit(annual_premium, period, high_income)
        
        # 低所得（所得税率が低い）
        low_income = 3000000
        low_tax_savings = calculator._calculate_tax_benefit(annual_premium, period, low_income)
        
        # 高所得の方が節税額が大きい
        assert high_tax_savings > low_tax_savings


class TestCalculateSurrenderDeduction:
    """解約控除計算のテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    def test_first_year(self, calculator):
        """初年度の解約控除（10%）"""
        surrender_value = 1000000
        years = 1
        
        deduction = calculator._calculate_surrender_deduction(surrender_value, years)
        
        # 控除率: 10% - 1% = 9%
        expected = surrender_value * 0.09
        assert abs(deduction - expected) < 1
    
    def test_fifth_year(self, calculator):
        """5年目の解約控除（5%）"""
        surrender_value = 7500000
        years = 5
        
        deduction = calculator._calculate_surrender_deduction(surrender_value, years)
        
        # 控除率: 10% - 5% = 5%
        expected = surrender_value * 0.05
        assert abs(deduction - expected) < 1
    
    def test_tenth_year(self, calculator):
        """10年目の解約控除（0%）"""
        surrender_value = 8000000
        years = 10
        
        deduction = calculator._calculate_surrender_deduction(surrender_value, years)
        
        # 控除率: 10% - 10% = 0%
        assert deduction == 0
    
    def test_after_tenth_year(self, calculator):
        """10年以降の解約控除（0%）"""
        surrender_value = 9000000
        years = 15
        
        deduction = calculator._calculate_surrender_deduction(surrender_value, years)
        
        # 控除率: max(0, 10% - 15%) = 0%
        assert deduction == 0
    
    def test_zero_value(self, calculator):
        """解約返戻金ゼロの場合"""
        surrender_value = 0
        years = 5
        
        deduction = calculator._calculate_surrender_deduction(surrender_value, years)
        
        assert deduction == 0


class TestCalculateWithdrawalTax:
    """一時所得課税計算のテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    def test_profit_below_threshold(self, calculator):
        """利益が50万円以下（非課税）"""
        profit = 400000
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        # 50万円以下は非課税
        assert tax == 0
    
    def test_profit_at_threshold(self, calculator):
        """利益が50万円ちょうど（非課税）"""
        profit = 500000
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        # 50万円ちょうどは非課税
        assert tax == 0
    
    def test_profit_above_threshold(self, calculator):
        """利益が50万円超（課税）"""
        profit = 800000
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        # (80万 - 50万) × 1/2 = 15万円が課税対象
        # 所得税+住民税で約3万円程度
        assert 20000 < tax < 50000
    
    def test_large_profit(self, calculator):
        """大きな利益の場合"""
        profit = 2000000
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        # (200万 - 50万) × 1/2 = 75万円が課税対象
        # 所得税+住民税で約15万円程度
        assert 100000 < tax < 200000
    
    def test_different_income_levels(self, calculator):
        """異なる所得レベルでの課税"""
        profit = 1000000
        
        # 高所得
        high_income = 10000000
        high_tax = calculator._calculate_withdrawal_tax(profit, high_income)
        
        # 低所得
        low_income = 3000000
        low_tax = calculator._calculate_withdrawal_tax(profit, low_income)
        
        # 高所得の方が税率が高いため税額も大きい
        assert high_tax > low_tax
    
    def test_zero_profit(self, calculator):
        """利益ゼロの場合"""
        profit = 0
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        assert tax == 0
    
    def test_negative_profit(self, calculator):
        """損失の場合（負の利益）"""
        profit = -100000
        taxable_income = 5000000
        
        tax = calculator._calculate_withdrawal_tax(profit, taxable_income)
        
        # 損失の場合は課税なし
        assert tax == 0


class TestInsuranceCalculatorIntegration:
    """InsuranceCalculatorの統合テスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用のCalculatorインスタンス"""
        return InsuranceCalculator()
    
    @pytest.fixture
    def plan(self):
        """テスト用の保険プラン"""
        return InsurancePlan(
            monthly_premium=30000,
            annual_rate=2.0,
            investment_period=20
        )
    
    def test_calculator_initialization(self, calculator):
        """Calculatorの初期化"""
        assert calculator.tax_helper is not None
        assert calculator.tax_calculator is not None
    
    def test_all_helper_methods_callable(self, calculator, plan):
        """全ヘルパーメソッドが呼び出し可能"""
        # _calculate_compound_interest
        fv = calculator._calculate_compound_interest(30000, 0.02/12, 240)
        assert fv > 0
        
        # _calculate_fees
        setup_fee, balance_fee = calculator._calculate_fees(plan, 8000000, 240)
        assert setup_fee > 0
        assert balance_fee > 0
        
        # _calculate_tax_benefit
        tax_savings = calculator._calculate_tax_benefit(360000, 20, 5000000)
        assert tax_savings > 0
        
        # _calculate_surrender_deduction
        deduction = calculator._calculate_surrender_deduction(7500000, 5)
        assert deduction > 0
        
        # _calculate_withdrawal_tax
        tax = calculator._calculate_withdrawal_tax(800000, 5000000)
        assert tax >= 0
    
    def test_realistic_scenario(self, calculator, plan):
        """現実的なシナリオでの統合テスト"""
        # 年金終価計算
        monthly_payment = plan.net_monthly_premium
        fv = calculator._calculate_compound_interest(
            monthly_payment,
            plan.monthly_rate,
            plan.total_months
        )
        
        # 手数料計算
        setup_fee, balance_fee = calculator._calculate_fees(plan, fv, plan.total_months)
        total_fees = setup_fee + balance_fee
        
        # 節税効果
        tax_savings = calculator._calculate_tax_benefit(
            plan.annual_premium,
            plan.investment_period,
            5000000
        )
        
        # 解約控除
        deduction = calculator._calculate_surrender_deduction(fv, plan.investment_period)
        
        # 最終価値
        net_value = fv - deduction + tax_savings
        
        # 総払込額
        total_paid = plan.annual_premium * plan.investment_period
        
        # 利益
        profit = net_value - total_paid
        
        # 一時所得課税
        withdrawal_tax = calculator._calculate_withdrawal_tax(profit, 5000000)
        
        # 最終的な正味価値
        final_value = net_value - withdrawal_tax
        
        # 検証
        assert fv > 0
        assert total_fees > 0
        assert tax_savings > 0
        assert final_value > total_paid  # 利益が出ている
