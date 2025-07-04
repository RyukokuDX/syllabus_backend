#!/bin/bash

# 漢字氏名がないファイルを再ダウンロードするバッチスクリプト

echo "漢字氏名がないファイルの検索を開始..."
missing_files=$(grep -L "漢字氏名" *.html)
total_count=$(echo "$missing_files" | wc -l)

echo "対象ファイル数: $total_count"
echo "再ダウンロードを開始します..."

count=0
parallel_count=0
max_parallel=3  # 同時実行数

for file in $missing_files; do
    # ファイル名から拡張子を除去してシラバス管理番号を取得
    syllabus_id=${file%.html}
    
    count=$((count + 1))
    parallel_count=$((parallel_count + 1))
    
    echo "[$count/$total_count] $syllabus_id を再ダウンロード中..."
    
    # バックグラウンドで実行
    python3 ../../single_syllabus_downloader.py "$syllabus_id" --overwrite -o . > "redownload_${syllabus_id}.log" 2>&1 &
    
    # 並列実行数が上限に達したら待機
    if [ $parallel_count -eq $max_parallel ]; then
        wait  # すべてのバックグラウンドプロセスの完了を待つ
        parallel_count=0
        echo "バッチ完了。次のバッチを開始..."
    fi
    
    # 100件ごとに進捗表示
    if [ $((count % 100)) -eq 0 ]; then
        echo "進捗: $count/$total_count 件完了"
    fi
done

# 残りのプロセスの完了を待つ
wait

echo "すべての再ダウンロードが完了しました。"
echo "漢字氏名の確認..."

# 再確認
remaining=$(grep -L "漢字氏名" *.html | wc -l)
echo "残り未処理件数: $remaining"

if [ $remaining -eq 0 ]; then
    echo "✅ すべてのファイルに漢字氏名が含まれています！"
else
    echo "⚠️  まだ $remaining 件のファイルに漢字氏名がありません。"
fi