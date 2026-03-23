# draftml — Claude Code プロジェクト指示書

## プロジェクト概要

AutoCAD → FreeCAD 1.0 + Claude Code MCP 移行プロジェクト。
建材の製造図面作図を自動化する。

## ドキュメント体系

| ファイル                     | 内容                                                     |
| ---------------------------- | -------------------------------------------------------- |
| `docs/00-requirements.md`    | 要件定義書（ビジネス要件・機能要件・成功基準）           |
| `docs/01-system-context.md`  | システム全体像（コンテキスト図・データフロー）           |
| `docs/02-adr/`               | ADR（技術選定記録）                                      |
| `docs/03-detailed-design.md` | 詳細設計書（パラメトリックモデル・パイプライン設計）     |
| `docs/04-operations.md`      | 運用・保守手順書（トラブルシューティング含む）           |
| `docs/05-release-plan.md`    | リリース計画（マイルストーン・ガントチャート・進捗管理） |

## コミット対象外ポリシー

以下は絶対にコミットしないこと:

- `.reference/` — 内部資料の原本
- `tasks/` — 進捗管理ファイル
- `*.docx`, `*.xlsx`, `*.pptx`, `*.pdf` — バイナリ形式の内部資料
- `output/` — 生成図面（成果物でありソースではない）
- `.env`, `*.key`, `*.pem` — 認証情報

## 技術スタック

- **CAD**: FreeCAD 1.0（PartDesign + TechDraw + Spreadsheet）
- **MCP**: contextform/freecad-mcp（推奨）/ neka-nat/freecad-mcp（バックアップ）
- **変換**: ODA File Converter（DWG → DXF）
- **スクリプト**: Python（FreeCAD内蔵）

## 検証コマンド

現時点では未定義。パイプライン構築（C-1）後に追加予定。
