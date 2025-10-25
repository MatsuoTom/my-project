# 金融分析プロジェクト

日本の年金制度と生命保険料控除の包括的な分析ツールセット

## 📁 プロジェクト構成

### 🏛️ **pension_calc/** - 年金分析システム
日本の年金制度（国民年金・厚生年金）の包括的な分析機能
```
pension_calc/
├── core/               # 年金計算エンジン
│   └── pension_utils.py    # 年金データと計算ユーティリティ
├── analysis/           # 年金分析機能
│   └── national_pension.py # 国民年金分析
├── ui/                 # 年金分析UI
│   ├── streamlit_app.py    # メインStreamlitアプリ
│   └── streamlit_app_backup.py
├── data/               # 年金データ
└── __init__.py
```

### 💰 **life_insurance/** - 生命保険料控除分析システム
旧生命保険料控除制度の節税効果と最適化分析機能
```
life_insurance/
├── core/               # 控除計算エンジン  
│   ├── deduction_calculator.py # 控除額計算
│   └── tax_calculator.py       # 税額・節税計算
├── analysis/           # 高度分析機能
│   ├── withdrawal_optimizer.py # 引き出しタイミング最適化
│   └── scenario_analyzer.py    # シナリオ・感度分析
├── ui/                 # WebアプリUI
│   └── streamlit_app.py        # インタラクティブWebアプリ
├── tests/              # テストスイート
└── __init__.py
```

### 🔧 **共通ファイル**
```
├── run_pension_app.py           # 年金アプリ起動スクリプト
├── run_life_insurance_app.py    # 生命保険料控除アプリ起動スクリプト
├── test_life_insurance_modules.py # 生命保険料控除モジュール統合テスト
├── main.py                      # プロジェクトエントリーポイント
├── pyproject.toml              # 依存関係管理
└── README.md                   # プロジェクト説明書
```

## 🚀 使用方法

### 年金分析システム
```bash
# 仮想環境有効化
.\.venv\Scripts\Activate.ps1

# 年金分析アプリ起動
python run_pension_app.py
```

### 生命保険料控除分析システム
```bash
# 仮想環境有効化  
.\.venv\Scripts\Activate.ps1

# 生命保険料控除分析アプリ起動
python run_life_insurance_app.py
```

## 📊 主要機能

### 年金分析システム
- 国民年金・厚生年金の加入履歴管理
- 将来年金受給額の予測計算
- 加入期間・納付額の最適化提案
- 年金制度の比較分析

### 生命保険料控除分析システム
- **基本控除計算**: 旧生命保険料控除額の正確な算出
- **節税効果分析**: 所得税・住民税の具体的な節税額計算  
- **引き出しタイミング最適化**: 解約返戻金を含む総合的な利益最大化
- **シナリオ分析**: 所得・保険料・運用利回りの包括的比較
- **感度分析**: パラメータ変動による影響度評価
- **リスク分析**: モンテカルロシミュレーション対応
- **インタラクティブUI**: Webベースの直感的操作環境

## 💡 分析例

### 生命保険料控除（年間保険料10万円、課税所得500万円の場合）
- **控除額**: 35,000円
- **年間節税効果**: 約15,200円  
- **最適引き出し**: 15年後
- **期待純利益**: 約42万円
- **実質利回り**: 1.67%

## 🛠️ 技術スタック
- **言語**: Python 3.12+
- **UI**: Streamlit
- **データ処理**: pandas, numpy  
- **可視化**: matplotlib, plotly, seaborn
- **金融データ**: yfinance
- **依存関係管理**: uv, pip

## 📋 開発・保守

### テスト実行
```bash
# 生命保険料控除モジュールテスト
python test_life_insurance_modules.py

# 年金モジュールテスト
python tests/test_pension_utils.py
```

### 新機能追加
各システムは独立しているため、相互に影響することなく機能拡張が可能です。

## 📞 サポート
- 年金分析に関する質問: `pension_calc/` 関連
- 生命保険料控除に関する質問: `life_insurance/` 関連  
- 共通基盤に関する質問: プロジェクトルート関連

---

**注意**: このツールは分析・参考用です。実際の金融判断は専門家にご相談ください。
