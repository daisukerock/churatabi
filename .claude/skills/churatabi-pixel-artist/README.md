# ちゅらたび Pixel Artist Skill v2.0

4方向のキャラクター原画から、原寸32x48pxの歩行12コマ、品質検査、ゲーム用スプライトシートまでを1回のPython実行で制作するSkill。

## インストール
このフォルダをClaude Codeプロジェクトの .claude/skills/churatabi-pixel-artist/ に置きます。すでに本リポジトリには追加済みです。

## 実行（Skillフォルダ内から）
初回だけ依存を導入：

    python -m pip install -r requirements.txt

4方向の原画を source_4views/ に準備。必要な名前：

    source_4views/front.png
    source_4views/back.png
    source_4views/left.png
    source_4views/right.png

一括実行：

    python scripts/run_pipeline.py --input-dir source_4views --output output/hero_draft_v2

正常終了すると：
- output/hero_draft_v2/normalized/：4方向のリサイズ済み原画
- output/hero_draft_v2/frames/：歩行12コマ
- output/hero_draft_v2/export/：96x192シート、JSON、GIF、4倍プレビュー
- output/hero_draft_v2/quality.json、manifest.json：QAと変換記録

## テスト

    python -m unittest discover -s tests -v

## 主な部品
- scripts/run_pipeline.py：原画を入力し、処理をすべて順番に実行する中心プログラム
- scripts/resize_sprite.py：リサイズ、透過、1px外郭、足元合わせ、パレット処理
- scripts/sprite_pipeline.py：12コマの検証、PNGシート、GIF、JSON出力
- scripts/create_hero.py：事前にコード定義した主人公の12コマデモ生成
- tests/test_run_pipeline.py：端から端までの実行テスト

## 制約
自動処理は入力された4方向の絵の細部を完全に「描き直す」ものではありません。現状の歩行は脚ドットの移動で生成する試作アニメーションです。顔や腕の自然な動き、元画像への忠実さ、iPhone実機での完成品質はAIが別途目視確認・再作画します。

出力のステータスはDRAFT_VISUAL_REVIEW_REQUIREDです。原画に4方向が揃わない場合は明示的に停止し、存在しない方向を勝手に完成扱いしません。原画や既存のゲーム本体は自動で上書きしません。
