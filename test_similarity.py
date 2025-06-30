#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
類似度計算テストスクリプト
Version: 1.0.0
"""

import re
from difflib import SequenceMatcher

def normalize_text(text: str) -> str:
    """テキストを正規化"""
    # 小文字化
    text = text.lower()
    # 記号を除去（ハイフン、アンダースコア、括弧は残す）
    text = re.sub(r'[^\w\s\-_()（）]', '', text)
    # 複数の空白を単一の空白に
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def calculate_similarity(title1: str, title2: str) -> float:
    """2つの書籍名の類似度を計算"""
    # テキストを正規化
    norm_title1 = normalize_text(title1)
    norm_title2 = normalize_text(title2)
    
    # 文字列類似度（SequenceMatcher）
    string_similarity = SequenceMatcher(None, norm_title1, norm_title2).ratio()
    
    # 単語レベルでの類似度
    words1 = set(norm_title1.split())
    words2 = set(norm_title2.split())
    
    if not words1 or not words2:
        word_similarity = 0.0
    else:
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        word_similarity = len(intersection) / len(union)
    
    # 重み付き平均（文字列類似度70%、単語類似度30%）
    return 0.7 * string_similarity + 0.3 * word_similarity

def test_similarity():
    """類似度計算のテスト"""
    test_cases = [
        ("振動学", "振動学 = Mechanical vibration"),
        ("材料の科学と工学〈1〉材料の微細構造", "機械材料入門")
    ]
    
    for title1, title2 in test_cases:
        similarity = calculate_similarity(title1, title2)
        print(f"類似度: {similarity:.3f}")
        print(f"  シラバス: {title1}")
        print(f"  CiNii: {title2}")
        print(f"  判定: {'類似度低い' if similarity < 0.05 else '類似度高い'}")
        print()

if __name__ == "__main__":
    test_similarity() 