#!/usr/bin/env python3
"""Generate the original 32x48 Churatabi traveler sprite in twelve frames.

All characters are rendered at native size (no downsampling).  This makes the
v1 prototype reproducible; it does not automatically trace an unrelated image.
"""
from pathlib import Path
import argparse
import sprite_pipeline as sp
from PIL import Image, ImageDraw

P = sp.PALETTE


class Painter:
    def __init__(self):
        self.im = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def R(self, coords, color):
        self.d.rectangle(coords, fill=P[color])
        return self

    def L(self, points, color, w=1):
        self.d.line(points, fill=P[color], width=w)
        return self

    def E(self, coords, color):
        self.d.ellipse(coords, fill=P[color])
        return self

    def G(self, points, color):
        self.d.polygon(points, fill=P[color])
        return self

    def X(self, points, color):
        for x, y in points:
            self.d.point((x, y), fill=P[color])
        return self

    def outlined(self, points, fill):
        self.d.polygon(points, fill=P[fill], outline=P['outline'])
        return self

    def finalize(self):
        return sp.enforce_outer_outline(self.im)


def torso_front(p, step):
    p.R((7,28,9,34),'backpack').R((23,28,25,34),'backpack')
    p.outlined([(10,25),(22,25),(25,29),(24,36),(21,38),(11,38),(8,36),(8,29)],'white_shirt')
    p.R((11,26,13,29),'shirt_shadow').R((21,27,22,35),'shirt_shadow')
    p.R((14,25,18,26),'white_shirt').R((15,26,17,27),'shirt_shadow')
    p.R((12,30,12,31),'white_shirt').R((14,32,19,32),'white_shirt')
    p.X([(13,34),(20,35)],'shirt_shadow')
    p.R((9,28,10,34),'backpack').R((22,28,23,34),'backpack')
    p.X([(10,29),(22,29)],'backpack_light')
    p.R((10,35,22,39),'blue')
    p.R((11,36,14,36),'blue_light').R((18,36,21,36),'blue_light')
    p.R((16,37,16,39),'blue_shadow')
    p.R((10,39,15,41),'blue').R((17,39,22,41),'blue')
    p.R((11,40,14,40),'blue_light').R((18,40,21,40),'blue_light')
    p.R((15,40,17,42),'outline')
    p.X([(11,38),(21,38)],'blue_shadow')


def shoes_front(p, step):
    dx = {'walk1':(-2,2), 'idle':(0,0), 'walk2':(2,-2)}[step]
    for x, shift in zip((11,19),dx):
        bx=x+shift
        legstart=40 if step!='idle' else 41
        p.R((bx,legstart,bx+3,44),'skin')
        p.R((bx+1,42,bx+2,43),'skin_light')
        p.R((bx-1,44,bx+5,47),'shoes')
        p.R((bx,45,bx+3,46),'shoe_light')
        p.R((bx-1,47,bx+5,47),'outline')
        p.X([(bx+4,45)],'skin_shadow')


def arms_front(p, step):
    if step=='walk1':
        p.G([(8,27),(6,27),(5,30),(5,34),(7,36),(9,35),(9,30)],'skin')
        p.R((6,32,7,33),'skin_light')
        p.G([(24,28),(26,29),(27,32),(27,36),(25,37),(23,35)],'skin_shadow')
        p.X([(24,34)],'skin_light')
    elif step=='walk2':
        p.G([(8,29),(6,30),(5,33),(6,37),(8,38),(9,36),(10,31)],'skin_shadow')
        p.R((7,35,8,36),'skin_light')
        p.G([(24,27),(26,27),(27,30),(27,34),(25,36),(23,35)],'skin')
        p.X([(25,34)],'skin_light')
    else:
        p.G([(9,27),(6,29),(5,32),(6,37),(8,38),(10,35)],'skin')
        p.R((6,32,7,34),'skin_light')
        p.G([(23,27),(26,29),(27,32),(26,37),(24,38),(22,35)],'skin')
        p.R((25,32,26,34),'skin_light')
    p.R((7,27,9,29),'white_shirt').R((23,27,25,29),'white_shirt')
    p.X([(7,28),(25,28)],'shirt_shadow')


def front_face(p,step):
    p.E((8,11,24,25),'skin')
    p.E((7,15,11,20),'skin_shadow').E((21,15,25,20),'skin_shadow')
    p.X([(8,17),(24,17)],'skin_light')
    p.R((11,15,21,22),'skin_light')
    p.R((13,23,19,24),'skin_shadow').R((14,24,18,25),'skin')
    p.G([(7,14),(6,10),(8,8),(8,5),(11,6),(12,3),(15,4),(17,2),(20,4),(22,3),
         (23,6),(26,7),(25,10),(26,13),(23,15),(21,12),(20,14),(18,13),(15,14),
         (13,13),(11,16),(9,14),(8,17)],'hair')
    p.G([(9,9),(11,5),(14,6),(15,4),(17,7),(20,5),(22,9),(19,10),(17,9),(14,10),(12,9)],'hair_light')
    p.L([(11,8),(13,7),(15,7)],'hair_light')
    p.X([(19,8),(20,8),(15,5)],'hair_light')
    p.G([(9,12),(12,12),(13,15),(10,15)],'hair')
    p.G([(18,12),(22,12),(21,15),(19,15)],'hair')
    p.R((12,16,13,17),'white_shirt').R((19,16,20,17),'white_shirt')
    p.R((13,16,13,18),'eyes').R((19,16,19,18),'eyes')
    p.X([(13,16),(19,16)],'white_shirt')
    p.R((12,15,13,15),'hair').R((19,15,20,15),'hair')
    p.X([(16,19)],'skin_shadow')
    p.X([(10,20),(22,20)],'skin_shadow')
    p.X([(11,21),(21,21)],'skin_light')
    p.X([(15,22),(17,22)],'skin_shadow')
    p.X([(16,23)],'skin_shadow')
    p.X([(14,24),(18,24)],'skin_light')


def make_front(step):
    p=Painter()
    shoes_front(p,step)
    arms_front(p,step)
    torso_front(p,step)
    front_face(p,step)
    return p.finalize()


def make_back(step):
    p=Painter()
    shoes_front(p,step)
    arms_front(p,step)
    p.outlined([(10,25),(22,25),(24,27),(24,36),(21,38),(11,38),(8,36),(8,28)],'white_shirt')
    p.R((10,36,22,41),'blue').R((11,37,14,38),'blue_light').R((18,37,21,38),'blue_light')
    p.R((16,40,16,41),'outline')
    p.G([(10,26),(12,24),(20,24),(22,26),(24,32),(23,36),(21,39),(11,39),(9,36),(8,31)],'backpack')
    p.R((12,26,20,27),'backpack_light')
    p.R((10,30,22,33),'backpack_light').R((11,34,21,36),'backpack')
    p.L([(11,29),(11,36),(13,38)],'shoes')
    p.L([(21,29),(21,36),(19,38)],'shoes')
    p.R((15,31,17,32),'shoes').R((16,31,16,32),'shoe_light')
    p.R((11,35,13,36),'shoe_light').R((19,35,21,36),'shoe_light')
    p.E((8,11,24,24),'skin_shadow')
    p.R((14,22,18,25),'skin')
    p.E((7,16,10,19),'skin').E((22,16,25,19),'skin')
    p.G([(7,16),(6,10),(8,6),(11,5),(13,2),(17,3),(19,4),(22,3),(25,8),
        (26,13),(24,17),(22,22),(19,23),(16,22),(13,23),(10,21),(9,18)],'hair')
    p.G([(10,8),(12,5),(14,7),(17,5),(20,6),(22,9),(19,10),(16,9),(14,10),(12,9)],'hair_light')
    p.L([(12,14),(10,17),(11,20)],'hair_light')
    p.X([(22,15),(20,19),(13,20)],'hair_light')
    p.R((12,22,19,23),'hair')
    return p.finalize()


def side_legs(p,step):
    if step=='idle':
        legs=[(12,0),(18,0)]
    elif step=='walk1':
        legs=[(10,-2),(19,2)]
    else:
        legs=[(14,2),(17,-2)]
    for i,(x,shift) in enumerate(legs):
        bx=x+shift
        p.R((bx,39,bx+3,44),'skin' if i==0 else 'skin_shadow')
        p.R((bx,41,bx+2,42),'skin_light')
        p.G([(bx-2,44),(bx+3,44),(bx+4,46),(bx+3,47),(bx-3,47),(bx-3,45)],'shoes')
        p.R((bx-2,45,bx+1,46),'shoe_light')
        p.R((bx-3,47,bx+3,47),'outline')


def make_left(step):
    p=Painter()
    side_legs(p,step)
    p.G([(22,26),(25,27),(28,30),(28,36),(25,39),(22,37),(19,32)],'backpack')
    p.L([(25,28),(27,30),(27,35)],'backpack_light')
    p.R((24,33,26,35),'shoes')
    p.G([(22,29),(24,30),(25,35),(23,39),(21,37)],'skin_shadow')
    p.outlined([(13,25),(21,25),(24,28),(24,36),(21,38),(13,38),(10,35),(11,28)],'white_shirt')
    p.R((19,27,21,35),'shirt_shadow').R((13,27,13,32),'white_shirt')
    p.R((12,36,22,40),'blue').R((14,37,20,37),'blue_light')
    p.R((12,40,16,41),'blue').R((18,40,22,41),'blue')
    p.R((16,40,17,41),'blue_shadow')
    p.R((19,26,20,34),'backpack').R((20,28,20,29),'backpack_light')
    if step=='walk1':
        p.G([(12,27),(11,28),(8,32),(8,36),(10,38),(12,36),(15,30)],'skin')
        p.X([(9,33),(9,34)],'skin_light')
    elif step=='walk2':
        p.G([(13,27),(11,29),(13,34),(16,37),(18,35),(17,33),(15,30)],'skin')
        p.X([(15,34),(16,34)],'skin_light')
    else:
        p.G([(12,27),(11,29),(10,32),(11,37),(13,38),(15,36),(15,30)],'skin')
        p.X([(11,33),(12,34)],'skin_light')
    p.R((11,27,13,29),'white_shirt')
    p.G([(12,11),(20,10),(24,13),(24,20),(20,24),(13,24),(9,21),(8,18),(10,16)],'skin')
    p.R((13,14,21,21),'skin_light')
    p.G([(9,18),(11,17),(11,20),(9,21),(7,20)],'skin')
    p.X([(8,19),(9,19)],'skin_light')
    p.G([(12,5),(14,3),(17,4),(19,2),(21,4),(24,5),(26,8),(25,12),
        (23,16),(21,13),(20,15),(17,13),(16,15),(13,14),(11,17),(10,14),(8,16),(7,11),(9,8)],'hair')
    p.G([(10,9),(12,6),(14,8),(17,5),(19,7),(22,7),(23,9),(18,10),(15,9)],'hair_light')
    p.X([(12,8),(16,6),(20,8)],'hair_light')
    p.G([(20,16),(23,15),(24,19),(22,21),(20,20)],'skin_shadow')
    p.X([(21,18)],'skin_light')
    p.R((12,17,13,19),'eyes')
    p.X([(12,17)],'white_shirt')
    p.X([(10,22),(12,22)],'skin_shadow')
    p.R((14,23,18,24),'skin_shadow')
    return p.finalize()


def generate(output: Path) -> dict:
    """Draw twelve exact sprites, run QA and export the validated assets."""
    output = Path(output)
    frames = output / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    for pose in sp.POSES:
        make_front(pose).save(frames / f'front_{pose}.png')
        make_back(pose).save(frames / f'back_{pose}.png')
        left = make_left(pose)
        left.save(frames / f'left_{pose}.png')
        left.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(frames / f'right_{pose}.png')
    result = sp.run_validate(frames, report=output / 'quality.json')
    if not result['ok']:
        raise RuntimeError(f'Sprite QA failed: {result["errors"]}')
    export = output / 'export'
    sp.pack(frames, export)
    sp.preview(export / 'spritesheet.png', export / 'preview_x4.png', 4)
    for direction in sp.DIRECTIONS:
        sp.create_gif(frames, export / f'{direction}.gif', direction, 4)
    return result


def main():
    parser = argparse.ArgumentParser(description='ちゅらたび主人公v1 スプライト自動生成・品質検査')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    generate(args.output)
    print(f'主人公スプライト完成（試作）: {args.output}')


if __name__ == '__main__':
    main()
