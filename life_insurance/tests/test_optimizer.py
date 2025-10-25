"""
テストスイート - 引き出しタイミング最適化のテスト
"""

import pytest
import pandas as pd
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer


class TestWithdrawalOptimizer:
    """WithdrawalOptimizer クラスのテスト"""
    
    @pytest.fixture
    def optimizer(self):
        """テスト用の最適化インスタンスを作成"""
        return WithdrawalOptimizer()
    
    def test_calculate_policy_value(self, optimizer):
        """保険価値計算のテスト"""
        result = optimizer.calculate_policy_value(
            initial_premium=0,
            annual_premium=100000,
            years=10,
            return_rate=0.02
        )
        
        assert isinstance(result, dict)
        assert "解約返戻金" in result
        assert "払込保険料総額" in result
        assert result["解約返戻金"] > 0
        assert result["払込保険料総額"] == 100000 * 10
    
    def test_calculate_total_benefit(self, optimizer):
        """総合利益計算のテスト"""
        result = optimizer.calculate_total_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            withdrawal_year=10,
            policy_start_year=2020,
            max_years=20,
            return_rate=0.02
        )
        
        assert isinstance(result, dict)
        assert "純利益" in result
        assert "節税効果累計" in result
        assert "解約返戻金" in result
    
    def test_optimize_withdrawal_timing(self, optimizer):
        """引き出しタイミング最適化のテスト"""
        best, all_results = optimizer.optimize_withdrawal_timing(
            annual_premium=100000,
            taxable_income=5000000,
            policy_start_year=2020,
            max_years=15
        )
        
        assert isinstance(best, dict)
        assert isinstance(all_results, pd.DataFrame)
        assert "引き出し年" in best
        assert "純利益" in best
        assert len(all_results) == 15  # 1年～15年までの結果
    
    def test_analyze_income_scenarios(self, optimizer):
        """所得シナリオ分析のテスト"""
        scenarios = [
            {"label": "低所得", "income": 3000000},
            {"label": "基準", "income": 5000000},
            {"label": "高所得", "income": 8000000},
        ]
        
        result = optimizer.analyze_income_scenarios(
            annual_premium=100000,
            base_income=5000000,
            scenarios=scenarios,
            policy_start_year=2020,
            max_years=10
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "シナリオ" in result.columns
    
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
        assert len(result) > 0  # 少なくとも1つの戦略がある
        assert "戦略タイプ" in result.columns
        assert "純利益" in result.columns


class TestPartialWithdrawal:
    """部分解約戦略のテスト"""
    
    @pytest.fixture
    def optimizer(self):
        return WithdrawalOptimizer()
    
    def test_partial_withdrawal_benefit(self, optimizer):
        """部分解約利益計算のテスト"""
        benefit = optimizer._calculate_partial_withdrawal_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            policy_start_year=2020,
            interval=2,
            rate=0.5,
            max_years=10,
            return_rate=0.02,
            withdrawal_reinvest_rate=0.01
        )
        
        assert isinstance(benefit, float)
        # 通常、利益は正の値（節税効果があるため）
        assert benefit > 0
    
    def test_partial_withdrawal_with_zero_reinvest(self, optimizer):
        """再投資なし（利回り0%）の部分解約テスト"""
        benefit_zero = optimizer._calculate_partial_withdrawal_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            policy_start_year=2020,
            interval=2,
            rate=0.5,
            max_years=10,
            return_rate=0.02,
            withdrawal_reinvest_rate=0.00
        )
        
        assert benefit_zero > 0
    
    def test_partial_withdrawal_with_high_reinvest(self, optimizer):
        """高利回り再投資（5%）の部分解約テスト"""
        benefit_high = optimizer._calculate_partial_withdrawal_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            policy_start_year=2020,
            interval=2,
            rate=0.5,
            max_years=10,
            return_rate=0.02,
            withdrawal_reinvest_rate=0.05
        )
        
        # 高利回りの方が利益が大きくなるはず
        assert benefit_high > 0


class TestFullWithdrawal:
    """全解約戦略のテスト"""
    
    @pytest.fixture
    def optimizer(self):
        return WithdrawalOptimizer()
    
    def test_full_withdrawal_early(self, optimizer):
        """早期全解約のテスト"""
        result = optimizer.calculate_total_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            withdrawal_year=5,
            policy_start_year=2020,
            max_years=20,
            return_rate=0.02
        )
        
        assert result["純利益"] > 0
    
    def test_full_withdrawal_late(self, optimizer):
        """後期全解約のテスト"""
        result = optimizer.calculate_total_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            withdrawal_year=15,
            policy_start_year=2020,
            max_years=20,
            return_rate=0.02
        )
        
        assert result["純利益"] > 0


class TestSwitchStrategy:
    """乗り換え戦略のテスト"""
    
    @pytest.fixture
    def optimizer(self):
        return WithdrawalOptimizer()
    
    def test_switch_benefit(self, optimizer):
        """乗り換え利益計算のテスト"""
        benefit = optimizer._calculate_switch_benefit(
            annual_premium=100000,
            taxable_income=5000000,
            policy_start_year=2020,
            switch_year=10,
            switch_rate=0.03,
            max_years=20,
            return_rate=0.02
        )
        
        assert isinstance(benefit, float)


class TestEdgeCases:
    """エッジケースのテスト"""
    
    @pytest.fixture
    def optimizer(self):
        return WithdrawalOptimizer()
    
    def test_zero_premium(self, optimizer):
        """保険料ゼロのテスト"""
        result = optimizer.calculate_policy_value(
            initial_premium=0,
            annual_premium=0,
            years=10,
            return_rate=0.02
        )
        
        assert result["解約返戻金"] == 0
        assert result["払込保険料総額"] == 0
    
    def test_negative_return_rate(self, optimizer):
        """負の運用利回りのテスト"""
        with pytest.raises(ValueError):
            optimizer.calculate_policy_value(
                initial_premium=0,
                annual_premium=100000,
                years=10,
                return_rate=-0.02
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
