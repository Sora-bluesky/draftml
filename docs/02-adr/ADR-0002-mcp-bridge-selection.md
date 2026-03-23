# ADR-0002: MCPブリッジの選定

- **日付**: 2026-03-23
- **ステータス**: accepted
- **決定者**: AI変革推進担当

## 背景

ADR-0001 で FreeCAD 1.0 の採用が決定した。次に、Claude Code と FreeCAD を接続するための MCP（Model Context Protocol）ブリッジの選定が必要となった。

MCPブリッジは、自然言語の指示を FreeCAD の操作に変換する役割を担い、BR-2（製造図面作図の60〜80%自動化）の実現に不可欠なコンポーネントである。

## 決定内容

**contextform/freecad-mcp** を推奨版として採用し、**neka-nat/freecad-mcp** をバックアップ版として併用する。

## 検討した代替案

### 1. contextform/freecad-mcp（推奨版として採用）

- メリット: Claude Code 標準対応・推奨、npm ベースの簡易インストール（`npx freecad-mcp-setup setup`）、AICopilot ワークベンチによる GUI統合
- デメリット: 比較的新しいプロジェクトであり、安定性の検証が必要
- GitHub: https://github.com/contextform/freecad-mcp

### 2. neka-nat/freecad-mcp（バックアップ版として採用）

- メリット: 安定版の実績、Claude Desktop 対応、`uvx` による簡易起動
- デメリット: Claude Code との統合が contextform 版ほど密ではない
- GitHub: https://github.com/neka-nat/freecad-mcp

### 3. 独自MCP開発

- メリット: 自社要件に完全最適化可能
- デメリット: **開発コスト・期間が大きい**、個人開発者のリソースでは現実的でない

## 選定理由

1. **二段構え戦略**: 推奨版とバックアップ版の2つを確保することで、片方が動作しない場合のリスクを軽減する
2. **contextform 版の優位性**: Claude Code 公式で推奨されており、セットアップが最も簡単（npm install → setup コマンド1つ）
3. **neka-nat 版の安定性**: 先行してリリースされており、動作実績がある。contextform 版で問題が発生した場合の即時切替が可能
4. **独自開発の回避**: 個人開発者のリソースを考慮し、既存のオープンソースMCPを活用する方針（コスト意識）

## リスクと軽減策

| リスク                                             | 影響度 | 軽減策                                                            |
| -------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| contextform 版の接続が不安定                       | 中     | neka-nat 版にフォールバック。切替手順を `04-operations.md` に記載 |
| 両方のMCPが FreeCAD のバージョンアップに追従しない | 低     | FreeCAD のバージョンを固定運用。アップデート前に MCP 互換性を確認 |
| RPC サーバーが予期せず停止する                     | 中     | FreeCAD 再起動 → RPC サーバー再起動の手順を標準化                 |

## 結果・影響

- Phase 1 環境構築では contextform 版を先にインストール（A-2）、neka-nat 版を後にインストール（A-3）
- 接続確認テスト（B-1）は contextform 版で実施。失敗した場合のみ neka-nat 版に切替
- MCP設定は `.mcp.json` でリポジトリ内に管理する
- Claude Desktop を使用する場合は neka-nat 版の `claude_desktop_config.json` 設定を使用する

---

_情報源: `.reference/handover.md` §1.3, §A-2, §A-3_
