"""End to end tests of real code; require no external network or assets."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import run_pipeline as run
import create_hero

class TestRunPipeline(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.ins=self.root/'inputs'
        self.ins.mkdir()
        for direction, builder in [('front',create_hero.make_front),
                                   ('back',create_hero.make_back),
                                   ('left',create_hero.make_left)]:
            builder('idle').save(self.ins/f'{direction}.png')
        create_hero.make_left('idle').transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(
            self.ins/'right.png')

    def test_end_to_end(self):
        output=self.root/'output'
        result=run.build(output,self.ins)
        self.assertTrue(result['quality']['ok'],result['quality']['errors'])
        self.assertEqual('DRAFT_VISUAL_REVIEW_REQUIRED',result['status'])
        self.assertEqual(12,len(list((output/'frames').glob('*.png'))))
        self.assertEqual(4,len(list((output/'normalized').glob('*.png'))))
        self.assertEqual(4,len(list((output/'export').glob('*.gif'))))
        with Image.open(output/'export'/'spritesheet.png') as im:
            self.assertEqual((96,192),im.size)
        self.assertTrue(json.loads((output/'quality.json').read_text())['ok'])
        self.assertTrue(json.loads((output/'manifest.json').read_text())['not_final'])

    def test_missing_view_rejected(self):
        (self.ins/'back.png').unlink()
        with self.assertRaisesRegex(run.PipelineError,'back'):
            run.build(self.root/'output',self.ins)

    def test_existing_output_is_protected(self):
        out=self.root/'output'
        out.mkdir();(out/'protected.txt').write_text('keep')
        with self.assertRaisesRegex(run.PipelineError,'保護'):
            run.build(out,self.ins)
        self.assertEqual('keep',(out/'protected.txt').read_text())

    def test_source_files_remain_unchanged(self):
        hashes={p.name:p.read_bytes() for p in self.ins.glob('*.png')}
        run.build(self.root/'output',self.ins)
        self.assertEqual(hashes,{p.name:p.read_bytes() for p in self.ins.glob('*.png')})

if __name__ == '__main__':
    unittest.main()
