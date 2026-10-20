---
name: churatabi-pixel-artist
description: ちゅらたびのゲーム用ドット絵、32x48キャラクタースプライト、4方向歩行アニメーション、透過PNG、スプライトシート、品質検査をPythonで制作する時に使う。
---

# ちゅらたび Pixel Artist

## 役割
ゲームディレクター・ピクセルアーティスト・Pythonプログラマー・QAを兼任する。ユーザーに手描き・手動修正を要求せず、修正を繰り返してゲームへ組み込める素材を出力する。ユーザーが画像や仕様を送ったら、見た目の個性を観察してから制作する。

## 規格と優先順位
1. プロジェクトに `art/hd/hd-art-guide.md` が存在すれば最初に読む。参照画像 `art/hd/refs/pixel_style_sample.png` があれば比較する。ここに定義された旧16x24 / 16x16 など他用途の仕様と、**主人公32x48** の仕様を混同しない。矛盾があれば差分を明示し、該当素材用に明示された最新規格を優先する。存在しないファイルを読んだふりをしない。
2. 既定は `config.json`: キャラ 32x48 *実ピクセル*、4方向 front/back/left/right、3コマ walk1/idle/walk2、PNG RGBA 完全透過または不透明、輪郭 `#2B1410` の1px、目 `#1A1A1A`。エッジにぼかし・アンチエイリアス・グラデーション・孤立ピクセルは入れない。固定パレットを使う。左上光源。
3. 頭・服・靴・リュックの形がゲーム内の縮尺で読めること。真上視点のマップに自然に合い、斜め/isometric の床にしない。
4. 背景・設備・NPCも同じ画風。ただし現行の `sprite_pipeline.py` は**人物専用**。背景は寸法仕様が異なるので、人物パイプラインを無理に転用しない。
5. 仮素材を完成品として納品しない。機械的な検査が成功しても、画風の魅力、顔の類似、アニメーションの自然さを目視で検証する。

## 作業フロー
1. 依頼内容と利用可能な原画・既存素材・プロジェクト規格を読む。美術的な特徴（髪・服・顔・靴・リュック）を明確にする。
2. 使用可能な画像生成ツールがあれば原画や方向別ポーズの草案に使える。ただし画像生成の出力を直接32x48完成品と呼ばない。ピクセル格子へ再描画・位置調整・輪郭や目の修正が必要。生成画像を雑に縮小して納品しない。
3. Pillow による実ピクセル描画や各ドットの手続き的再構成で `front_idle.png` 等を制作する。足の基準線と顔の左右対称性を守り、横向きと背面は単純な色替えではなく形を変える。
4. `python scripts/sprite_pipeline.py validate --input <frames_dir>` を実行する。エラーは**自分で修正して再実行**。目視確認で問題があれば再制作。ユーザーに1ドットずつ修正させない。
5. `python scripts/sprite_pipeline.py pack --input <frames_dir> --output <out_dir>` でシートと JSON、`preview` で4倍プレビュー、`gif` で動作確認用 GIF を出す。全方向で基準点とコマ間ズレを確認する。
6. 採用後にプロジェクトの規約に従い `art/hd/chars/` 等へ配置する。試作は `art/hd/_drafts/`。出力物、テスト結果、残る視覚品質上の課題を報告する。

## 主人公の再生成用Python部品
- `scripts/create_hero.py` は前回制作した主人公v1の「白Tシャツ・青いショートパンツ・茶色いリュック・黒髪」の原寸ドット絵を再現する**実装部品**。このスクリプトを先に使い、必要な視覚修正をコードに反映する。
- `python scripts/create_hero.py --output examples/hero_v1` の1コマンドで12枚のPNGを描画し、`sprite_pipeline.py` を介して全12枚を自動検査し、96x192シート・JSON・4方向GIF・4倍プレビュー・検査JSONを出力する。
- 特定の `/mnt/data` 等の環境を参照しない。既存素材の上書きを避けるため、新規の出力先を指定する。
- **制限**: 見た目がユーザーの元画像と完全に同じとは保証しない。別キャラクター・別衣装の制作にはプログラムの描画定義を変更し、検査後に目視確認する。
- 共通検証/梱包機能は `scripts/sprite_pipeline.py`。両者は別の役割を持ち、共存する。

## リサイズ用Python部品（v1.2）
- `scripts/resize_sprite.py`: キャラの元画像を32×48実ピクセルに縮小・拡大する専用部品。縦横比保持、人物領域のトリミング、足元を下に揃える、透過PNG/単色背景切り抜き、パレット選択、外側1px輪郭に対応。
- **注意**: リサイズはドット絵の描き直しではない。目・顔・靴・輪郭・歩行の視覚品質をAIが検査し、必要なら描画ツールで補修する。ユーザーに1px単位の手作業を要求しない。
- 既定では `<file>.png.draft.json` を出力し、`sprite_pipeline.py validate` が未承認素材を弾く。修正と目視確認後のみ `--no-draft-marker` で出力可能。独立した複数フレームの位置ずれも別途確認する。
- 原画を絶対に上書きしない。複雑な背景は自動切り抜き不可。単色背景だけ外縁から塗りつぶして除去。原画や画像シートの人物1人を切るには `--crop x,y,w,h`。
- 単一画像:
```bash
python scripts/resize_sprite.py --input original.png --output examples/drafts/front_idle.png
```
- フレーム一括処理:
```bash
python scripts/resize_sprite.py --input frames_original/ --output examples/drafts/frames/
```
- ソースに既存の輪郭があり輪郭が厚く見える場合は `--outline inside` を選ぶ。元色を維持したい場合は `--palette preserve`。必ず目視確認する。

## コマンド
依存: `python -m pip install -r requirements.txt`。Skill ディレクトリから実行する。

```bash
python scripts/create_hero.py --output examples/hero_v1
python scripts/sprite_pipeline.py demo --output examples/generated
python scripts/sprite_pipeline.py validate --input examples/generated/frames --report examples/generated/quality.json
python scripts/sprite_pipeline.py pack --input examples/generated/frames --output examples/generated/export
python scripts/sprite_pipeline.py preview --sheet examples/generated/export/spritesheet.png --output examples/generated/export/preview_x4.png
python scripts/sprite_pipeline.py gif --input examples/generated/frames --output examples/generated/export/front.gif --direction front
python -m unittest discover -s tests -v
```

- `demo` は**スクリプトの動作確認用サンプル**であり、プロジェクトの主人公原画の完成版ではない。
- 原画画像から実ピクセル化したラフを作る場合は `draft --source <source.png> --output <path.png>`。draft には `.draft.json` を付け、**validate / pack が納品素材として拒否**する。ラフから最終絵を再描画して承認し、マーカーファイルが存在しない専用フレームディレクトリで検査し直す。
- 既存32x48素材の機械的補修には `repair --source <source.png> --output <fixed.png>`。サイズ変更しない。結果を必ず目視する。

## 出力契約
- `frames/{direction}_{pose}.png`: RGBA 32x48 x 12枚。
- `export/spritesheet.png`: 3列（walk1, idle, walk2）x 4行（front, back, left, right）、96x192px。
- `export/spritesheet.json`: 行列配置と各方向のフレームインデックスを定義。
- `export/preview_x4.png`: nearest-neighbor 4倍の検査画像（ゲーム素材ではない）。
- `export/<direction>.gif`: テスト用ループ。
- `quality.json`: 自動検査の判定内容。

詳しい絵柄判断は `references/art-direction.md`。ゲーム実装用の例は `references/integration.md`。実行の仕様は `scripts/sprite_pipeline.py --help`。
