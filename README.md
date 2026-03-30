# 金融分析ツール統合プロジェクト

[![CI/CD Pipeline](https://github.com/MatsuoTom/my-project/actions/workflows/ci.yml/badge.svg)](https://github.com/MatsuoTom/my-project/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

生命保険分析、年金シミュレーション、投資シミュレーション、車両維持費計画を統合した Python プロジェクトです。

## プロジェクト構成（現行）

```text
my-project/
├── common/                      # 共通基盤
│   ├── calculators/
│   ├── models/
│   ├── utils/
│   └── tests/
├── life_insurance/              # 生命保険分析
│   ├── analysis/
│   ├── core/
│   ├── models/
│   ├── ui/
│   ├── utils/
│   └── tests/
├── pension_calc/                # 年金シミュレーション
│   ├── analysis/
│   ├── core/
│   ├── data/
│   └── ui/
├── investment_simulation/       # 投資シミュレーション
│   ├── analysis/
│   ├── core/
│   ├── data/
│   ├── ui/
│   └── tests/
├── vehicle_finance/             # 車両維持費計画
│   ├── core/
│   ├── data/
│   ├── ui/
│   └── tests/
├── tests/                       # ルート統合テスト
├── scripts/                     # 起動スクリプト群
├── docs/                        # 開発/運用ドキュメント
├── REFACTORING/                 # フェーズ別リファクタ記録
├── main.py                      # 統合ランチャー
├── pyproject.toml               # 依存関係・pytest・coverage設定
└── run_tests.ps1                # テスト実行補助
```

## クイックスタート

### 1) 仮想環境の有効化（Windows PowerShell）

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) 依存関係のインストール

```bash
pip install -e .
```

### 3) 統合ランチャー起動（推奨）

```bash
python main.py
```

## 個別起動

```bash
python scripts/run_life_insurance_app.py
python scripts/run_pension_app.py
python scripts/run_investment_app.py
python scripts/run_vehicle_app.py
```

または直接 Streamlit 実行:

```bash
streamlit run life_insurance/ui/streamlit_app.py --server.port=8507
streamlit run pension_calc/ui/streamlit_app.py --server.port=8508
streamlit run investment_simulation/ui/streamlit_app.py --server.port=8512
streamlit run vehicle_finance/ui/streamlit_app.py --server.port=8509
```

## 実行導線の役割分担

- `main.py`: 利用者向けの統合ランチャーです。複数アプリの入口を一本化します。
- `scripts/`: 個別アプリや補助スクリプトの直接起動用です。開発・検証時に使います。
- `README.md` と `docs/` を実行コマンドの正本とし、古い手順は更新または参照化します。

## テスト実行

### 全体

```bash
pytest
```

### 主な対象ディレクトリ

```bash
pytest common/tests life_insurance/tests investment_simulation/tests vehicle_finance/tests tests -v
```

### カバレッジ

```bash
pytest --cov=common --cov=life_insurance --cov=pension_calc --cov=investment_simulation --cov=vehicle_finance --cov-report=term-missing
```

## 開発メモ

- pytest の探索パスは pyproject.toml の tool.pytest.ini_options.testpaths を参照します。
- カバレッジ対象は pyproject.toml の tool.coverage.run.source を参照します。
- pension_calc は現時点で専用 tests ディレクトリを持たないため、主にルート tests から検証しています。
- vehicle_finance/data/saved_plans はローカル実行データのため Git 追跡対象外で運用します。

## ドキュメント運用（Phase 3）

- 現行の仕様・運用ガイドは `docs/` を正本とします。
- フェーズ実施時の計画・履歴は `REFACTORING/` を参照します。
- 旧版や退避資料は `archive/` を参照します。
- 配置ルールの詳細は `docs/DOCUMENTATION_STRUCTURE.md` を参照してください。
- docs の入口は `docs/INDEX.md` を参照してください。
