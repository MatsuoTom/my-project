"""共通基盤パッケージのテストモジュール

このパッケージは、common/パッケージの各機能に対する
単体テストを含みます。

Test Modules:
    test_base_calculator: BaseFinancialCalculator, CompoundInterestMixin のテスト
    test_financial_plan: FinancialPlan のテスト
    test_math_utils: math_utils のテスト
    test_date_utils: date_utils のテスト

Usage:
    # すべてのテストを実行
    pytest common/tests/ -v
    
    # 特定のテストモジュールを実行
    pytest common/tests/test_base_calculator.py -v
"""
