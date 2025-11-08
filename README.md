# 金融分析ツール統合プロジェクト

[![CI/CD Pipeline](https://github.com/MatsuoTom/my-project/actions/workflows/ci.yml/badge.svg)](https://github.com/MatsuoTom/my-project/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: Private](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)

このプロジェクトは、生命保険分析・年金シミュレーション・投資シミュレーションを統合した金融分析ツールです。Phase 3-5のリファクタリングにより、共通基盤を構築し、高品質なテスト環境とCI/CDパイプラインを整備しました。

## � プロジェクトの特徴

### 🎯 統合された3つのツール

1. **生命保険分析ツール**: 旧生命保険料控除の節税効果分析
2. **年金シミュレーター**: 国民年金・厚生年金の受給額試算
3. **投資シミュレーター**: NISA・投資信託の分析（開発中）

### ✅ 高品質な開発基盤（Phase 3-5完了）

- **286件のテスト**: 95.8%パス（2.34秒で実行）
- **CI/CDパイプライン**: GitHub Actions（9環境マトリックステスト）
- **コード品質管理**: Black自動フォーマット、flake8、mypy
- **テストカバレッジ**: 65.16%測定
- **共通基盤**: 重複コードを削減し、保守性を向上
- **テスト駆動開発**: TDD原則に基づく堅牢な設計

## 🏗️ プロジェクト構造

```
my-project/
├── common/                      # 共通基盤（Phase 3で作成）
│   ├── base_calculator.py       # 基底計算機クラス
│   ├── date_utils.py            # 日付・年齢・和暦ユーティリティ
│   ├── math_utils.py            # 金融計算ユーティリティ
│   ├── financial_plan.py        # FinancialPlanモデル
│   └── tests/                   # 共通基盤のテスト（163件）
│
├── life_insurance/              # 生命保険分析
│   ├── core/                    # コア計算機能
│   │   ├── tax_calculator.py    # 税額計算
│   │   └── deduction_calculator.py # 控除計算
│   ├── analysis/                # 分析ロジック
│   │   ├── scenario_analyzer.py # シナリオ分析
│   │   ├── withdrawal_optimizer.py # 引き出し最適化
│   │   └── insurance_calculator.py # 保険計算機
│   ├── ui/                      # Streamlitアプリ
│   │   ├── streamlit_app.py     # メインアプリ
│   │   └── comparison_app.py    # 比較分析
│   ├── models.py                # データモデル
│   └── tests/                   # テスト（107件）
│
├── pension_calc/                # 年金シミュレーション
│   ├── core/                    # コア計算機能
│   │   └── pension_utils.py     # 年金計算ユーティリティ
│   ├── analysis/                # 分析ロジック
│   │   └── national_pension.py  # 国民年金分析
│   ├── ui/                      # Streamlitアプリ
│   │   └── streamlit_app.py     # 年金分析アプリ
│   └── data/                    # データファイル
│
├── investment_simulation/       # 投資シミュレーション（開発中）
│   ├── core/                    # コア機能
│   ├── ui/                      # Streamlitアプリ
│   └── data/                    # データファイル
│
├── tests/                       # 統合テスト（13件）
│   └── test_pension_calculator_integration.py
│
├── REFACTORING/                 # リファクタリングドキュメント
│   ├── PHASE_3/                 # Phase 3: 共通基盤構築
│   └── PHASE_4/                 # Phase 4: レガシーテスト対応
│
├── main.py                      # 統合ランチャー
├── pyproject.toml               # 依存関係管理
└── README.md                    # このファイル
```

## 🚀 クイックスタート

### 統合ランチャーを使用（推奨）

```bash
python main.py
```

対話型メニューから使いたいツールを選択できます。

### 個別起動

#### 生命保険分析ツール

```bash
python run_life_insurance_app.py
# または
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501
```

#### 年金シミュレーションツール

```bash
python run_pension_app.py
# または
streamlit run pension_calc/ui/streamlit_app.py --server.port=8502
```

#### 投資シミュレーションツール（開発中）

```bash
# 実装予定
```

## 🌐 Streamlit Cloud デプロイ（オプション）

### デプロイ可能なアプリ

このプロジェクトのStreamlitアプリは、Streamlit Cloudに無料でデプロイできます：

1. **生命保険分析ツール**: `life_insurance/ui/streamlit_app.py`
2. **年金シミュレーター**: `pension_calc/ui/streamlit_app.py`
3. **投資シミュレーター**: `investment_simulation/ui/streamlit_app.py`（開発中）

### クイックデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud) にサインアップ
2. GitHubリポジトリと連携
3. 各アプリのメインファイルパスを指定してデプロイ

詳細な手順は [`REFACTORING/PHASE_5/STREAMLIT_DEPLOY_GUIDE.md`](REFACTORING/PHASE_5/STREAMLIT_DEPLOY_GUIDE.md) を参照してください。

### デプロイ済みURL（例）

デプロイ後、以下のようなURLが利用可能になります：

- **生命保険分析**: `https://my-project-life-insurance.streamlit.app`（デプロイ後に設定）
- **年金シミュレーター**: `https://my-project-pension.streamlit.app`（デプロイ後に設定）

## 📊 主な機能

### 生命保険分析ツール

- **生命保険料控除分析**: 旧生命保険料控除制度の節税効果計算
- **投資信託比較**: 生命保険と投資信託の収益性比較
- **引き出しタイミング最適化**: 部分解約戦略の自動提案
- **詳細シミュレーション**: 手数料・税金を考慮した実損益計算
- **シナリオ分析**: 複数条件下での比較検討
- **リスク分析**: モンテカルロシミュレーション

### 年金シミュレーションツール

- **年金試算**: 国民年金・厚生年金の受給額計算
- **納付実績分析**: 過去の納付状況の可視化
- **損益分析**: 納付額と受給額の比較
- **将来予測**: キャリアモデル別の年金シミュレーション
- **最適化分析**: 最適な受給開始年齢の算出
- **データ永続化**: CSV形式での実績データ管理

### 投資シミュレーションツール（開発中）

- NISA投資シミュレーション
- 銘柄マスタ管理
- 月次投資データ入力
- 投資分析（実装予定）

## 🛠️ 開発環境セットアップ

### 必要な環境

- **Python**: 3.12以上
- **推奨IDE**: VS Code
- **OS**: Windows / macOS / Linux

### 依存パッケージのインストール

```bash
# 基本パッケージ
pip install streamlit pandas plotly numpy matplotlib seaborn

# 追加パッケージ
pip install openpyxl yfinance

# または pyproject.toml から一括インストール
pip install -e .
```

### 仮想環境の使用（推奨）

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境の有効化
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# 依存関係インストール
pip install streamlit pandas plotly numpy matplotlib seaborn openpyxl yfinance
```

## 🧪 テスト実行

### 全体テスト（推奨）

```bash
# 全テスト実行（286件、2.34秒）
pytest common/tests/ tests/ life_insurance/tests/ -v

# 簡潔な出力
pytest common/tests/ tests/ life_insurance/tests/ -q

# カバレッジ測定
pytest common/tests/ tests/ life_insurance/tests/ --cov=common --cov=life_insurance --cov=pension_calc --cov-report=term-missing
```

### CI/CD環境（GitHub Actions）

- **マトリックステスト**: Ubuntu, Windows, macOS × Python 3.10, 3.11, 3.12 = 9環境
- **コード品質チェック**: flake8, black, mypy
- **テストカバレッジ**: 65.16%（common: 98%, life_insurance: 76%, pension_calc: 22%）
- **自動実行**: プッシュ・プルリクエスト時に自動テスト

### テスト構成

| カテゴリ | テスト数 | 説明 |
|---------|---------|------|
| **common/tests/** | 163件 | 共通基盤のテスト |
| - test_base_calculator.py | 28件 | 基底計算機クラス |
| - test_date_utils.py | 55件 | 日付・年齢ユーティリティ |
| - test_financial_plan.py | 26件 | FinancialPlanモデル |
| - test_math_utils.py | 54件 | 金融計算ユーティリティ |
| **tests/** | 16件 | 統合テスト |
| - test_pension_calculator_integration.py | 13件 | 年金計算統合テスト |
| - test_pension_utils.py | 3件 | 年金計算ユーティリティ |
| **life_insurance/tests/** | 107件 | 生命保険分析テスト |
| - test_deduction.py | 11件 | 控除計算 |
| - test_tax.py | 11件 | 税金計算 |
| - test_insurance_calculator_core.py | 22件 | 保険計算機コア |
| - test_models.py | 42件 | データモデル |
| - test_tax_helpers.py | 21件 | 税金ヘルパー |
| **合計** | **286件** | **274 passed, 10 failed, 2 skipped** |

### 個別プロジェクトのテスト

```bash
# 共通基盤のテスト
pytest common/tests/ -v

# 生命保険分析のテスト
pytest life_insurance/tests/ -v

# 年金計算統合テスト
pytest tests/test_pension_calculator_integration.py -v
```

## 💡 使用方法

### 1. 統合ランチャーから起動

```bash
python main.py
```

対話型メニューから使いたいツールを選択します。

### 2. 個別プロジェクトの直接起動

各プロジェクトを個別に起動することも可能です：

```bash
# 生命保険分析
python run_life_insurance_app.py

# 年金シミュレーション
python run_pension_app.py
```

### 3. ポート設定

複数のStreamlitアプリを同時に起動する場合は、異なるポートを指定してください：

```bash
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501
streamlit run pension_calc/ui/streamlit_app.py --server.port=8502
```

### 4. 比較アプリ（オプション）

```bash
streamlit run life_insurance/ui/comparison_app.py --server.port=8510
```

## 📈 主な計算機能

### 共通基盤（Phase 3で作成）

- **複利計算**: 現在価値・将来価値・複利現価・複利終価
- **年金計算**: 年金終価・年金現価（前払・後払）
- **IRR/NPV計算**: 内部収益率・正味現在価値
- **日付・年齢計算**: 和暦変換・年齢計算・経過月数計算
- **税金計算**: 所得税・住民税（累進課税対応）

### 生命保険分析

- 生命保険料控除額計算（旧制度）
- 実質利回り計算
- 部分解約シミュレーション
- 投資信託との比較分析
- シナリオ分析
- モンテカルロシミュレーション

### 年金計算

- 国民年金・厚生年金の受給額計算
- 納付月数・金額の管理
- 将来受給額の予測
- 損益分岐点分析
- キャリアモデル連携
- 最適受給開始年齢の算出

## 🔧 カスタマイズ



## 🧪 テスト実行## 📄 ライセンス



```bashこのプロジェクトは個人利用目的で作成されています。

# 全体テスト

python -m pytest tests/## 🤝 コントリビューション



# 個別プロジェクトのテスト改善提案やバグ報告は歓迎します。

python -m pytest life_insurance/tests/

python -m pytest pension_calc/tests/## 📞 サポート

```

質問や問題がある場合は、各プロジェクトのコードコメントや計算ロジックを参照してください。
## 📈 主な計算機能

### 生命保険分析
- 生命保険料控除額計算
- 実質利回り計算
- 部分解約シミュレーション
- 投資信託との比較分析

### 年金計算（高度版）
- **基礎年金・厚生年金の詳細計算**: 調整率・報酬比例部分を考慮
- **キャリアモデル連携**: 年齢・役職・年収に基づく将来納付額予測
- **損益分岐点分析**: 累計納付額と累計受給額の詳細推移
- **最適化分析**: 生涯総受給額を最大化する受給開始年齢の算出
- **データ永続化**: CSV形式での実績データ管理

## 🔧 カスタマイズ

### キャリアモデルの調整

`pension_calc/core/pension_utils.py`の`get_career_model()`関数で、年齢・役職・年収の設定を変更可能。

### 計算パラメーターの変更

各プロジェクトの設定ファイルで、税率や手数料率などのパラメーターを調整できます。

### UIのカスタマイズ

Streamlitアプリのレイアウトや表示項目は、各`streamlit_app.py`ファイルで変更可能です。

## 📊 技術仕様

### アーキテクチャ（Phase 3-4で構築）

- **共通基盤**: 複数プロジェクト間でコードを共有
  - 基底計算機クラス（複利計算Mixin付き）
  - 日付・年齢・和暦ユーティリティ
  - 金融計算ユーティリティ（複利、年金、IRR、NPV）
  - FinancialPlanモデル

- **テスト駆動開発**: 283件のテスト（100%パス、2.13秒）
  - 共通基盤: 163件
  - 年金計算: 13件
  - 生命保険: 107件

- **高品質な設計**:
  - 公開APIをテスト（内部実装の詳細はテストしない）
  - 実装と期待値の統一
  - レガシーコードの削減

### 年金シミュレーター（高度版）の特徴

- **タブベースUI**: 6つの専門タブによる機能分離
- **リアルタイム計算**: パラメーター変更時の即座な再計算
- **データ永続化**: pandas DataFrameのCSV保存・読込
- **キャリアモデル**: 企業キャリアパスの標準化されたデータセット
- **高精度計算**: 厚生年金料率18.3%、調整率0.4%/0.7%を正確に適用

### 対応データ形式

- **入力**: CSV、Excel（.xlsx/.xls）
- **出力**: CSV、インタラクティブグラフ（Plotly）
- **データ構造**: 年度・年齢・加入制度・お勤め先・加入月数・納付額・推定年収

### パフォーマンス

- **テスト実行**: 2.13秒（283件）
- **Streamlitアプリ**: 1-5秒（初期表示 + 計算）
- **グラフ描画**: Plotlyによる高速レンダリング

## � ドキュメント

### プロジェクトドキュメント

- **README.md** (このファイル): プロジェクト概要とセットアップ
- **.github/copilot-instructions.md**: AI作業指示書（開発者向け）

### Phase 3: 共通基盤構築

- **REFACTORING/PHASE_3/IMPLEMENTATION_PLAN.md**: Phase 3実装計画
- **REFACTORING/PHASE_3/COMPLETION_REPORT.md**: Phase 3完了レポート
- **REFACTORING/COMMON_BASE_DESIGN.md**: 共通基盤の設計ドキュメント

### Phase 4: レガシーテスト対応

- **REFACTORING/PHASE_4/IMPLEMENTATION_PLAN.md**: Phase 4実装計画
- **REFACTORING/PHASE_4/COMPLETION_REPORT.md**: Phase 4完了レポート
- **REFACTORING/PHASE_4/UI_OPTIMIZATION_ANALYSIS.md**: UI最適化分析
- **REFACTORING/LEGACY_TESTS_PLAN.md**: レガシーテスト対応計画

## 🎓 開発の歴史

### Phase 1: プロジェクト基盤整備とTDD（2024年）

- 生命保険分析ツールの基礎開発
- 年金シミュレーターの基礎開発
- テスト駆動開発の導入

### Phase 2: コア機能の統合と基盤構築（2024年）

- 2つのプロジェクトを統合
- 統合ランチャーの作成
- 基本的な機能統合

### Phase 3: 共通基盤の作成（2025年10月）

- **目標**: 重複コードの削減、保守性向上
- **成果**: 
  - 共通基盤の構築（4モジュール）
  - 163件のテストを作成
  - 261件のテストが全パス

### Phase 4: レガシーテスト対応（2025年11月）

- **目標**: レガシーテスト29件の対応
- **成果**:
  - レガシーテスト29件 → 0件（100%解消）
  - 283件のテストが全パス（100%）
  - 実行時間: 2.13秒（高速）
  - 技術的負債削減: 不要なテスト41件を削除

### Phase 5: CI/CD構築（2025年11月）

- **目標**: 継続的インテグレーション・継続的デリバリーの構築
- **成果**:
  - GitHub Actions CI/CDパイプライン構築
  - 9環境マトリックステスト（3 OS × 3 Python）
  - テストカバレッジ測定（65.16%）
  - コード品質管理（Black、flake8、mypy）
  - コード品質改善: 1,591件 → 308件（80%削減）
  - README.mdにバッジ追加

## �📄 ライセンス

このプロジェクトは個人利用目的で作成されています。

## 🤝 コントリビューション

改善提案やバグ報告は歓迎します。

## 📞 サポート

質問や問題がある場合は、以下を参照してください：
- 各プロジェクトのコードコメント
- `📋 計算方法`タブの詳細説明（年金シミュレーター）
- `🛠️ 開発者情報`サイドバーでのデバッグ情報
- `REFACTORING/`ディレクトリ内のドキュメント

## 📝 データ編集の使い方

### 年金シミュレーター

1. 「💰 支払実績」タブでデータを直接編集
2. 「💾 保存」ボタンでCSVに永続化
3. 「📥 実績ファイルのインポート」でCSV/Excelファイルを取込

### 投資シミュレーター

1. 「月次データ管理」画面に移動
2. 編集テーブル（data_editor）でセルを直接修正
3. 「保存」ボタンまたは「更新」ボタンで保存
4. 変更内容は即座に反映され、グラフも自動更新

### データ形式

- CSV形式でのエクスポート・インポート
- Excel形式（.xlsx/.xls）の取込
- 一括登録の場合は、空欄以外の行のみ登録

---

**最終更新**: 2025年11月8日（Phase 5進行中）  
**バージョン**: v0.7.0-phase5-in-progress  
**テスト成功率**: 95.8%（274 passed, 10 failed, 2 skipped / 286件）  
**CI/CD**: [![CI Status](https://github.com/MatsuoTom/my-project/actions/workflows/ci.yml/badge.svg)](https://github.com/MatsuoTom/my-project/actions)
