"""
データモデルのテストスイート

このモジュールはInsurancePlan、FundPlan、InsuranceResultのテストを提供します。
"""

import pytest
from life_insurance.models import InsurancePlan, FundPlan, InsuranceResult
from life_insurance.models.calculation_result import (
    SwitchingResult,
    PartialWithdrawalResult,
    ComparisonResult,
)


class TestInsurancePlan:
    """InsurancePlanのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        assert plan.monthly_premium == 30000
        assert plan.annual_rate == 2.0
        assert plan.investment_period == 20

    def test_default_values(self):
        """デフォルト値の確認"""
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        assert plan.fee_rate == 0.013
        assert plan.balance_fee_rate == 0.00008
        assert plan.withdrawal_fee_rate == 0.01

    def test_annual_premium(self):
        """年間保険料の計算"""
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        assert plan.annual_premium == 360000

    def test_total_months(self):
        """総月数の計算"""
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        assert plan.total_months == 240

    def test_monthly_rate(self):
        """月次利回りの計算"""
        plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        expected = 2.0 / 100 / 12
        assert abs(plan.monthly_rate - expected) < 1e-10

    def test_net_monthly_premium(self):
        """手数料控除後の月額保険料"""
        plan = InsurancePlan(
            monthly_premium=30000, annual_rate=2.0, investment_period=20, fee_rate=0.013
        )
        expected = 30000 * (1 - 0.013)
        assert abs(plan.net_monthly_premium - expected) < 1e-6

    def test_validation_negative_premium(self):
        """負の保険料でエラー"""
        with pytest.raises(ValueError, match="月額保険料は正の値"):
            InsurancePlan(monthly_premium=-1000, annual_rate=2.0, investment_period=20)

    def test_validation_zero_premium(self):
        """ゼロ保険料でエラー"""
        with pytest.raises(ValueError, match="月額保険料は正の値"):
            InsurancePlan(monthly_premium=0, annual_rate=2.0, investment_period=20)

    def test_validation_negative_period(self):
        """負の投資期間でエラー"""
        with pytest.raises(ValueError, match="投資期間は正の値"):
            InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=-5)

    def test_validation_invalid_fee_rate(self):
        """不正な手数料率でエラー"""
        with pytest.raises(ValueError, match="積立手数料率は0以上1未満"):
            InsurancePlan(
                monthly_premium=30000, annual_rate=2.0, investment_period=20, fee_rate=1.5
            )

    def test_to_dict(self):
        """辞書形式への変換"""
        plan = InsurancePlan(
            monthly_premium=30000, annual_rate=2.0, investment_period=20, fee_rate=0.013
        )
        result = plan.to_dict()
        assert result["monthly_premium"] == 30000
        assert result["annual_rate"] == 2.0
        assert result["investment_period"] == 20
        assert result["fee_rate"] == 0.013

    def test_from_dict(self):
        """辞書形式からの作成"""
        data = {
            "monthly_premium": 30000,
            "annual_rate": 2.0,
            "investment_period": 20,
            "fee_rate": 0.013,
        }
        plan = InsurancePlan.from_dict(data)
        assert plan.monthly_premium == 30000
        assert plan.annual_rate == 2.0
        assert plan.investment_period == 20
        assert plan.fee_rate == 0.013

    def test_from_dict_with_defaults(self):
        """辞書形式からの作成（デフォルト値使用）"""
        data = {
            "monthly_premium": 30000,
            "annual_rate": 2.0,
            "investment_period": 20,
        }
        plan = InsurancePlan.from_dict(data)
        assert plan.fee_rate == 0.013


class TestFundPlan:
    """FundPlanのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        assert fund.annual_return == 5.0
        assert fund.annual_fee == 0.5

    def test_default_tax_rate(self):
        """デフォルト税率の確認"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        assert fund.tax_rate == 0.20315

    def test_net_return(self):
        """手数料控除後リターンの計算"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        assert fund.net_return == 4.5

    def test_monthly_return(self):
        """月次リターンの計算"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        expected = 4.5 / 12
        assert abs(fund.monthly_return - expected) < 1e-10

    def test_monthly_return_rate(self):
        """月次リターン率（小数）の計算"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        expected = (4.5 / 12) / 100
        assert abs(fund.monthly_return_rate - expected) < 1e-10

    def test_annual_return_rate(self):
        """年間リターン率（小数）の計算"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        expected = 5.0 / 100
        assert abs(fund.annual_return_rate - expected) < 1e-10

    def test_net_return_rate(self):
        """手数料控除後リターン率（小数）の計算"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        expected = 4.5 / 100
        assert abs(fund.net_return_rate - expected) < 1e-10

    def test_validation_negative_fee(self):
        """負の手数料でエラー"""
        with pytest.raises(ValueError, match="年間コストは0以上"):
            FundPlan(annual_return=5.0, annual_fee=-0.5)

    def test_validation_invalid_tax_rate(self):
        """不正な税率でエラー"""
        with pytest.raises(ValueError, match="税率は0以上1以下"):
            FundPlan(annual_return=5.0, annual_fee=0.5, tax_rate=1.5)

    def test_to_dict(self):
        """辞書形式への変換"""
        fund = FundPlan(annual_return=5.0, annual_fee=0.5)
        result = fund.to_dict()
        assert result["annual_return"] == 5.0
        assert result["annual_fee"] == 0.5
        assert result["tax_rate"] == 0.20315

    def test_from_dict(self):
        """辞書形式からの作成"""
        data = {
            "annual_return": 5.0,
            "annual_fee": 0.5,
            "tax_rate": 0.20315,
        }
        fund = FundPlan.from_dict(data)
        assert fund.annual_return == 5.0
        assert fund.annual_fee == 0.5
        assert fund.tax_rate == 0.20315


class TestInsuranceResult:
    """InsuranceResultのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        assert result.insurance_value == 7500000
        assert result.total_paid == 7200000
        assert result.net_value == 7750000

    def test_profit_calculation(self):
        """利益の計算"""
        result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        expected_profit = 7750000 - 7200000
        assert result.profit == expected_profit

    def test_profit_rate_calculation(self):
        """利益率の計算"""
        result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        expected_rate = (550000 / 7200000) * 100
        assert abs(result.profit_rate - expected_rate) < 1e-6

    def test_gross_value_calculation(self):
        """総価値の計算"""
        result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        expected = 7500000 + 250000
        assert result.gross_value == expected

    def test_validation_negative_total_paid(self):
        """負の総払込額でエラー"""
        with pytest.raises(ValueError, match="総払込額は0以上"):
            InsuranceResult(
                insurance_value=7500000,
                total_paid=-100,
                total_fees=250000,
                tax_savings=500000,
                net_value=7750000,
                return_rate=2.5,
            )

    def test_validation_negative_fees(self):
        """負の手数料でエラー"""
        with pytest.raises(ValueError, match="総手数料は0以上"):
            InsuranceResult(
                insurance_value=7500000,
                total_paid=7200000,
                total_fees=-100,
                tax_savings=500000,
                net_value=7750000,
                return_rate=2.5,
            )

    def test_to_dict(self):
        """辞書形式への変換"""
        result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        data = result.to_dict()
        assert data["insurance_value"] == 7500000
        assert data["total_paid"] == 7200000
        assert data["net_value"] == 7750000
        assert "profit" in data
        assert "profit_rate" in data


class TestSwitchingResult:
    """SwitchingResultのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        result = SwitchingResult(
            insurance_value=3000000,
            insurance_tax_savings=200000,
            fund_value=4500000,
            total_value=7700000,
            tax=50000,
            switch_year=5,
        )
        assert result.insurance_value == 3000000
        assert result.switch_year == 5

    def test_to_dict(self):
        """辞書形式への変換"""
        result = SwitchingResult(
            insurance_value=3000000,
            insurance_tax_savings=200000,
            fund_value=4500000,
            total_value=7700000,
            tax=50000,
            switch_year=5,
        )
        data = result.to_dict()
        assert data["switch_year"] == 5
        assert data["total_value"] == 7700000


class TestPartialWithdrawalResult:
    """PartialWithdrawalResultのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        result = PartialWithdrawalResult(
            remaining_insurance=5000000,
            reinvestment_value=2000000,
            tax_savings=400000,
            total_fees=150000,
            total_value=7400000,
            final_ratio=0.6,
            withdrawal_years=[5, 10, 15],
        )
        assert result.remaining_insurance == 5000000
        assert result.final_ratio == 0.6
        assert len(result.withdrawal_years) == 3

    def test_to_dict(self):
        """辞書形式への変換"""
        result = PartialWithdrawalResult(
            remaining_insurance=5000000,
            reinvestment_value=2000000,
            tax_savings=400000,
            total_fees=150000,
            total_value=7400000,
            final_ratio=0.6,
            withdrawal_years=[5, 10, 15],
        )
        data = result.to_dict()
        assert data["final_ratio"] == 0.6
        assert data["withdrawal_years"] == [5, 10, 15]


class TestComparisonResult:
    """ComparisonResultのテスト"""

    def test_basic_creation(self):
        """基本的な作成"""
        insurance_result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        fund_result = {"value": 8000000, "profit": 800000}
        comparison = ComparisonResult(
            insurance_result=insurance_result,
            fund_result=fund_result,
            difference=-250000,
            breakeven_year=12,
        )
        assert comparison.difference == -250000
        assert comparison.breakeven_year == 12

    def test_to_dict(self):
        """辞書形式への変換"""
        insurance_result = InsuranceResult(
            insurance_value=7500000,
            total_paid=7200000,
            total_fees=250000,
            tax_savings=500000,
            net_value=7750000,
            return_rate=2.5,
        )
        fund_result = {"value": 8000000, "profit": 800000}
        comparison = ComparisonResult(
            insurance_result=insurance_result,
            fund_result=fund_result,
            difference=-250000,
            breakeven_year=12,
        )
        data = comparison.to_dict()
        assert "insurance_result" in data
        assert "fund_result" in data
        assert data["breakeven_year"] == 12
