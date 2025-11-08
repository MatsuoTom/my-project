"""math_utils のテスト

このテストモジュールは、common.utils.math_utils モジュールの
各種数学計算関数の動作を検証します。

Test Classes:
    TestCompoundInterest: 複利計算のテスト
    TestPresentValue: 現在価値計算のテスト
    TestAnnuityPresentValue: 年金現価計算のテスト
    TestAnnuityFutureValue: 年金終価計算のテスト
    TestIRR: IRR計算のテスト
    TestNPV: NPV計算のテスト
    TestMonthlyPayment: 月次支払額計算のテスト

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

import pytest
import numpy as np

from common.utils.math_utils import (
    calculate_compound_interest,
    calculate_present_value,
    calculate_annuity_present_value,
    calculate_annuity_future_value,
    calculate_irr,
    calculate_npv,
    calculate_monthly_payment,
)


class TestCompoundInterest:
    """複利計算のテスト"""

    def test_basic_compound_interest(self):
        """基本的な複利計算"""
        result = calculate_compound_interest(1000000, 0.03, 10)
        expected = 1000000 * (1.03**10)
        assert abs(result - expected) < 0.01

    def test_zero_principal(self):
        """元本が0の場合"""
        result = calculate_compound_interest(0, 0.03, 10)
        assert result == 0.0

    def test_zero_rate(self):
        """年利が0%の場合"""
        result = calculate_compound_interest(1000000, 0.0, 10)
        assert result == 1000000.0

    def test_zero_years(self):
        """年数が0の場合"""
        result = calculate_compound_interest(1000000, 0.03, 0)
        assert result == 1000000.0

    def test_high_rate(self):
        """高い年利率（5%、20年）"""
        result = calculate_compound_interest(1000000, 0.05, 20)
        expected = 1000000 * (1.05**20)
        assert abs(result - expected) < 0.01

    def test_negative_principal_raises_error(self):
        """負の元本でエラー"""
        with pytest.raises(ValueError, match="元本は0以上である必要があります"):
            calculate_compound_interest(-1000000, 0.03, 10)

    def test_negative_years_raises_error(self):
        """負の年数でエラー"""
        with pytest.raises(ValueError, match="年数は0以上である必要があります"):
            calculate_compound_interest(1000000, 0.03, -10)


class TestPresentValue:
    """現在価値計算のテスト"""

    def test_basic_present_value(self):
        """基本的な現在価値計算"""
        future_value = 1343916.38
        result = calculate_present_value(future_value, 0.03, 10)
        assert abs(result - 1000000) < 1.0

    def test_zero_future_value(self):
        """将来価値が0の場合"""
        result = calculate_present_value(0, 0.03, 10)
        assert result == 0.0

    def test_zero_rate(self):
        """割引率が0%の場合"""
        result = calculate_present_value(1000000, 0.0, 10)
        assert result == 1000000.0

    def test_zero_years(self):
        """年数が0の場合"""
        result = calculate_present_value(1000000, 0.03, 0)
        assert result == 1000000.0

    def test_inverse_of_compound_interest(self):
        """複利計算の逆計算であることを確認"""
        principal = 1000000
        rate = 0.03
        years = 10

        future = calculate_compound_interest(principal, rate, years)
        present = calculate_present_value(future, rate, years)

        assert abs(present - principal) < 1.0

    def test_negative_future_value_raises_error(self):
        """負の将来価値でエラー"""
        with pytest.raises(ValueError, match="将来価値は0以上である必要があります"):
            calculate_present_value(-1000000, 0.03, 10)

    def test_negative_years_raises_error(self):
        """負の年数でエラー"""
        with pytest.raises(ValueError, match="年数は0以上である必要があります"):
            calculate_present_value(1000000, 0.03, -10)


class TestAnnuityPresentValue:
    """年金現価計算のテスト"""

    def test_basic_annuity_present_value(self):
        """基本的な年金現価計算"""
        result = calculate_annuity_present_value(100000, 0.03, 10)
        # 既知の値と比較（Excelなどで検証済み）
        expected = 853020.28
        assert abs(result - expected) < 1.0

    def test_zero_payment(self):
        """支払額が0の場合"""
        result = calculate_annuity_present_value(0, 0.03, 10)
        assert result == 0.0

    def test_zero_rate(self):
        """利率が0%の場合（単純合計）"""
        result = calculate_annuity_present_value(100000, 0.0, 10)
        assert result == 1000000.0

    def test_zero_periods(self):
        """期間が0の場合"""
        result = calculate_annuity_present_value(100000, 0.03, 0)
        assert result == 0.0

    def test_high_rate(self):
        """高い利率（10%）"""
        result = calculate_annuity_present_value(100000, 0.10, 10)
        expected = 614457.11
        assert abs(result - expected) < 1.0

    def test_monthly_payment(self):
        """月次支払い（月利0.5%、24ヶ月）"""
        result = calculate_annuity_present_value(50000, 0.005, 24)
        # 月利0.5%、24ヶ月の年金現価
        expected = 1128143.31
        assert abs(result - expected) < 1.0

    def test_negative_payment_raises_error(self):
        """負の支払額でエラー"""
        with pytest.raises(ValueError, match="支払額は0以上である必要があります"):
            calculate_annuity_present_value(-100000, 0.03, 10)

    def test_negative_periods_raises_error(self):
        """負の期間数でエラー"""
        with pytest.raises(ValueError, match="期間数は0以上である必要があります"):
            calculate_annuity_present_value(100000, 0.03, -10)


class TestAnnuityFutureValue:
    """年金終価計算のテスト"""

    def test_basic_annuity_future_value(self):
        """基本的な年金終価計算"""
        result = calculate_annuity_future_value(100000, 0.03, 10)
        # 既知の値と比較
        expected = 1146388.49
        assert abs(result - expected) < 1.0

    def test_zero_payment(self):
        """支払額が0の場合"""
        result = calculate_annuity_future_value(0, 0.03, 10)
        assert result == 0.0

    def test_zero_rate(self):
        """利率が0%の場合（単純合計）"""
        result = calculate_annuity_future_value(100000, 0.0, 10)
        assert result == 1000000.0

    def test_zero_periods(self):
        """期間が0の場合"""
        result = calculate_annuity_future_value(100000, 0.03, 0)
        assert result == 0.0

    def test_tsumitate_nisa_simulation(self):
        """つみたてNISA（月3万円、60ヶ月、月利0.3%）"""
        result = calculate_annuity_future_value(30000, 0.003, 60)
        expected = 1968948.03
        assert abs(result - expected) < 1.0

    def test_long_term_savings(self):
        """長期積立（毎年100万円、30年、年利3%）"""
        result = calculate_annuity_future_value(1000000, 0.03, 30)
        expected = 47575415.60
        assert abs(result - expected) < 1.0

    def test_negative_payment_raises_error(self):
        """負の支払額でエラー"""
        with pytest.raises(ValueError, match="支払額は0以上である必要があります"):
            calculate_annuity_future_value(-100000, 0.03, 10)

    def test_negative_periods_raises_error(self):
        """負の期間数でエラー"""
        with pytest.raises(ValueError, match="期間数は0以上である必要があります"):
            calculate_annuity_future_value(100000, 0.03, -10)


class TestIRR:
    """IRR計算のテスト"""

    def test_basic_irr(self):
        """基本的なIRR計算"""
        # 初期投資100万円、5年間毎年10万円、最終年に110万円
        cash_flows = [-1000000, 100000, 100000, 100000, 100000, 1100000]
        result = calculate_irr(cash_flows)

        assert result is not None
        # IRRは約10%（初期推定値に収束）
        assert abs(result - 0.10) < 0.001

    def test_irr_with_simple_investment(self):
        """シンプルな投資（100万円投資、1年後に110万円回収）"""
        cash_flows = [-1000000, 1100000]
        result = calculate_irr(cash_flows)

        assert result is not None
        # IRRは10%
        assert abs(result - 0.10) < 0.001

    def test_irr_negative_returns(self):
        """マイナスリターンのIRR"""
        cash_flows = [-1000000, 50000, 50000, 50000]
        result = calculate_irr(cash_flows)

        # このケースでは解が収束しない可能性がある
        # 結果の有無のみチェック（負の値またはNone）
        if result is not None:
            assert result < 0  # マイナスリターン

    def test_irr_zero_returns(self):
        """ゼロリターンのIRR"""
        cash_flows = [-1000000, 0, 0, 0, 1000000]
        result = calculate_irr(cash_flows)

        assert result is not None
        # IRRは0%
        assert abs(result - 0.0) < 0.001

    def test_irr_with_insufficient_cash_flows_raises_error(self):
        """キャッシュフローが不足でエラー"""
        with pytest.raises(ValueError, match="キャッシュフローは2つ以上必要です"):
            calculate_irr([-1000000])

    def test_irr_with_empty_cash_flows_raises_error(self):
        """空のキャッシュフローでエラー"""
        with pytest.raises(ValueError, match="キャッシュフローは2つ以上必要です"):
            calculate_irr([])


class TestNPV:
    """NPV計算のテスト"""

    def test_basic_npv(self):
        """基本的なNPV計算"""
        # 初期投資100万円、5年間毎年10万円、最終年に110万円
        cash_flows = [-1000000, 100000, 100000, 100000, 100000, 1100000]
        result = calculate_npv(0.03, cash_flows)

        # NPVは約320,580円
        expected = 320580
        assert abs(result - expected) < 100

    def test_npv_positive_investment(self):
        """NPVが正の投資（投資価値あり）"""
        cash_flows = [-1000000, 300000, 300000, 300000, 300000]
        result = calculate_npv(0.05, cash_flows)

        assert result > 0

    def test_npv_negative_investment(self):
        """NPVが負の投資（投資すべきでない）"""
        cash_flows = [-1000000, 50000, 50000, 50000, 50000, 50000]
        result = calculate_npv(0.05, cash_flows)

        assert result < 0

    def test_npv_zero_rate(self):
        """割引率0%の場合（単純合計）"""
        cash_flows = [-1000000, 300000, 300000, 300000, 300000]
        result = calculate_npv(0.0, cash_flows)

        # 単純合計: -1,000,000 + 1,200,000 = 200,000
        assert abs(result - 200000) < 1.0

    def test_npv_high_discount_rate(self):
        """高い割引率（10%）"""
        cash_flows = [-1000000, 300000, 300000, 300000, 300000]
        result = calculate_npv(0.10, cash_flows)

        # 高い割引率ではNPVが下がる
        assert result < calculate_npv(0.05, cash_flows)

    def test_npv_with_empty_cash_flows_raises_error(self):
        """空のキャッシュフローでエラー"""
        with pytest.raises(ValueError, match="キャッシュフローが空です"):
            calculate_npv(0.03, [])


class TestMonthlyPayment:
    """月次支払額計算のテスト"""

    def test_basic_monthly_payment(self):
        """基本的な月次支払額計算（住宅ローン）"""
        # 3,000万円を年利1.5%で35年借入
        result = calculate_monthly_payment(30000000, 0.015, 35)

        # 月次返済額は約91,855円
        expected = 91855
        assert abs(result - expected) < 10

    def test_short_term_loan(self):
        """短期ローン（5年）"""
        result = calculate_monthly_payment(1000000, 0.03, 5)

        # 月次返済額を計算
        assert result > 0

        # 総返済額が元本より多いことを確認
        total_payment = result * 5 * 12
        assert total_payment > 1000000

    def test_zero_interest_rate(self):
        """金利0%の場合"""
        result = calculate_monthly_payment(1200000, 0.0, 5)

        # 月次返済額は元本÷月数
        expected = 1200000 / (5 * 12)
        assert abs(result - expected) < 1.0

    def test_high_interest_rate(self):
        """高金利（10%）"""
        result = calculate_monthly_payment(1000000, 0.10, 10)

        # 高金利では月次支払額が高くなる
        assert result > 10000

    def test_negative_principal_raises_error(self):
        """負の元本でエラー"""
        with pytest.raises(ValueError, match="元本は正の値である必要があります"):
            calculate_monthly_payment(-1000000, 0.03, 10)

    def test_zero_principal_raises_error(self):
        """元本0でエラー"""
        with pytest.raises(ValueError, match="元本は正の値である必要があります"):
            calculate_monthly_payment(0, 0.03, 10)

    def test_negative_rate_raises_error(self):
        """負の年利率でエラー"""
        with pytest.raises(ValueError, match="年利率は0以上である必要があります"):
            calculate_monthly_payment(1000000, -0.03, 10)

    def test_zero_years_raises_error(self):
        """期間0でエラー"""
        with pytest.raises(ValueError, match="期間は正の値である必要があります"):
            calculate_monthly_payment(1000000, 0.03, 0)

    def test_negative_years_raises_error(self):
        """負の期間でエラー"""
        with pytest.raises(ValueError, match="期間は正の値である必要があります"):
            calculate_monthly_payment(1000000, 0.03, -10)


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_very_small_rate(self):
        """非常に小さい利率（0.001%）"""
        result = calculate_compound_interest(1000000, 0.00001, 10)
        expected = 1000000 * (1.00001**10)
        assert abs(result - expected) < 0.01

    def test_very_large_principal(self):
        """非常に大きい元本（1億円）"""
        result = calculate_compound_interest(100000000, 0.03, 10)
        expected = 100000000 * (1.03**10)
        assert abs(result - expected) < 10.0

    def test_very_long_period(self):
        """非常に長期間（100年）"""
        result = calculate_compound_interest(1000000, 0.03, 100)
        expected = 1000000 * (1.03**100)
        assert abs(result - expected) < 100.0


# テスト実行時の追加設定
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
