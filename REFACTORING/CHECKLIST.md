# 🎯 リファクタリングプロジェクト - 開始チェックリスト

このチェックリストを使って、リファクタリングを確実に開始しましょう。

---

## ✅ 準備完了確認

### 環境確認
- [ ] プロジェクトディレクトリに移動: `cd c:\Users\tomma\Documents\python-projects\my-project`
- [ ] 仮想環境が有効化されている: `.\.venv\Scripts\Activate.ps1`
- [ ] 必要なパッケージがインストールされている: `pip list | Select-String "streamlit|pandas|pytest"`

### 既存コードの確認
- [ ] 既存テストがパス: `pytest life_insurance/tests/ -v`
- [ ] アプリが起動する: `streamlit run life_insurance/ui/streamlit_app.py --server.port=8501`
- [ ] 計算が正しく動作する（手動確認）

### ドキュメント確認
- [ ] `REFACTORING/INDEX.md` を読んだ
- [ ] `REFACTORING/QUICKSTART.md` を読んだ
- [ ] `REFACTORING/PHASE_1/TASKS.md` を確認した

### バックアップ（推奨）
- [ ] 現在のコードをコミット: `git add .; git commit -m "refactor: Phase 1開始前のベースライン"`
- [ ] または、ブランチ作成: `git checkout -b refactor/phase-1`

---

## 🚀 Phase 1 - 最初の1時間

### ステップ 1: ディレクトリ作成（5分）

```powershell
# 実行するコマンド
New-Item -ItemType Directory -Force -Path "life_insurance\utils"
New-Item -ItemType File -Force -Path "life_insurance\utils\__init__.py"
```

**確認:**
- [ ] `life_insurance/utils/` ディレクトリが存在する
- [ ] `life_insurance/utils/__init__.py` ファイルが存在する

---

### ステップ 2: テンプレートファイルのコピー（5分）

#### 方法A: PowerShellでコピー

```powershell
Copy-Item "REFACTORING\PHASE_1\templates\tax_helpers.py" "life_insurance\utils\tax_helpers.py"
Copy-Item "REFACTORING\PHASE_1\templates\test_tax_helpers.py" "life_insurance\tests\test_tax_helpers.py"
```

#### 方法B: 手動コピー

1. `REFACTORING/PHASE_1/templates/tax_helpers.py` を開く
2. 内容を全コピー
3. `life_insurance/utils/tax_helpers.py` を作成して貼り付け
4. 同様に `test_tax_helpers.py` もコピー

**確認:**
- [ ] `life_insurance/utils/tax_helpers.py` が存在する
- [ ] `life_insurance/tests/test_tax_helpers.py` が存在する
- [ ] ファイルサイズが0バイトでない

---

### ステップ 3: テスト実行（5分）

```bash
# 新しいテストを実行
pytest life_insurance/tests/test_tax_helpers.py -v
```

**期待結果:**
```
==================== test session starts ====================
collected XX items

life_insurance/tests/test_tax_helpers.py::TestTaxDeductionHelper::test_calculate_annual_tax_savings_basic PASSED
...
==================== XX passed in X.XXs ====================
```

**確認:**
- [ ] すべてのテストがPASSED
- [ ] エラーがない

**もしエラーが出たら:**
1. インポートエラー → `life_insurance/utils/__init__.py` が存在するか確認
2. その他のエラー → `REFACTORING/PHASE_1/TASKS.md` のトラブルシューティングを参照

---

### ステップ 4: 最初の置換（15分）

#### 4.1 インポート追加

`life_insurance/ui/streamlit_app.py` を開き、インポート部分（約19行目付近）に追加:

```python
from life_insurance.utils.tax_helpers import get_tax_helper
```

**確認:**
- [ ] インポート文を追加した

#### 4.2 最初の置換箇所を修正

約102行目付近の `show_home_page()` 関数内:

**置換前（約5行）:**
```python
calculator = LifeInsuranceDeductionCalculator()
quick_deduction = calculator.calculate_old_deduction(quick_premium)
tax_calc = TaxCalculator()
tax_result = tax_calc.calculate_tax_savings(quick_deduction, 5000000)
annual_tax_savings = tax_result["合計節税額"]
```

**置換後（3行）:**
```python
tax_helper = get_tax_helper()
tax_result = tax_helper.calculate_annual_tax_savings(quick_premium, 5000000)
annual_tax_savings = tax_result['total_savings']
```

**確認:**
- [ ] 置換を実施した
- [ ] ファイルを保存した

---

### ステップ 5: 動作確認（10分）

```bash
# テスト実行
pytest life_insurance/tests/ -v

# アプリ起動
streamlit run life_insurance/ui/streamlit_app.py --server.port=8501
```

**ブラウザで確認:**
- [ ] ホームページが正常に表示される
- [ ] クイック計算が動作する
- [ ] 結果が正しい（元と同じ）

---

### ステップ 6: 最初のコミット（5分）

```bash
git add life_insurance/utils/
git add life_insurance/tests/test_tax_helpers.py
git add life_insurance/ui/streamlit_app.py
git commit -m "feat: Phase 1開始 - 税金ヘルパー追加（1/30箇所置換）"
```

**確認:**
- [ ] コミット完了
- [ ] `git status` でクリーンな状態

---

## 🎉 最初の1時間完了！

おめでとうございます！以下を達成しました:

✅ 新しいヘルパーモジュールを追加  
✅ 包括的なテストスイートを作成  
✅ 最初の重複コードを削減  
✅ 既存機能が正常に動作することを確認  
✅ 変更を安全にコミット

**削減したコード:** 約2行（5行 → 3行）  
**残りの置換箇所:** 29箇所

---

## 📋 次のステップ

### 今週中に実施（推奨）

1. `REFACTORING/PHASE_1/TASKS.md` を開く
2. タスク1.2の残り9箇所（2-10番目）を置換
3. 10箇所完了後:
   - テスト実行
   - アプリ動作確認
   - コミット: `"refactor: Phase 1 - 税金計算共通化（1-10箇所）"`

### 来週以降

- 残りの20箇所を10箇所ずつ置換
- 各バッチ完了後にテストとコミット
- 全30箇所完了で Phase 1 完了

---

## 📊 進捗の記録

`REFACTORING/PROGRESS.md` を開いて、以下を記入してください:

```markdown
### Week 1

#### 完了タスク
- [x] Phase 1 セットアップ完了
- [x] tax_helpers.py 実装完了
- [x] test_tax_helpers.py 作成完了
- [x] 最初の1箇所置換完了

#### 進行中タスク
- [ ] 残りの29箇所を置換中

#### ブロッカー
- なし

#### 次週の計画
1. 残り9箇所（2-10番目）を置換
2. 第1バッチ完了
3. 第2バッチ開始（11-20番目）
```

---

## 🆘 困ったときは

### トラブルシューティング

`REFACTORING/PHASE_1/TASKS.md` の最後にトラブルシューティングセクションがあります。

### よくある問題

**インポートエラー:**
- `__init__.py` が存在するか確認
- プロジェクトルートから実行しているか確認

**計算結果が異なる:**
- 辞書のキー名を確認: `['total_savings']`
- デフォルト課税所得: 5,000,000円

**テストが失敗:**
- 元のコードに戻して確認
- 段階的に変更を適用

---

## 🎯 目標を再確認

### Phase 1の目標

- **期間:** 1-2週間
- **削減行数:** ~500行
- **置換箇所:** 30箇所
- **新規追加:** テストスイート200行

### 今週の目標

- [ ] 最初の10箇所を置換
- [ ] テストカバレッジを測定
- [ ] `PROGRESS.md` を更新

---

**あなたならできます！** 🚀

小さな一歩の積み重ねが、大きな成果につながります。
質問や不明点があれば、各ドキュメントを参照してください。

---

**最終更新:** 2025年10月25日  
**次のアクション:** ステップ1からステップ6を実行
