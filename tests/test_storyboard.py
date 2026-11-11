import unittest
from tools.build_storyboard import build,validate_manifest

def manifest():
    return {"schema_version":"0.1","sources":[
        {"id":"clip01","source_file":"/test/a.mp4","duration_seconds":10,"segments":[
            {"id":"a1","start_seconds":0,"end_seconds":5,"thumbnail":"a1.jpg","thumbnail_time_seconds":2.5},
            {"id":"a2","start_seconds":5,"end_seconds":10,"thumbnail":"a2.jpg","thumbnail_time_seconds":7.5}]},
        {"id":"clip02","source_file":"/test/b.mp4","duration_seconds":8,"segments":[
            {"id":"b1","start_seconds":0,"end_seconds":8,"thumbnail":"b1.jpg","thumbnail_time_seconds":4}]}]}
class StoryboardTests(unittest.TestCase):
    def test_duration_and_source_ranges(self):
        x=build(manifest(),12)
        self.assertEqual(x["actual_duration_seconds"],12)
        self.assertEqual([s["segment_id"] for s in x["shots"]],["a1","b1"])
        self.assertEqual(x["shots"][1]["source_out_seconds"],7)
        self.assertFalse(x["ai_selected"])
    def test_insufficient_material(self):
        x=build(manifest(),30)
        self.assertTrue(x["incomplete"])
        self.assertEqual(x["actual_duration_seconds"],18)
    def test_reject_invalid_interval(self):
        x=manifest();x["sources"][0]["segments"][0]["end_seconds"]=11
        with self.assertRaises(ValueError): validate_manifest(x)
    def test_reject_duplicate_id(self):
        x=manifest();x["sources"][1]["segments"][0]["id"]="a1"
        with self.assertRaises(ValueError): validate_manifest(x)
if __name__=="__main__": unittest.main()
