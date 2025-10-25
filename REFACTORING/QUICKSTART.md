# 🎯 リファクタリング クイックスタートガイド

このガイドでは、リファクタリングプロジェクトを今すぐ開始する手順を説明します。

---

## ✅ 開始前のチェックリスト

- [ ] 既存のコードが正常に動作することを確認
- [ ] 仮想環境が有効化されている
- [ ] 必要なパッケージがインストールされている
- [ ] テストが実行可能

```bash
# 仮想環境の有効化
.\.venv\Scripts\Activate.ps1

# 既存テストの実行
pytest life_insurance/tests/ -v

# アプリの起動確認
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501
```

---

## 🚀 Phase 1を今すぐ始める

### ステップ 1: ディレクトリ作成

```powershell
# life_insurance/utils/ ディレクトリ作成
New-Item -ItemType Directory -Force -Path "life_insurance\utils"
New-Item -ItemType File -Force -Path "life_insurance\utils\__init__.py"
```

### ステップ 2: tax_helpers.py をコピー

```powershell
# テンプレートからコピー
Copy-Item "REFACTORING\PHASE_1\templates\tax_helpers.py" "life_insurance\utils\tax_helpers.py"
```

または、手動で作成:
1. `life_insurance/utils/tax_helpers.py` を作成
2. `REFACTORING/PHASE_1/templates/tax_helpers.py` の内容をコピー

### ステップ 3: テストファイルをコピー

```powershell
# テストファイルをコピー
Copy-Item "REFACTORING\PHASE_1\templates\test_tax_helpers.py" "life_insurance\tests\test_tax_helpers.py"
```

### ステップ 4: テスト実行

```bash
# 新しいテストを実行
pytest life_insurance/tests/test_tax_helpers.py -v

# すべてのテストを実行
pytest life_insurance/tests/ -v
```

### ステップ 5: 最初の置換を実施

`life_insurance/ui/streamlit_app.py` を開き、以下を追加:

```python
# インポート部分に追加（他のインポートの後）
from life_insurance.utils.tax_helpers import get_tax_helper
```

最初の置換箇所（行102付近）:

**置換前:**
```python
calculator = LifeInsuranceDeductionCalculator()
quick_deduction = calculator.calculate_old_deduction(quick_premium)
tax_calc = TaxCalculator()
tax_result = tax_calc.calculate_tax_savings(quick_deduction, 5000000)
annual_tax_savings = tax_result["合計節税額"]
```

**置換後:**
```python
tax_helper = get_tax_helper()
tax_result = tax_helper.calculate_annual_tax_savings(quick_premium, 5000000)
annual_tax_savings = tax_result['total_savings']
```

### ステップ 6: 動作確認

```bash
# アプリを起動
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501

# ブラウザで動作確認
# - ホームページが正常に表示される
# - 計算結果が正しい
```

### ステップ 7: コミット

```bash
git add life_insurance/utils/
git add life_insurance/tests/test_tax_helpers.py
git add life_insurance/ui/streamlit_app.py
git commit -m "feat: Phase 1開始 - 税金ヘルパー追加（1/30箇所置換）"
```

---

## 📝 次のステップ

1. `REFACTORING/PHASE_1/TASKS.md` を開く
2. タスク1.2の残りの置換箇所を順次実施
3. 10箇所ごとにテスト実行とコミット
4. 全30箇所完了後、Phase 1を完了としてマーク

---

## 🆘 トラブルシューティング

### インポートエラー
```
ModuleNotFoundError: No module named 'life_insurance.utils'
```

**解決策:**
```bash
# __init__.py が存在するか確認
ls life_insurance/utils/__init__.py

# プロジェクトルートから実行しているか確認
pwd  # my-project ディレクトリであるべき
```

### テストエラー
```
ImportError: cannot import name 'get_tax_helper'
```

**解決策:**
- `tax_helpers.py` が正しくコピーされているか確認
- ファイルの内容が完全であるか確認

### 計算結果の不一致
```
AssertionError: Expected 12500, got 12000
```

**解決策:**
- 辞書のキー名を確認: `tax_result['total_savings']`
- 元のコードで使っていた `["合計節税額"]` を `['total_savings']` に変更

---

## 📚 参考ドキュメント

- [Phase 1 詳細タスク](./PHASE_1/TASKS.md)
- [マスタープラン](./MASTER_PLAN.md)
- [進捗トラッキング](./PROGRESS.md)

---

**今すぐ始めましょう！** 🚀

最初のステップは小さく、安全です。1箇所ずつ確実に進めていきましょう。
