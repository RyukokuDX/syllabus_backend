#!/bin/bash

# Batch re-download script for files missing kanji names
# This version processes files in smaller batches to avoid timeouts

LOG_PREFIX="redownload"
MAX_PARALLEL=2  # Reduced from 3 to avoid timeouts
BATCH_SIZE=10   # Process 10 files at a time

# Get list of files missing kanji names
grep -L "漢字氏名" *.html > missing_kanji_files.txt

total_files=$(cat missing_kanji_files.txt | wc -l | tr -d ' ')
echo "Total files needing re-download: $total_files"

processed=0
batch_num=1

while IFS= read -r filename; do
    if [ ! -f "$filename" ]; then
        echo "Skipping non-existent file: $filename"
        continue
    fi
    
    # Extract syllabus ID from filename
    syllabus_id=$(basename "$filename" .html)
    
    echo "[$batch_num] Processing $syllabus_id... ($((processed + 1))/$total_files)"
    
    # Run download in background
    python3 ../../single_syllabus_downloader.py "$syllabus_id" --overwrite -o . > "${LOG_PREFIX}_${syllabus_id}.log" 2>&1 &
    
    processed=$((processed + 1))
    
    # Check if we've reached the parallel limit
    if (( processed % MAX_PARALLEL == 0 )); then
        echo "Waiting for batch $batch_num to complete..."
        wait  # Wait for all background jobs to finish
        
        # Check success rate
        successful=0
        for ((i = processed - MAX_PARALLEL + 1; i <= processed; i++)); do
            current_file=$(sed -n "${i}p" missing_kanji_files.txt)
            current_id=$(basename "$current_file" .html)
            if grep -q "Successfully downloaded" "${LOG_PREFIX}_${current_id}.log" 2>/dev/null; then
                successful=$((successful + 1))
            fi
        done
        
        echo "Batch $batch_num completed: $successful/$MAX_PARALLEL successful"
        echo "Progress: $processed/$total_files files processed ($(( processed * 100 / total_files ))%)"
        echo "---"
        
        batch_num=$((batch_num + 1))
        
        # Brief pause between batches
        sleep 2
    fi
    
    # Process in smaller batches for better control
    if (( processed % BATCH_SIZE == 0 )); then
        echo "Completed batch of $BATCH_SIZE files. Checking remaining files..."
        remaining_missing=$(grep -L "漢字氏名" *.html | wc -l | tr -d ' ')
        echo "Files still missing kanji names: $remaining_missing"
    fi
    
done < missing_kanji_files.txt

# Wait for any remaining background jobs
echo "Waiting for final batch to complete..."
wait

echo "Re-download process completed!"
echo "Final check:"
final_missing=$(grep -L "漢字氏名" *.html | wc -l | tr -d ' ')
echo "Files still missing kanji names: $final_missing"