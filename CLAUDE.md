# draftml — Claude Code プロジェクト指示書

## プロジェクト概要

AutoCAD → FreeCAD 1.0 + Claude Code MCP 移行プロジェクト。
MDF木質建材（ドア枠・窓枠等）の製造図面作図を自動化する。

## ドキュメント体系（ローカル専用・コミット対象外）

| ファイル                     | 内容                                                     |
| ---------------------------- | -------------------------------------------------------- |
| `docs/00-requirements.md`    | 要件定義書（ビジネス要件・機能要件・成功基準）           |
| `docs/01-system-context.md`  | システム全体像（コンテキスト図・データフロー）           |
| `docs/02-adr/`               | ADR（技術選定記録）                                      |
| `docs/03-detailed-design.md` | 詳細設計書（パラメトリックモデル・パイプライン設計）     |
| `docs/04-operations.md`      | 運用・保守手順書（トラブルシューティング含む）           |
| `docs/05-release-plan.md`    | リリース計画（マイルストーン・ガントチャート・進捗管理） |

> 上記はすべてローカル専用。`.gitignore` で除外済み。

## コミット対象外ポリシー

以下は絶対にコミットしないこと（2層ゲートで保護）:

| 対象                                  | 理由                                   | ゲート                    |
| ------------------------------------- | -------------------------------------- | ------------------------- |
| `docs/`                               | 内部開発資料                           | .gitignore + pre-commit   |
| `scripts/`                            | 内部スクリプト                         | .gitignore + pre-commit   |
| `HANDOFF.md`                          | セッション引き継ぎ（内部）             | .gitignore + pre-commit   |
| `.claude/`                            | Claude Code ローカル設定               | .gitignore + pre-commit   |
| `.reference/`                         | 内部資料の原本                         | .gitignore + pre-commit   |
| `tasks/`                              | 進捗管理ファイル                       | .gitignore + pre-commit   |
| `*.docx`, `*.xlsx`, `*.pptx`, `*.pdf` | バイナリ形式の内部資料                 | .gitignore + pre-commit   |
| `output/`                             | 生成図面（成果物でありソースではない） | .gitignore                |
| `.env`, `*.key`, `*.pem`, `*.secret`  | 認証情報                               | .gitignore + pre-commit   |
| プライベートパス (`C:\Users\...`)     | 個人情報                               | pre-commit (content scan) |

**ゲート構成**:

- **ゲート1**: `.gitignore` — パッシブ除外（パターンマッチ）
- **ゲート2**: `.git/hooks/pre-commit` — アクティブ検証（パス・拡張子・コンテンツスキャン）
- `--no-verify` でのバイパスは禁止

## 技術スタック

- **CAD**: FreeCAD 1.0（テンプレート設計・DXF検証）
- **図面生成**: ezdxf（Pythonライブラリ、パラメトリックDXF生成）— ADR-0003
- **MCP**: contextform/freecad-mcp（推奨）/ neka-nat/freecad-mcp（バックアップ）
- **変換**: ODA File Converter（DWG → DXF、DXF → PDF）
- **スクリプト**: Python（FreeCAD内蔵 + ezdxf）

## 検証コマンド

### 進捗自動更新

セッション開始時に以下を実行し、ロードマップを自動更新する:

```bash
python tasks/check_progress.py --apply
```

- タスク完了条件をファイルシステムの実態から自動判定
- `docs/05-release-plan.md` のチェックボックスと残タスク数を更新
- `--apply` なしでドライラン（変更せず結果のみ表示）
- MCP接続チェックは `check_freecad_connection` で別途実施

### コミット前検証

pre-commit hook が自動実行される（手動実行不要）。内部ファイルやプライベートパスの混入を検出してコミットを拒否する。
