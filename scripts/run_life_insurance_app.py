#!/usr/bin/env python
"""
生命保険料控除分析アプリケーション起動スクリプト

このスクリプトで Streamlit アプリケーションを起動します。
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """メイン実行関数"""
    print("🏦 生命保険料控除分析ツール")
    print("=" * 50)
    
    # プロジェクトルートを取得
    project_root = Path(__file__).parent
    app_path = project_root / "life_insurance" / "ui" / "streamlit_app.py"
    
    # アプリケーションファイルの存在確認
    if not app_path.exists():
        print(f"❌ エラー: アプリケーションファイルが見つかりません")
        print(f"   パス: {app_path}")
        return 1
    
    print(f"📂 プロジェクトディレクトリ: {project_root}")
    print(f"🚀 アプリケーション起動中...")
    print(f"   ファイル: {app_path}")
    print()
    
    # 環境変数設定（必要に応じて）
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)
    
    try:
        # Streamlitアプリケーションを起動
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8508",
            "--server.address=localhost",
            "--browser.serverAddress=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        print("💡 ブラウザでアプリケーションが開きます")
        print("   URL: http://localhost:8508")
        print()
        print("⏹️  停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        # カレントディレクトリを変更
        os.chdir(project_root)
        
        # アプリケーション実行
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 アプリケーションを停止しました")
        return 0
    except FileNotFoundError:
        print("❌ エラー: Streamlitがインストールされていません")
        print("   インストール方法: pip install streamlit")
        return 1
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())