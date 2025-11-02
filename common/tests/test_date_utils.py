"""date_utils のテスト

このテストモジュールは、common.utils.date_utils モジュールの
各種日付計算関数の動作を検証します。

Test Classes:
    TestCalculateAge: 年齢計算のテスト
    TestCalculateYearsBetween: 年数計算のテスト
    TestCalculateMonthsBetween: 月数計算のテスト
    TestToWareki: 西暦→和暦変換のテスト
    TestFromWareki: 和暦→西暦変換のテスト
    TestParseWareki: 和暦文字列パースのテスト
    TestWarekiToSeireki: 和暦文字列→西暦変換のテスト

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

import pytest
from datetime import date

from common.utils.date_utils import (
    calculate_age,
    calculate_years_between,
    calculate_months_between,
    to_wareki,
    from_wareki,
    parse_wareki,
    wareki_to_seireki,
)


class TestCalculateAge:
    """年齢計算のテスト"""
    
    def test_basic_age_calculation(self):
        """基本的な年齢計算"""
        birth_date = date(1990, 5, 15)
        reference_date = date(2025, 1, 10)
        age = calculate_age(birth_date, reference_date)
        assert age == 34
    
    def test_age_before_birthday(self):
        """誕生日前の年齢計算"""
        birth_date = date(1990, 5, 15)
        reference_date = date(2025, 5, 14)  # 誕生日の前日
        age = calculate_age(birth_date, reference_date)
        assert age == 34
    
    def test_age_on_birthday(self):
        """誕生日当日の年齢計算"""
        birth_date = date(1990, 5, 15)
        reference_date = date(2025, 5, 15)  # 誕生日当日
        age = calculate_age(birth_date, reference_date)
        assert age == 35
    
    def test_age_after_birthday(self):
        """誕生日後の年齢計算"""
        birth_date = date(1990, 5, 15)
        reference_date = date(2025, 5, 16)  # 誕生日の翌日
        age = calculate_age(birth_date, reference_date)
        assert age == 35
    
    def test_age_zero(self):
        """0歳の計算"""
        birth_date = date(2025, 1, 1)
        reference_date = date(2025, 1, 10)
        age = calculate_age(birth_date, reference_date)
        assert age == 0
    
    def test_age_with_leap_year(self):
        """閏年生まれの年齢計算"""
        birth_date = date(2000, 2, 29)  # 閏年生まれ
        reference_date = date(2025, 3, 1)
        age = calculate_age(birth_date, reference_date)
        assert age == 25
    
    def test_age_default_reference_date(self):
        """基準日省略時は今日の日付を使用"""
        birth_date = date(1990, 1, 1)
        age = calculate_age(birth_date)
        # 年齢は0以上であることを確認
        assert age >= 0
    
    def test_age_future_birth_date_raises_error(self):
        """未来の生年月日でエラー"""
        birth_date = date(2030, 1, 1)
        reference_date = date(2025, 1, 1)
        with pytest.raises(ValueError, match="生年月日.*は基準日.*より前である必要があります"):
            calculate_age(birth_date, reference_date)


class TestCalculateYearsBetween:
    """年数計算のテスト"""
    
    def test_basic_years_calculation(self):
        """基本的な年数計算"""
        start = date(2020, 1, 1)
        end = date(2025, 1, 1)
        years = calculate_years_between(start, end)
        assert years == 5.0
    
    def test_years_with_partial_year(self):
        """1年未満の端数がある場合（precise=False）"""
        start = date(2020, 1, 1)
        end = date(2025, 6, 1)
        years = calculate_years_between(start, end, precise=False)
        assert years == 5.0  # 満年数
    
    def test_years_precise(self):
        """精密計算（precise=True）"""
        start = date(2020, 1, 1)
        end = date(2025, 6, 1)
        years = calculate_years_between(start, end, precise=True)
        # 約5.42年
        assert 5.4 < years < 5.5
    
    def test_years_same_date(self):
        """同じ日付の場合"""
        start = date(2020, 1, 1)
        end = date(2020, 1, 1)
        years = calculate_years_between(start, end)
        assert years == 0.0
    
    def test_years_less_than_one_year(self):
        """1年未満の場合"""
        start = date(2020, 1, 1)
        end = date(2020, 12, 31)
        years = calculate_years_between(start, end)
        assert years == 0.0
    
    def test_years_start_after_end_raises_error(self):
        """開始日が終了日より後でエラー"""
        start = date(2025, 1, 1)
        end = date(2020, 1, 1)
        with pytest.raises(ValueError, match="開始日.*は終了日.*より前である必要があります"):
            calculate_years_between(start, end)


class TestCalculateMonthsBetween:
    """月数計算のテスト"""
    
    def test_basic_months_calculation(self):
        """基本的な月数計算"""
        start = date(2020, 1, 1)
        end = date(2025, 1, 1)
        months = calculate_months_between(start, end)
        assert months == 60
    
    def test_months_same_month(self):
        """同月内の場合"""
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)
        months = calculate_months_between(start, end)
        assert months == 0
    
    def test_months_one_month(self):
        """1ヶ月の場合"""
        start = date(2025, 1, 1)
        end = date(2025, 2, 1)
        months = calculate_months_between(start, end)
        assert months == 1
    
    def test_months_with_partial_month(self):
        """端数がある場合"""
        start = date(2025, 1, 15)
        end = date(2025, 2, 14)
        months = calculate_months_between(start, end)
        assert months == 0  # 満月数は0
    
    def test_months_exactly_one_month(self):
        """ちょうど1ヶ月の場合"""
        start = date(2025, 1, 15)
        end = date(2025, 2, 15)
        months = calculate_months_between(start, end)
        assert months == 1
    
    def test_months_cross_year(self):
        """年をまたぐ場合"""
        start = date(2024, 11, 1)
        end = date(2025, 2, 1)
        months = calculate_months_between(start, end)
        assert months == 3
    
    def test_months_start_after_end_raises_error(self):
        """開始日が終了日より後でエラー"""
        start = date(2025, 1, 1)
        end = date(2020, 1, 1)
        with pytest.raises(ValueError, match="開始日.*は終了日.*より前である必要があります"):
            calculate_months_between(start, end)


class TestToWareki:
    """西暦→和暦変換のテスト"""
    
    def test_reiwa_regular_year(self):
        """令和の通常年"""
        assert to_wareki(2025) == "令和7年"
        assert to_wareki(2023) == "令和5年"
    
    def test_reiwa_first_year(self):
        """令和元年"""
        assert to_wareki(2019) == "令和元年"
    
    def test_heisei_last_year(self):
        """平成最後の年"""
        assert to_wareki(2018) == "平成30年"
    
    def test_heisei_regular_year(self):
        """平成の通常年"""
        assert to_wareki(2000) == "平成12年"
        assert to_wareki(1995) == "平成7年"
    
    def test_heisei_first_year(self):
        """平成元年"""
        assert to_wareki(1989) == "平成元年"
    
    def test_showa_last_year(self):
        """昭和最後の年"""
        assert to_wareki(1988) == "昭和63年"
    
    def test_showa_regular_year(self):
        """昭和の通常年"""
        assert to_wareki(1980) == "昭和55年"
        assert to_wareki(1950) == "昭和25年"
    
    def test_showa_first_year(self):
        """昭和元年"""
        assert to_wareki(1926) == "昭和元年"
    
    def test_taisho_last_year(self):
        """大正最後の年"""
        assert to_wareki(1925) == "大正14年"
    
    def test_taisho_first_year(self):
        """大正元年"""
        assert to_wareki(1912) == "大正元年"
    
    def test_meiji_year(self):
        """明治の年"""
        assert to_wareki(1900) == "明治33年"
        assert to_wareki(1868) == "明治元年"
    
    def test_before_meiji(self):
        """明治以前"""
        assert to_wareki(1867) == "1867年"
        assert to_wareki(1800) == "1800年"


class TestFromWareki:
    """和暦→西暦変換のテスト"""
    
    def test_reiwa_to_seireki(self):
        """令和から西暦へ"""
        assert from_wareki("令和", 7) == 2025
        assert from_wareki("令和", 1) == 2019
    
    def test_heisei_to_seireki(self):
        """平成から西暦へ"""
        assert from_wareki("平成", 30) == 2018
        assert from_wareki("平成", 1) == 1989
    
    def test_showa_to_seireki(self):
        """昭和から西暦へ"""
        assert from_wareki("昭和", 64) == 1989
        assert from_wareki("昭和", 1) == 1926
    
    def test_taisho_to_seireki(self):
        """大正から西暦へ"""
        assert from_wareki("大正", 14) == 1925
        assert from_wareki("大正", 1) == 1912
    
    def test_meiji_to_seireki(self):
        """明治から西暦へ"""
        assert from_wareki("明治", 33) == 1900
        assert from_wareki("明治", 1) == 1868
    
    def test_invalid_era_raises_error(self):
        """不正な元号でエラー"""
        with pytest.raises(ValueError, match="不正な元号です"):
            from_wareki("江戸", 1)
    
    def test_invalid_year_zero_raises_error(self):
        """和暦年0でエラー"""
        with pytest.raises(ValueError, match="和暦年は1以上である必要があります"):
            from_wareki("令和", 0)
    
    def test_invalid_year_negative_raises_error(self):
        """負の和暦年でエラー"""
        with pytest.raises(ValueError, match="和暦年は1以上である必要があります"):
            from_wareki("令和", -1)
    
    def test_year_out_of_range_raises_error(self):
        """範囲外の和暦年でエラー"""
        with pytest.raises(ValueError, match="平成は30年までです"):
            from_wareki("平成", 31)


class TestParseWareki:
    """和暦文字列パースのテスト"""
    
    def test_parse_reiwa_with_nen(self):
        """令和（年付き）"""
        era, year = parse_wareki("令和7年")
        assert era == "令和"
        assert year == 7
    
    def test_parse_reiwa_without_nen(self):
        """令和（年なし）"""
        era, year = parse_wareki("令和7")
        assert era == "令和"
        assert year == 7
    
    def test_parse_gannen_with_nen(self):
        """元年（年付き）"""
        era, year = parse_wareki("令和元年")
        assert era == "令和"
        assert year == 1
    
    def test_parse_gannen_without_nen(self):
        """元年（年なし）"""
        era, year = parse_wareki("令和元")
        assert era == "令和"
        assert year == 1
    
    def test_parse_heisei(self):
        """平成"""
        era, year = parse_wareki("平成30年")
        assert era == "平成"
        assert year == 30
    
    def test_parse_showa(self):
        """昭和"""
        era, year = parse_wareki("昭和64年")
        assert era == "昭和"
        assert year == 64
    
    def test_parse_invalid_format_raises_error(self):
        """不正なフォーマットでエラー"""
        with pytest.raises(ValueError, match="不正な和暦文字列です"):
            parse_wareki("2025年")
    
    def test_parse_invalid_era_raises_error(self):
        """不正な元号でエラー"""
        with pytest.raises(ValueError, match="不正な和暦文字列です"):
            parse_wareki("江戸元年")


class TestWarekiToSeireki:
    """和暦文字列→西暦変換のテスト"""
    
    def test_wareki_string_to_seireki(self):
        """和暦文字列から西暦へ"""
        assert wareki_to_seireki("令和7年") == 2025
        assert wareki_to_seireki("令和元年") == 2019
        assert wareki_to_seireki("平成30年") == 2018
        assert wareki_to_seireki("昭和64年") == 1989
    
    def test_wareki_string_without_nen(self):
        """年なしの和暦文字列"""
        assert wareki_to_seireki("令和7") == 2025
        assert wareki_to_seireki("平成30") == 2018


class TestEdgeCases:
    """エッジケースのテスト"""
    
    def test_leap_year_february(self):
        """閏年の2月29日"""
        # 閏年生まれの人の年齢
        birth_date = date(2000, 2, 29)
        
        # 閏年の誕生日
        age_on_leap = calculate_age(birth_date, date(2024, 2, 29))
        assert age_on_leap == 24
        
        # 非閏年の誕生日後（3月1日）
        age_after_leap = calculate_age(birth_date, date(2023, 3, 1))
        assert age_after_leap == 23
    
    def test_year_end_boundary(self):
        """年末年始の境界"""
        start = date(2024, 12, 31)
        end = date(2025, 1, 1)
        
        months = calculate_months_between(start, end)
        assert months == 0
        
        years = calculate_years_between(start, end)
        assert years == 0.0
    
    def test_era_transition_boundary(self):
        """元号の境界"""
        # 平成→令和の境界
        assert to_wareki(2018) == "平成30年"
        assert to_wareki(2019) == "令和元年"
        
        # 昭和→平成の境界
        assert to_wareki(1988) == "昭和63年"
        assert to_wareki(1989) == "平成元年"


# テスト実行時の追加設定
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
