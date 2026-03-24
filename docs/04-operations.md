# 運用・保守手順書

> draftml — AutoCAD → FreeCAD + Claude Code MCP 移行プロジェクト

**最終更新**: 2026-03-23
**ステータス**: スケルトン（Phase 1 完了後に運用実績を反映して整理する）

---

> **注意**: 本書は Phase 1 完了後に整理するドキュメントです。
> 環境構築手順は handover.md から先行転記しています。

---

## 1. 環境構築手順

### 1.1 FreeCAD 1.0 のインストール（A-1）

1. https://www.freecad.org/downloads.php から最新版（1.0以上）をダウンロード
2. インストーラーを実行（デフォルト設定でOK）
3. 初回起動時に単位系を設定: `Edit > Preferences > General > Units > Metric (mm/kg/s/degree)`
4. 確認: `Help > About` でバージョンが 1.0 以上であること

### 1.2 contextform/freecad-mcp のインストール（A-2）

**前提条件**: Node.js 18 以上がインストール済みであること

```bash
npm install -g freecad-mcp-setup@latest
npx freecad-mcp-setup setup
```

**FreeCAD 側設定**:

1. FreeCAD を起動
2. ワークベンチ一覧から `AICopilot` を選択
3. `FreeCAD MCP メニュー > Start RPC Server` をクリック
4. ステータスバーに `RPC Server: Running` が表示されることを確認

**確認**:

```bash
claude mcp list
# freecad が一覧に含まれていればOK
```

### 1.3 neka-nat/freecad-mcp のインストール（A-3、バックアップ用）

**前提条件**: uv がインストール済みであること（`pip install uv`）

Claude Desktop 設定（`claude_desktop_config.json` に追記）:

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uvx",
      "args": ["freecad-mcp"]
    }
  }
}
```

### 1.4 ODA File Converter のインストール（A-4）

1. https://www.opendesign.com/guestfiles/oda_file_converter からダウンロード（無料・要メール登録）
2. インストール後、GUI で以下を設定:
   - Input Folder: 変換対象 DWG フォルダ
   - Output Format: DXF
   - Recurse: チェック（サブフォルダも変換）

---

## 2. 日常運用

### 2.1 新規図面作成フロー

<!-- TODO: Phase 1 PoC 完了後に、検証済みの手順を記載する -->

```
1. FreeCAD を起動し、RPC サーバーを開始
2. Claude Code で製品の仕様を指示
3. 生成された図面を目視確認
4. PDF / DXF で出力
```

### 2.2 一括生成フロー

<!-- TODO: C-1 パイプライン構築後に、実際の手順を記載する -->

```
1. products.csv に品番データを準備
2. FreeCAD を起動し、RPC サーバーを開始
3. batch_generate.py を実行
4. output/ フォルダの生成結果を確認
```

### 2.3 既存 DWG 変換フロー

<!-- TODO: C-3 DWG一括変換後に、実際の手順と注意点を記載する -->

```
1. ODA File Converter で DWG → DXF に変換
2. FreeCAD で DXF を開いて目視確認
3. ジオメトリに問題がある場合は Claude Code で再モデリング
```

---

## 3. トラブルシューティング

handover.md §4 から転記・構造化。Phase 1 の運用を通じて拡充する。

### 3.1 MCP 接続エラー

| 症状                                        | 原因                           | 対処                                                                        |
| ------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------- |
| Claude Code から FreeCAD を操作できない     | RPC サーバーが起動していない   | FreeCAD で `FreeCAD MCP メニュー > Start RPC Server` を実行                 |
| RPC サーバー起動済みだが応答しない          | FreeCAD がフリーズしている     | FreeCAD を再起動し、RPC サーバーを再起動                                    |
| contextform 版で接続できない                | MCP設定の問題                  | `claude mcp list` で確認。neka-nat 版（A-3）に切替                          |
| `view_control(screenshot)` でセッション破壊 | base64画像がコンテキストに混入 | **使用禁止**。テキストベース確認（`execute_python`）+ ファイル保存SS を使用 |

### 3.2 DXF 出力の不具合

| 症状                               | 原因               | 対処                                               |
| ---------------------------------- | ------------------ | -------------------------------------------------- |
| 寸法テキストが表示されない         | DXF ビューアの設定 | QCAD で開いて Property Editor から Auto 表示に変更 |
| 寸法テキストが表示されない（代替） | DXF の制限         | PDF 出力を主として使用する                         |

### 3.3 DWG 変換後の不具合

| 症状                   | 原因                     | 対処                                 |
| ---------------------- | ------------------------ | ------------------------------------ |
| ジオメトリが崩れる     | 複雑な 3D 要素の変換失敗 | Claude Code に 3D 再モデリングを指示 |
| テキストが文字化けする | フォントの不一致         | FreeCAD でフォントを手動設定         |

### 3.4 FreeCAD の動作問題

<!-- TODO: Phase 1 で遭遇した問題を追記する -->

| 症状                            | 原因                       | 対処                                |
| ------------------------------- | -------------------------- | ----------------------------------- |
| FreeCAD が起動しない            | —                          | 再インストール                      |
| モデルの再計算が失敗する        | —                          | スケッチの拘束を確認                |
| `execute_python` で文字化けする | cp932 エンコーディング問題 | Python コードに日本語を含めないこと |

---

## 4. バックアップ・リカバリ

### 4.1 自動バックアップ設定

FreeCAD の自動バックアップを有効化:

- `Preferences > General > Document > Auto save`: ON
- 間隔: 5分

### 4.2 ファイルの管理方針

| ファイル種別                     | バックアップ方法                          | 保管場所                        |
| -------------------------------- | ----------------------------------------- | ------------------------------- |
| FreeCAD プロジェクト（`.FCStd`） | Git + 自動バックアップ                    | リポジトリ + ローカル           |
| 出力ファイル（PDF/DXF）          | 再生成可能（ソースは CSV + テンプレート） | output/（必要に応じて外部保管） |
| 自動化スクリプト                 | Git                                       | リポジトリ                      |
| products.csv                     | Git                                       | リポジトリ                      |

---

## 5. バージョン管理

### 5.1 アップデート手順

FreeCAD や MCP のアップデート前に必ず確認すること:

1. **現行バージョンを記録する**: FreeCAD、MCP、ODA File Converter のバージョンをメモ
2. **検証環境で動作確認**: 可能であれば別環境でアップデート後の動作を確認
3. **バックアップを取得**: 現行の FreeCAD プロジェクトファイルをバックアップ
4. **アップデートを実行**: 上記を確認した上で実行
5. **動作確認**: B-1 の接続確認テスト（5ステップ）を再実施

### 5.2 互換性チェックリスト

| 項目                  | 確認内容                                   |
| --------------------- | ------------------------------------------ |
| FreeCAD ↔ MCP         | RPC 接続が正常に動作するか                 |
| FreeCAD ↔ TechDraw    | 既存テンプレートで図面が正しく生成されるか |
| FreeCAD ↔ Spreadsheet | パラメータバインディングが維持されているか |
| スクリプト            | Python API の互換性が保たれているか        |
| ODA File Converter    | DWG → DXF 変換が正常に動作するか           |

---

_本書は Phase 1 完了後に運用実績を反映して整理・拡充されます。_
