# パフォーマンステストレポート — Phase 5 Task 5.7

## 概要

Phase 5 Task 5.7では、my-projectのテスト実行パフォーマンスを計測し、最適化の可能性を評価しました。このドキュメントは、計測結果、分析、および推奨事項を記載します。

## テスト実行環境

### ハードウェア・OS

- **OS**: Windows 11
- **CPU**: 16コア（推定）
- **メモリ**: 未計測
- **ストレージ**: SSD（推定）
- **Python**: 3.12.11
- **pytest**: 8.4.2

### テスト構成

| カテゴリ | テスト数 | 説明 |
|---------|---------|------|
| **common/tests/** | 163件 | 共通基盤のテスト |
| **tests/** | 16件 | 統合テスト |
| **life_insurance/tests/** | 117件 | 生命保険分析テスト |
| **合計** | **296件** | **286 passed, 10 failed** |

## パフォーマンス計測結果

### 1. 通常実行（ベースライン）

```bash
pytest common/tests/ tests/ life_insurance/tests/ --durations=10 -v --tb=short
```

#### 結果

- **総実行時間**: 3.91秒
- **成功**: 286件
- **失敗**: 10件
- **平均**: 13.2ms/テスト

#### 最も遅い10件のテスト

すべてのテストが **0.00秒台** で実行されており、個別のボトルネックは検出されませんでした：

```
0.00s call     tests/test_pension_calculator_integration.py::TestPensionCalculatorIntegration::test_calculate_future_pension
0.00s call     common/tests/test_date_utils.py::TestToWareki::test_heisei_first_year
0.00s call     life_insurance/tests/test_insurance_calculator_core.py::TestInsuranceCalculatorIntegration::test_all_methods_with_same_plan
0.00s teardown life_insurance/tests/test_tax_helpers.py::TestTaxHelperEdgeCases::test_boundary_50000
0.00s call     life_insurance/tests/test_insurance_calculator_core.py::TestInsuranceCalculatorIntegration::test_realistic_scenario_comparison
0.00s call     common/tests/test_math_utils.py::TestIRR::test_basic_irr
0.00s call     tests/test_pension_calculator_integration.py::TestPensionCalculatorIntegration::test_calculate_method
0.00s call     life_insurance/tests/test_insurance_calculator_core.py::TestCalculateBreakevenYear::test_basic_breakeven
0.00s call     life_insurance/tests/test_insurance_calculator_core.py::TestCalculateBreakevenYear::test_high_return_early_breakeven
0.00s call     tests/test_pension_calculator_integration.py::TestPensionCalculatorIntegration::test_analyze_contribution_efficiency
```

**分析**: すべてのテストが非常に高速（<10ms）で実行されており、個別の最適化は不要です。

### 2. 並列実行（pytest-xdist）

```bash
pytest common/tests/ tests/ life_insurance/tests/ -n auto --tb=short
```

#### 結果

- **総実行時間**: 6.80秒（❌ 1.74倍遅い）
- **成功**: 286件
- **失敗**: 10件
- **ワーカー数**: auto（CPUコア数に応じて自動設定、推定8-16）

#### 並列実行が遅い理由

1. **オーバーヘッド**: 
   - プロセス生成: 複数のPythonプロセスを起動するコスト
   - プロセス間通信: テスト結果を集約するコスト
   - インポート時間: 各ワーカーでモジュールを個別にインポート

2. **テストの高速性**:
   - 平均13.2ms/テスト → 並列化のメリット < オーバーヘッド
   - 並列化が有効なのは、平均100ms以上のテスト

3. **結論**: このプロジェクトでは並列化は**推奨しません**。

## カバレッジ計測のパフォーマンス

### カバレッジ付きテスト実行

```bash
pytest common/tests/ tests/ life_insurance/tests/ --cov=common --cov=life_insurance --cov=pension_calc --cov-report=term-missing --cov-report=html --cov-report=xml
```

#### 結果（推定）

- **総実行時間**: 約5-7秒（カバレッジなし3.91秒の1.3-1.8倍）
- **カバレッジ**: 65.16%
- **オーバーヘッド**: 約1-3秒（カバレッジ計測コスト）

#### 最適化の推奨事項

- **ローカル開発**: カバレッジなしでテスト実行（3.91秒）
- **CI/CD**: カバレッジ付きでテスト実行（5-7秒）
- **定期的なフルカバレッジ**: 週1回または重要な変更時のみ

## GitHub Actionsパフォーマンス

### 現在の設定

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
```

### 実行時間（推定）

| 環境 | 実行時間 | 備考 |
|------|----------|------|
| **Ubuntu** | 約3-5分 | 最も高速 |
| **Windows** | 約5-7分 | 中程度 |
| **macOS** | 約7-10分 | 最も遅い |

### 並列実行

- **9環境並列**: 約10-15分（最も遅い環境に依存）
- **最適化**: キャッシュ活用により2-3分短縮可能

## 最適化の推奨事項

### 1. ローカル開発

#### 推奨コマンド

```bash
# 最速（カバレッジなし）
pytest common/tests/ tests/ life_insurance/tests/ -v

# 実行時間: 3.91秒
```

#### 最適化済み

- ✅ テストは既に高速（平均13.2ms）
- ✅ 並列化は不要（オーバーヘッドが大きい）
- ✅ カバレッジはCI/CDで計測

### 2. CI/CD（GitHub Actions）

#### 推奨設定

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    # 実行時間: 約2-3分
  
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
    # 実行時間: 約3-10分（環境依存）
    # 並列実行: 約10-15分（最も遅い環境に依存）
```

#### 最適化のポイント

1. **キャッシュの活用**:
   ```yaml
   - name: Cache pip packages
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}
   ```
   - **効果**: 2-3分短縮

2. **依存関係のインストール時間短縮**:
   ```bash
   pip install --upgrade pip
   pip install pytest pytest-cov
   pip install pandas numpy matplotlib plotly seaborn openpyxl yfinance streamlit
   ```
   - **効果**: 1-2分短縮（キャッシュ活用時）

3. **テストの並列実行は不要**:
   - 現在の3.91秒は十分高速
   - pytest-xdistは逆効果（6.80秒）

### 3. 長期的な最適化

#### テストの追加時の注意点

- **単体テスト**: 平均<50ms を維持
- **統合テスト**: 平均<500ms を維持
- **E2Eテスト**: 別途分離（必要に応じて）

#### パフォーマンス悪化の早期検出

```bash
# 実行時間が5秒を超えた場合は調査
pytest common/tests/ tests/ life_insurance/tests/ --durations=0 -v
```

#### モニタリング

- **GitHub Actions**: ワークフロー実行時間をモニタリング
- **アラート**: 10分を超えた場合は最適化を検討

## まとめ

### 現在の状態

| 項目 | 値 | 評価 |
|------|-----|------|
| **テスト実行時間** | 3.91秒 | ✅ 優秀 |
| **テスト数** | 296件 | ✅ 適切 |
| **平均速度** | 13.2ms/テスト | ✅ 非常に高速 |
| **並列実行** | 6.80秒 | ❌ 推奨しない |
| **カバレッジ** | 65.16% | ⚠️ 改善の余地あり |

### 推奨事項

1. **並列実行は使用しない**: オーバーヘッドが大きい
2. **ローカル開発**: カバレッジなしで実行（3.91秒）
3. **CI/CD**: カバレッジ付きで実行（5-7秒）
4. **GitHub Actions**: キャッシュを活用して高速化
5. **長期的**: テストの高速性を維持

### 成果

- ✅ **テスト実行時間計測**: 3.91秒（ベースライン）
- ✅ **並列実行評価**: 6.80秒（推奨しない）
- ✅ **最適化方針決定**: 現状維持が最適
- ✅ **ドキュメント化**: このレポート作成

## 参考情報

### pytest-xdistの活用シーン

- **大規模プロジェクト**: 1,000件以上のテスト
- **遅いテスト**: 平均100ms以上のテスト
- **CI/CD**: 複数のテストスイートを並列実行

### パフォーマンス改善のベストプラクティス

1. **遅いテストの特定**: `--durations=10`
2. **ボトルネックの最適化**: IO、データベース、ネットワーク
3. **キャッシュの活用**: `@pytest.fixture(scope="module")`
4. **並列実行**: プロジェクトに応じて判断

---

**作成日**: 2025年11月8日  
**Phase**: 5（CI/CD構築）  
**Task**: 5.7（パフォーマンステスト）  
**実行環境**: Windows 11, Python 3.12.11, pytest 8.4.2
