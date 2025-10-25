# 🚀 Git活用ガイド — my-project

**最終更新:** 2025年10月25日  
**Git バージョン:** 2.51.1

---

## ✅ インストール完了

- ✅ Git for Windows 2.51.1 インストール済み
- ✅ 基本設定完了（user.name, user.email）
- ✅ リポジトリ初期化完了
- ✅ 最初のコミット完了（71ファイル、21,290行）
- ✅ タグ付け完了（v0.1.0-phase1-task1.1）

---

## 🎯 基本コマンド（よく使う）

### 環境変数を読み込む（各セッション開始時）
```powershell
# PowerShellでGitコマンドを使う前に実行
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**または新しいPowerShellウィンドウを開く** → 自動的に読み込まれます

### ステータス確認
```bash
git status          # 変更されたファイルを確認
git st              # エイリアス（短縮版）
```

### 変更をコミット
```bash
# 1. ファイルをステージング
git add ファイル名
git add .           # すべての変更をステージング

# 2. コミット
git commit -m "説明メッセージ"

# 3. 確認
git log --oneline -5
```

### 履歴確認
```bash
git log --oneline --graph -10      # 最新10件を視覚的に表示
git visual                          # エイリアス（全履歴）
git last                            # 最後のコミットを表示
```

### 差分確認
```bash
git diff                    # 変更内容を確認
git diff --stat             # 変更ファイル一覧
git diff HEAD~1 HEAD        # 最後のコミットとの差分
```

---

## 🔄 リファクタリング用ワークフロー

### パターン1: 小さな変更ごとにコミット（推奨）

```bash
# 1箇所変更して保存
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor: Replace 2nd duplicate code block (line 423)"

# 動作確認 → OK

# 次の箇所を変更
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor: Replace 3rd duplicate code block (line 517)"

# 動作確認 → OK
# → 問題が起きても、どこで壊れたか特定できる
```

### パターン2: ブランチで安全に実験

```bash
# 新しいブランチで作業
git checkout -b experiment/new-approach

# 実験的な変更...
git add .
git commit -m "WIP: Testing alternative implementation"

# 動作確認 → ダメだった
git checkout main           # メインブランチに戻る
git branch -D experiment/new-approach  # 実験ブランチ削除

# または、良かった場合
git checkout main
git merge experiment/new-approach  # マージ
```

### パターン3: 一時保存（作業中断）

```bash
# 作業途中で別タスクが入った
git stash                   # 現在の変更を一時保存

# 別の作業...
git checkout -b hotfix/urgent
# 修正...
git commit -m "fix: Critical bug"

# 元の作業に戻る
git checkout main
git stash pop               # 保存した変更を復元
```

---

## 📋 Phase 1 での推奨コミット戦略

### タスク1.2: streamlit_app.py への統合

**10箇所ごとにコミット:**
```bash
# 2-10箇所目を置換
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor(phase1): Replace duplicates 2-10 in streamlit_app.py

- Replace tax calculation blocks (lines 423, 517, 782, ...)
- Use get_tax_helper() for consistency
- Reduce 72 lines of code

Progress: 10/30 locations (33%)"

# 動作確認してOK

# 11-20箇所目を置換
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor(phase1): Replace duplicates 11-20 in streamlit_app.py

Progress: 20/30 locations (67%)"
```

### タスク完了時にタグ付け
```bash
# タスク1.2完了
git tag -a v0.1.1-phase1-task1.2 -m "Task 1.2 completed: 30 duplicates replaced"

# タスク1.3完了（動作確認）
git tag -a v0.1.2-phase1-task1-complete -m "Task 1 complete: Tax helpers fully integrated"
```

---

## 🛠️ トラブルシューティング

### 間違えてコミットした
```bash
# 最後のコミットを取り消す（変更は残る）
git reset --soft HEAD~1

# 最後のコミットを完全に削除（変更も消える）
git reset --hard HEAD~1  # 注意：変更が失われる！
```

### 特定のファイルだけ元に戻す
```bash
git checkout HEAD -- ファイル名
```

### コミットメッセージを修正
```bash
git commit --amend -m "新しいメッセージ"
```

### 前のコミットに戻る
```bash
# コミット履歴を確認
git log --oneline

# 特定のコミットに戻る
git checkout <コミットID>

# 確認後、最新に戻る
git checkout main
```

---

## 📊 進捗確認コマンド

### 今週の変更を確認
```bash
git log --since="1 week ago" --oneline
```

### ファイルごとの変更履歴
```bash
git log --oneline -- life_insurance/ui/streamlit_app.py
```

### 統計情報
```bash
git log --stat
git log --numstat
```

### コミット数
```bash
git rev-list --count HEAD
```

---

## 🎨 便利なエイリアス（設定済み）

| エイリアス | 実際のコマンド | 説明 |
|-----------|---------------|------|
| `git st` | `git status` | ステータス確認 |
| `git co` | `git checkout` | ブランチ切り替え |
| `git br` | `git branch` | ブランチ一覧 |
| `git ci` | `git commit` | コミット |
| `git unstage` | `git reset HEAD --` | ステージング解除 |
| `git last` | `git log -1 HEAD` | 最後のコミット |
| `git visual` | `git log --oneline --decorate --graph --all` | 視覚的な履歴 |

---

## 📝 コミットメッセージのルール

### 推奨フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

### タイプ
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `test`: テスト追加
- `docs`: ドキュメント
- `chore`: その他（設定など）

### 例
```bash
git commit -m "refactor(phase1): Replace tax calculation duplicates

- Use TaxDeductionHelper for consistency
- Reduce code duplication from 30 to 3 lines per occurrence
- Maintain backward compatibility

Refs: REFACTORING/PHASE_1/TASKS.md"
```

---

## 🎯 次のステップ

### 今すぐできること
```bash
# 現在の状態を確認
git status

# 履歴を確認
git visual

# タグを確認
git tag
```

### 次の作業前に
```bash
# 作業用ブランチを作成（推奨）
git checkout -b phase1/task1.2-replacements

# 作業...

# 完了したらマージ
git checkout main
git merge phase1/task1.2-replacements
git tag v0.1.1-phase1-task1.2
```

---

## 📞 ヘルプ

### コマンドのヘルプ
```bash
git help <command>
git <command> --help
```

### よくある質問

**Q: PowerShellを閉じたらgitコマンドが使えなくなった**
A: 新しいPowerShellウィンドウを開くか、環境変数を再読み込みしてください。

**Q: コミット前に変更を確認したい**
A: `git diff` で差分を確認してから `git add` してください。

**Q: 間違えてコミットした**
A: `git reset --soft HEAD~1` でコミットを取り消せます（変更は残ります）。

---

**現在のステータス:**
- ✅ v0.1.0-phase1-task1.1 タグ付け済み
- 📍 Phase 1 Task 1.2 進行中
- 🎯 次: streamlit_app.py の2-10箇所目を置換

詳細な進捗は `REFACTORING/PROGRESS.md` を参照してください。
