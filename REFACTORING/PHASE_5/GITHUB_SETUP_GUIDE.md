# GitHub リポジトリセットアップガイド

**日付**: 2025年11月3日  
**目的**: Phase 5（CI/CD構築）のためのGitHubリポジトリ設定

---

## 📋 セットアップの流れ

### ステップ1: GitHubでリポジトリを作成

1. **GitHub（https://github.com）にアクセス**
   - アカウントがない場合は新規登録

2. **新しいリポジトリを作成**
   - 右上の「+」ボタン → 「New repository」
   - または: https://github.com/new に直接アクセス

3. **リポジトリ設定**
   ```
   Repository name: my-project
   Description: 日本の年金・生命保険・投資シミュレーション
   
   Public or Private: お好みで選択
   - Public: 誰でも閲覧可能（GitHub Actionsの無料枠が大きい）
   - Private: 自分だけ閲覧可能
   
   ❌ Initialize this repository with:
   - README, .gitignore, license は追加しない
     （既にローカルにあるため）
   ```

4. **リポジトリを作成**
   - 「Create repository」ボタンをクリック

---

### ステップ2: リモートリポジトリをローカルに追加

GitHubでリポジトリを作成すると、以下のようなURLが表示されます：

```
https://github.com/<あなたのユーザー名>/my-project.git
```

このURLを使って、PowerShellで以下のコマンドを実行します：

```powershell
# リモートリポジトリを追加
git remote add origin https://github.com/<あなたのユーザー名>/my-project.git

# リモート設定を確認
git remote -v
```

**期待される出力**:
```
origin  https://github.com/<あなたのユーザー名>/my-project.git (fetch)
origin  https://github.com/<あなたのユーザー名>/my-project.git (push)
```

---

### ステップ3: コードをプッシュ

```powershell
# mainブランチをプッシュ
git push -u origin main

# すべてのタグをプッシュ
git push origin --tags
```

**認証が求められた場合**:
- **Personal Access Token（推奨）**を使用
- または **GitHub CLI**（`gh auth login`）

---

### ステップ4: プッシュの確認

GitHubのリポジトリページ（https://github.com/<あなたのユーザー名>/my-project）で以下を確認：

1. **ファイルが表示されている**
   - README.md
   - pyproject.toml
   - life_insurance/
   - pension_calc/
   - 等

2. **タグが表示されている**
   - 「Tags」タブで以下が確認できる：
     - v0.6.0-phase4-complete
     - v0.4.0-phase2-complete
     - v0.3.0-phase1-complete
     - 等

3. **コミット履歴が表示されている**
   - 最新のコミット: "feat(phase3-4): Phase 3-4完了..."

---

## 🔐 GitHub認証の設定

### Personal Access Token (PAT) の作成

1. **GitHub設定ページにアクセス**
   - https://github.com/settings/tokens

2. **新しいトークンを作成**
   - 「Generate new token」→「Generate new token (classic)」
   - Note: `my-project-token`
   - Expiration: 任意（90 days推奨）
   - Select scopes:
     - ✅ `repo` (すべてのリポジトリアクセス)
     - ✅ `workflow` (GitHub Actions)

3. **トークンをコピー**
   - 生成されたトークンを安全な場所に保存
   - **このトークンは二度と表示されません**

4. **トークンを使用してプッシュ**
   ```powershell
   git push -u origin main
   # Username: あなたのGitHubユーザー名
   # Password: 生成したPersonal Access Token
   ```

---

## 🎯 GitHub Actions の有効化

リポジトリをプッシュした後:

1. **GitHubリポジトリの「Actions」タブにアクセス**
   - https://github.com/<あなたのユーザー名>/my-project/actions

2. **GitHub Actionsが有効化されていることを確認**
   - 初回は「Get started with GitHub Actions」と表示される可能性あり
   - Phase 5で`.github/workflows/ci.yml`を作成後、自動で実行される

---

## ✅ セットアップ完了チェックリスト

### 必須項目

- [ ] GitHubアカウントを作成
- [ ] 新しいリポジトリ（my-project）を作成
- [ ] リモートリポジトリをローカルに追加（`git remote add origin`）
- [ ] mainブランチをプッシュ（`git push -u origin main`）
- [ ] タグをプッシュ（`git push origin --tags`）
- [ ] GitHubでファイルが表示されることを確認
- [ ] GitHub Actionsタブが表示されることを確認

### オプション項目

- [ ] Personal Access Tokenを作成
- [ ] README.mdにリポジトリバッジを追加
- [ ] リポジトリの説明（Description）を設定
- [ ] リポジトリのトピック（Topics）を追加

---

## 🚨 トラブルシューティング

### エラー: `remote origin already exists`

```powershell
# 既存のリモートを削除
git remote remove origin

# 再度リモートを追加
git remote add origin https://github.com/<あなたのユーザー名>/my-project.git
```

### エラー: `Authentication failed`

- Personal Access Tokenを使用していることを確認
- トークンの権限（`repo`, `workflow`）を確認
- トークンの有効期限を確認

### エラー: `! [rejected] main -> main (fetch first)`

```powershell
# リモートの変更を取得してマージ
git pull origin main --allow-unrelated-histories

# 再度プッシュ
git push -u origin main
```

---

## 📞 次のステップ

セットアップが完了したら、**Task 5.1: GitHub Actions の基本設定**に進みます。

GitHubリポジトリのURLを教えていただければ、次のタスクをサポートします！

---

**作成日**: 2025年11月3日  
**更新日**: 2025年11月3日  
**バージョン**: 1.0
