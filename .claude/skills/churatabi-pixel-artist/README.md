# ちゅらたび Pixel Artist Skill v1.1

Claude Code / Codex / Agent Skills 形式に対応する `SKILL.md` + Python ツール一式。

## Claude Code の導入
このフォルダ `churatabi-pixel-artist` を、プロジェクトの `.claude/skills/` に置く。Claude Code から `/churatabi-pixel-artist` を呼び出すか、キャラのスプライト制作を依頼する。Pillow は `python -m pip install -r .claude/skills/churatabi-pixel-artist/requirements.txt` で導入する。

## Codex の導入
同じフォルダをプロジェクトの `.agents/skills/` に置く。`SKILL.md` を読ませる。Codex のワークフローでもコマンドを実行できる。

## 追加したPython部品
`scripts/create_hero.py` は主人公v1の再生成・品質検査・書き出し用。 `scripts/sprite_pipeline.py` は共通の検査・シート作成・GIF出力用です。画像生成AIが出した画像を機械的に縮小して完成扱いにはしません。

```bash
# Skill フォルダ内から実行
python -m pip install -r requirements.txt
python scripts/create_hero.py --output examples/hero_v1
python -m unittest discover -s tests -v
```

出力: `examples/hero_v1/frames/` に32x48透過PNG×12、 `export/` に96x192シート、フレーム定義JSON、歩行GIF・4倍プレビュー、 `quality.json` に自動検査結果。既存ゲームの画像そのものと同一という保証はないため、採用には目視検査が必要です。

## Skill単体の動作確認
```bash
python -m pip install -r requirements.txt
python scripts/sprite_pipeline.py demo --output examples/generated
python -m unittest discover -s tests -v
```

動作確認で生成されるデモPNGは仮のサンプルキャラクターであり、既存主人公アセットの代替ではありません。

## 安全性
外部通信・認証情報へのアクセスはしない。画像はユーザーのローカルファイルから処理する。既存ファイルはコマンドで明示的に指定した出力先以外変更しない。出力ディレクトリ上に同名ファイルがある場合は上書きされるため、プロジェクトでは新規作業ディレクトリを使う。
