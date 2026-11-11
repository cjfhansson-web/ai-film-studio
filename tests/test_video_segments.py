import unittest
from tools.analyze_video import segments

class SegmentTests(unittest.TestCase):
    def test_split_long_clip(self):
        self.assertEqual(segments(13,[],6),[(0.0,6.0),(6.0,12.0),(12.0,13)])
    def test_scene_cut(self):
        self.assertEqual(segments(10,[4],6),[(0.0,4),(4,10)])
    def test_short_tail_merged(self):
        self.assertEqual(segments(6.2,[],6),[(0.0,6.2)])
    def test_bad_boundaries_ignored(self):
        self.assertEqual(segments(4,[-1,0,5],6),[(0.0,4)])
if __name__=="__main__": unittest.main()
