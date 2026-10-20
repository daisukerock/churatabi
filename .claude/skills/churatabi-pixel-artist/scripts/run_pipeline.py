#!/usr/bin/env python3
"""Churatabi four-view to walking sprites: explicit, repeatable end-to-end pipeline.

Input: four direction images. Output: original-size normalized sprites,
12 native frames, validation, sheet, gifs and JSON. Computational cleanup and
procedural posing are a DRAFT, never a guarantee of an artist-quality redraw.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile
from PIL import Image

import resize_sprite as rz
import sprite_pipeline as sp

DIRECTIONS = tuple(sp.DIRECTIONS)
POSES = tuple(sp.POSES)
EYE = tuple(bytes.fromhex(sp.PALETTE['eyes'][1:]))
HAIR = tuple(bytes.fromhex(sp.PALETTE['hair'][1:]))
SKIN = tuple(bytes.fromhex(sp.PALETTE['skin_light'][1:]))
OUTLINE = sp.OUTLINE
SIZE = (sp.W, sp.H)


class PipelineError(RuntimeError):
    pass


def find_views(input_dir: Path) -> dict[str, Path]:
    """Select four explicit views; never pretend one image contains other poses."""
    if not input_dir.is_dir():
        raise PipelineError(f'入力フォルダがありません: {input_dir}')
    choices = {}
    for direction in DIRECTIONS:
        candidates = [input_dir / f'{direction}{ext}'
                      for ext in ('.png', '.webp', '.jpg', '.jpeg')]
        candidates += [input_dir / f'{direction}_idle{ext}'
                       for ext in ('.png', '.webp', '.jpg', '.jpeg')]
        matches = [f for f in candidates if f.is_file()]
        if len(matches) != 1:
            raise PipelineError(
                f'{direction} の原画は1枚必要です（{len(matches)}枚）。'
                f'ファイル名は {direction}.png または {direction}_idle.png など')
        choices[direction] = matches[0]
    return choices


def eye_normalize(front: Image.Image) -> tuple[Image.Image, dict]:
    """Normalize pupils to 2 symmetrical 1px marks; preserve face otherwise.

    Other dark eye-color speckles in an illustration can be hair. Replace
    them with hair color so the existing pipeline's broad pupil QA is valid.
    This is a conservative *stylization*, not faithful face recognition.
    """
    im = front.copy().convert('RGBA')
    px = im.load()
    changed = 0
    for y in range(12, 22):
        for x in range(sp.W):
            if px[x, y][3] and px[x, y][:3] == EYE:
                px[x, y] = (*HAIR, 255)
                changed += 1
    # Symmetric relative to center line x=16; an artist should review this.
    positions = [(13, 18), (19, 18)]
    for x, y in positions:
        if px[x, y][3] == 0:
            raise PipelineError('顔の目を置く座標に人物がありません。手描き補修が必要です')
        px[x,y] = (*EYE,255)
    return im, {'replaced_existing_dark_pixels': changed,
                'pupil_coordinates': [list(v) for v in positions],
                'review': '自動的に目を対称化。原画と同じ顔かを必ず確認'}


def walk_variant(base: Image.Image, pose: str, direction: str) -> Image.Image:
    """Pose two lower-body halves independently while fixing shoe baseline.

    This creates usable distinct prototype frames but does not hallucinate
    anatomy, full arm poses or genuinely observed movement from one still.
    """
    if pose == 'idle':
        return base.copy()
    left_dx, right_dx = ((-2, 2) if pose == 'walk1' else (2, -2))
    if direction == 'right':
        left_dx, right_dx = -left_dx, -right_dx
    out = base.copy().convert('RGBA')
    source = base.convert('RGBA')
    dst = out.load(); src = source.load()
    top = 39
    # Clear existing lower legs, then translate the two halves independently.
    for y in range(top, sp.H):
        for x in range(sp.W):
            dst[x,y] = (0,0,0,0)
    for y in range(top, sp.H):
        for x in range(sp.W):
            if src[x,y][3] == 0:
                continue
            shift = left_dx if x < 16 else right_dx
            nx = x + shift
            if 0 < nx < sp.W - 1:
                dst[nx,y] = src[x,y]
    # Maintain continuity at the waist with original shorts region.
    for y in range(37, 40):
        for x in range(sp.W):
            if src[x,y][3] and dst[x,y][3] == 0:
                dst[x,y] = src[x,y]
    return sp.enforce_outer_outline(out)


def check_source_view_consistency(frames: Path) -> list[str]:
    notes = []
    images = [Image.open(frames / f'{d}_idle.png').convert('RGBA')
              for d in DIRECTIONS]
    widths = []
    tops = []
    for image in images:
        bbox = image.getchannel('A').getbbox()
        if not bbox:
            notes.append('空画像あり')
            continue
        widths.append(bbox[2] - bbox[0])
        tops.append(bbox[1])
    if widths and max(widths) - min(widths) >= 9:
        notes.append('方向によって幅が大きく異なります。プロポーションを目視確認')
    if tops and max(tops) - min(tops) >= 6:
        notes.append('方向によって頭頂の高さが異なります。歩行時の上下位置を確認')
    return notes


def build(output: Path, input_dir: Path, options: rz.Options | None = None,
          *, overwrite: bool = False) -> dict:
    """Single-command pipeline; no partial output ever called a released asset."""
    if options is None:
        options = rz.Options(width=sp.W,height=sp.H,margin=1,
                             background='auto',outline='inside',
                             palette='project',mark_draft=True)
    if (options.width, options.height) != SIZE:
        raise PipelineError(f'ゲーム主人公のサイズは {SIZE} 固定です')
    views = find_views(Path(input_dir))
    dest = Path(output).resolve()
    if dest.exists() and any(dest.iterdir()) and not overwrite:
        raise PipelineError(f'既存の出力を保護しました: {dest}。別ディレクトリを指定してください')
    if Path(input_dir).resolve() == dest or dest in [p.resolve().parent for p in views.values()]:
        raise PipelineError('入力画像のあるフォルダを出力先として使えません')
    with tempfile.TemporaryDirectory(prefix='churatabi_pipeline_') as tmp:
        root = Path(tmp)
        drafts = root / 'normalized'
        frames = root / 'frames'
        exports = root / 'export'
        drafts.mkdir(); frames.mkdir()
        resizing = {}
        for direction, path in views.items():
            try:
                image, info = rz.process_image(path, options)
            except (OSError, rz.ResizeError) as exc:
                raise PipelineError(f'{direction} のリサイズ失敗: {exc}') from exc
            image.save(drafts / f'{direction}_idle.png')
            resizing[direction] = {'source': str(path), **info}
        face, face_info = eye_normalize(Image.open(drafts/'front_idle.png'))
        face.save(drafts/'front_idle.png')
        for direction in DIRECTIONS:
            with Image.open(drafts / f'{direction}_idle.png') as img:
                idle = img.convert('RGBA')
            for pose in POSES:
                result = walk_variant(idle, pose, direction)
                result.save(frames / f'{direction}_{pose}.png')
        checks = sp.run_validate(frames, root/'quality.json')
        issues = check_source_view_consistency(frames)
        checks['visual_review_required'] = True
        checks['art_review_warnings'] = issues + [
            '歩行は脚を移動させた試作。関節・腕振り・各方向の一貫性は目視で評価',
            '左右の歩行と顔の特徴はAI画像生成・手描きとの比較が必要',
        ]
        (root/'quality.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2), encoding='utf-8')
        metadata = {
            'status': 'DRAFT_VISUAL_REVIEW_REQUIRED' if checks['ok'] else 'FAILED_AUTOMATED_QA',
            'source_views': {k:str(v) for k,v in views.items()},
            'resizing': resizing,
            'face_retouch': face_info,
            'quality': checks,
            'run_command': 'python scripts/run_pipeline.py --input-dir INPUT --output OUTPUT',
            'not_final': True,
        }
        (root/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
        if checks['ok']:
            sp.pack(frames, exports)
            sp.preview(exports/'spritesheet.png', exports/'preview_x4.png', 4)
            for direction in DIRECTIONS:
                sp.create_gif(frames,exports/f'{direction}.gif',direction,4)
        if dest.exists() and overwrite:
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(root, dest)
        if not checks['ok']:
            raise PipelineError(f'品質検査に不合格です。理由: {checks["errors"]}。'
                                f'出力フォルダ {dest} のquality.jsonを確認してください')
        return metadata


def main(argv=None):
    p = argparse.ArgumentParser(description='ちゅらたび：原画4方向→32×48→補正→歩行→検査→納品候補を一括出力')
    p.add_argument('--input-dir', required=True, type=Path, help='front/back/left/right画像があるフォルダ')
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--background', default='auto', help='auto, keep, white, black, #RRGGBB')
    p.add_argument('--sampling', choices=['nearest','box'], default='nearest')
    p.add_argument('--palette', choices=['project','preserve'], default='project')
    p.add_argument('--outline', choices=['inside','outside','none'], default='inside')
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args(argv)
    options = rz.Options(width=32,height=48,background=args.background,
                         sampling=args.sampling,palette=args.palette,
                         outline=args.outline)
    try:
        result = build(args.output,args.input_dir,options,overwrite=args.overwrite)
    except PipelineError as exc:
        p.exit(2,f'エラー: {exc}\n')
    print(json.dumps({'ok':result['quality']['ok'], 'status':result['status'],
                      'output':str(args.output),'frames':12},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
