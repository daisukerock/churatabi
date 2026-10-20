import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import sprite_pipeline as sp


class TestSpritePipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.frames = Path(self.tmp.name) / 'frames'
        self.frames.mkdir()
        for direction in sp.DIRECTIONS:
            for pose in sp.POSES:
                sp.draw_character(direction, pose).save(self.frames / f'{direction}_{pose}.png')

    def test_demo_frames_are_clean(self):
        report = sp.run_validate(self.frames)
        self.assertTrue(report['ok'], report['errors'])
        self.assertEqual(12, report['checked_frames'])

    def test_pack_geometry_and_metadata(self):
        out = Path(self.tmp.name) / 'export'
        sp.pack(self.frames, out)
        with Image.open(out / 'spritesheet.png') as img:
            self.assertEqual((96,192), img.size)
            self.assertEqual('RGBA', img.mode)
        data = json.loads((out/'spritesheet.json').read_text())
        self.assertEqual(12, len(data['frames']))
        self.assertEqual([0,1,2,1], data['animations']['front']['frames'])

    def test_reject_wrong_dimensions(self):
        f = self.frames / 'front_idle.png'
        Image.open(f).resize((31,48)).save(f)
        self.assertFalse(sp.run_validate(self.frames)['ok'])

    def test_reject_half_alpha(self):
        f = self.frames / 'front_idle.png'
        im = Image.open(f).convert('RGBA')
        im.putpixel((15,20), (235,190,150,128))
        im.save(f)
        self.assertFalse(sp.run_validate(self.frames)['ok'])

    def test_reject_identical_poses(self):
        (self.frames / 'front_walk1.png').write_bytes((self.frames/'front_idle.png').read_bytes())
        self.assertFalse(sp.run_validate(self.frames)['ok'])

    def test_reject_draft_marker(self):
        (self.frames / 'note.draft.json').write_text('{"draft":true}')
        self.assertFalse(sp.run_validate(self.frames)['ok'])

    def test_repair_refuses_resize(self):
        src=Path(self.tmp.name)/'bad.png'
        Image.new('RGBA',(80,90),'white').save(src)
        with self.assertRaises(SystemExit):
            sp.repair(src, Path(self.tmp.name)/'out.png')


if __name__ == '__main__':
    unittest.main()
