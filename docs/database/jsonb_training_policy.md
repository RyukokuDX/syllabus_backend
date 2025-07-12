---
title: JSONBキャッシュ LLM学習データ作成ポリシー
default_file_version: v1.0.1
project_version: v3.0.2
last_updated: 2025-07-09
---

# JSONBキャッシュ LLM学習データ作成ポリシー

- File Version: v1.0.1
- Project Version: v3.0.2
- Last Updated: 2025-07-09

[readmeへ](../../README.md) | [構造定義へ](./jsonb_cache.md) | [サンプルへ](./jsonb_cache_samples.md)

## 目次
1. 目的・対象読者
2. 基本方針
3. 学習データ構造と分離ルール
4. サンプル作成・収集・前処理
5. エッジケース・多様性の確保
6. LLM学習時の注意点
7. 推奨プロンプト・学習データ例
8. 運用・バージョン管理
9. 関連ドキュメント

## 1. 目的・対象読者
- 本ドキュメントは、syllabus_backendプロジェクトのJSONBキャッシュ仕様に基づき、ローカルLLM向け学習データを作成・運用するためのガイドラインである。
- 対象：データ作成者、LLM運用担当、開発者

## 2. 基本方針
- 構造定義（仕様）とサンプル（実データ例）は必ず分離し、混在させない。
- サンプルは現実のキャッシュデータ（例：tests/json_output/total.json）に厳密に準拠する。
- 属性名・型・値の現実性を重視し、架空の値や仕様外の構造を避ける。
- 学習データ（order・SQL・レスポンスJSON）は、ファイル名でペアリングしつつ、mdファイル（例：trainer.md）でorder（自然言語クエリ）・SQLファイル・レスポンスJSONファイルの対応関係を一覧管理する。
- ファイル名は「時刻」や連番ではなく、orderの要点やクエリの主旨など内容を反映したものとする。
- 最終的な学習用JSONは自動生成スクリプトで統合する。

## 3. 学習データ構造と分離ルール
- 構造定義は[jsonb_cache.md](./jsonb_cache.md)に、サンプルは[jsonb_cache_samples.md](./jsonb_cache_samples.md)に記載。
- 学習データは「プロンプト（自然言語クエリ）」＋「レスポンス（SQLまたはJSON）」のペア形式を推奨。
- サンプルは現実のキャッシュ出力から自動抽出・整形すること。
- SQLは`trainer/sql/`、レスポンスJSONは`trainer/response/`等のディレクトリで管理し、ファイル名でペアリングする。
- mdファイル（例：docs/trainer.md）でorder・SQL・レスポンスJSONの対応関係を一覧化し、運用ルール・命名規則も明記する。

### ファイル命名規則（推奨）
- 英小文字＋アンダースコア区切り
- order（自然言語クエリ）の要点を短く英語で表現
- SQLとJSONは同じファイル名＋拡張子（.sql/.json）でペア
- 年度・言語・バージョン等が必要な場合は末尾に付与
- 例：
  - math_required.sql / math_required.json
  - cg_vr.sql / cg_vr.json
  - math_required_2025.sql / math_required_2025.json

### mdファイル管理例
| order（自然言語クエリ） | SQLファイル | レスポンスJSON |
|------------------------|------------|---------------|
| 数理の前期の必修科目一覧 | math_required.sql | math_required.json |
| CGとVRの開講情報を教えて | cg_vr.sql | cg_vr.json |

- mdファイルが「正」のリストとなり、ファイル名の混乱や重複・用途不明ファイルの発生を防ぐ。
- 自動統合スクリプトはmdファイルを基準にorder・SQL・レスポンスJSONを突き合わせて学習用JSONを生成する。

### SQLファイルのメタデータ記法（YAML front matter風）
- SQLファイル冒頭にYAML front matter風のメタデータをSQLコメント（--）で記載することで、orderや説明、バージョン、レスポンスファイル名等を機械可読かつ拡張性高く管理できる。
- 推奨例：

```sql
-- ---
-- order: 数理の専門応用科目のうち、成績評価基準一覧に「レポート」を含まないものを抽出
-- desc: 数理の専門応用科目で、成績評価基準に「レポート」が含まれない科目名を一覧で取得する
-- author: 藤原和将
-- file_version: v1.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: math_noreport.json
-- ---

SELECT
	cache_data->>'科目名' AS subject_name
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
	AND EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'履修情報一覧') AS ri
		CROSS JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r
		WHERE r->>'学部課程' LIKE '%数理%'
			AND r->>'科目小区分' = '専門応用科目'
	)
	AND NOT EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'開講情報一覧') AS open
		CROSS JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl
		CROSS JOIN LATERAL jsonb_array_elements(syl->'成績評価基準一覧') AS g
		WHERE g->>'項目' LIKE '%レポート%'
	)
ORDER BY subject_name;
```

- 必須項目：order, desc, file_version, project_version, last_updated, response_id
- 任意でauthorやtags等も追加可能
- SQL本体はメタデータコメントの下に記載

## 4. サンプル作成・収集・前処理
- サンプルは実際のキャッシュデータから多様なパターン（典型・エッジケース）を抽出。
- 配列型・null・複数教員・空配列など、現実に出現する全パターンを網羅。
- 属性名・値の揺れやバリエーションも意識して収集。
- 前処理時は、不要なIDや内部コードを除去し、LLMが誤学習しないよう配慮。

## 5. エッジケース・多様性の確保
- 空配列、null値、複数教員、参考書なし、学修プログラム複数/空、年度違い、属性値の欠損など、現実に即した多様なケースを必ず含める。
- サンプルの一部は[jsonb_cache_samples.md](./jsonb_cache_samples.md)を参照。

## 6. LLM学習時の注意点
- 配列型は必ず配列で表現（1件でも[]で囲む）。
- nullや空配列の混入に注意し、型整合性を保つ。
- 属性名・命名規則は仕様（jsonb_cache.md）に厳密に従う。
- 架空の属性や現実に存在しない値は使用しない。
- サンプルの現実性・一貫性を重視。

## 7. 推奨プロンプト・学習データ例
- 例1: 科目名から開講情報を取得するプロンプト
  - プロンプト: 「CGとVRの開講情報を教えて」
  - レスポンス: [jsonb_cache_samples.md](./jsonb_cache_samples.md)の該当JSON
- 例2: 学修プログラムIDで履修要件を取得
  - プロンプト: 「学修プログラム5の履修要件を一覧で」
  - レスポンス: 実データから該当部分を抽出
- 例3: エッジケース（教員が複数、参考書なし等）
  - プロンプト: 「AI入門の担当教員一覧と参考書を教えて」
  - レスポンス: 複数教員・参考書空配列のサンプル

## 8. 運用・バージョン管理
- サンプル・仕様の更新時は必ずバージョン情報を明記。
- サンプル追加・修正時は現実データとの整合性を都度確認。
- ドキュメント・サンプルの差分管理・履歴管理を徹底。

## 9. 関連ドキュメント
- [JSONBキャッシュ仕様書](./jsonb_cache.md)
- [JSONBキャッシュサンプル集](./jsonb_cache_samples.md)
- [データベース設計ポリシー](./policy.md)
- [データベース更新手順書](./updateflow.md)
- [ドキュメント作成ガイドライン](../doc.md)

[🔝 ページトップへ](#jsonbキャッシュ-llm学習データ作成ポリシー) 