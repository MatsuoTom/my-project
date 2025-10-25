#!/usr/bin/env python
"""
年金シミュレーションアプリ起動スクリプト（scripts/ 配置）
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run Pension Streamlit App")
    parser.add_argument("--port", type=int, default=8508, help="Port to run the app on")
    args = parser.parse_args()
    print("🧓 年金シミュレーションツール")
    print("=" * 50)

    project_root = Path(__file__).resolve().parents[1]
    app_path = project_root / "pension_calc" / "ui" / "streamlit_app.py"

    if not app_path.exists():
        print(f"❌ エラー: アプリケーションファイルが見つかりません: {app_path}")
        return 1

    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)

    def build_cmd(port: int):
        return [
            sys.executable, "-m", "streamlit", "run", str(app_path),
            f"--server.port={port}",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]

    print(f"💡 ブラウザでアプリケーションが開きます: http://localhost:{args.port}")
    print("⏹️  停止するには Ctrl+C")
    print("=" * 50)

    try:
        os.chdir(project_root)
        # ポート競合時に 2 段までフォールバック
        ports_to_try = [args.port, args.port + 1, args.port + 2]
        last_err = None
        for p in ports_to_try:
            print(f"🚀 起動中: http://localhost:{p}")
            ret = subprocess.run(build_cmd(p), env=env)
            if ret.returncode == 0:
                return 0
            last_err = ret.returncode
            print(f"⚠️ ポート {p} での起動に失敗（returncode={ret.returncode}）。次を試します…")
        print("❌ すべての候補ポートで起動できませんでした。別のポートを指定してください（--port）。")
        return last_err or 1
        return 0
    except KeyboardInterrupt:
        print("\n👋 停止しました")
        return 0
    except FileNotFoundError:
        print("❌ Streamlit が見つかりません。pip install streamlit でインストールしてください。")
        return 1
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
