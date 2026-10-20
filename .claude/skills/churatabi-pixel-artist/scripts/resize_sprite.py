#!/usr/bin/env python3
"""Churatabi sprite resizer: native 32x48 drafts with baseline, binary alpha,
palette snapping, and one-pixel contours. Pillow dependency. Not a redraw.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import json
import re
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
DEFAULT_W, DEFAULT_H = int(CONFIG['width']), int(CONFIG['height'])
PROJECT_PALETTE = tuple(tuple(bytes.fromhex(v.lstrip('#'))) for v in CONFIG['palette'].values())
PROJECT_OUTLINE = tuple(bytes.fromhex(CONFIG['outline'].lstrip('#')))
SUPPORTED = {'.png', '.webp', '.jpg', '.jpeg', '.bmp'}
CLEAR = (0,0,0,0)

class ResizeError(ValueError):
    pass

@dataclass
class Options:
    width: int = DEFAULT_W
    height: int = DEFAULT_H
    margin: int = 1
    alpha_cutoff: int = 128
    background: str = 'auto'
    tolerance: int = 16
    palette: str = 'project'
    sampling: str = 'nearest'
    outline: str = 'outside'
    outline_color: tuple[int,int,int] = PROJECT_OUTLINE
    crop: tuple[int,int,int,int] | None = None
    mark_draft: bool = True

def parse_hex(value):
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ResizeError('カラーコードは #RRGGBB 形式で指定してください')
    return tuple(bytes.fromhex(value[1:]))

def parse_crop(value):
    try:
        x,y,w,h = [int(part.strip()) for part in value.split(',')]
    except (ValueError, TypeError):
        raise ResizeError('cropは x,y,width,height の4整数で指定してください')
    if w < 1 or h < 1 or x < 0 or y < 0:
        raise ResizeError('cropの座標は0以上、幅と高さは1以上にしてください')
    return (x,y,w,h)

def closest_color(c, palette):
    return min(palette,key=lambda p: sum((p[i]-c[i])**2 for i in range(3)))

def color_match(a,b,tolerance):
    return max(abs(a[i]-b[i]) for i in range(3)) <= tolerance

def make_transparent(im,options):
    im=im.convert('RGBA')
    lo,hi=im.getchannel('A').getextrema()
    mode=options.background.lower()
    if mode=='keep':
        if lo==hi==255:
            raise ResizeError('不透明画像です。--background auto または色コードで背景を指定してください')
        return im,'existing-alpha'
    if mode=='auto' and lo<255:
        return im,'existing-alpha'
    w,h=im.size
    pix=im.load()
    if mode=='auto':
        samples=[pix[0,0][:3],pix[w-1,0][:3],pix[0,h-1][:3],pix[w-1,h-1][:3]]
        if any(not color_match(samples[0],c,options.tolerance) for c in samples[1:]):
            raise ResizeError('四隅の背景色が異なります。透過PNGまたは--background #RRGGBBを指定してください')
        target=samples[0]
    elif mode in ('white','black'):
        target=(255,255,255) if mode=='white' else (0,0,0)
    else:
        target=parse_hex(mode)
    outside=bytearray(w*h)
    q=deque()
    for x in range(w):
        q.append((x,0));q.append((x,h-1))
    for y in range(h):
        q.append((0,y));q.append((w-1,y))
    while q:
        x,y=q.popleft()
        i=y*w+x
        if outside[i]:continue
        rgba=pix[x,y]
        if rgba[3]==0 or not color_match(rgba[:3],target,options.tolerance):
            continue
        outside[i]=1
        if x>0:q.append((x-1,y))
        if x+1<w:q.append((x+1,y))
        if y>0:q.append((x,y-1))
        if y+1<h:q.append((x,y+1))
    result=Image.new('RGBA',(w,h),CLEAR)
    out=result.load()
    for y in range(h):
        for x in range(w):
            if not outside[y*w+x]:out[x,y]=pix[x,y]
    if not any(a>=options.alpha_cutoff for a in result.getchannel('A').get_flattened_data()):
        raise ResizeError('背景除去後、人物が残りません')
    return result,f'edge-fill:{target}'

def geometry(im,options):
    if not (8<=options.width<=2048 and 8<=options.height<=2048):
        raise ResizeError('出力サイズは各辺8〜2048px')
    if not (0<=options.margin<=min(options.width,options.height)//3):
        raise ResizeError('marginが大きすぎます')
    if not (1<=options.alpha_cutoff<=255):
        raise ResizeError('alpha_cutoffは1〜255です')
    if options.outline not in ('outside','inside','none'):
        raise ResizeError('outlineはoutside/inside/none')
    if options.sampling not in ('nearest','box'):
        raise ResizeError('samplingはnearest/box')
    pad=1 if options.outline=='outside' else 0
    left_margin=max(options.margin,pad+1) if pad else options.margin
    top_margin=max(options.margin,pad+1) if pad else options.margin
    max_w=options.width-2*left_margin
    max_h=options.height-top_margin-pad
    if max_w<1 or max_h<1:raise ResizeError('余白が大きすぎます')
    mask=im.getchannel('A').point(lambda a:255 if a>=options.alpha_cutoff else 0)
    bbox=mask.getbbox()
    if bbox is None:raise ResizeError('透明画像、またはalpha閾値以下の画像です')
    cropped=im.crop(bbox)
    objw,objh=cropped.size
    ratio=min(max_w/objw,max_h/objh)
    dw=max(1,min(max_w,round(objw*ratio)))
    dh=max(1,min(max_h,round(objh*ratio)))
    filt=Image.Resampling.NEAREST if options.sampling=='nearest' else Image.Resampling.BOX
    cropped=cropped.resize((dw,dh),filt)
    binary=cropped.getchannel('A').point(lambda a:255 if a>=options.alpha_cutoff else 0)
    cropped.putalpha(binary)
    out=Image.new('RGBA',(options.width,options.height),CLEAR)
    x=(options.width-dw)//2
    y=options.height-pad-dh
    if x<left_margin or x+dw>options.width-left_margin or y<top_margin:
        raise ResizeError('内側配置に失敗しました')
    out.paste(cropped,(x,y),cropped)
    return out,dict(source_bbox=list(bbox),source_visible_size=[objw,objh],
                    content_size=[dw,dh],content_offset=[x,y],scale=ratio)

def exact_binary_rgba(img):
    rgba=img.convert('RGBA')
    p=rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r,g,b,a=p[x,y]
            p[x,y]=(r,g,b,255) if a>=128 else CLEAR
    return rgba

def apply_palette(im,colors):
    cache={};out=im.copy();pix=out.load();changed=0
    for y in range(out.height):
        for x in range(out.width):
            c=pix[x,y]
            if c[3]==0:continue
            rgb=c[:3]
            if rgb not in cache:cache[rgb]=closest_color(rgb,colors)
            mapped=cache[rgb]
            changed+=rgb!=mapped
            pix[x,y]=(*mapped,255)
    return out,changed

def apply_contour(im,mode,outline_rgb):
    if mode=='none':return im
    alpha=im.getchannel('A')
    if mode=='outside':
        ring=ImageChops.subtract(alpha.filter(ImageFilter.MaxFilter(3)),alpha)
        shape=Image.new('RGBA',im.size,(*outline_rgb,255))
        base=Image.new('RGBA',im.size,CLEAR)
        base.paste(shape,(0,0),ring)
        base.alpha_composite(im)
        return base
    p=im.load()
    w,h=im.size
    candidates=[]
    for y in range(h):
        for x in range(w):
            if p[x,y][3]==0:continue
            if any(xx<0 or xx>=w or yy<0 or yy>=h or p[xx,yy][3]==0
                   for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),
                                 (x-1,y-1),(x-1,y+1),(x+1,y-1),(x+1,y+1))):
                candidates.append((x,y))
    for x,y in candidates:p[x,y]=(*outline_rgb,255)
    return im

def process_image(source,options):
    with Image.open(source) as f:
        before=ImageOps.exif_transpose(f)
        source_dimensions=before.size
        if options.crop:
            x,y,w,h=options.crop
            if x+w>before.width or y+h>before.height:
                raise ResizeError(f'crop領域が原画サイズ {before.size} を超えています')
            before=before.crop((x,y,x+w,y+h))
        im,bg=make_transparent(before,options)
    img,detail=geometry(im,options)
    img=exact_binary_rgba(img)
    unique_before=len({rgb[:3] for rgb in img.get_flattened_data() if rgb[3]})
    if options.palette=='project':
        img,changes=apply_palette(img,PROJECT_PALETTE)
    elif options.palette=='preserve':
        changes=0
    else:
        raise ResizeError('paletteはprojectまたはpreserve')
    img=apply_contour(img,options.outline,options.outline_color)
    alphas=set(img.getchannel('A').get_flattened_data())
    assert alphas.issubset({0,255})
    assert img.size==(options.width,options.height)
    return img,{**detail,'source_size':list(source_dimensions),
                'target_size':[options.width,options.height],
                'background_mode':bg,'palette':options.palette,
                'sample':options.sampling,'outline':options.outline,
                'source_colors_after_resize':unique_before,
                'pixels_recolored':changes,'alpha_values':sorted(alphas),
                'warnings':['自動リサイズは描き直しではありません。顔・目・手足・歩行を目視検査してください。']}

def safe_output_paths(input_path,output_path):
    if input_path.is_file():
        if output_path.exists() and output_path.is_dir():
            return [(input_path,output_path/input_path.with_suffix('.png').name)]
        if output_path.suffix.lower()!='.png':
            raise ResizeError('単一画像の出力先は.pngを指定してください')
        return [(input_path,output_path)]
    if input_path.is_dir():
        if output_path.suffix:
            raise ResizeError('入力がフォルダの場合、出力はフォルダ')
        images=sorted(p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
        if not images:raise ResizeError('画像ファイルがありません')
        return [(p,output_path/(p.stem+'.png')) for p in images]
    raise ResizeError(f'入力画像が見つかりません: {input_path}')

def resize_batch(input_path,output_path,options,force=False):
    pairs=safe_output_paths(Path(input_path),Path(output_path))
    if len({q.resolve() for _,q in pairs})!=len(pairs):
        raise ResizeError('出力先ファイル名が衝突')
    for p,q in pairs:
        if p.resolve()==q.resolve():
            raise ResizeError('原画の上書きは禁止です。別のoutputを指定')
        if q.exists() and not force:
            raise ResizeError(f'出力がすでに存在します。--forceで上書き: {q}')
        marker=q.with_name(q.name+'.draft.json')
        if options.mark_draft and marker.exists() and not force:
            raise ResizeError(f'前回のdraft判定があります。--forceを指定: {marker}')
    results=[]
    for p,q in pairs:
        image,meta=process_image(p,options)
        meta['source_file']=str(p)
        meta['output_file']=str(q)
        results.append((q,image,meta))
    for q,image,meta in results:
        q.parent.mkdir(parents=True,exist_ok=True)
        image.save(q,'PNG')
        marker=q.with_name(q.name+'.draft.json')
        if options.mark_draft:
            marker.write_text(json.dumps({'draft':True,
                'reason':'automatically resized; visual review and redraw details as necessary',
                'metadata':meta},ensure_ascii=False,indent=2),encoding='utf-8')
        else:
            marker.unlink(missing_ok=True)
        print(f'OK: {q} {meta["target_size"]} crop={meta["source_bbox"]} content={meta["content_size"]}')
    summary={'ok':True,
       'status':'DRAFT_REVIEW_REQUIRED' if options.mark_draft else 'RESIZED_NOT_ART_VERIFIED',
       'files':len(results),'results':[m for _,_,m in results]}
    if len(results)>1:
        (Path(output_path)/'resize-report.json').write_text(
            json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary

def cli(argv=None):
    parser=argparse.ArgumentParser(description='ちゅらたび: 正確なピクセルへのリサイズ')
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--width',type=int,default=DEFAULT_W)
    parser.add_argument('--height',type=int,default=DEFAULT_H)
    parser.add_argument('--margin',type=int,default=1)
    parser.add_argument('--crop',type=parse_crop,help='x,y,width,height')
    parser.add_argument('--background',default='auto',help='auto/keep/white/black/#RRGGBB')
    parser.add_argument('--tolerance',type=int,default=16)
    parser.add_argument('--alpha-cutoff',type=int,default=128)
    parser.add_argument('--palette',choices=['project','preserve'],default='project')
    parser.add_argument('--sampling',choices=['nearest','box'],default='nearest')
    parser.add_argument('--outline',choices=['outside','inside','none'],default='outside')
    parser.add_argument('--outline-color',type=parse_hex,default=PROJECT_OUTLINE)
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--no-draft-marker',action='store_true')
    args=parser.parse_args(argv)
    if not (0<=args.tolerance<=255):parser.error('toleranceは0〜255')
    if not (1<=args.alpha_cutoff<=255):parser.error('alpha-cutoffは1〜255')
    options=Options(width=args.width,height=args.height,margin=args.margin,
        alpha_cutoff=args.alpha_cutoff,background=args.background,
        tolerance=args.tolerance,palette=args.palette,sampling=args.sampling,
        outline=args.outline,outline_color=args.outline_color,crop=args.crop,
        mark_draft=not args.no_draft_marker)
    try:
        result=resize_batch(args.input,args.output,options,args.force)
        print(json.dumps({'ok':True,'files':result['files'],
                          'status':result['status']},ensure_ascii=False))
    except (ResizeError,FileNotFoundError,OSError) as exc:
        parser.exit(2,f'リサイズ失敗: {exc}\n')

if __name__=='__main__':
    cli()
