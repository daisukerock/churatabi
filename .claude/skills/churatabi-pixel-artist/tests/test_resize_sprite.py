"""Regression tests for sprite resizing, silhouette and batch export."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import resize_sprite as r

class TestResizeSprite(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.src=self.root/'input.png'

    def sample(self):
        im=Image.new('RGBA',(160,240),(0,0,0,0))
        d=ImageDraw.Draw(im)
        d.ellipse((40,5,119,78),fill='#3D302A')
        d.rectangle((45,75,115,173),fill='#FAF4E8')
        d.rectangle((51,172,71,236),fill='#377C9E')
        d.rectangle((88,172,108,236),fill='#377C9E')
        im.save(self.src)

    def test_rgba_dimensions_binary_and_outline(self):
        self.sample()
        img,meta=r.process_image(self.src,r.Options())
        self.assertEqual((32,48),img.size)
        self.assertEqual('RGBA',img.mode)
        self.assertEqual({0,255},set(img.getchannel('A').get_flattened_data()))
        self.assertTrue(all(img.getpixel((x,0))[3]==0 for x in range(32)))
        self.assertTrue(all(img.getpixel((0,y))[3]==0 for y in range(48)))
        self.assertTrue(any(img.getpixel((x,47))[3]==255 for x in range(32)))
        self.assertEqual('project',meta['palette'])
        self.assertTrue(all(c[:3] in r.PROJECT_PALETTE for c in img.get_flattened_data() if c[3]))
        for y in range(48):
            for x in range(32):
                if img.getpixel((x,y))[3]==0:continue
                exposed=any(xx<0 or xx>=32 or yy<0 or yy>=48 or
                    img.getpixel((xx,yy))[3]==0 for xx,yy in (
                      (x-1,y),(x+1,y),(x,y-1),(x,y+1),
                      (x-1,y-1),(x-1,y+1),(x+1,y-1),(x+1,y+1)))
                if exposed:self.assertEqual(r.PROJECT_OUTLINE,img.getpixel((x,y))[:3])

    def test_aspect_ratio_baseline(self):
        self.sample()
        _,d=r.process_image(self.src,r.Options())
        ow,oh=d['source_visible_size']
        nw,nh=d['content_size']
        self.assertLess(abs(nw/nh-ow/oh),0.1)
        self.assertEqual(46,d['content_offset'][1]+nh-1)

    def test_white_background_keeps_enclosed_shirt(self):
        im=Image.new('RGB',(80,120),'white')
        d=ImageDraw.Draw(im)
        d.rectangle((15,20,65,110),fill='#2B1410')
        d.rectangle((18,24,62,106),fill='white')
        im.save(self.src)
        img,meta=r.process_image(self.src,r.Options())
        self.assertEqual(0,img.getpixel((0,0))[3])
        self.assertTrue(meta['background_mode'].startswith('edge-fill'))
        self.assertTrue(any(c[:3]==(250,244,232) for c in img.get_flattened_data() if c[3]))

    def test_background_complex_rejected(self):
        im=Image.new('RGB',(80,120),'white')
        im.putpixel((79,119),(0,0,0))
        im.save(self.src)
        with self.assertRaisesRegex(r.ResizeError,'四隅'):
            r.process_image(self.src,r.Options())

    def test_transparent_image_rejected(self):
        Image.new('RGBA',(80,120),(0,0,0,0)).save(self.src)
        with self.assertRaises(r.ResizeError):
            r.process_image(self.src,r.Options())

    def test_crop(self):
        im=Image.new('RGBA',(400,400),(0,0,0,0))
        ImageDraw.Draw(im).rectangle((110,110,170,220),fill='#377C9E')
        im.save(self.src)
        img,d=r.process_image(self.src,r.Options(crop=(100,100,100,140)))
        self.assertEqual([10,10,71,121],d['source_bbox'])
        self.assertEqual((32,48),img.size)

    def test_single_draft_and_protect_source(self):
        self.sample()
        dst=self.root/'out.png'
        result=r.resize_batch(self.src,dst,r.Options())
        self.assertEqual(1,result['files'])
        self.assertTrue(dst.is_file())
        self.assertTrue(json.loads((self.root/'out.png.draft.json').read_text())['draft'])
        with self.assertRaises(r.ResizeError):
            r.resize_batch(self.src,dst,r.Options())
        with self.assertRaises(r.ResizeError):
            r.resize_batch(self.src,self.src,r.Options(),force=True)

    def test_batch(self):
        self.sample()
        source=self.root/'frames'
        source.mkdir()
        for i in range(3):
            (source/f'frame_{i}.png').write_bytes(self.src.read_bytes())
        dest=self.root/'batch'
        result=r.resize_batch(source,dest,r.Options())
        self.assertEqual(3,result['files'])
        self.assertEqual(3,len(list(dest.glob('*.png'))))
        self.assertEqual(3,len(list(dest.glob('*.draft.json'))))
        self.assertEqual(3,len(json.loads((dest/'resize-report.json').read_text())['results']))

    def test_invalid_dimensions(self):
        self.sample()
        with self.assertRaises(r.ResizeError):
            r.process_image(self.src,r.Options(margin=18))
        with self.assertRaises(r.ResizeError):
            r.process_image(self.src,r.Options(alpha_cutoff=0))

    def test_keep_palette(self):
        self.sample()
        im,_=r.process_image(self.src,r.Options(outline='none',palette='preserve'))
        self.assertEqual((32,48),im.size)
        self.assertTrue(any(a for *_,a in im.get_flattened_data()))

if __name__=='__main__':
    unittest.main()
