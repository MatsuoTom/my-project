"""
税金ヘルパーのテストスイート

TaxDeductionHelper クラスの全機能を網羅的にテストします。
"""

import pytest
from life_insurance.utils.tax_helpers import (
    TaxDeductionHelper,
    get_tax_helper,
    reset_tax_helper
)


class TestTaxDeductionHelper:
    """TaxDeductionHelper クラスの基本機能テスト"""
    
    @pytest.fixture
    def helper(self):
        """テスト用ヘルパーインスタンス"""
        return TaxDeductionHelper()
    
    def test_calculate_annual_tax_savings_basic(self, helper):
        """基本的な年間節税額計算"""
        result = helper.calculate_annual_tax_savings(120000, 5000000)
        
        assert 'deduction' in result
        assert 'income_tax_savings' in result
        assert 'resident_tax_savings' in result
        assert 'total_savings' in result
        
        # 控除額は50,000円（上限）
        assert result['deduction'] == 50000
        
        # 節税額は正の値
        assert result['total_savings'] > 0
        assert result['income_tax_savings'] > 0
        assert result['resident_tax_savings'] > 0
        
        # 合計 = 所得税 + 住民税
        assert result['total_savings'] == (
            result['income_tax_savings'] + result['resident_tax_savings']
        )
    
    def test_calculate_annual_tax_savings_different_premiums(self, helper):
        """異なる保険料での計算"""
        # 少額の保険料
        result_low = helper.calculate_annual_tax_savings(30000, 5000000)
        assert result_low['deduction'] == 27500  # 30000 * 0.5 + 12500
        
        # 中額の保険料
        result_mid = helper.calculate_annual_tax_savings(60000, 5000000)
        assert result_mid['deduction'] == 40000  # 60000 * 0.25 + 25000
        
        # 高額の保険料（上限到達）
        result_high = helper.calculate_annual_tax_savings(150000, 5000000)
        assert result_high['deduction'] == 50000  # 上限
        
        # 節税額は保険料に応じて増加
        assert result_low['total_savings'] < result_mid['total_savings']
        assert result_mid['total_savings'] < result_high['total_savings']
    
    def test_calculate_annual_tax_savings_different_incomes(self, helper):
        """異なる課税所得での計算"""
        annual_premium = 100000
        
        # 低所得（税率が低い）
        result_low = helper.calculate_annual_tax_savings(annual_premium, 3000000)
        
        # 高所得（税率が高い）
        result_high = helper.calculate_annual_tax_savings(annual_premium, 10000000)
        
        # 控除額は同じ
        assert result_low['deduction'] == result_high['deduction']
        
        # 節税額は高所得者の方が大きい
        assert result_low['total_savings'] < result_high['total_savings']
    
    def test_calculate_annual_tax_savings_zero_premium(self, helper):
        """保険料0円のケース"""
        result = helper.calculate_annual_tax_savings(0, 5000000)
        
        assert result['deduction'] == 0
        assert result['total_savings'] == 0
        assert result['income_tax_savings'] == 0
        assert result['resident_tax_savings'] == 0
    
    def test_calculate_annual_tax_savings_negative_premium(self, helper):
        """負の保険料（エラーケース）"""
        with pytest.raises(ValueError, match="年間保険料は0以上"):
            helper.calculate_annual_tax_savings(-1000, 5000000)
    
    def test_calculate_annual_tax_savings_default_income(self, helper):
        """デフォルト課税所得（500万円）での計算"""
        # 課税所得を省略
        result = helper.calculate_annual_tax_savings(100000)
        
        assert 'total_savings' in result
        assert result['total_savings'] > 0
    
    def test_calculate_total_tax_savings_over_years(self, helper):
        """複数年の節税額計算"""
        annual_premium = 100000
        years = 20
        taxable_income = 5000000
        
        total = helper.calculate_total_tax_savings_over_years(
            annual_premium, years, taxable_income
        )
        
        # 年間節税額の20倍
        annual_result = helper.calculate_annual_tax_savings(
            annual_premium, taxable_income
        )
        expected = annual_result['total_savings'] * years
        
        assert total == expected
        assert total > 0
    
    def test_calculate_total_tax_savings_over_years_single_year(self, helper):
        """1年間の節税額計算"""
        annual_premium = 100000
        
        total = helper.calculate_total_tax_savings_over_years(
            annual_premium, 1, 5000000
        )
        
        annual = helper.calculate_annual_tax_savings(
            annual_premium, 5000000
        )
        
        assert total == annual['total_savings']
    
    def test_calculate_total_tax_savings_over_years_invalid_years(self, helper):
        """無効な年数（エラーケース）"""
        with pytest.raises(ValueError, match="年数は1以上"):
            helper.calculate_total_tax_savings_over_years(100000, 0)
        
        with pytest.raises(ValueError, match="年数は1以上"):
            helper.calculate_total_tax_savings_over_years(100000, -5)
    
    def test_calculate_monthly_premium_for_max_deduction(self, helper):
        """控除額最大化のための月額保険料計算"""
        monthly = helper.calculate_monthly_premium_for_max_deduction()
        
        # 年間10万円 / 12 ≈ 8333円
        assert 8000 < monthly < 9000
        
        # 年間換算で約10万円
        annual = monthly * 12
        assert 99000 < annual <= 100000
    
    def test_compare_premium_scenarios(self, helper):
        """複数保険料オプションの比較"""
        options = [60000, 100000, 150000]
        results = helper.compare_premium_scenarios(options, 5000000)
        
        # 全オプションの結果が含まれる
        assert len(results) == 3
        assert 60000 in results
        assert 100000 in results
        assert 150000 in results
        
        # 各結果は適切な構造を持つ
        for premium, result in results.items():
            assert 'deduction' in result
            assert 'total_savings' in result
            assert result['total_savings'] > 0
        
        # 保険料が増えると節税額も増える（上限まで）
        assert (
            results[60000]['total_savings'] < 
            results[100000]['total_savings']
        )


class TestTaxHelperSingleton:
    """シングルトンパターンのテスト"""
    
    def test_get_tax_helper_returns_same_instance(self):
        """複数回呼び出しで同じインスタンスが返される"""
        # リセット
        reset_tax_helper()
        
        helper1 = get_tax_helper()
        helper2 = get_tax_helper()
        
        assert helper1 is helper2
    
    def test_get_tax_helper_returns_valid_instance(self):
        """有効なヘルパーインスタンスが返される"""
        reset_tax_helper()
        
        helper = get_tax_helper()
        
        assert isinstance(helper, TaxDeductionHelper)
        assert hasattr(helper, 'calculate_annual_tax_savings')
        assert hasattr(helper, 'calculate_total_tax_savings_over_years')
    
    def test_reset_tax_helper(self):
        """シングルトンのリセット"""
        reset_tax_helper()
        
        helper1 = get_tax_helper()
        reset_tax_helper()
        helper2 = get_tax_helper()
        
        # リセット後は異なるインスタンス
        assert helper1 is not helper2


class TestTaxHelperEdgeCases:
    """エッジケース・境界値テスト"""
    
    @pytest.fixture
    def helper(self):
        return TaxDeductionHelper()
    
    def test_boundary_25000(self, helper):
        """境界値: 25,000円"""
        result = helper.calculate_annual_tax_savings(25000, 5000000)
        assert result['deduction'] == 25000  # そのまま
    
    def test_boundary_25001(self, helper):
        """境界値: 25,001円"""
        result = helper.calculate_annual_tax_savings(25001, 5000000)
        expected_deduction = 25001 * 0.5 + 12500
        assert result['deduction'] == expected_deduction
    
    def test_boundary_50000(self, helper):
        """境界値: 50,000円"""
        result = helper.calculate_annual_tax_savings(50000, 5000000)
        expected_deduction = 50000 * 0.5 + 12500
        assert result['deduction'] == expected_deduction
    
    def test_boundary_50001(self, helper):
        """境界値: 50,001円"""
        result = helper.calculate_annual_tax_savings(50001, 5000000)
        expected_deduction = 50001 * 0.25 + 25000
        assert result['deduction'] == expected_deduction
    
    def test_boundary_100000(self, helper):
        """境界値: 100,000円（上限到達）"""
        result = helper.calculate_annual_tax_savings(100000, 5000000)
        assert result['deduction'] == 50000  # 上限
    
    def test_boundary_100001(self, helper):
        """境界値: 100,001円（上限超過）"""
        result = helper.calculate_annual_tax_savings(100001, 5000000)
        assert result['deduction'] == 50000  # 上限のまま
    
    def test_very_large_premium(self, helper):
        """非常に大きな保険料"""
        result = helper.calculate_annual_tax_savings(10000000, 5000000)
        assert result['deduction'] == 50000  # 上限
    
    def test_very_low_income(self, helper):
        """非常に低い課税所得"""
        result = helper.calculate_annual_tax_savings(100000, 1000000)
        
        # 控除額は変わらない
        assert result['deduction'] == 50000
        
        # 節税額は低い（税率が低いため）
        assert result['total_savings'] > 0
        assert result['total_savings'] < 10000
    
    def test_very_high_income(self, helper):
        """非常に高い課税所得"""
        result = helper.calculate_annual_tax_savings(100000, 50000000)
        
        # 控除額は変わらない
        assert result['deduction'] == 50000
        
        # 節税額は高い（税率が高いため）
        assert result['total_savings'] > 15000


class TestTaxHelperIntegration:
    """統合テスト: 実際のユースケース"""
    
    def test_typical_user_scenario(self):
        """典型的なユーザーシナリオ"""
        helper = get_tax_helper()
        
        # 月額1万円の保険、年収500万円のユーザー
        monthly_premium = 10000
        annual_premium = monthly_premium * 12
        taxable_income = 5000000
        
        # 年間節税額
        annual_result = helper.calculate_annual_tax_savings(
            annual_premium, taxable_income
        )
        
        assert annual_result['total_savings'] > 0
        print(f"年間節税額: {annual_result['total_savings']:,.0f}円")
        
        # 20年間の累計節税額
        total_over_20_years = helper.calculate_total_tax_savings_over_years(
            annual_premium, 20, taxable_income
        )
        
        assert total_over_20_years == annual_result['total_savings'] * 20
        print(f"20年間の累計節税額: {total_over_20_years:,.0f}円")
    
    def test_optimization_scenario(self):
        """最適化シナリオ: どの保険料が最も効率的か"""
        helper = get_tax_helper()
        
        options = [60000, 100000, 120000, 150000]
        results = helper.compare_premium_scenarios(options, 5000000)
        
        # 各オプションの節税効率（節税額/保険料）を計算
        for premium, result in results.items():
            efficiency = result['total_savings'] / premium
            print(f"保険料 {premium:,}円: 節税効率 {efficiency:.2%}")
        
        # 10万円前後が最も効率的（控除上限に到達）
        assert results[100000]['deduction'] == 50000
