"""
PensionCalculatorと共通基盤の統合テスト

Phase 3でBaseFinancialCalculatorを継承したPensionCalculatorの動作確認
"""

import pytest
from pension_calc.core.pension_utils import PensionCalculator, SAMPLE_PENSION_RECORDS


class TestPensionCalculatorIntegration:
    """PensionCalculator統合テスト"""
    
    def test_calculator_initialization(self):
        """初期化テスト"""
        calculator = PensionCalculator()
        assert calculator is not None
        assert calculator.df is not None
        assert len(calculator.df) > 0
    
    def test_calculator_with_sample_data(self):
        """サンプルデータでの計算"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        assert len(calculator.records) == len(SAMPLE_PENSION_RECORDS)
        assert calculator.df is not None
    
    def test_calculate_future_pension(self):
        """将来年金計算"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        result = calculator.calculate_future_pension(retirement_age=65)
        
        assert "年間受給額" in result
        assert "月額受給額" in result
        assert "総納付額" in result
        assert "加入月数" in result
        assert result["年間受給額"] > 0
        assert result["月額受給額"] > 0
    
    def test_calculate_method(self):
        """calculate抽象メソッドの実装テスト"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        result = calculator.calculate(retirement_age=65)
        
        # calculate_future_pensionと同じ結果を返す
        assert "年間受給額" in result
        assert result["年間受給額"] > 0
    
    def test_validate_inputs_valid_age(self):
        """有効な退職年齢の検証"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        assert calculator.validate_inputs(retirement_age=65) is True
        assert calculator.validate_inputs(retirement_age=60) is True
        assert calculator.validate_inputs(retirement_age=75) is True
    
    def test_validate_inputs_invalid_age(self):
        """無効な退職年齢の検証"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        
        with pytest.raises(ValueError, match="退職年齢は60歳から75歳の範囲である必要があります"):
            calculator.validate_inputs(retirement_age=59)
        
        with pytest.raises(ValueError, match="退職年齢は60歳から75歳の範囲である必要があります"):
            calculator.validate_inputs(retirement_age=76)
    
    def test_validate_inputs_empty_data(self):
        """空データの検証"""
        calculator = PensionCalculator([])
        
        with pytest.raises(ValueError, match="年金記録データが空です"):
            calculator.validate_inputs(retirement_age=65)
    
    def test_analyze_contribution_efficiency(self):
        """納付効率性分析"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        result = calculator.analyze_contribution_efficiency()
        
        assert "損益分岐年数" in result
        assert "年間利回り相当" in result
        assert "総納付額" in result
        assert "年間受給額" in result
        assert result["損益分岐年数"] > 0
    
    def test_inheritance_from_base_calculator(self):
        """BaseFinancialCalculatorの継承確認"""
        from common.calculators.base_calculator import BaseFinancialCalculator
        
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        assert isinstance(calculator, BaseFinancialCalculator)
    
    def test_calculate_with_different_retirement_ages(self):
        """異なる退職年齢での計算"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        
        result_60 = calculator.calculate(retirement_age=60)
        result_65 = calculator.calculate(retirement_age=65)
        result_70 = calculator.calculate(retirement_age=70)
        
        assert result_60["受給開始年齢"] == 60
        assert result_65["受給開始年齢"] == 65
        assert result_70["受給開始年齢"] == 70
        
        # 年金額は退職年齢によらず同じ（簡易計算のため）
        assert result_60["年間受給額"] > 0
        assert result_65["年間受給額"] > 0
        assert result_70["年間受給額"] > 0


class TestPensionCalculatorBackwardCompatibility:
    """後方互換性テスト"""
    
    def test_old_usage_still_works(self):
        """既存の使い方が引き続き機能する"""
        # Phase 3以前の使い方
        calculator = PensionCalculator()
        result = calculator.calculate_future_pension()
        
        assert "年間受給額" in result
        assert result["年間受給額"] > 0
    
    def test_records_property_accessible(self):
        """recordsプロパティにアクセス可能"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        assert calculator.records == SAMPLE_PENSION_RECORDS
    
    def test_df_property_accessible(self):
        """dfプロパティにアクセス可能"""
        calculator = PensionCalculator(SAMPLE_PENSION_RECORDS)
        assert calculator.df is not None
        assert len(calculator.df) == len(SAMPLE_PENSION_RECORDS)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
