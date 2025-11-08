"""日付計算ユーティリティ

このモジュールは、年齢計算、期間計算、和暦変換等の
日付関連のユーティリティ関数を提供します。

Functions:
    calculate_age: 年齢計算（満年齢）
    calculate_years_between: 2つの日付間の年数計算
    calculate_months_between: 2つの日付間の月数計算
    to_wareki: 西暦から和暦に変換
    from_wareki: 和暦から西暦に変換
    parse_wareki: 和暦文字列をパース

Example:
    >>> from datetime import date
    >>> from common.utils.date_utils import calculate_age, to_wareki
    >>>
    >>> # 年齢計算
    >>> age = calculate_age(date(1990, 5, 15), date(2025, 1, 10))
    >>> print(f"{age}歳")
    34歳
    >>>
    >>> # 和暦変換
    >>> wareki = to_wareki(2025)
    >>> print(wareki)
    令和7年

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

from datetime import date, timedelta
from typing import Optional, Tuple
import re


def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> int:
    """年齢計算（満年齢）

    生年月日から基準日時点の満年齢を計算します。

    Args:
        birth_date: 生年月日
        reference_date: 基準日（Noneの場合は今日）

    Returns:
        int: 年齢（満年齢）

    Raises:
        ValueError: 生年月日が未来の日付の場合

    Examples:
        >>> from datetime import date
        >>>
        >>> # 1990年5月15日生まれの人の2025年1月10日時点の年齢
        >>> age = calculate_age(date(1990, 5, 15), date(2025, 1, 10))
        >>> print(age)
        34
        >>>
        >>> # 誕生日前と後での違い
        >>> age_before = calculate_age(date(1990, 5, 15), date(2025, 5, 14))
        >>> age_after = calculate_age(date(1990, 5, 15), date(2025, 5, 15))
        >>> print(f"誕生日前: {age_before}歳, 誕生日後: {age_after}歳")
        誕生日前: 34歳, 誕生日後: 35歳

    Notes:
        - 誕生日当日に年齢が増える
        - 満年齢の計算（数え年ではない）
    """
    if reference_date is None:
        reference_date = date.today()

    if birth_date > reference_date:
        raise ValueError(
            f"生年月日（{birth_date}）は基準日（{reference_date}）より前である必要があります"
        )

    age = reference_date.year - birth_date.year

    # 誕生日がまだ来ていない場合は1歳引く
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def calculate_years_between(start_date: date, end_date: date, precise: bool = False) -> float:
    """2つの日付間の年数を計算

    開始日から終了日までの年数を計算します。

    Args:
        start_date: 開始日
        end_date: 終了日
        precise: True の場合は小数点以下も計算（デフォルト: False）

    Returns:
        float: 年数（precise=Falseの場合は整数部分のみ）

    Examples:
        >>> from datetime import date
        >>>
        >>> # 2020年1月1日から2025年1月1日まで
        >>> years = calculate_years_between(date(2020, 1, 1), date(2025, 1, 1))
        >>> print(years)
        5.0
        >>>
        >>> # 精密計算（小数点以下も含む）
        >>> years_precise = calculate_years_between(
        ...     date(2020, 1, 1),
        ...     date(2025, 6, 1),
        ...     precise=True
        ... )
        >>> print(f"{years_precise:.2f}年")
        5.42年

    Notes:
        - precise=Trueの場合、365.25日を1年として計算
        - precise=Falseの場合、満年数を返す
    """
    if start_date > end_date:
        raise ValueError(f"開始日（{start_date}）は終了日（{end_date}）より前である必要があります")

    if precise:
        # 精密計算（365.25日を1年として計算）
        days = (end_date - start_date).days
        return days / 365.25
    else:
        # 満年数計算
        years = end_date.year - start_date.year
        if (end_date.month, end_date.day) < (start_date.month, start_date.day):
            years -= 1
        return float(years)


def calculate_months_between(start_date: date, end_date: date) -> int:
    """2つの日付間の月数を計算

    開始日から終了日までの月数を計算します。

    Args:
        start_date: 開始日
        end_date: 終了日

    Returns:
        int: 月数（満月数）

    Examples:
        >>> from datetime import date
        >>>
        >>> # 2020年1月1日から2025年1月1日まで
        >>> months = calculate_months_between(date(2020, 1, 1), date(2025, 1, 1))
        >>> print(f"{months}ヶ月")
        60ヶ月
        >>>
        >>> # 同月内の場合
        >>> months = calculate_months_between(date(2025, 1, 1), date(2025, 1, 31))
        >>> print(f"{months}ヶ月")
        0ヶ月

    Notes:
        - 満月数の計算（日単位は考慮しない）
        - 1ヶ月未満は0ヶ月として扱う
    """
    if start_date > end_date:
        raise ValueError(f"開始日（{start_date}）は終了日（{end_date}）より前である必要があります")

    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    # 日が開始日より前の場合は1ヶ月引く
    if end_date.day < start_date.day:
        months -= 1

    return months


def to_wareki(year: int) -> str:
    """西暦から和暦に変換

    西暦年を和暦表記に変換します。

    Args:
        year: 西暦年

    Returns:
        str: 和暦表記（例: "令和7年"）

    Examples:
        >>> to_wareki(2025)
        '令和7年'
        >>> to_wareki(2019)
        '令和元年'
        >>> to_wareki(2018)
        '平成30年'
        >>> to_wareki(1989)
        '平成元年'
        >>> to_wareki(1926)
        '昭和元年'
        >>> to_wareki(1925)
        '大正14年'

    Notes:
        - 令和: 2019年～
        - 平成: 1989年～2018年
        - 昭和: 1926年～1988年
        - 大正: 1912年～1925年
        - 明治: 1868年～1911年
        - 元年は「元年」と表記
    """
    if year >= 2019:
        wareki_year = year - 2018
        return f"令和{wareki_year if wareki_year > 1 else '元'}年"
    elif year >= 1989:
        wareki_year = year - 1988
        return f"平成{wareki_year if wareki_year > 1 else '元'}年"
    elif year >= 1926:
        wareki_year = year - 1925
        return f"昭和{wareki_year if wareki_year > 1 else '元'}年"
    elif year >= 1912:
        wareki_year = year - 1911
        return f"大正{wareki_year if wareki_year > 1 else '元'}年"
    elif year >= 1868:
        wareki_year = year - 1867
        return f"明治{wareki_year if wareki_year > 1 else '元'}年"
    else:
        return f"{year}年"


def from_wareki(era: str, year: int) -> int:
    """和暦から西暦に変換

    和暦（元号と年）から西暦年に変換します。

    Args:
        era: 元号（"令和", "平成", "昭和", "大正", "明治"）
        year: 和暦年（元年は1）

    Returns:
        int: 西暦年

    Raises:
        ValueError: 不正な元号または年数の場合

    Examples:
        >>> from_wareki("令和", 7)
        2025
        >>> from_wareki("令和", 1)
        2019
        >>> from_wareki("平成", 30)
        2018
        >>> from_wareki("昭和", 64)
        1989

    Notes:
        - 元年は year=1 として指定
        - 各元号の有効範囲をチェック
    """
    era_map = {
        "令和": (2019, 2018, None),  # (開始年, オフセット, 終了年)
        "平成": (1989, 1988, 2018),
        "昭和": (1926, 1925, 1989),  # 昭和64年は1989年1月1-7日
        "大正": (1912, 1911, 1925),
        "明治": (1868, 1867, 1911),
    }

    if era not in era_map:
        raise ValueError(f"不正な元号です: {era}")

    start_year, offset, end_year = era_map[era]
    seireki = offset + year

    # 範囲チェック
    if year < 1:
        raise ValueError(f"和暦年は1以上である必要があります: {year}")

    if end_year is not None and seireki > end_year:
        max_year = end_year - offset
        raise ValueError(f"{era}は{max_year}年までです: {year}年")

    return seireki


def parse_wareki(wareki_str: str) -> Tuple[str, int]:
    """和暦文字列をパース

    和暦文字列（例: "令和7年"）を元号と年に分解します。

    Args:
        wareki_str: 和暦文字列（例: "令和7年", "平成30年", "昭和元年"）

    Returns:
        Tuple[str, int]: (元号, 和暦年)

    Raises:
        ValueError: 不正な和暦文字列の場合

    Examples:
        >>> parse_wareki("令和7年")
        ('令和', 7)
        >>> parse_wareki("令和元年")
        ('令和', 1)
        >>> parse_wareki("平成30年")
        ('平成', 30)

    Notes:
        - "元年"は year=1 として返す
        - "年"は省略可能
    """
    # 正規表現パターン: (元号)(数字または"元")(年?)
    pattern = r"^(令和|平成|昭和|大正|明治)(元|\d+)年?$"
    match = re.match(pattern, wareki_str)

    if not match:
        raise ValueError(f"不正な和暦文字列です: {wareki_str}")

    era = match.group(1)
    year_str = match.group(2)

    # "元"を1に変換
    year = 1 if year_str == "元" else int(year_str)

    return era, year


def wareki_to_seireki(wareki_str: str) -> int:
    """和暦文字列を西暦年に変換

    和暦文字列（例: "令和7年"）を西暦年に変換します。
    parse_wareki() と from_wareki() を組み合わせた便利関数です。

    Args:
        wareki_str: 和暦文字列（例: "令和7年", "平成30年"）

    Returns:
        int: 西暦年

    Examples:
        >>> wareki_to_seireki("令和7年")
        2025
        >>> wareki_to_seireki("平成元年")
        1989
        >>> wareki_to_seireki("昭和64年")
        1989
    """
    era, year = parse_wareki(wareki_str)
    return from_wareki(era, year)


# モジュールレベルのエクスポート
__all__ = [
    "calculate_age",
    "calculate_years_between",
    "calculate_months_between",
    "to_wareki",
    "from_wareki",
    "parse_wareki",
    "wareki_to_seireki",
]
