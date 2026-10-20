---
name: churatabi-pixel-artist
description: ちゅらたびの主人公を32x48px実ピクセルで制作し、4方向原画から歩行12コマへ一括変換・自動品質検査・ゲーム用シート化する時に使うPython Skill。
---

# ちゅらたび Pixel Artist v2 — 一括制作Skill

## 最重要ルール
- ユーザーに手作業のピクセル修正を求めない。画像制作、修正、検証はAIが担当する。
- 既存の主人公原画があるときは、その絵柄・服・髪・顔を基準にする。デモ主人公で置き換えない。
- メインの実行スクリプトは scripts/run_pipeline.py。リサイズ・コマ生成・QA・出力を一度に呼び出す。
- 原画の特徴を保持した32x48ドットへの完全自動再描画は、まだ実装されていない。現在の工程は機械的補正＋脚移動による歩行試作で、採用前の目視修正が必要。
- 自動QAが合格しても製品版とは呼ばない。DRAFT_VISUAL_REVIEW_REQUIRED として出力する。
- 正面1枚から見えない背面・左右をPythonだけで正確に復元したと主張しない。4方向の原画がなければ生成ツールで不足分を準備するか不足を報告する。

## 準拠する規格
- 寸法：32×48px、原寸の透過PNG、RGBAアルファ0/255。
- 方向：front/back/left/right。ポーズ：walk1/idle/walk2。合計12コマ。
- 外郭：#2B1410、瞳：#1A1A1A。左上光源、共通色は config.json、靴底基準y=47。
- プロジェクトに art/hd/hd-art-guide.md があれば読み、最新の対象素材の規格と差分を照合する。存在しなければ無いことを記録する。
- すべての出力画像はnearest-neighborで表示し、iPhone Safariでの見え方は別途確認する。

## 1コマンドで順番に処理
最初にPython Pillowの依存を満たす。

    python -m pip install -r requirements.txt

入力フォルダに次の4画像を置く（拡張子png/webp/jpg/jpeg、_idle名でもよい）。

    original_4views/front.png
    original_4views/back.png
    original_4views/left.png
    original_4views/right.png

実行：

    python scripts/run_pipeline.py --input-dir original_4views --output output/draft_v2

この1コマンドで以下を順に行う。
1. 4方向の入力画像と出力先の安全性を確認する。
2. resize_sprite.process_image により切り出し→縦横比保持→32x48→透過/パレット変換→輪郭→足元合わせを行う。既存線画ではinside輪郭を既定にする。
3. 正面の瞳を左右対称の規定位置へ補正する。原画の目の同一性を保証する工程ではない。
4. 静止画4方向から下半身をドット単位で移動し、歩行試作のwalk1/idle/walk2を作る。
5. sprite_pipeline.run_validate で12コマ全ての寸法・アルファ・外郭・色・靴底・瞳・重複を検査。失敗したら品質レポートを保存し、原因を修正して再実行する。
6. QA合格なら spritesheet.png (96x192)、spritesheet.json、方向別GIF、4倍プレビューを出す。
7. manifest.json と quality.json に変換情報と検査結果を記録する。

## 出力と品質の取り扱い
- normalized/：4方向の正規化した静止画像。
- frames/：32x48の12枚。
- export/spritesheet.png：96x192（3列 x 4行）。
- export/spritesheet.json：フレーム一覧と方向別アニメーション定義。
- export/front.gif、back.gif、left.gif、right.gif：確認用の歩行GIF。
- export/preview_x4.png：4倍拡大のチェック画像。
- quality.json：機械検査、manifest.json：入力と変換記録。
- ステータスはDRAFT_VISUAL_REVIEW_REQUIRED。自動検査通過は採用許可ではない。

## AIが行う採用前の視覚確認
- 原画と同じ人物に見えるか、黒髪・白Tシャツ・青短パン・リュック・靴の特徴が残っているか。
- 目の左右対称だけでなく表情が生きているか。
- 足が地面を滑らないか、上半身や手の振りに不自然さがないか。
- 4方向で頭身・バッグの位置・頭頂と靴底が一致しているか。
- 縮小による潰れ・色混入を検出したらPython描画や画像生成で再作画し、再検査する。
- 仮素材は勝手に既存ゲームへ上書きせず、承認したものだけ art/hd/chars/ に移す。

## 失敗時
- 4方向が足りない：見つからない方向を明示する。AIで不足方向を作れない環境では停止する。
- 背景が複雑：透過素材を別途用意するか、単色のみ--background指定で除去。
- 出力先に既存ファイル：保護して停止。必要なら新しい出力先を指定。明示的な上書きのみ--overwrite。
- 不合格の修正方法を推定し、AI自身が元画像・コードを修正して検査し直す。不可能な場合はエラーを隠さない。

## 補助コマンド
    python scripts/create_hero.py --output examples/hero_demo
    python scripts/resize_sprite.py --input source.png --output draft/front.png
    python scripts/sprite_pipeline.py validate --input output/frames --report output/quality.json
    python -m unittest discover -s tests -v

create_hero.pyは座標定義済みのデモ用主人公であり、任意の原画の再描画装置ではない。
