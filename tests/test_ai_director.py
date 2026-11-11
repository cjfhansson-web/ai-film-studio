"""Offline tests for AI frame selection. No API key or network needed."""
import tempfile
import unittest
from pathlib import Path
from tools.ai_director import collect

class FrameSelectionTests(unittest.TestCase):
    def test_even_selection_and_real_paths(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            frames=[]
            for i in range(12):
                name=f"f{i}.jpg"
                (folder/name).write_bytes(b"test")
                frames.append({"image":name,"time_seconds":i})
            manifest={"sources":[{"id":"clip01","segments":[{"id":"s1","still_frames":frames}]}]}
            selected=collect(manifest,folder,4)
            self.assertEqual(len(selected),4)
            self.assertEqual([x[2] for x in selected],[0,4,7,11])
    def test_missing_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest={"sources":[{"id":"clip01","segments":[{"id":"s1","still_frames":[{"image":"missing.jpg","time_seconds":0}]}]}]}
            with self.assertRaises(ValueError):collect(manifest,Path(d),24)
if __name__=="__main__":unittest.main()
