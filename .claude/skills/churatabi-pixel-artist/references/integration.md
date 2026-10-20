# Webゲーム実装サンプル

`spritesheet.png` は3列×4行、1セル32x48。0始まり、行の並びは front / back / left / right。各行は walk1 / idle / walk2。`spritesheet.json` に同じ並びを記録。

## Phaser 3
```js
this.load.spritesheet('hero', 'art/hd/chars/spritesheet.png', {
  frameWidth: 32,
  frameHeight: 48
});
// spriteSheet.json の animations.front 等がフレームを指定
this.anims.create({
  key: 'hero-walk-front',
  frames: this.anims.generateFrameNumbers('hero', { frames: [0, 1, 2, 1] }),
  frameRate: 6,
  repeat: -1
});
// 静止正面: hero.setFrame(1)
// カメラ/Canvasの拡大は整数倍に。描画の補間は無効に。
```

## Canvas 2D
```js
ctx.imageSmoothingEnabled = false;
const col = 1; // idle
const row = 0; // front
ctx.drawImage(sheet, col*32, row*48, 32, 48, dx, dy, 128, 192);
```
