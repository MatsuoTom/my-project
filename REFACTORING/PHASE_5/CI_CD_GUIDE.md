# CI/CD ガイド — Phase 5

## 概要

このドキュメントは、my-projectのCI/CDパイプライン（GitHub Actions）の使用方法とメンテナンス方法を説明します。

## CI/CDパイプラインの構成

### ワークフロー構成

- **ファイル**: `.github/workflows/ci.yml`
- **トリガー**: 
  - `push` イベント（mainブランチ）
  - `pull_request` イベント（mainブランチ）
  - 手動実行（`workflow_dispatch`）

### ジョブ構成

#### 1. Code Quality Check（lintジョブ）

- **目的**: コード品質の自動チェック
- **実行環境**: Ubuntu最新版
- **チェック項目**:
  - **flake8**: Pythonコードリンター
    - 最大行長: 100文字
    - 除外: E203, W503, E501（Black互換）
    - 複雑度制限: 15
  - **black**: コード自動フォーマッターのチェック
    - チェックモード（--check）で差分を検出
    - 行長: 100文字
  - **mypy**: 型チェック（オプション、continue-on-error: true）
    - Python 3.12対応
    - 型ヒントの段階的導入をサポート

#### 2. Test（testジョブ）

- **目的**: 複数環境での自動テスト実行
- **マトリックス構成**: 9環境
  - **OS**: Ubuntu, Windows, macOS
  - **Python**: 3.10, 3.11, 3.12
- **テスト項目**:
  - 全テスト実行（common, life_insurance, tests）
  - カバレッジ測定（pytest-cov）
  - カバレッジレポートアップロード

### テストカバレッジ

- **全体**: 65.16%
- **common**: 98%（高カバレッジ）
- **life_insurance**: 76%（良好）
- **pension_calc**: 22%（改善の余地あり）

## 使用方法

### ローカル環境でのCI/CDチェック実行

#### 1. コード品質チェック

```powershell
# flake8チェック
flake8 common/ life_insurance/ pension_calc/ --count --statistics

# Blackフォーマットチェック
black common/ life_insurance/ pension_calc/ tests/ --check --diff

# Blackフォーマット適用
black common/ life_insurance/ pension_calc/ tests/ --line-length 100

# mypyチェック（オプション）
mypy common/ life_insurance/ pension_calc/ --ignore-missing-imports
```

#### 2. テスト実行

```powershell
# 全テスト実行
pytest common/tests/ tests/ life_insurance/tests/ -v

# カバレッジ測定
pytest common/tests/ tests/ life_insurance/tests/ --cov=common --cov=life_insurance --cov=pension_calc --cov-report=term-missing --cov-report=html

# カバレッジレポート（HTMLファイル）
# htmlcov/index.html をブラウザで開く
```

### GitHub Actionsでの実行確認

1. **プッシュ時の自動実行**:
   ```powershell
   git add .
   git commit -m "feat: 新機能追加"
   git push origin main
   ```

2. **実行結果の確認**:
   - GitHubリポジトリの「Actions」タブにアクセス
   - 最新のワークフロー実行を確認
   - 各ジョブの詳細ログを表示

3. **手動実行**:
   - GitHubリポジトリの「Actions」タブ
   - 「CI/CD Pipeline」ワークフローを選択
   - 「Run workflow」ボタンをクリック

### バッジの確認

README.mdに以下のバッジが表示されます：

- **CI/CD Pipeline**: ビルド状態（passing/failing）
- **Python Version**: サポートされるPythonバージョン
- **Code Style**: Blackフォーマットの使用
- **License**: ライセンス情報

## メンテナンス

### CI/CDワークフローの更新

#### 1. 新しいPythonバージョンの追加

`.github/workflows/ci.yml`のmatrix.python-versionを更新：

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.10', '3.11', '3.12', '3.13']  # 3.13を追加
```

#### 2. 新しいコード品質チェックツールの追加

lintジョブにステップを追加：

```yaml
- name: Run pylint
  run: |
    pip install pylint
    pylint common/ life_insurance/ pension_calc/ --rcfile=.pylintrc
  continue-on-error: true
```

#### 3. テストの除外パターン変更

`.coveragerc`を編集：

```ini
[run]
omit = 
    */tests/*
    */test_*.py
    */ui/*
    */streamlit_app*.py
    */新しい除外パターン/*
```

### トラブルシューティング

#### テスト失敗時の対処法

1. **ローカルでの再現**:
   ```powershell
   # 同じ環境でテスト実行
   pytest common/tests/ tests/ life_insurance/tests/ -v --tb=short
   ```

2. **特定の環境でのみ失敗**:
   - OS固有の問題（パス区切り文字、改行コード）
   - Python バージョン固有の問題（構文、標準ライブラリの差異）

3. **カバレッジ測定失敗**:
   ```powershell
   # カバレッジ設定を確認
   cat .coveragerc
   
   # 手動でカバレッジ測定
   pytest --cov=common --cov=life_insurance --cov=pension_calc --cov-report=term
   ```

#### コード品質チェック失敗時の対処法

1. **flake8エラー**:
   ```powershell
   # エラー箇所を確認
   flake8 common/ life_insurance/ pension_calc/ --show-source
   
   # 自動修正可能な場合
   autopep8 --in-place --aggressive --aggressive <ファイル名>
   ```

2. **Blackフォーマットエラー**:
   ```powershell
   # 差分を確認
   black common/ life_insurance/ pension_calc/ tests/ --check --diff
   
   # 自動修正
   black common/ life_insurance/ pension_calc/ tests/ --line-length 100
   ```

3. **mypyエラー**（オプション）:
   ```powershell
   # エラー箇所を確認
   mypy common/ life_insurance/ pension_calc/ --show-error-codes
   
   # 型ヒントを追加または修正
   ```

## ベストプラクティス

### コミット前のチェックリスト

1. **ローカルテスト実行**:
   ```powershell
   pytest common/tests/ tests/ life_insurance/tests/ -v
   ```

2. **コード品質チェック**:
   ```powershell
   flake8 common/ life_insurance/ pension_calc/ --count
   black common/ life_insurance/ pension_calc/ tests/ --check
   ```

3. **カバレッジ確認**:
   ```powershell
   pytest --cov=common --cov=life_insurance --cov=pension_calc --cov-report=term
   ```

4. **コミット・プッシュ**:
   ```powershell
   git add .
   git commit -m "feat: 機能追加（テスト・品質チェック済み）"
   git push origin main
   ```

### 継続的な改善

- **テストカバレッジ向上**: 現在65.16% → 目標80%
- **コード品質改善**: 残存問題308件の段階的修正
- **型ヒントの追加**: mypyの警告を段階的に解消
- **ドキュメント充実**: README.md、コメント、docstringの追加

## パフォーマンス

### CI/CD実行時間

- **lintジョブ**: 約2-3分
  - flake8: 30秒
  - black: 20秒
  - mypy: 1-2分

- **testジョブ**: 約5-7分（9環境並列実行）
  - セットアップ: 1-2分
  - テスト実行: 3-5分
  - カバレッジアップロード: 30秒

### 最適化のヒント

1. **キャッシュの活用**:
   - pip依存関係のキャッシュ（既に有効）
   - テスト結果のキャッシュ

2. **並列実行の活用**:
   - マトリックステストの並列実行（既に有効）
   - 独立したテストファイルの並列実行

3. **テストの最適化**:
   - 遅いテストの特定と最適化
   - 不要なテストの削除

## 関連ドキュメント

- **IMPLEMENTATION_PLAN.md**: Phase 5の実装計画
- **COMPLETION_REPORT.md**: Phase 5の完了レポート（作成予定）
- **.github/workflows/ci.yml**: CI/CDワークフロー定義
- **.coveragerc**: カバレッジ設定
- **.flake8**: flake8設定
- **pyproject.toml**: Black、mypy、pytest設定

## 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)

---

**作成日**: 2025年11月8日  
**Phase**: 5（CI/CD構築）  
**ステータス**: 進行中
