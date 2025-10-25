"""
テストスイート - 税額計算のテスト
"""

import pytest
from life_insurance.core.tax_calculator import TaxCalculator


class TestTaxCalculator:
    """TaxCalculator クラスのテスト"""
    
    @pytest.fixture
    def calculator(self):
        """テスト用の計算機インスタンスを作成"""
        return TaxCalculator()
    
    def test_get_income_tax_rate_lowest_bracket(self, calculator):
        """最低税率区分のテスト（195万円以下: 5%）"""
        assert calculator.get_income_tax_rate(1000000) == 0.05
        assert calculator.get_income_tax_rate(1950000) == 0.05
    
    def test_get_income_tax_rate_middle_brackets(self, calculator):
        """中間税率区分のテスト"""
        # 195万～330万円: 10%
        assert calculator.get_income_tax_rate(2000000) == 0.10
        assert calculator.get_income_tax_rate(3300000) == 0.10
        
        # 330万～695万円: 20%
        assert calculator.get_income_tax_rate(5000000) == 0.20
        assert calculator.get_income_tax_rate(6950000) == 0.20
    
    def test_get_income_tax_rate_highest_bracket(self, calculator):
        """最高税率区分のテスト（4000万円超: 45%）"""
        assert calculator.get_income_tax_rate(50000000) == 0.45
        assert calculator.get_income_tax_rate(100000000) == 0.45
    
    def test_calculate_income_tax(self, calculator):
        """所得税計算のテスト"""
        # 課税所得500万円の場合
        result = calculator.calculate_income_tax(5000000)
        
        assert isinstance(result, dict)
        assert "所得税" in result
        assert "復興特別所得税" in result
        assert "合計税額" in result
        
        # 500万円の所得税: 5,000,000 × 20% - 427,500 = 572,500円
        expected_income_tax = 5000000 * 0.20 - 427500
        assert abs(result["所得税"] - expected_income_tax) < 1
    
    def test_calculate_tax_savings(self, calculator):
        """節税効果計算のテスト"""
        result = calculator.calculate_tax_savings(
            deduction_amount=50000,
            taxable_income=5000000
        )
        
        assert isinstance(result, dict)
        assert "所得税節税額" in result
        assert "住民税節税額" in result
        assert "合計節税額" in result
        
        # 控除額50,000円、税率20%の場合
        # 所得税節税: 50,000 × 20% × (1 + 2.1%) = 10,210円
        # 住民税節税: 50,000 × 10% = 5,000円
        assert result["所得税節税額"] > 10000
        assert result["住民税節税額"] == 5000
    
    def test_get_tax_bracket_info(self, calculator):
        """税率区分情報取得のテスト"""
        result = calculator.get_tax_bracket_info(5000000)
        
        assert isinstance(result, dict)
        assert "現在の税率" in result
        assert "次の税率" in result
        assert "次の区分まで" in result
        
        # 500万円の場合: 20%区分、次は23%区分（695万円）
        assert result["現在の税率"] == 0.20
        assert result["次の税率"] == 0.23
    
    def test_simulate_income_changes(self, calculator):
        """所得変動シミュレーションのテスト"""
        scenarios = [
            {"label": "低所得", "income": 3000000},
            {"label": "中所得", "income": 5000000},
            {"label": "高所得", "income": 8000000},
        ]
        
        result = calculator.simulate_income_changes(
            base_income=5000000,
            scenarios=scenarios
        )
        
        assert len(result) == 3
        assert "label" in result.columns
        assert "所得税" in result.columns


class TestTaxBrackets:
    """税率区分の境界値テスト"""
    
    @pytest.fixture
    def calculator(self):
        return TaxCalculator()
    
    def test_bracket_boundaries(self, calculator):
        """各税率区分の境界値テスト"""
        # 195万円の境界
        assert calculator.get_income_tax_rate(1950000) == 0.05
        assert calculator.get_income_tax_rate(1950001) == 0.10
        
        # 330万円の境界
        assert calculator.get_income_tax_rate(3300000) == 0.10
        assert calculator.get_income_tax_rate(3300001) == 0.20
        
        # 695万円の境界
        assert calculator.get_income_tax_rate(6950000) == 0.20
        assert calculator.get_income_tax_rate(6950001) == 0.23
    
    def test_zero_income(self, calculator):
        """所得ゼロのテスト"""
        result = calculator.calculate_income_tax(0)
        assert result["所得税"] == 0
        assert result["復興特別所得税"] == 0
        assert result["合計税額"] == 0
    
    def test_negative_income(self, calculator):
        """負の所得のテスト"""
        with pytest.raises(ValueError):
            calculator.calculate_income_tax(-1000000)


class TestReconstructionTax:
    """復興特別所得税のテスト"""
    
    @pytest.fixture
    def calculator(self):
        return TaxCalculator()
    
    def test_reconstruction_tax_calculation(self, calculator):
        """復興特別所得税の計算テスト"""
        result = calculator.calculate_income_tax(5000000)
        
        # 復興特別所得税 = 所得税 × 2.1%
        expected_reconstruction = result["所得税"] * 0.021
        assert abs(result["復興特別所得税"] - expected_reconstruction) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
