# ちゅらたび — 那覇空港、旅のはじまり

オリジナルの到着ロビー1シーン。**完成候補 / iPhone実機未検証**。

https://daisukerock.github.io/churatabi/preview/arrival/

床をタップで移動、人・設備をタップで調べる。「いまの寄り道」を押すと目標の場所が見える。
矢印 / WASD移動、Enter / Spaceで話す。音は右上からON。進行はブラウザに保存。

## 保守・検証

配信は静的ファイルのみ。ランタイム依存・外部CDN・トラッキングなし。
リポジトリルートから `python3 -m http.server 8765 --bind 127.0.0.1` で起動。
Node 22以降とPillow、Playwright 1.62.1を使う。

```
npm install
npx playwright install chromium webkit
npm test
python3 tests/assets.py
npm run test:browser
npm run test:edge
```

既存Chromeを使う場合は `CHROME_EXECUTABLE` に実行ファイルのパスを指定できる。
ブラウザテストは別のローカルサーバーがポート8765で動いている前提。テスト専用ブラウザ内だけで操作する。
`?qa` は読み取り専用の状態確認を有効化し、ゲーム操作や状態変更は注入しない。

PNG原画の再生成は `python3 tools/draw-arrival.py`。現在の原画生成はmacOSヒラギノフォントを参照する。
フォント自体は同梱しない。再生成にそのフォントがない環境ではフォントパスを適切に変更する。

全画像とゲームの会話は本プロジェクト用に新規制作。既存ゲームからの画像流用なし。
公式サイトの写真の転載なし。効果音はWeb Audio合成。

詳細な判定と未検証項目は [制作記録](../../docs/arrival-scene-status.md)、証跡は `docs/qa/`。
