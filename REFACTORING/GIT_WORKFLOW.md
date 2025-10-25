# 🔄 Git Workflow — Phase 1 リファクタリング

**最終更新:** 2025年10月25日  
**プロジェクト:** my-project リファクタリング

---

## 📊 現在の状態

### コミット履歴
```
* 3570629 (HEAD -> main) docs: Add release notes for v0.1.0-phase1-task1.1
* 096f603 docs: Add Git usage guide for refactoring workflow
* 1a088f8 (tag: v0.1.0-phase1-task1.1) checkpoint: Phase 1 Task 1.1 completed
```

### タグ
- ✅ **v0.1.0-phase1-task1.1** — Phase 1 Task 1.1 完了

### ブランチ
- **main** — メインブランチ（現在位置）

---

## 🎯 今後のワークフロー

### Task 1.2: streamlit_app.py への統合（30箇所置換）

#### ステップ1: 作業ブランチ作成（推奨）
```bash
git checkout -b phase1/task1.2-replacements
```

**メリット:**
- メインブランチを保護
- 実験的な変更を安全に試せる
- 必要に応じて破棄可能

#### ステップ2: 段階的な置換（10箇所ずつ）

##### 2-10箇所目（9箇所）
```bash
# 編集...
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor(phase1): Replace duplicates 2-10 in streamlit_app.py

- Replace tax calculation blocks (lines 423, 517, 782, ...)
- Use get_tax_helper() for consistency
- Reduce 72 lines of duplicate code

Progress: 10/30 locations (33%)"

# 動作確認
streamlit run life_insurance/ui/streamlit_app.py
# OK なら次へ
```

##### 11-20箇所目（10箇所）
```bash
# 編集...
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor(phase1): Replace duplicates 11-20 in streamlit_app.py

Progress: 20/30 locations (67%)"

# 動作確認
# OK なら次へ
```

##### 21-30箇所目（10箇所）
```bash
# 編集...
git add life_insurance/ui/streamlit_app.py
git commit -m "refactor(phase1): Replace duplicates 21-30 in streamlit_app.py

Progress: 30/30 locations (100%)"

# 動作確認
# OK なら完了
```

#### ステップ3: メインブランチにマージ
```bash
git checkout main
git merge phase1/task1.2-replacements

# タグ付け
git tag -a v0.1.1-phase1-task1.2 -m "Phase 1 Task 1.2 completed: All 30 duplicates replaced"

# 作業ブランチ削除（オプション）
git branch -d phase1/task1.2-replacements
```

---

## 🔧 便利なコマンド

### 現在の状態確認
```bash
# ステータス
git status

# 履歴
git log --oneline --graph -10

# タグ一覧
git tag -l
```

### 変更内容の確認
```bash
# 現在の変更
git diff

# 最後のコミットとの差分
git diff HEAD~1 HEAD

# 特定のファイルの変更履歴
git log --oneline -- life_insurance/ui/streamlit_app.py
```

### 統計情報
```bash
# コミット数
git rev-list --count HEAD

# 変更統計
git log --stat

# 誰が何を変更したか
git blame life_insurance/ui/streamlit_app.py
```

---

## 🚨 トラブルシューティング

### 間違えてコミットした
```bash
# コミットを取り消す（変更は残る）
git reset --soft HEAD~1

# 編集し直してから再コミット
git add .
git commit -m "正しいメッセージ"
```

### 動作確認してダメだった
```bash
# 最後のコミットに戻る
git reset --hard HEAD~1

# または特定のコミットに戻る
git reset --hard <コミットID>
```

### 特定のファイルだけ元に戻す
```bash
git checkout HEAD -- life_insurance/ui/streamlit_app.py
```

---

## 📝 コミットメッセージルール

### フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（タイプ）
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `test`: テスト追加
- `docs`: ドキュメント
- `chore`: その他（設定、ビルド等）

### 例
```bash
git commit -m "refactor(phase1): Replace tax calculation duplicates

- Use TaxDeductionHelper for consistency
- Reduce code duplication from 11 to 3 lines per occurrence
- Maintain backward compatibility

Refs: REFACTORING/PHASE_1/TASKS.md
Progress: 10/30 locations (33%)"
```

---

## 🎯 Phase 1 完了までのロードマップ

### Task 1: 税金ヘルパー実装
- [x] ✅ Task 1.1: モジュール作成（v0.1.0-phase1-task1.1）
- [ ] 🔄 Task 1.2: 30箇所置換（次: v0.1.1-phase1-task1.2）
- [ ] ⏳ Task 1.3: 動作確認とE2Eテスト（次: v0.1.2-phase1-task1-complete）

### Task 2: 年金価値計算ヘルパー
- [ ] ⏳ Task 2.1: モジュール作成（次: v0.2.0-phase1-task2.1）
- [ ] ⏳ Task 2.2: 統合
- [ ] ⏳ Task 2.3: 動作確認

### Task 3: プロット共通ヘルパー
- [ ] ⏳ Task 3.1: モジュール作成（次: v0.3.0-phase1-task3.1）
- [ ] ⏳ Task 3.2: 統合
- [ ] ⏳ Task 3.3: 動作確認

### Phase 1 完了
- [ ] ⏳ v1.0.0-phase1-complete

---

## 📊 進捗メトリクス（Gitから自動取得）

### コミット数
```bash
git rev-list --count HEAD
# 現在: 3件
```

### 削減行数（累計）
```bash
git log --numstat --pretty="%H" | awk '{deleted+=$2} END {print "Deleted:", deleted}'
# 現在: 8行
```

### ファイル変更統計
```bash
git log --stat | grep "files changed"
```

---

## 🔗 関連ドキュメント

- **Git使い方:** `REFACTORING/GIT_GUIDE.md`
- **リリースノート:** `REFACTORING/RELEASE_NOTES.md`
- **進捗トラッキング:** `REFACTORING/PROGRESS.md`
- **タスク詳細:** `REFACTORING/PHASE_1/TASKS.md`

---

**次のアクション:**
1. 作業ブランチを作成: `git checkout -b phase1/task1.2-replacements`
2. 2-10箇所目を置換
3. コミット & 動作確認
4. 11-20箇所目を置換...

**ステータス:** ✅ Task 1.1 完了、Task 1.2 準備完了
