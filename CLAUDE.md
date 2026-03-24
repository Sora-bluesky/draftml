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

## 設計駆動開発ルール（Design-Driven Development）

### 原則: spec.yaml が唯一の実装仕様

`docs/spec.yaml` は設計の機械検証可能な部分を定義する。`check_progress.py` がこのファイルを読み取り、実装との整合性を自動検証する。

1. **spec.yaml に存在しないスクリプトを新規作成してはならない**
   - 新規スクリプトが必要な場合、先に spec.yaml に `status: planned` で登録する
   - 登録後に実装を開始し、完了したら `status: implemented` に更新する

2. **spec.yaml に存在しないパラメトリック寸法を実装してはならない**
   - `parametric_model` セクションのインデックスと完全一致すること
   - 追加寸法が必要と判明した場合、spec.yaml を先に更新する

3. **マイルストーンの依存関係を飛ばしてはならない**
   - `check_progress.py --gate <MS>` が PASS するまで次の MS に着手不可

4. **`git add -f docs/` および `git add -f scripts/` を実行してはならない**
   - .gitignore による除外を強制突破する操作は禁止

### セッション開始時の必須手順

```bash
# Step 1: 進捗自動更新 + 設計ヘルスチェック（ハードゲート）
python tasks/check_progress.py --apply --strict
```

- **FAIL の場合**: 設計と実装の乖離を修正するまで新規実装に着手しない
- **WARN の場合**: 設計 TODO の存在を認識した上で作業開始可能
- **PASS の場合**: HANDOFF.md の Next Tasks に従って実装を開始する

### spec.yaml 更新ルール

| タイミング                       | 操作                                           |
| -------------------------------- | ---------------------------------------------- |
| 新規スクリプト作成前             | spec.yaml に `status: planned` で追加          |
| スクリプト実装完了後             | spec.yaml の `status` を `implemented` に変更  |
| パラメトリック寸法の追加・変更時 | spec.yaml の `parametric_model` を先に更新     |
| マイルストーン完了時             | `check_progress.py --gate <MS>` を実行して記録 |

## 検証コマンド

### 進捗自動更新 + 設計ゲート

セッション開始時に以下を実行:

```bash
python tasks/check_progress.py --apply --strict
```

- Phase 1: タスク完了条件をファイルシステムの実態から自動判定
- Phase 2: `docs/spec.yaml` と実装の整合性を検証
- `--strict`: FAIL があれば exit 1（ハードゲート）
- `--gate M7`: 特定マイルストーンの成果物をチェック
- MCP接続チェックは `check_freecad_connection` で別途実施

### コミット前検証

git-guard（グローバル pre-commit hook）が自動実行される。シークレット・個人情報の混入を検出してコミットを拒否する。
