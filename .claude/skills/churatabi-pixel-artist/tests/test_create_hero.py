"""Tests for the reusable native-pixel protagonist sprite generator."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import create_hero
import sprite_pipeline as sp


class TestCreateHero(unittest.TestCase):
    def test_generates_and_validates_all_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'hero'
            result = create_hero.generate(root)
            self.assertTrue(result['ok'], result['errors'])
            self.assertEqual(12, result['checked_frames'])
            frames = list((root / 'frames').glob('*.png'))
            self.assertEqual(12, len(frames))
            for frame in frames:
                with Image.open(frame) as im:
                    self.assertEqual((32, 48), im.size)
                    self.assertEqual('RGBA', im.mode)
            with Image.open(root / 'export' / 'spritesheet.png') as im:
                self.assertEqual((96, 192), im.size)
            with Image.open(root / 'export' / 'preview_x4.png') as im:
                self.assertEqual((384, 768), im.size)
            for direction in sp.DIRECTIONS:
                self.assertTrue((root / 'export' / f'{direction}.gif').is_file())
            self.assertEqual(
                12,
                len(json.loads((root / 'export' / 'spritesheet.json').read_text())['frames']),
            )

    def test_frames_are_deterministic(self):
        for pose in sp.POSES:
            self.assertEqual(create_hero.make_front(pose).tobytes(),
                             create_hero.make_front(pose).tobytes())
            self.assertEqual(create_hero.make_back(pose).tobytes(),
                             create_hero.make_back(pose).tobytes())
            self.assertEqual(create_hero.make_left(pose).tobytes(),
                             create_hero.make_left(pose).tobytes())

    def test_front_eye_symmetry(self):
        eye_color = tuple(bytes.fromhex(sp.PALETTE['eyes'][1:]))
        for pose in sp.POSES:
            img = create_hero.make_front(pose)
            eyes = {(x,y) for y in range(12,22) for x in range(32)
                    if img.getpixel((x,y))[:3] == eye_color and img.getpixel((x,y))[3] == 255}
            self.assertTrue(eyes)
            self.assertTrue(all((32-x,y) in eyes for x,y in eyes))


if __name__ == '__main__':
    unittest.main()
