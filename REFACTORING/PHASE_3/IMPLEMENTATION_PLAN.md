# Phase 3: 共通基盤構築 - 実装計画

**バージョン:** 1.0  
**作成日:** 2025-01-10  
**ステータス:** 🚀 開始  
**想定期間:** 3-4週間  
**優先度:** 🟡 中

---

## 📋 概要

### 目的
- プロジェクト全体で共有できる共通基盤レイヤーを構築
- `life_insurance` と `pension_calc` モジュール間のコード重複を削減
- 保守性・拡張性・テスト容易性の向上

### 期待効果
- **コード削減:** ~200行（共通化により）
- **保守性向上:** DRY原則の徹底、単一責任の原則適用
- **拡張性向上:** 新機能追加時の共通基盤利用
- **一貫性向上:** プロジェクト全体での統一されたAPI設計

### 前提条件
- ✅ Phase 1完了（税金ヘルパー統合、25テスト全パス）
- ✅ Phase 2完了（コア計算ロジック統合、88テスト全パス）
- ✅ Gitタグ: `v0.4.0-phase2-complete`

---

## 🏗️ アーキテクチャ設計

### ディレクトリ構造
```
common/
├── __init__.py
├── calculators/
│   ├── __init__.py
│   ├── base_calculator.py       # 基底計算クラス + ミックスイン
│   └── tax_calculator.py        # 税金計算（Phase 1から移行検討）
├── models/
│   ├── __init__.py
│   └── financial_plan.py        # 金融プラン基底データクラス
└── utils/
    ├── __init__.py
    ├── math_utils.py            # 数学計算ユーティリティ
    └── date_utils.py            # 日付計算ユーティリティ
```

### クラス設計

#### 1. `BaseFinancialCalculator` (基底計算クラス)
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

class BaseFinancialCalculator(ABC):
    """金融計算の抽象基底クラス
    
    すべての金融計算機（保険、年金等）の共通インターフェース
    """
    
    @abstractmethod
    def calculate(self, *args, **kwargs):
        """計算実行（サブクラスで実装）"""
        pass
    
    @abstractmethod
    def validate_inputs(self, *args, **kwargs) -> bool:
        """入力値検証（サブクラスで実装）"""
        pass
```

#### 2. `CompoundInterestMixin` (複利計算ミックスイン)
```python
class CompoundInterestMixin:
    """複利計算の共通機能を提供するミックスイン
    
    保険・年金・投資計算で共通利用される複利計算ロジック
    """
    
    def calculate_compound_interest(
        self,
        principal: float,
        rate: float,
        years: int
    ) -> float:
        """複利計算
        
        Args:
            principal: 元本
            rate: 年利率（例: 0.03 = 3%）
            years: 年数
        
        Returns:
            複利計算後の金額
        """
        return principal * (1 + rate) ** years
    
    def calculate_present_value(
        self,
        future_value: float,
        rate: float,
        years: int
    ) -> float:
        """現在価値計算（割引計算）"""
        return future_value / (1 + rate) ** years
```

#### 3. `FinancialPlan` (金融プラン基底データクラス)
```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class FinancialPlan:
    """金融プランの基底データクラス
    
    保険プラン、年金プランの共通属性
    """
    name: str                          # プラン名
    start_age: int                     # 開始年齢
    end_age: Optional[int] = None      # 終了年齢（Noneは終身）
    annual_payment: float = 0.0        # 年間支払額
    
    def __post_init__(self):
        """バリデーション"""
        if self.start_age < 0:
            raise ValueError("開始年齢は0以上である必要があります")
        if self.end_age and self.end_age <= self.start_age:
            raise ValueError("終了年齢は開始年齢より大きい必要があります")
        if self.annual_payment < 0:
            raise ValueError("年間支払額は0以上である必要があります")
    
    @property
    def duration_years(self) -> Optional[int]:
        """期間（年数）"""
        if self.end_age:
            return self.end_age - self.start_age
        return None
```

---

## 📝 タスク一覧

### Task 3.1: ディレクトリ構造作成 ⏱️ 30分
**優先度:** 🔴 最高

- [ ] `common/__init__.py` 作成
- [ ] `common/calculators/__init__.py` 作成
- [ ] `common/models/__init__.py` 作成
- [ ] `common/utils/__init__.py` 作成

**成功基準:**
- ✓ すべてのディレクトリが作成される
- ✓ Pythonモジュールとして認識される（インポート可能）

---

### Task 3.2: BaseFinancialCalculator実装 ⏱️ 3-4時間
**優先度:** 🔴 最高

#### 実装内容
1. **`common/calculators/base_calculator.py` 作成**
   - `BaseFinancialCalculator` 抽象基底クラス
   - `CompoundInterestMixin` ミックスイン
   - 型ヒント完備
   - docstring充実

2. **テスト作成: `common/tests/test_base_calculator.py`**
   - CompoundInterestMixinの複利計算テスト（10ケース）
   - 現在価値計算テスト（5ケース）
   - エッジケース（rate=0, years=0等）

**成功基準:**
- ✓ すべてのテストがパス
- ✓ 型チェック（mypy）がパス
- ✓ docstring完備

**実装例:**
```python
# common/calculators/base_calculator.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseFinancialCalculator(ABC):
    """金融計算の抽象基底クラス"""
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> Dict[str, Any]:
        """計算実行
        
        Returns:
            計算結果の辞書
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, *args, **kwargs) -> bool:
        """入力値検証
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        pass

class CompoundInterestMixin:
    """複利計算ミックスイン"""
    
    def calculate_compound_interest(
        self,
        principal: float,
        rate: float,
        years: int
    ) -> float:
        """複利計算
        
        Args:
            principal: 元本
            rate: 年利率（小数、例: 0.03 = 3%）
            years: 年数
        
        Returns:
            複利計算後の金額
        
        Examples:
            >>> mixin = CompoundInterestMixin()
            >>> mixin.calculate_compound_interest(1000000, 0.03, 10)
            1343916.38
        """
        if principal < 0:
            raise ValueError("元本は0以上である必要があります")
        if years < 0:
            raise ValueError("年数は0以上である必要があります")
        
        return principal * (1 + rate) ** years
    
    def calculate_present_value(
        self,
        future_value: float,
        rate: float,
        years: int
    ) -> float:
        """現在価値計算（割引計算）
        
        Args:
            future_value: 将来価値
            rate: 割引率（小数）
            years: 年数
        
        Returns:
            現在価値
        """
        if future_value < 0:
            raise ValueError("将来価値は0以上である必要があります")
        if years < 0:
            raise ValueError("年数は0以上である必要があります")
        
        return future_value / (1 + rate) ** years
```

---

### Task 3.3: FinancialPlan基底クラス実装 ⏱️ 2-3時間
**優先度:** 🟠 高

#### 実装内容
1. **`common/models/financial_plan.py` 作成**
   - `FinancialPlan` データクラス
   - バリデーション機能
   - 計算プロパティ（duration_years等）

2. **テスト作成: `common/tests/test_financial_plan.py`**
   - 正常系テスト（5ケース）
   - バリデーションテスト（10ケース）
   - プロパティ計算テスト（5ケース）

**成功基準:**
- ✓ すべてのテストがパス
- ✓ バリデーションが正常動作
- ✓ 型ヒント完備

---

### Task 3.4: 数学ユーティリティ実装 ⏱️ 4-5時間
**優先度:** 🟠 高

#### 実装内容
1. **`common/utils/math_utils.py` 作成**
   - 複利計算関数群
   - 年金現価計算（PV of annuity）
   - IRR（内部収益率）計算
   - NPV（正味現在価値）計算

2. **テスト作成: `common/tests/test_math_utils.py`**
   - 各関数の計算精度テスト（20ケース）
   - エッジケーステスト（10ケース）
   - 既知値との比較テスト

**実装例:**
```python
# common/utils/math_utils.py
from typing import List
import numpy as np

def calculate_annuity_present_value(
    payment: float,
    rate: float,
    periods: int
) -> float:
    """年金現価計算（定額年金の現在価値）
    
    Args:
        payment: 期間あたりの支払額
        rate: 期間あたりの利率（小数）
        periods: 期間数
    
    Returns:
        年金の現在価値
    
    Formula:
        PV = payment × [(1 - (1 + rate)^(-periods)) / rate]
    
    Examples:
        >>> calculate_annuity_present_value(100000, 0.03, 10)
        853020.28
    """
    if rate == 0:
        return payment * periods
    
    return payment * (1 - (1 + rate) ** (-periods)) / rate

def calculate_irr(cash_flows: List[float]) -> float:
    """内部収益率（IRR）計算
    
    Args:
        cash_flows: キャッシュフロー（初期投資は負、以降の収入は正）
    
    Returns:
        IRR（小数）
    
    Examples:
        >>> calculate_irr([-1000000, 100000, 100000, 100000, 100000, 1100000])
        0.0341
    """
    return np.irr(cash_flows)

def calculate_npv(
    rate: float,
    cash_flows: List[float]
) -> float:
    """正味現在価値（NPV）計算
    
    Args:
        rate: 割引率（小数）
        cash_flows: キャッシュフロー（期間0から始まる）
    
    Returns:
        NPV
    
    Examples:
        >>> calculate_npv(0.03, [-1000000, 100000, 100000, 100000, 100000, 1100000])
        31234.56
    """
    return np.npv(rate, cash_flows)
```

**成功基準:**
- ✓ すべてのテストがパス
- ✓ 計算精度が既知値と一致（誤差 < 0.01%）
- ✓ docstring充実

---

### Task 3.5: 日付ユーティリティ実装 ⏱️ 2-3時間
**優先度:** 🟡 中

#### 実装内容
1. **`common/utils/date_utils.py` 作成**
   - 年齢計算関数
   - 期間計算関数
   - 和暦変換関数

2. **テスト作成: `common/tests/test_date_utils.py`**
   - 年齢計算テスト（10ケース）
   - 期間計算テスト（5ケース）
   - 和暦変換テスト（10ケース）

**実装例:**
```python
# common/utils/date_utils.py
from datetime import date, timedelta
from typing import Optional

def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> int:
    """年齢計算
    
    Args:
        birth_date: 生年月日
        reference_date: 基準日（Noneの場合は今日）
    
    Returns:
        年齢（満年齢）
    
    Examples:
        >>> calculate_age(date(1990, 5, 15), date(2025, 1, 10))
        34
    """
    if reference_date is None:
        reference_date = date.today()
    
    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age

def calculate_years_between(start_date: date, end_date: date) -> float:
    """2つの日付間の年数を計算（小数点付き）
    
    Args:
        start_date: 開始日
        end_date: 終了日
    
    Returns:
        年数（小数、365日 = 1年として計算）
    
    Examples:
        >>> calculate_years_between(date(2020, 1, 1), date(2025, 1, 1))
        5.0
    """
    days = (end_date - start_date).days
    return days / 365.25  # 閏年を考慮

def to_wareki(year: int) -> str:
    """西暦から和暦に変換
    
    Args:
        year: 西暦年
    
    Returns:
        和暦表記（例: "令和7年"）
    
    Examples:
        >>> to_wareki(2025)
        '令和7年'
    """
    if year >= 2019:
        return f"令和{year - 2018}年"
    elif year >= 1989:
        return f"平成{year - 1988}年"
    elif year >= 1926:
        return f"昭和{year - 1925}年"
    else:
        return f"{year}年"
```

**成功基準:**
- ✓ すべてのテストがパス
- ✓ エッジケース対応（閏年、和暦境界等）

---

### Task 3.6: life_insuranceへの適用 ⏱️ 3-4時間
**優先度:** 🟠 高

#### 実装内容
1. **`InsuranceValueCalculator` の継承変更**
   ```python
   # Before
   class InsuranceValueCalculator:
       ...
   
   # After
   from common.calculators.base_calculator import (
       BaseFinancialCalculator, 
       CompoundInterestMixin
   )
   
   class InsuranceValueCalculator(BaseFinancialCalculator, CompoundInterestMixin):
       ...
   ```

2. **共通ユーティリティの利用**
   - `math_utils` の関数を利用
   - `date_utils` の関数を利用
   - 重複コードの削除

3. **テスト更新**
   - 既存テスト（88件）が全パスすることを確認
   - 新しい継承構造でのテスト追加

**成功基準:**
- ✓ 既存テスト88件が全パス
- ✓ 計算結果が変更前と一致
- ✓ インポートエラーなし

---

### Task 3.7: pension_calcへの適用 ⏱️ 4-5時間
**優先度:** 🟠 高

#### 実装内容
1. **pension_calcでの共通基盤利用**
   - `pension_utils.py` で共通ユーティリティを利用
   - 重複している複利計算等を共通化

2. **テスト作成**
   - `tests/test_pension_utils_with_common.py` 作成
   - 共通基盤利用後の計算テスト（15ケース）

**成功基準:**
- ✓ pension_calcのテストが全パス
- ✓ 計算結果が変更前と一致
- ✓ Streamlitアプリが正常起動

---

### Task 3.8: レガシーテスト更新 ⏱️ 5-6時間
**優先度:** 🟠 高

#### 背景
Phase 2完了時点で29件のレガシーテストが失敗（旧API依存）

#### 実装内容
1. **test_deduction.py 更新（7件失敗）**
   - 新APIに対応した関数呼び出しに変更
   - 期待値の更新（必要に応じて）

2. **test_optimizer.py 更新（13件失敗）**
   - 新APIに対応した関数呼び出しに変更
   - データ構造の変更に対応

3. **test_tax.py 更新（9件失敗）**
   - 新APIに対応した関数呼び出しに変更
   - 期待値の更新

**成功基準:**
- ✓ すべてのレガシーテストが更新される
- ✓ 29件すべてがパスする
- ✓ 既存の動作が保証される

**実装ガイドライン:**
```python
# Before (旧API)
result = _calculate_partial_withdrawal_value(...)

# After (新API)
from life_insurance.models import InsurancePlan, FundPlan
from life_insurance.analysis.insurance_calculator import InsuranceValueCalculator

calculator = InsuranceValueCalculator()
result = calculator.calculate_partial_withdrawal(
    insurance_plan=InsurancePlan(...),
    fund_plan=FundPlan(...),
    ...
)
```

---

### Task 3.9: Phase 3完了確認 ⏱️ 2-3時間
**優先度:** 🔴 最高

#### 実施内容
1. **全テスト実行**
   ```powershell
   pytest life_insurance/tests/ -v
   pytest pension_calc/tests/ -v  # 存在する場合
   pytest common/tests/ -v
   ```

2. **コードカバレッジ確認**
   ```powershell
   pytest --cov=common --cov=life_insurance --cov=pension_calc --cov-report=html
   ```
   - 目標: 80%以上

3. **ドキュメント作成**
   - `REFACTORING/PHASE_3/PROGRESS.md`
   - `REFACTORING/PHASE_3/COMPLETION_REPORT.md`

4. **Git処理**
   ```powershell
   git add -A
   git commit -m "feat(common): Phase 3完了 - 共通基盤構築"
   git tag -a v0.5.0-phase3-complete -m "Phase 3完了..."
   ```

**成功基準:**
- ✓ すべてのテストがパス（Phase 1+2+3で142件以上）
- ✓ カバレッジ80%以上
- ✓ ドキュメント完備
- ✓ Gitコミット・タグ完了

---

## 📊 進捗トラッキング

### 週次目標

#### Week 1（2025-01-10～01-16）
- [ ] Task 3.1: ディレクトリ構造作成
- [ ] Task 3.2: BaseFinancialCalculator実装
- [ ] Task 3.3: FinancialPlan基底クラス実装

**目標:** 共通基盤の基礎構築完了

#### Week 2（2025-01-17～01-23）
- [ ] Task 3.4: 数学ユーティリティ実装
- [ ] Task 3.5: 日付ユーティリティ実装

**目標:** ユーティリティ層完成

#### Week 3（2025-01-24～01-30）
- [ ] Task 3.6: life_insuranceへの適用
- [ ] Task 3.7: pension_calcへの適用

**目標:** 既存モジュールへの統合完了

#### Week 4（2025-01-31～02-06）
- [ ] Task 3.8: レガシーテスト更新
- [ ] Task 3.9: Phase 3完了確認

**目標:** Phase 3完了

---

## 🎯 成功基準（Phase 3全体）

### 必須基準
1. ✅ **テスト成功率100%**
   - Phase 1テスト: 25件全パス
   - Phase 2テスト: 88件全パス
   - Phase 3新規テスト: 30件以上全パス
   - レガシーテスト: 29件全パス
   - **合計:** 172件以上全パス

2. ✅ **コード品質**
   - 型ヒント完備（mypy検証）
   - docstring充実
   - カバレッジ80%以上

3. ✅ **機能保証**
   - life_insurance Streamlitアプリ正常起動
   - pension_calc Streamlitアプリ正常起動
   - 計算結果が変更前と一致

4. ✅ **ドキュメント**
   - PROGRESS.md作成
   - COMPLETION_REPORT.md作成
   - 各関数のdocstring完備

### 期待効果
- **コード削減:** ~200行
- **重複削減:** 共通ロジックの一元化
- **保守性向上:** 共通基盤による統一されたAPI
- **拡張性向上:** 新機能追加の容易化

---

## ⚠️ リスク管理

### 潜在的リスク

1. **既存機能への影響**
   - リスク: 共通化により既存コードが動作不良
   - 対策: 各タスク後に必ずテスト実行、段階的実装

2. **依存関係の複雑化**
   - リスク: common/への依存が増えて管理が困難
   - 対策: 明確なインターフェース設計、循環依存の回避

3. **テスト更新の遅延**
   - リスク: レガシーテスト29件の更新に時間がかかる
   - 対策: Task 3.8を優先、段階的に更新

### 緊急時対応

**問題が発生した場合:**
1. 直前のGitコミットに戻す
2. 問題の切り分け（テスト実行、ログ確認）
3. 小さな単位で再実装
4. 必要に応じてTask順序の見直し

**ロールバック手順:**
```powershell
# Phase 2の安定版に戻す
git checkout v0.4.0-phase2-complete

# または直前のコミットに戻す
git reset --hard HEAD~1
```

---

## 📝 メモ・補足

### 実装時の注意点

1. **インポート順序**
   ```python
   # 標準ライブラリ
   from abc import ABC, abstractmethod
   from dataclasses import dataclass
   from typing import Optional, List
   
   # サードパーティ
   import numpy as np
   import pandas as pd
   
   # プロジェクト内（common）
   from common.calculators.base_calculator import BaseFinancialCalculator
   from common.utils.math_utils import calculate_compound_interest
   
   # プロジェクト内（他モジュール）
   from life_insurance.models import InsurancePlan
   ```

2. **命名規約**
   - クラス: PascalCase（例: `BaseFinancialCalculator`）
   - 関数: snake_case（例: `calculate_compound_interest`）
   - 定数: UPPER_SNAKE_CASE（例: `DEFAULT_RATE`）
   - プライベート: `_private_method`

3. **型ヒント**
   ```python
   from typing import Optional, List, Dict, Any
   
   def calculate(
       amount: float,
       rate: float,
       years: int,
       options: Optional[Dict[str, Any]] = None
   ) -> Dict[str, float]:
       ...
   ```

4. **docstring形式（Google Style）**
   ```python
   def function_name(param1: int, param2: str) -> bool:
       """関数の概要（1行）
       
       詳細説明（複数行可）
       
       Args:
           param1: パラメータ1の説明
           param2: パラメータ2の説明
       
       Returns:
           戻り値の説明
       
       Raises:
           ValueError: エラー条件の説明
       
       Examples:
           >>> function_name(10, "test")
           True
       """
       ...
   ```

---

## 🔗 関連ドキュメント

- [REFACTORING/README.md](../README.md) - リファクタリング全体概要
- [REFACTORING/MASTER_PLAN.md](../MASTER_PLAN.md) - マスタープラン
- [REFACTORING/PHASE_2/COMPLETION_REPORT.md](../PHASE_2/COMPLETION_REPORT.md) - Phase 2完了レポート
- [life_insurance/models/__init__.py](../../life_insurance/models/__init__.py) - Phase 2データクラス
- [life_insurance/analysis/insurance_calculator.py](../../life_insurance/analysis/insurance_calculator.py) - Phase 2計算エンジン

---

**最終更新:** 2025-01-10  
**次のマイルストーン:** Task 3.1完了（ディレクトリ構造作成）
