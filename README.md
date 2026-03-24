# draftml

AutoCAD から FreeCAD + Claude Code MCP への移行による、建材製造図面の作図自動化プロジェクト。

## 目標

1. AutoCAD ライセンス費の完全廃止
2. Claude Code MCP による製造図面作図の 60〜80% 自動化

## 技術スタック

| コンポーネント | ツール                                                                         |
| -------------- | ------------------------------------------------------------------------------ |
| CAD エンジン   | [FreeCAD 1.0](https://www.freecad.org/)                                        |
| AI連携         | [contextform/freecad-mcp](https://github.com/contextform/freecad-mcp)          |
| DWG変換        | [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) |
| 自動化         | Python（FreeCAD 内蔵）                                                         |

## ドキュメント

- [要件定義書](docs/00-requirements.md)
- [システム全体像](docs/01-system-context.md)
- [ADR（技術選定記録）](docs/02-adr/)
- [詳細設計書](docs/03-detailed-design.md)
- [運用・保守手順書](docs/04-operations.md)
- [リリース計画](docs/05-release-plan.md)

## セットアップ

1. [FreeCAD 1.0](https://www.freecad.org/downloads.php) をインストール
2. MCP ブリッジをインストール: `npm install -g freecad-mcp-setup@latest && npx freecad-mcp-setup setup`
3. FreeCAD で AICopilot ワークベンチから RPC サーバーを起動

詳細は [運用・保守手順書](docs/04-operations.md) を参照。

## ライセンス

MIT
