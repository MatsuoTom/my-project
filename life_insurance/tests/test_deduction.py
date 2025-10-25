"""
テストスイート - 生命保険料控除計算のテスト
"""

import pytest
from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator


class TestDeductionCalculator:
    """LifeInsuranceDeductionCalculator クラスのテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用の計算機インスタンスを作成"""
        return LifeInsuranceDeductionCalculator()
    
    def test_calculate_old_deduction_zero(self, calculator):
        """保険料が0円の場合のテスト"""
        assert calculator.calculate_old_deduction(0) == 0
    
    def test_calculate_old_deduction_below_25000(self, calculator):
        """保険料が25,000円以下の場合のテスト（全額控除）"""
        assert calculator.calculate_old_deduction(10000) == 10000
        assert calculator.calculate_old_deduction(25000) == 25000
    
    def test_calculate_old_deduction_25001_to_50000(self, calculator):
        """保険料が25,001～50,000円の場合のテスト"""
        # 30,000円の場合: 30,000 × 0.5 + 12,500 = 27,500円
        assert calculator.calculate_old_deduction(30000) == 27500
        # 50,000円の場合: 50,000 × 0.5 + 12,500 = 37,500円
        assert calculator.calculate_old_deduction(50000) == 37500
    
    def test_calculate_old_deduction_50001_to_100000(self, calculator):
        """保険料が50,001～100,000円の場合のテスト"""
        # 60,000円の場合: 60,000 × 0.25 + 25,000 = 40,000円
        assert calculator.calculate_old_deduction(60000) == 40000
        # 100,000円の場合: 100,000 × 0.25 + 25,000 = 50,000円
        assert calculator.calculate_old_deduction(100000) == 50000
    
    def test_calculate_old_deduction_above_100000(self, calculator):
        """保険料が100,001円以上の場合のテスト（上限50,000円）"""
        assert calculator.calculate_old_deduction(120000) == 50000
        assert calculator.calculate_old_deduction(200000) == 50000
        assert calculator.calculate_old_deduction(1000000) == 50000
    
    def test_get_deduction_breakdown(self, calculator):
        """控除額の内訳取得テスト"""
        result = calculator.get_deduction_breakdown(60000)
        
        assert isinstance(result, dict)
        assert "年間保険料" in result
        assert "控除額" in result
        assert "適用区分" in result
        assert result["年間保険料"] == 60000
        assert result["控除額"] == 40000
    
    def test_calculate_multiple_contracts(self, calculator):
        """複数契約の合算控除テスト"""
        contracts = [30000, 40000, 50000]
        result = calculator.calculate_multiple_contracts(contracts)
        
        assert isinstance(result, dict)
        assert "合計保険料" in result
        assert "合計控除額" in result
        # 合計120,000円 → 上限50,000円
        assert result["合計保険料"] == 120000
        assert result["合計控除額"] == 50000
    
    def test_optimize_premium_distribution(self, calculator):
        """保険料配分最適化のテスト"""
        result = calculator.optimize_premium_distribution(
            total_budget=100000,
            num_contracts=2
        )
        
        assert isinstance(result, dict)
        assert "最適配分" in result
        assert "合計控除額" in result
        assert len(result["最適配分"]) == 2


class TestEdgeCases:
    """エッジケースのテスト"""
    
    @pytest.fixture
    def calculator(self):
        return LifeInsuranceDeductionCalculator()
    
    def test_negative_premium(self, calculator):
        """負の保険料のテスト"""
        with pytest.raises(ValueError):
            calculator.calculate_old_deduction(-1000)
    
    def test_extremely_large_premium(self, calculator):
        """極端に大きい保険料のテスト"""
        result = calculator.calculate_old_deduction(10000000)
        assert result == 50000  # 上限は50,000円
    
    def test_boundary_values(self, calculator):
        """境界値のテスト"""
        # 25,000円と25,001円の境界
        assert calculator.calculate_old_deduction(25000) == 25000
        assert calculator.calculate_old_deduction(25001) == 25000.5
        
        # 50,000円と50,001円の境界
        assert calculator.calculate_old_deduction(50000) == 37500
        assert calculator.calculate_old_deduction(50001) == 37500.25
        
        # 100,000円と100,001円の境界
        assert calculator.calculate_old_deduction(100000) == 50000
        assert calculator.calculate_old_deduction(100001) == 50000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
