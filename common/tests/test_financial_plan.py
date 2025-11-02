"""FinancialPlan のテスト

このテストモジュールは、common.models.financial_plan モジュールの
FinancialPlan データクラスの動作を検証します。

Test Classes:
    TestFinancialPlanBasic: 基本機能のテスト
    TestFinancialPlanValidation: バリデーションのテスト
    TestFinancialPlanProperties: プロパティのテスト
    TestFinancialPlanStringRepresentation: 文字列表現のテスト

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

import pytest
from common.models.financial_plan import FinancialPlan


class TestFinancialPlanBasic:
    """FinancialPlan の基本機能テスト"""
    
    def test_create_basic_plan(self):
        """基本的なプラン作成のテスト"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        
        assert plan.name == "定期保険"
        assert plan.start_age == 30
        assert plan.end_age == 60
        assert plan.annual_payment == 100000
    
    def test_create_lifetime_plan(self):
        """終身プラン作成のテスト"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        
        assert plan.name == "終身保険"
        assert plan.start_age == 30
        assert plan.end_age is None
        assert plan.annual_payment == 150000
    
    def test_create_with_default_payment(self):
        """デフォルトの支払額（0円）でのプラン作成"""
        plan = FinancialPlan(
            name="無料相談",
            start_age=20,
            end_age=25
        )
        
        assert plan.annual_payment == 0.0
    
    def test_create_with_zero_payment(self):
        """支払額0円での明示的なプラン作成"""
        plan = FinancialPlan(
            name="無料プラン",
            start_age=20,
            end_age=25,
            annual_payment=0.0
        )
        
        assert plan.annual_payment == 0.0


class TestFinancialPlanValidation:
    """FinancialPlan のバリデーションテスト"""
    
    def test_negative_start_age_raises_error(self):
        """負の開始年齢でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="開始年齢は0以上である必要があります"):
            FinancialPlan(
                name="無効プラン",
                start_age=-1,
                end_age=30,
                annual_payment=100000
            )
    
    def test_end_age_less_than_start_age_raises_error(self):
        """終了年齢が開始年齢以下でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="終了年齢.*は開始年齢.*より大きい必要があります"):
            FinancialPlan(
                name="無効プラン",
                start_age=30,
                end_age=25,
                annual_payment=100000
            )
    
    def test_end_age_equal_to_start_age_raises_error(self):
        """終了年齢と開始年齢が同じでValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="終了年齢.*は開始年齢.*より大きい必要があります"):
            FinancialPlan(
                name="無効プラン",
                start_age=30,
                end_age=30,
                annual_payment=100000
            )
    
    def test_negative_annual_payment_raises_error(self):
        """負の年間支払額でValueErrorが発生することを確認"""
        with pytest.raises(ValueError, match="年間支払額は0以上である必要があります"):
            FinancialPlan(
                name="無効プラン",
                start_age=30,
                end_age=60,
                annual_payment=-100000
            )
    
    def test_zero_start_age_is_valid(self):
        """開始年齢0歳は有効であることを確認"""
        plan = FinancialPlan(
            name="出生時プラン",
            start_age=0,
            end_age=18,
            annual_payment=50000
        )
        assert plan.start_age == 0
    
    def test_lifetime_plan_with_none_end_age_is_valid(self):
        """終身プラン（end_age=None）は有効であることを確認"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        assert plan.end_age is None


class TestFinancialPlanProperties:
    """FinancialPlan のプロパティテスト"""
    
    def test_duration_years_normal_plan(self):
        """通常のプランの期間（年数）計算"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        assert plan.duration_years == 30
    
    def test_duration_years_short_plan(self):
        """短期プランの期間（年数）計算"""
        plan = FinancialPlan(
            name="短期プラン",
            start_age=25,
            end_age=30,
            annual_payment=50000
        )
        assert plan.duration_years == 5
    
    def test_duration_years_lifetime_plan(self):
        """終身プランの期間はNone"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        assert plan.duration_years is None
    
    def test_total_payment_normal_plan(self):
        """通常のプランの総支払額計算"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        assert plan.total_payment == 3000000.0
    
    def test_total_payment_with_fractional_amount(self):
        """小数点付き年間支払額での総支払額計算"""
        plan = FinancialPlan(
            name="変額プラン",
            start_age=30,
            end_age=40,
            annual_payment=123456.78
        )
        expected = 123456.78 * 10
        assert abs(plan.total_payment - expected) < 0.01
    
    def test_total_payment_lifetime_plan(self):
        """終身プランの総支払額はNone"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        assert plan.total_payment is None
    
    def test_total_payment_zero_payment_plan(self):
        """支払額0円のプランの総支払額は0円"""
        plan = FinancialPlan(
            name="無料プラン",
            start_age=20,
            end_age=25,
            annual_payment=0.0
        )
        assert plan.total_payment == 0.0
    
    def test_is_lifetime_false_for_normal_plan(self):
        """通常のプランはis_lifetimeがFalse"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        assert plan.is_lifetime is False
    
    def test_is_lifetime_true_for_lifetime_plan(self):
        """終身プランはis_lifetimeがTrue"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        assert plan.is_lifetime is True


class TestFinancialPlanStringRepresentation:
    """FinancialPlan の文字列表現テスト"""
    
    def test_str_normal_plan(self):
        """通常のプランの文字列表現"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        result = str(plan)
        
        assert "定期保険" in result
        assert "30歳" in result
        assert "60歳" in result
        assert "10万円" in result
        assert "300万円" in result
    
    def test_str_lifetime_plan(self):
        """終身プランの文字列表現"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        result = str(plan)
        
        assert "終身保険" in result
        assert "30歳" in result
        assert "終身" in result
        assert "15万円" in result
        # 終身プランには総額が表示されない
        assert "総額" not in result
    
    def test_repr_normal_plan(self):
        """通常のプランのrepr表現"""
        plan = FinancialPlan(
            name="定期保険",
            start_age=30,
            end_age=60,
            annual_payment=100000
        )
        result = repr(plan)
        
        assert "FinancialPlan" in result
        assert "name='定期保険'" in result
        assert "start_age=30" in result
        assert "end_age=60" in result
        assert "annual_payment=100000" in result
    
    def test_repr_lifetime_plan(self):
        """終身プランのrepr表現"""
        plan = FinancialPlan(
            name="終身保険",
            start_age=30,
            end_age=None,
            annual_payment=150000
        )
        result = repr(plan)
        
        assert "FinancialPlan" in result
        assert "name='終身保険'" in result
        assert "start_age=30" in result
        assert "end_age=None" in result
        assert "annual_payment=150000" in result


class TestFinancialPlanEdgeCases:
    """FinancialPlan のエッジケーステスト"""
    
    def test_very_long_duration_plan(self):
        """非常に長期間のプラン"""
        plan = FinancialPlan(
            name="超長期プラン",
            start_age=0,
            end_age=100,
            annual_payment=50000
        )
        assert plan.duration_years == 100
        assert plan.total_payment == 5000000.0
    
    def test_very_high_annual_payment(self):
        """非常に高額な年間支払額"""
        plan = FinancialPlan(
            name="高額プラン",
            start_age=30,
            end_age=60,
            annual_payment=10000000
        )
        assert plan.annual_payment == 10000000
        assert plan.total_payment == 300000000.0
    
    def test_plan_with_fractional_payment(self):
        """小数点付き年間支払額のプラン"""
        plan = FinancialPlan(
            name="変額プラン",
            start_age=30,
            end_age=35,
            annual_payment=123456.789
        )
        assert plan.annual_payment == 123456.789
        expected_total = 123456.789 * 5
        assert abs(plan.total_payment - expected_total) < 0.001


# テスト実行時の追加設定
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
