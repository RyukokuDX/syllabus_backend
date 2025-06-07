#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# - 更新の登録を要求された場合は、/docs/version_control.md に準拠して実行

import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

def load_version_json(version_dir: str, file_path: str) -> Optional[Dict]:
    """バージョンディレクトリからJSONファイルを読み込む"""
    json_path = os.path.join(version_dir, file_path + '.json')
    if not os.path.exists(json_path):
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_version_dirs() -> List[str]:
    """バージョンディレクトリの一覧を取得"""
    version_dir = os.path.join(os.getcwd(), 'version')
    if not os.path.exists(version_dir):
        return []
    
    return sorted([d for d in os.listdir(version_dir) 
                  if os.path.isdir(os.path.join(version_dir, d)) and d.startswith('v')],
                 key=lambda x: [int(n) for n in x[1:].split('.')[:2]])  # major.minorのみでソート

def format_change_history(version_data: Dict) -> str:
    """変更履歴を整形して文字列として返す"""
    if not version_data or 'path_level' not in version_data:
        return "変更履歴なし"
    
    history = []
    for level, change in sorted(version_data['path_level'].items()):
        history.append(f"レベル {level}:")
        history.append(f"  日時: {change['date']}")
        history.append(f"  概要: {change['summary']}")
        history.append(f"  詳細: {change['details']}")
        history.append("")
    
    return "\n".join(history)

def display_file_history(file_path: str, relative_path: bool = False) -> None:
    """ファイルの変更履歴を表示"""
    if relative_path:
        file_path = os.path.relpath(file_path, os.getcwd())
    
    version_dirs = get_version_dirs()
    if not version_dirs:
        print("バージョンディレクトリが見つかりません")
        return
    
    print(f"\nファイル: {file_path} の変更履歴")
    print("=" * 50)
    
    for version_dir in version_dirs:
        version_data = load_version_json(os.path.join('version', version_dir), file_path)
        if version_data:
            print(f"\nバージョン: {version_data['meta_data']['version']}")
            print(f"作成日時: {version_data['meta_data']['created_at']}")
            print("-" * 30)
            print(format_change_history(version_data))

def main():
    parser = argparse.ArgumentParser(description='ファイルの変更履歴を表示')
    parser.add_argument('file_path', help='変更履歴を表示するファイルのパス')
    parser.add_argument('--relative', action='store_true',
                       help='プロジェクトルートからの相対パスとして解釈')
    
    args = parser.parse_args()
    display_file_history(args.file_path, args.relative)

if __name__ == '__main__':
    main() 