# ちゅらたび Pixel Artist Skill v1.0

Claude Code / Codex / Agent Skills 形式に対応する `SKILL.md` + Python ツール一式。

## Claude Code の導入
このフォルダ `churatabi-pixel-artist` を、プロジェクトの `.claude/skills/` に置く。Claude Code から `/churatabi-pixel-artist` を呼び出すか、キャラのスプライト制作を依頼する。Pillow は `python -m pip install -r .claude/skills/churatabi-pixel-artist/requirements.txt` で導入する。

## Codex の導入
同じフォルダをプロジェクトの `.agents/skills/` に置く。`SKILL.md` を読ませる。Codex のワークフローでもコマンドを実行できる。

## Skill単体の動作確認
```bash
python -m pip install -r requirements.txt
python scripts/sprite_pipeline.py demo --output examples/generated
python -m unittest discover -s tests -v
```

動作確認で生成されるデモPNGは仮のサンプルキャラクターであり、既存主人公アセットの代替ではありません。

## 安全性
外部通信・認証情報へのアクセスはしない。画像はユーザーのローカルファイルから処理する。既存ファイルはコマンドで明示的に指定した出力先以外変更しない。出力ディレクトリ上に同名ファイルがある場合は上書きされるため、プロジェクトでは新規作業ディレクトリを使う。
