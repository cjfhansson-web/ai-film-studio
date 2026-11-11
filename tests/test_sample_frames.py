import unittest
from tools.sample_frames import sample_times
class SamplingTests(unittest.TestCase):
    def test_one_per_second(self):self.assertEqual(sample_times(2,5),[2,3,4])
    def test_subsecond(self):self.assertEqual(sample_times(0,1,0.25),[0,0.25,0.5,0.75])
    def test_no_end_overrun(self):self.assertEqual(sample_times(0,2.1),[0,1,2])
    def test_invalid(self):
        with self.assertRaises(ValueError):sample_times(3,1)
        with self.assertRaises(ValueError):sample_times(0,3,0)
if __name__=="__main__":unittest.main()
