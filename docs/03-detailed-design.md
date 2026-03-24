# 詳細設計書

> draftml — AutoCAD → FreeCAD + Claude Code MCP 移行プロジェクト

**最終更新**: 2026-03-23
**ステータス**: スケルトン（Phase 1 PoC の結果を反映しながら段階的に詳細化する）

---

> **注意**: 本書は PoC（B-2）の結果を反映しながら育てるドキュメントです。
> 各セクションの `<!-- TODO -->` は、Phase 1 の該当タスク完了後に記載してください。

---

## 1. パラメトリックモデル設計

### 1.1 Spreadsheet スキーマ

FreeCAD Spreadsheet ワークベンチで管理するパラメータの定義。

| セル  | パラメータ名 | 型     | 単位 | 説明       | 制約 |
| ----- | ------------ | ------ | ---- | ---------- | ---- |
| A2/B2 | Width        | 数値   | mm   | 製品の幅   | > 0  |
| A3/B3 | Height       | 数値   | mm   | 製品の高さ | > 0  |
| A4/B4 | Length       | 数値   | mm   | 製品の長さ | > 0  |
| A5/B5 | Thickness    | 数値   | mm   | 板厚       | > 0  |
| A6/B6 | HoleDiam     | 数値   | mm   | 穴径       | >= 0 |
| A7/B7 | PartNo       | 文字列 | —    | 品番       | —    |

<!-- TODO: B-2 PoC の結果に基づき、実際に必要なパラメータを追加・修正する -->

### 1.2 products.csv スキーマ

一括生成パイプライン（C-1）で使用する品番リストの列定義。

| 列名      | 型     | 必須   | 説明                            | 例             |
| --------- | ------ | ------ | ------------------------------- | -------------- |
| part_no   | 文字列 | はい   | 品番（出力ファイル名に使用）    | C-100-50-20-32 |
| width     | 数値   | はい   | 幅 (mm)                         | 100            |
| height    | 数値   | はい   | 高さ (mm)                       | 50             |
| length    | 数値   | はい   | 長さ (mm)                       | 2000           |
| thickness | 数値   | はい   | 板厚 (mm)                       | 3.2            |
| hole_diam | 数値   | いいえ | 穴径 (mm)。0 または空欄は穴なし | 13             |

<!-- TODO: C-1 パイプライン構築時に、実際の製品データに合わせて列を追加する -->

### 1.3 PartDesign スケッチ ← Spreadsheet バインディング

PartDesign のスケッチ寸法と Spreadsheet セルのバインディング定義。

<!-- TODO: B-2 PoC で実際のモデルを作成した後に、バインディング一覧を記載する -->

```
例:
Sketch.Width  = Spreadsheet.Width
Sketch.Height = Spreadsheet.Height
Pad.Length    = Spreadsheet.Length
```

---

## 2. 図面テンプレート設計

### 2.1 図枠 SVG 仕様

| 項目       | 値                                                          |
| ---------- | ----------------------------------------------------------- |
| サイズ     | A3 横（420 x 297 mm）                                       |
| フォント   | Noto Sans CJK JP（元テンプレートは MS Gothic + ARIALN.TTF） |
| 配置先     | `templates/frame_a3_landscape.svg`                          |
| 元ファイル | 社内 AutoCAD テンプレート（.reference/ に保管）             |
| 元ブロック | 社内標準図枠ブロック（94要素）                              |

**表題欄の構成**（AutoCAD ATTDEF → FreeCAD TechDraw 変数へのマッピング）:

| AutoCAD 属性タグ | 内容             | FreeCAD TechDraw 変数       |
| ---------------- | ---------------- | --------------------------- |
| —                | 会社名（固定）   | —（SVG固定テキスト）        |
| TITLE/NAME       | 図面タイトル     | `FC:Title`                  |
| DOC.NO.          | ドキュメント番号 | `FC:DrawingNo`              |
| NAME             | 作成者           | `FC:Author`                 |
| DATE             | 日付             | `FC:Date`                   |
| APPBY            | 承認者           | `FC:ApprovedBy`（カスタム） |
| NO.              | シート番号       | `FC:SheetNo`（カスタム）    |
| TOTAL            | 総シート数       | `FC:SheetTotal`（カスタム） |
| REV.NOTE         | 改訂メモ（2欄）  | `FC:Revision`               |

### 2.2 TechDraw ビュー配置ルール

<!-- TODO: B-2 PoC の結果に基づき、最適な配置座標を記載する -->

| ビュー | 投影方向 | 配置位置（案） | スケール |
| ------ | -------- | -------------- | -------- |
| 正面図 | Front    | 左上           | 1:1      |
| 側面図 | Right    | 右上           | 1:1      |
| 上面図 | Top      | 左下           | 1:1      |
| 断面図 | Section  | 右下           | 1:1      |

---

## 3. 自動化パイプライン設計

### 3.1 一括生成フロー

```
1. products.csv を読み込む
2. 各行について:
   a. Spreadsheet にパラメータを設定
   a'. パラメータ範囲チェック（幅/高さ/長さ > 0、板厚の上下限）
   b. PartDesign モデルを再計算（recompute）
   b'. Shape.isValid() チェック + BoundBox 寸法照合
   c. TechDraw ページを更新
   d. PDF / DXF をエクスポート
   e. output/{品番}.pdf, output/{品番}.dxf として保存
3. 処理結果のサマリーを出力（成功数 / 失敗数 / 品質チェック警告数 / エラー詳細）
```

**エラーハンドリング方針**:

- 1品番の処理に失敗しても、残りの品番は継続して処理する
- 失敗した品番はエラーログに記録し、最後にサマリーとして出力する

<!-- TODO: C-1 パイプライン構築時に、実装の詳細を追記する -->

### 3.2 スクリプト構成

| スクリプト                    | 役割               | 入力               | 出力                       |
| ----------------------------- | ------------------ | ------------------ | -------------------------- |
| `scripts/generate_drawing.py` | 単一品番の図面生成 | パラメータ（引数） | PDF / DXF                  |
| `scripts/batch_generate.py`   | CSV一括処理        | products.csv       | output/_.pdf, output/_.dxf |
| `scripts/convert_dwg.py`      | DWG→DXF一括変換    | DWGフォルダパス    | DXFファイル群              |

<!-- TODO: C-1, C-3 タスク完了時に、各スクリプトの引数・オプション・使用方法を追記する -->

### 3.3 MCP 連携設計

> 2026-03-23 調査結果（18リポジトリ・6記事）を反映。execute_python 優先原則を採用。

#### 利用可能ツール（contextform/freecad-mcp）

| ツール                     | 用途                      | 使用方針                              |
| -------------------------- | ------------------------- | ------------------------------------- |
| `check_freecad_connection` | 接続確認                  | セッション開始時に必ず実行            |
| `test_echo`                | エコーテスト              | デバッグ時のみ                        |
| `part_operations`          | Part 操作                 | 単純な形状作成に使用                  |
| `partdesign_operations`    | PartDesign 操作           | スケッチベースのモデリングに使用      |
| `view_control`             | ビュー / ドキュメント操作 | **screenshot 操作は使用禁止**（後述） |
| `execute_python`           | Python 実行               | **最優先ツール**（後述）              |
| `continue_selection`       | インタラクティブ選択      | エッジ / フェース選択後の処理         |

#### execute_python 優先原則

調査の結果、MCP 経由の CAD 操作は `execute_python` による直接 Python 実行が最も柔軟で信頼性が高いことが判明（bonninr/freecad_mcp の 2 ツール設計が証明）。

**方針**: 複雑な操作は `execute_python` を使用。MCP 専用ツールは単純操作のみ。

| 操作               | 使用ツール                         | 理由                                 |
| ------------------ | ---------------------------------- | ------------------------------------ |
| ドキュメント作成   | `view_control`                     | 単純操作                             |
| Box / Cylinder作成 | `part_operations`                  | 単純操作                             |
| TechDraw 作成      | **`execute_python`**               | MCP 専用ツールなし                   |
| PDF 出力           | **`execute_python`**               | MCP 専用ツールなし                   |
| スクリーンショット | **`execute_python`** (`saveImage`) | `view_control screenshot` は使用禁止 |
| パラメータ一括設定 | **`execute_python`**               | Spreadsheet 操作は MCP ツールなし    |
| 品質チェック       | **`execute_python`**               | カスタムロジック                     |

#### テキストベース状態確認パターン

`view_control(operation: screenshot)` は base64 画像が会話コンテキストに混入しセッションが復旧不能になるため、**使用禁止**。

代わりに以下の 2 段階で状態を確認する:

**Step 1: テキストベース確認（主）**

```python
doc = FreeCAD.ActiveDocument
for obj in doc.Objects:
    if hasattr(obj, 'Shape'):
        bb = obj.Shape.BoundBox
        print(f"{obj.Name}: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
        print(f"  Volume: {obj.Shape.Volume:.1f} mm3, Valid: {obj.Shape.isValid()}")
```

**Step 2: ファイル保存スクリーンショット（副）**

```python
import FreeCADGui
FreeCADGui.ActiveDocument.ActiveView.saveImage(
    "{PROJECT_ROOT}/output/screenshot.png",
    1024, 768
)
```

保存後、Claude Code の Read ツールで画像ファイルを確認する。

---

## 4. ファイル命名規則

| 種別                | パターン                    | 例                       |
| ------------------- | --------------------------- | ------------------------ |
| 出力図面（PDF）     | `{品番}.pdf`                | `C-100-50-20-32.pdf`     |
| 出力図面（DXF）     | `{品番}.dxf`                | `C-100-50-20-32.dxf`     |
| 図枠テンプレート    | `frame_{サイズ}_{向き}.svg` | `frame_a3_landscape.svg` |
| FreeCADプロジェクト | `{品番}.FCStd`              | `C-100-50-20-32.FCStd`   |
| 変換済みDXF         | `{元ファイル名}.dxf`        | `existing_drawing.dxf`   |

---

## 5. プロンプトテンプレート設計

Claude Code への標準的な指示パターン。B-2 PoC および C-1 パイプライン構築で検証済み。

### 5.1 基本原則（execute_python 優先）

複雑な操作は `execute_python` で Python スクリプトを直接実行する。MCP の個別ツール（`part_operations` 等）は単純な操作のみに使用する。

**理由**: MCP ツールは1操作ずつ応答待ちが発生し、レスポンスオフセット（N回目のリクエストに N-1回目の結果が返る）が起きやすい。`execute_python` なら一括実行で確実。

### 5.2 検証済みプロンプトテンプレート

| 操作                   | テンプレート                                                                                                                                     | 検証状況                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| C チャンネル 3D モデル | `execute_python で C チャンネルを作成して。Part API の 12 点ポリゴン押し出しで。幅:[W]mm / 高さ:[H]mm / リップ:[Lp]mm / 板厚:[T]mm / 長さ:[L]mm` | B-2 で検証済み            |
| 製造図面生成           | `TechDraw で A3 横の製造図面を作成して。正面図(1:10)・上面図(1:10)・側面図(1:10)・断面図(1:1)、5 寸法を記入して PDF と DXF で出力`               | B-2 で検証済み            |
| CSV 一括生成           | `products.csv を読み込み、各行の仕様で図面を一括生成して output/ に保存して。scripts/batch_generate.py を使用`                                   | C-1 で検証済み(5品番)     |
| 品質チェック           | `生成した 3D モデルの Shape.isValid()、BoundBox、Volume を検証して`                                                                              | B-2/C-1 で 8 項目検証済み |

### 5.3 execute_python 使用時の注意事項

| 項目               | 内容                                                                                   |
| ------------------ | -------------------------------------------------------------------------------------- |
| 文字コード         | ASCII のみ（cp932 制約）。日本語コメント禁止                                           |
| GUI 更新           | `FreeCADGui.updateGui()` + `time.sleep(0.3)` を TechDraw 操作前に挿入                  |
| スクリーンショット | `view_control(screenshot)` は使用禁止（base64 でコンテキスト汚染）                     |
| 結果確認           | ファイル出力で検証。レスポンスオフセットに注意                                         |
| テンプレート       | `FreeCAD.getResourceDir() + "Mod/TechDraw/Templates/A3_Landscape_ISO5457_minimal.svg"` |

### 5.4 スケール自動選択ルール

| 部材長さ | スケール | 用途                               |
| -------- | -------- | ---------------------------------- |
| > 2000mm | 1:10     | 長尺部材（C チャンネル 3000mm 等） |
| > 500mm  | 1:5      | 中尺部材                           |
| <= 500mm | 1:2      | 短尺部材                           |
| 断面図   | 1:1      | 常に原寸（EndView）                |

### 5.5 ビュー配置座標（A3 横 420x297mm）

| ビュー    | 投影方向 | スケール | X   | Y   |
| --------- | -------- | -------- | --- | --- |
| FrontView | (0,-1,0) | auto     | 210 | 230 |
| TopView   | (0,0,-1) | auto     | 210 | 195 |
| RightView | (1,0,0)  | auto     | 60  | 150 |
| EndView   | (0,0,1)  | 1:1      | 280 | 80  |

---

_本書は Phase 1 の作業進行に伴い、PoC 結果・パイプライン実装の詳細を反映して更新済み。_
