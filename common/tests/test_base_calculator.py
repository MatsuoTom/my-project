"""BaseFinancialCalculator と CompoundInterestMixin のテスト

このテストモジュールは、common.calculators.base_calculator モジュールの
BaseFinancialCalculator と CompoundInterestMixin の動作を検証します。

Test Classes:
    TestBaseFinancialCalculator: BaseFinancialCalculator の抽象基底クラステスト
    TestCompoundInterestMixin: CompoundInterestMixin の複利計算テスト

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

import pytest
from abc import ABC
from typing import Dict, Any

from common.calculators.base_calculator import (
    BaseFinancialCalculator,
    CompoundInterestMixin,
)


class TestBaseFinancialCalculator:
    """BaseFinancialCalculator の抽象基底クラステスト"""

    def test_cannot_instantiate_abstract_class(self):
        """抽象基底クラスは直接インスタンス化できないことを確認"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseFinancialCalculator()

    def test_subclass_must_implement_calculate(self):
        """サブクラスはcalculate()を実装する必要があることを確認"""

        # calculate()のみ未実装のサブクラス
        class IncompleteCalculator(BaseFinancialCalculator):
            def validate_inputs(self, *args, **kwargs) -> bool:
                return True

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteCalculator()

    def test_subclass_must_implement_validate_inputs(self):
        """サブクラスはvalidate_inputs()を実装する必要があることを確認"""

        # validate_inputs()のみ未実装のサブクラス
        class IncompleteCalculator(BaseFinancialCalculator):
            def calculate(self, *args, **kwargs) -> Dict[str, Any]:
                return {}

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteCalculator()

    def test_complete_subclass_can_be_instantiated(self):
        """両メソッドを実装したサブクラスはインスタンス化できることを確認"""

        class CompleteCalculator(BaseFinancialCalculator):
            def calculate(self, amount: float) -> Dict[str, float]:
                return {"result": amount * 2}

            def validate_inputs(self, amount: float) -> bool:
                return amount >= 0

        calc = CompleteCalculator()
        assert calc is not None
        assert isinstance(calc, BaseFinancialCalculator)

    def test_subclass_calculate_method(self):
        """サブクラスのcalculate()メソッドが正常動作することを確認"""

        class SimpleCalculator(BaseFinancialCalculator):
            def calculate(self, principal: float, rate: float) -> Dict[str, float]:
                if not self.validate_inputs(principal, rate):
                    raise ValueError("Invalid inputs")
                return {"principal": principal, "rate": rate, "result": principal * (1 + rate)}

            def validate_inputs(self, principal: float, rate: float) -> bool:
                return principal >= 0 and -1 < rate < 1

        calc = SimpleCalculator()
        result = calc.calculate(1000, 0.05)

        assert result["principal"] == 1000
        assert result["rate"] == 0.05
        assert result["result"] == 1050.0

    def test_subclass_validate_inputs_method(self):
        """サブクラスのvalidate_inputs()メソッドが正常動作することを確認"""

        class ValidatingCalculator(BaseFinancialCalculator):
            def calculate(self, amount: float) -> Dict[str, float]:
                return {"result": amount}

            def validate_inputs(self, amount: float) -> bool:
                if amount < 0:
                    raise ValueError("Amount must be non-negative")
                return True

        calc = ValidatingCalculator()

        # 正常値
        assert calc.validate_inputs(100) is True
        assert calc.validate_inputs(0) is True

        # 異常値
        with pytest.raises(ValueError, match="Amount must be non-negative"):
            calc.validate_inputs(-100)


class TestCompoundInterestMixin:
    """CompoundInterestMixin の複利計算テスト"""

    @pytest.fixture
    def mixin(self):
        """テスト用のミックスインインスタンス"""
        return CompoundInterestMixin()

    # ========================================
    # calculate_compound_interest() のテスト
    # ========================================

    def test_compound_interest_basic(self, mixin):
        """複利計算の基本動作確認"""
        result = mixin.calculate_compound_interest(1000000, 0.03, 10)
        expected = 1000000 * (1.03**10)
        assert abs(result - expected) < 0.01

    def test_compound_interest_zero_principal(self, mixin):
        """元本が0の場合、結果も0になることを確認"""
        result = mixin.calculate_compound_interest(0, 0.03, 10)
        assert result == 0.0

    def test_compound_interest_zero_rate(self, mixin):
        """年利が0%の場合、元本のままであることを確認"""
        result = mixin.calculate_compound_interest(1000000, 0.0, 10)
        assert result == 1000000.0

    def test_compound_interest_zero_years(self, mixin):
        """年数が0の場合、元本のままであることを確認"""
        result = mixin.calculate_compound_interest(1000000, 0.03, 0)
        assert result == 1000000.0

    def test_compound_interest_high_rate(self, mixin):
        """高い年利率での計算確認（5%、20年）"""
        result = mixin.calculate_compound_interest(1000000, 0.05, 20)
        expected = 1000000 * (1.05**20)
        assert abs(result - expected) < 0.01

    def test_compound_interest_long_period(self, mixin):
        """長期間での計算確認（30年）"""
        result = mixin.calculate_compound_interest(1000000, 0.03, 30)
        expected = 1000000 * (1.03**30)
        assert abs(result - expected) < 0.01

    def test_compound_interest_negative_rate(self, mixin):
        """負の年利率での計算確認（減少計算）"""
        result = mixin.calculate_compound_interest(1000000, -0.02, 10)
        expected = 1000000 * (0.98**10)
        assert abs(result - expected) < 0.01

    def test_compound_interest_small_principal(self, mixin):
        """小額の元本での計算確認"""
        result = mixin.calculate_compound_interest(1000, 0.03, 10)
        expected = 1000 * (1.03**10)
        assert abs(result - expected) < 0.01

    def test_compound_interest_large_principal(self, mixin):
        """高額の元本での計算確認"""
        result = mixin.calculate_compound_interest(100000000, 0.03, 10)
        expected = 100000000 * (1.03**10)
        assert abs(result - expected) < 1.0  # 誤差許容を大きく

    def test_compound_interest_negative_principal_raises_error(self, mixin):
        """負の元本でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="元本は0以上である必要があります"):
            mixin.calculate_compound_interest(-1000000, 0.03, 10)

    def test_compound_interest_negative_years_raises_error(self, mixin):
        """負の年数でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="年数は0以上である必要があります"):
            mixin.calculate_compound_interest(1000000, 0.03, -10)

    # ========================================
    # calculate_present_value() のテスト
    # ========================================

    def test_present_value_basic(self, mixin):
        """現在価値計算の基本動作確認"""
        future_value = 1343916.38
        result = mixin.calculate_present_value(future_value, 0.03, 10)
        expected = future_value / (1.03**10)
        assert abs(result - 1000000) < 1.0

    def test_present_value_zero_future_value(self, mixin):
        """将来価値が0の場合、結果も0になることを確認"""
        result = mixin.calculate_present_value(0, 0.03, 10)
        assert result == 0.0

    def test_present_value_zero_rate(self, mixin):
        """割引率が0%の場合、将来価値のままであることを確認"""
        result = mixin.calculate_present_value(1000000, 0.0, 10)
        assert result == 1000000.0

    def test_present_value_zero_years(self, mixin):
        """年数が0の場合、将来価値のままであることを確認"""
        result = mixin.calculate_present_value(1000000, 0.03, 0)
        assert result == 1000000.0

    def test_present_value_high_rate(self, mixin):
        """高い割引率での計算確認（5%、20年）"""
        future_value = 2653297.71
        result = mixin.calculate_present_value(future_value, 0.05, 20)
        assert abs(result - 1000000) < 1.0

    def test_present_value_inverse_of_compound_interest(self, mixin):
        """現在価値計算が複利計算の逆であることを確認"""
        principal = 1000000
        rate = 0.03
        years = 10

        # 複利計算
        future = mixin.calculate_compound_interest(principal, rate, years)

        # 現在価値計算（逆計算）
        present = mixin.calculate_present_value(future, rate, years)

        # 元に戻ることを確認
        assert abs(present - principal) < 1.0

    def test_present_value_negative_future_value_raises_error(self, mixin):
        """負の将来価値でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="将来価値は0以上である必要があります"):
            mixin.calculate_present_value(-1000000, 0.03, 10)

    def test_present_value_negative_years_raises_error(self, mixin):
        """負の年数でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="年数は0以上である必要があります"):
            mixin.calculate_present_value(1000000, 0.03, -10)

    # ========================================
    # calculate_future_value() のテスト
    # ========================================

    def test_future_value_basic(self, mixin):
        """将来価値計算の基本動作確認"""
        result = mixin.calculate_future_value(1000000, 0.03, 10)
        expected = 1000000 * (1.03**10)
        assert abs(result - expected) < 0.01

    def test_future_value_equivalent_to_compound_interest(self, mixin):
        """calculate_future_value()がcalculate_compound_interest()と同じであることを確認"""
        principal = 1000000
        rate = 0.03
        years = 10

        future1 = mixin.calculate_future_value(principal, rate, years)
        future2 = mixin.calculate_compound_interest(principal, rate, years)

        assert future1 == future2

    # ========================================
    # ミックスインと基底クラスの統合テスト
    # ========================================

    def test_mixin_with_base_calculator(self):
        """ミックスインと基底クラスを組み合わせた実際の使用例"""

        class InsuranceCalculator(BaseFinancialCalculator, CompoundInterestMixin):
            def calculate(self, principal: float, rate: float, years: int) -> Dict[str, float]:
                if not self.validate_inputs(principal, rate, years):
                    raise ValueError("Invalid inputs")

                future = self.calculate_compound_interest(principal, rate, years)
                present = self.calculate_present_value(future, rate, years)

                return {
                    "principal": principal,
                    "rate": rate,
                    "years": years,
                    "future_value": future,
                    "present_value": present,
                }

            def validate_inputs(self, principal: float, rate: float, years: int) -> bool:
                return principal >= 0 and years >= 0

        calc = InsuranceCalculator()
        result = calc.calculate(1000000, 0.03, 10)

        assert result["principal"] == 1000000
        assert result["rate"] == 0.03
        assert result["years"] == 10
        assert abs(result["future_value"] - 1343916.38) < 1.0
        assert abs(result["present_value"] - 1000000) < 1.0


# テスト実行時の追加設定
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
