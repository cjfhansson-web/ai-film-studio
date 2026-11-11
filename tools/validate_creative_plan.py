"""Validate AI-directed storyboard against real source footage. No external services."""
import json
import math
from pathlib import Path

KINDS={"source","pickup","generated"}
def finite(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def validate(plan,manifest):
    errors=[]
    sources={s["id"]:s for s in manifest.get("sources",[])}
    segments={(s["id"],g["id"]):g for s in manifest.get("sources",[]) for g in s.get("segments",[])}
    if not isinstance(plan.get("variants"),list) or len(plan["variants"])<2:
        errors.append("At least two variants required")
        return errors
    ids=set();has_original_only=False
    for variant in plan["variants"]:
        vid=variant.get("id")
        if not vid or vid in ids: errors.append("Variant ID missing or duplicated")
        ids.add(vid)
        shots=variant.get("shots")
        if not isinstance(shots,list) or not shots:
            errors.append(f"{vid}: no shots");continue
        original_only=True
        for i,shot in enumerate(shots):
            name=f"{vid}/shot{i+1}"
            kind=shot.get("kind")
            if kind not in KINDS: errors.append(f"{name}: unknown kind");continue
            d=shot.get("timeline_duration_seconds")
            if not finite(d) or d<=0: errors.append(f"{name}: invalid duration");continue
            if kind=="source":
                sid=shot.get("source_id")
                source=sources.get(sid)
                seg=segments.get((sid,shot.get("segment_id")))
                a,b=shot.get("source_in_seconds"),shot.get("source_out_seconds")
                if not source or not seg: errors.append(f"{name}: source/segment not found");continue
                if not finite(a) or not finite(b) or not (seg["start_seconds"]-0.001<=a<b<=seg["end_seconds"]+0.001):
                    errors.append(f"{name}: out of verified source range")
                if finite(a) and finite(b) and abs((b-a)-d)>0.05:
                    errors.append(f"{name}: source and timeline durations differ")
                if not shot.get("still_frames"):
                    errors.append(f"{name}: missing still frames")
                else:
                    for frame in shot["still_frames"]:
                        t=frame.get("time_seconds")
                        if not finite(t) or not finite(a) or not finite(b) or not a-0.001<=t<=b+0.001:
                            errors.append(f"{name}: still outside shot");break
            else:
                original_only=False
                if not shot.get("creative_reason"):errors.append(f"{name}: missing creative reason")
                if not shot.get("cinematography_brief"):errors.append(f"{name}: missing photography brief")
                if not shot.get("generation_prompt"):errors.append(f"{name}: missing video prompt")
                if shot.get("reference_image_status")=="generated" and not shot.get("reference_image"):
                    errors.append(f"{name}: generated reference image missing")
            if not shot.get("narrative_role"):errors.append(f"{name}: narrative role missing")
        has_original_only|=original_only
    if not has_original_only:errors.append("One variant must use only existing footage")
    return errors

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("plan",type=Path);p.add_argument("manifest",type=Path)
    a=p.parse_args()
    errors=validate(json.loads(a.plan.read_text()),json.loads(a.manifest.read_text()))
    if errors:
        for e in errors:print("ERROR:",e)
        raise SystemExit(1)
    print("Storyboard valid against verified source segments")
if __name__=="__main__":main()
