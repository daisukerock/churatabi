#!/usr/bin/env python3
"""Churatabi pixel art sprite pipeline. Dependency: Pillow.

Exports real (non-upscaled) RGBA sprites; rejects any draft marker during QA.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
W, H = CONFIG['width'], CONFIG['height']
DIRECTIONS = CONFIG['directions']
POSES = CONFIG['poses']
PALETTE = {key: value.upper() for key, value in CONFIG['palette'].items()}
OUTLINE = tuple(bytes.fromhex(PALETTE['outline'][1:]))
RGB_SET = {tuple(bytes.fromhex(code[1:])) for code in PALETTE.values()}
CLEAR = (0, 0, 0, 0)


def clr(key):
    return PALETTE[key]


def paint(d: ImageDraw.ImageDraw, box, fill, outline=True, shape='rect'):
    kw = {'fill': clr(fill)}
    if outline:
        kw['outline'] = clr('outline')
        kw['width'] = 1
    if shape == 'ellipse':
        d.ellipse(box, **kw)
    elif shape == 'poly':
        d.polygon(box, **kw)
    else:
        d.rectangle(box, **kw)


def enforce_outer_outline(img):
    """Use a 1px boundary on 8-connected silhouette; no interpolation."""
    src = img.convert('RGBA')
    pixels = src.load()
    to_ink = []
    for y in range(H):
        for x in range(W):
            if pixels[x, y][3] == 0:
                continue
            if any(
                nx < 0 or nx >= W or ny < 0 or ny >= H or pixels[nx, ny][3] == 0
                for nx, ny in [(x-1,y), (x+1,y), (x,y-1), (x,y+1), (x-1,y-1), (x+1,y+1), (x-1,y+1), (x+1,y-1)]
            ):
                to_ink.append((x, y))
    for pos in to_ink:
        pixels[pos] = (*OUTLINE, 255)
    return src


def draw_character(direction, pose):
    """Construct a deliberately small self-contained demonstration tourist sprite."""
    if direction == 'right':
        return draw_character('left', pose).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    img = Image.new('RGBA', (W, H), CLEAR)
    d = ImageDraw.Draw(img)
    stride = {'walk1': -2, 'idle': 0, 'walk2': 2}[pose]
    swing = 0 if pose == 'idle' else (1 if pose == 'walk1' else -1)
    # Draw back layer: straps, backpack and limbs.
    if direction == 'back':
        paint(d, [8, 24, 24, 37], 'backpack', shape='ellipse')
        paint(d, [11, 29, 21, 39], 'backpack')
        paint(d, [13, 31, 19, 34], 'backpack_light', outline=False)
    elif direction == 'left':
        paint(d, [19, 25, 27, 37], 'backpack', shape='ellipse')
        paint(d, [22, 29, 26, 34], 'backpack_light', outline=False)

    # Legs and shoes; exact bottom row is outline, shoe body one row higher.
    leftx = 11 + stride
    rightx = 19 - stride
    paint(d, [leftx + 1, 37, leftx + 4, 44], 'skin')
    paint(d, [rightx, 37, rightx + 3, 44], 'skin')
    paint(d, [leftx - 1, 43, leftx + 5, 47], 'shoes')
    paint(d, [rightx - 1, 43, rightx + 5, 47], 'shoes')
    paint(d, [leftx + 1, 44, leftx + 3, 45], 'shoe_light', outline=False)
    paint(d, [rightx + 1, 44, rightx + 3, 45], 'shoe_light', outline=False)
    # Arms and shirt.
    paint(d, [6, 25 + swing, 10, 35 + swing], 'skin', shape='ellipse')
    paint(d, [22, 25 - swing, 26, 35 - swing], 'skin', shape='ellipse')
    paint(d, [9, 24, 23, 37], 'white_shirt')
    paint(d, [11, 25, 12, 34], 'shirt_shadow', outline=False)
    paint(d, [20, 25, 21, 34], 'shirt_shadow', outline=False)
    # Shorts/waist.
    paint(d, [10, 36, 22, 41], 'blue')
    paint(d, [11, 37, 20, 38], 'blue_light', outline=False)
    paint(d, [16, 38, 16, 41], 'blue_shadow', outline=False)

    if direction == 'front':
        # Straps in foreground, under the head.
        paint(d, [10, 24, 11, 34], 'backpack', outline=False)
        paint(d, [21, 24, 22, 34], 'backpack', outline=False)
        paint(d, [9, 6, 24, 22], 'skin', shape='ellipse')
        paint(d, [11, 17, 12, 18], 'skin_shadow', outline=False)
        paint(d, [8, 4, 24, 12], 'hair', shape='ellipse')
        paint(d, [9, 9, 13, 13], 'hair')
        paint(d, [19, 8, 23, 12], 'hair')
        paint(d, [12, 5, 20, 7], 'hair_light', outline=False)
        d.point((12, 16), fill=clr('eyes'))
        d.point((20, 16), fill=clr('eyes'))
        d.line([(15, 19), (16, 20), (17, 19)], fill=clr('skin_shadow'), width=1)
        # collar
        paint(d, [14, 24, 18, 25], 'shirt_shadow', outline=False)
    elif direction == 'back':
        paint(d, [9, 6, 24, 23], 'hair', shape='ellipse')
        paint(d, [11, 17, 21, 22], 'hair_light', outline=False)
        paint(d, [10, 9, 23, 17], 'hair', outline=False)
        # Backpack overlays back of shirt.
        paint(d, [10, 26, 22, 38], 'backpack')
        paint(d, [12, 29, 20, 33], 'backpack_light', outline=False)
        paint(d, [12, 35, 20, 36], 'shoes', outline=False)
    elif direction == 'left':
        paint(d, [8, 8, 23, 23], 'skin', shape='ellipse')
        paint(d, [8, 5, 23, 13], 'hair', shape='ellipse')
        paint(d, [17, 5, 23, 15], 'hair')
        paint(d, [10, 5, 18, 7], 'hair_light', outline=False)
        paint(d, [9, 17, 11, 18], 'skin_light', outline=False)
        d.point((12, 16), fill=clr('eyes'))
        d.point((10, 20), fill=clr('skin_shadow'))
        paint(d, [8, 26, 10, 35], 'skin', shape='ellipse')
        paint(d, [22, 27, 27, 36], 'backpack', shape='ellipse')
        paint(d, [24, 29, 25, 32], 'backpack_light', outline=False)
    return enforce_outer_outline(img)


def marker_for(path):
    return path.with_name(path.name + '.draft.json')


def find_draft_markers(folder):
    return list(folder.glob('*.draft.json'))


def run_validate(folder, report=None):
    folder = Path(folder)
    issues = []
    marker_files = find_draft_markers(folder)
    if marker_files:
        issues.append(f'未承認draftマーカーが存在: {[p.name for p in marker_files]}')
    fingerprints = {}
    stats = {}
    for direction in DIRECTIONS:
        for pose in POSES:
            name = f'{direction}_{pose}.png'
            path = folder / name
            if not path.is_file():
                issues.append(f'{name}: ファイルがありません')
                continue
            try:
                with Image.open(path) as source:
                    fmt, origmode = source.format, source.mode
                    img = source.convert('RGBA')
            except Exception as exc:
                issues.append(f'{name}: 画像が開けません: {exc}')
                continue
            if fmt != 'PNG':
                issues.append(f'{name}: PNGではありません')
            if origmode != 'RGBA':
                issues.append(f'{name}: RGBAではありません ({origmode})')
            if img.size != (W, H):
                issues.append(f'{name}: サイズ {img.size} != {(W,H)}')
                continue
            rgba = list(img.getdata())
            visible = [(r,g,b) for r,g,b,a in rgba if a > 0]
            transparent_alphas = {a for _,_,_,a in rgba}
            if not visible:
                issues.append(f'{name}: 空画像です')
                continue
            if not transparent_alphas.issubset({0,255}):
                issues.append(f'{name}: 半透明ピクセルがあります')
            foreign = Counter(rgb for rgb in visible if rgb not in RGB_SET)
            if foreign:
                issues.append(f'{name}: パレット外の色が{sum(foreign.values())}ピクセルあります')
            pix = img.load()
            boundary_bad = 0
            for y in range(H):
                for x in range(W):
                    if pix[x,y][3] == 0:
                        continue
                    exposed = any(
                        nx < 0 or nx >= W or ny < 0 or ny >= H or pix[nx,ny][3] == 0
                        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1))
                    )
                    if exposed and pix[x,y][:3] != OUTLINE:
                        boundary_bad += 1
            if boundary_bad:
                issues.append(f'{name}: 外側輪郭の色が不正な境界ピクセル {boundary_bad}')
            if not any(pix[x,47][:3] == OUTLINE and pix[x,47][3] == 255 for x in range(W)):
                issues.append(f'{name}: y=47 の靴底輪郭がありません')
            # Foot fill must survive at y=46, not an entirely outlined bar.
            if not any(pix[x,46][3] == 255 and pix[x,46][:3] != OUTLINE for x in range(W)):
                issues.append(f'{name}: y=46 の靴塗りがありません')
            if any(pix[x,0][3] > 0 for x in range(W)):
                issues.append(f'{name}: 上端が接触しています')
            if direction == 'front':
                eyes = {(x,y) for y in range(12,22) for x in range(W) if pix[x,y][:3] == tuple(bytes.fromhex(PALETTE['eyes'][1:])) and pix[x,y][3] == 255}
                if not eyes or any((W-x, y) not in eyes for x,y in eyes):
                    issues.append(f'{name}: 正面の目が中心x=16で対称ではありません')
            if any(pix[0,y][3] > 0 or pix[W-1,y][3] > 0 for y in range(H)):
                issues.append(f'{name}: 左右端が接触しています')
            fingerprints[(direction, pose)] = img.tobytes()
            stats[name] = {'pixels': len(visible), 'colors': len(set(visible)), 'size': [W,H]}
    for direction in DIRECTIONS:
        keys = [(direction,p) for p in POSES]
        if all(k in fingerprints for k in keys):
            if len({fingerprints[k] for k in keys}) < len(keys):
                issues.append(f'{direction}: 歩行コマに重複があります')
    output = {'ok': len(issues) == 0, 'errors': issues, 'files': stats, 'checked_frames': len(stats), 'visual_review_required': True}
    if report:
        target = Path(report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


def check_or_exit(folder):
    result = run_validate(folder)
    if not result['ok']:
        raise SystemExit('品質検査NG。エラーを修正後に再実行してください。')


def pack(folder, output):
    check_or_exit(folder)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGBA', (W*len(POSES), H*len(DIRECTIONS)), CLEAR)
    animations = {}
    frames = []
    for row, direction in enumerate(DIRECTIONS):
        ids = []
        for col, pose in enumerate(POSES):
            index = row*len(POSES)+col
            src = Path(folder) / f'{direction}_{pose}.png'
            img = Image.open(src).convert('RGBA')
            sheet.paste(img, (col*W, row*H))
            ids.append(index)
            frames.append({'index': index, 'direction': direction, 'pose': pose, 'x': col*W, 'y': row*H, 'w': W, 'h': H})
        animations[direction] = {'frames': [ids[0],ids[1],ids[2],ids[1]], 'fps': CONFIG['fps'], 'idle': ids[1]}
    sheet.save(output / 'spritesheet.png')
    metadata = {'image': 'spritesheet.png', 'frameWidth': W, 'frameHeight': H, 'columns': len(POSES), 'rows': len(DIRECTIONS), 'directions': DIRECTIONS, 'poses': POSES, 'frames': frames, 'animations': animations}
    (output / 'spritesheet.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"出力: {output / 'spritesheet.png'} (96x192) / spritesheet.json")


def preview(sheetpath, dest, scale):
    with Image.open(sheetpath) as im:
        if im.size != (W*len(POSES), H*len(DIRECTIONS)):
            raise SystemExit(f'シート寸法が不正: {im.size}')
        im = im.convert('RGBA')
    canvas = Image.new('RGBA', im.size, '#E6D7BE')
    d = ImageDraw.Draw(canvas)
    for y in range(0, canvas.height, 8):
        for x in range(0, canvas.width, 8):
            if (x//8 + y//8) % 2 == 0:
                d.rectangle((x,y,x+7,y+7), fill='#F8EEDF')
    canvas.alpha_composite(im)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.resize((canvas.width*scale, canvas.height*scale), Image.Resampling.NEAREST).convert('RGB').save(dest)
    print(f'プレビュー: {dest}')


def create_gif(folder, dest, direction, scale):
    check_or_exit(folder)
    seq = ['walk1', 'idle', 'walk2', 'idle']
    images = []
    for pose in seq:
        with Image.open(Path(folder) / f'{direction}_{pose}.png') as im:
            sprite = im.convert('RGBA')
        bg = Image.new('RGBA', sprite.size, '#E6D7BE')
        bg.alpha_composite(sprite)
        images.append(bg.resize((W*scale,H*scale), Image.Resampling.NEAREST).convert('P', palette=Image.Palette.ADAPTIVE))
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(dest, save_all=True, append_images=images[1:], duration=[150,150,150,150], loop=0, disposal=2, optimize=False)
    print(f'歩行GIF: {dest}')


def demo(output):
    folder = Path(output)
    frames = folder / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    for direction in DIRECTIONS:
        for pose in POSES:
            draw_character(direction, pose).save(frames / f'{direction}_{pose}.png')
    result = run_validate(frames, folder / 'quality.json')
    if not result['ok']:
        raise SystemExit('デモ作成失敗: 品質検査NG')
    exp = folder / 'export'
    pack(frames, exp)
    preview(exp / 'spritesheet.png', exp / 'preview_x4.png', 4)
    for direction in DIRECTIONS:
        create_gif(frames, exp / f'{direction}.gif', direction, 4)
    print(f'デモ完成（見た目は仮作品）: {folder}')


def repair(source, dest):
    with Image.open(source) as im:
        im = im.convert('RGBA')
    if im.size != (W, H):
        raise SystemExit('repairは32x48のみ。サイズ変更して自動合格にしません。')
    out = Image.new('RGBA', (W,H), CLEAR)
    src = im.load(); dst = out.load()
    for y in range(H):
        for x in range(W):
            r,g,b,a = src[x,y]
            if a < 128:
                continue
            rgb = min(RGB_SET, key=lambda c: (r-c[0])**2 + (g-c[1])**2 + (b-c[2])**2)
            dst[x,y] = (*rgb,255)
    out = enforce_outer_outline(out)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    print(f'機械的な補修: {dest}。修復後も目視確認が必須です。')


def draft(source, dest):
    """Nearest neighbour sizing for rough REFERENCE ONLY. Never approved in pack/validate."""
    with Image.open(source) as im:
        im = im.convert('RGBA')
    bounds = im.getbbox()
    if bounds is None:
        raise SystemExit('原画が完全透明です')
    im = im.crop(bounds)
    im.thumbnail((W-4, H-6), Image.Resampling.NEAREST)
    placement = Image.new('RGBA', (W,H), CLEAR)
    px = (W-im.width)//2
    py = H-1-im.height
    placement.alpha_composite(im, (px,py))
    temp = Path(dest)
    temp.parent.mkdir(parents=True, exist_ok=True)
    # Repair sanitizes palette and alpha but never claims this is re-drawing.
    intermediate = temp.with_name(temp.stem + '.__temp__.png')
    placement.save(intermediate)
    try:
        repair(intermediate,temp)
    finally:
        intermediate.unlink(missing_ok=True)
    marker_for(temp).write_text(json.dumps({'draft': True, 'source': str(source), 'reason': 'nearest-neighbor thumbnail is never a final redraw'}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('未承認ラフを作成。機械的なサイズ合わせは作品の完成ではありません。')


def main(argv=None):
    p = argparse.ArgumentParser(description='ちゅらたび: 32x48px ドット絵スプライト制作・QAパイプライン')
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('demo', help='12枚のデモを描き、シート・GIFまで制作')
    a.add_argument('--output', required=True)
    a = sub.add_parser('validate', help='12枚を検査してNGなら非ゼロ終了')
    a.add_argument('--input', required=True)
    a.add_argument('--report')
    a = sub.add_parser('pack', help='合格した12枚からシートとJSONを出力')
    a.add_argument('--input', required=True)
    a.add_argument('--output', required=True)
    a = sub.add_parser('preview', help='拡大プレビュー（検査用）')
    a.add_argument('--sheet', required=True)
    a.add_argument('--output', required=True)
    a.add_argument('--scale', type=int, default=4)
    a = sub.add_parser('gif', help='4コマを行ったり来たりするGIF')
    a.add_argument('--input', required=True)
    a.add_argument('--output', required=True)
    a.add_argument('--direction', choices=DIRECTIONS, default='front')
    a.add_argument('--scale', type=int, default=4)
    a = sub.add_parser('repair', help='32x48px透過PNGの色/アルファ/外輪郭を補修（再描画ではない）')
    a.add_argument('--source', required=True)
    a.add_argument('--output', required=True)
    a = sub.add_parser('draft', help='外部画像を非承認のピクセルラフにする')
    a.add_argument('--source', required=True)
    a.add_argument('--output', required=True)
    args = p.parse_args(argv)
    if args.command == 'demo':
        demo(args.output)
    elif args.command == 'validate':
        result = run_validate(args.input, args.report)
        if not result['ok']:
            raise SystemExit(1)
    elif args.command == 'pack':
        pack(args.input, args.output)
    elif args.command == 'preview':
        if args.scale < 1 or args.scale > 16:
            raise SystemExit('scaleは1から16まで')
        preview(args.sheet, args.output, args.scale)
    elif args.command == 'gif':
        if args.scale < 1 or args.scale > 16:
            raise SystemExit('scaleは1から16まで')
        create_gif(args.input, args.output, args.direction, args.scale)
    elif args.command == 'repair':
        repair(args.source, args.output)
    elif args.command == 'draft':
        draft(args.source, args.output)


if __name__ == '__main__':
    main()
