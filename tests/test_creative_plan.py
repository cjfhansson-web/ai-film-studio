import unittest
from tools.validate_creative_plan import validate
def manifest():
    return {"sources":[{"id":"clip01","duration_seconds":10,"segments":[{"id":"s1","start_seconds":0,"end_seconds":10,"still_frames":[{"time_seconds":2,"image":"x.jpg"}]}]}]}
def source():
    return {"kind":"source","source_id":"clip01","segment_id":"s1","source_in_seconds":1,"source_out_seconds":4,"timeline_duration_seconds":3,"still_frames":[{"time_seconds":2,"image":"x.jpg"}],"narrative_role":"Opening"}
def pickup():
    return {"kind":"pickup","timeline_duration_seconds":3,"narrative_role":"Turn","creative_reason":"Missing visual bridge","cinematography_brief":"Close up","generation_prompt":"Cinematic close up"}
def plan():
    return {"variants":[{"id":"A","shots":[source()]},{"id":"B","shots":[source(),pickup()]}]}
class CreativePlanTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(validate(plan(),manifest()),[])
    def test_hallucinated_source(self):
        p=plan();p["variants"][0]["shots"][0]["source_id"]="unknown"
        self.assertTrue(any("not found" in x for x in validate(p,manifest())))
    def test_outside_source(self):
        p=plan();p["variants"][0]["shots"][0]["source_out_seconds"]=20
        self.assertTrue(any("out of verified" in x for x in validate(p,manifest())))
    def test_requires_existing_only_variant(self):
        p=plan();p["variants"][0]["shots"].append(pickup())
        self.assertTrue(any("only existing" in x for x in validate(p,manifest())))
    def test_invented_still(self):
        p=plan();p["variants"][0]["shots"][0]["still_frames"][0]["image"]="invented.jpg"
        self.assertTrue(any("not present" in x for x in validate(p,manifest())))
    def test_missing_prompt(self):
        p=plan();del p["variants"][1]["shots"][1]["generation_prompt"]
        self.assertTrue(any("video prompt" in x for x in validate(p,manifest())))
if __name__=="__main__":unittest.main()
