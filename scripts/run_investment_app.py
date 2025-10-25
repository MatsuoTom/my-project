#!/usr/bin/env python3
"""
NISA投資シミュレーションアプリ起動スクリプト

ポート自動調整機能付きでStreamlitアプリを起動します。
- デフォルトポート: 8512
- 競合時の自動調整: 8513, 8514, ...
"""

import subprocess
import sys
import os
import socket
from pathlib import Path
import argparse

def is_port_in_use(port: int) -> bool:
    """指定ポートが使用中かチェック"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def find_available_port(start_port: int = 8512, max_attempts: int = 10) -> int:
    """利用可能なポートを見つける"""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"利用可能なポートが見つかりません (試行範囲: {start_port}-{start_port + max_attempts - 1})")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='NISA投資シミュレーションアプリを起動')
    parser.add_argument('--port', type=int, default=8512, help='使用ポート番号 (default: 8512)')
    args = parser.parse_args()
    
    # プロジェクトルートディレクトリの設定
    project_root = Path(__file__).parent.parent
    app_path = project_root / "investment_simulation" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ アプリファイルが見つかりません: {app_path}")
        sys.exit(1)
    
    # 利用可能なポートを探す
    try:
        if is_port_in_use(args.port):
            print(f"⚠️ ポート {args.port} は使用中です。別のポートを探しています...")
            port = find_available_port(args.port)
            print(f"✅ ポート {port} を使用します")
        else:
            port = args.port
            print(f"✅ ポート {port} を使用します")
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # 環境変数の設定
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)
    
    # Streamlitアプリの起動
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        f"--server.port={port}",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]
    
    print(f"🚀 NISA投資シミュレーションを起動中...")
    print(f"📍 URL: http://localhost:{port}")
    print(f"📁 アプリパス: {app_path}")
    print("🛑 終了するには Ctrl+C を押してください")
    print("-" * 50)
    
    try:
        # 作業ディレクトリを設定して実行
        subprocess.run(cmd, cwd=project_root, env=env, check=True)
    except KeyboardInterrupt:
        print("\n👋 アプリを終了しました")
    except subprocess.CalledProcessError as e:
        print(f"❌ アプリの起動に失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()