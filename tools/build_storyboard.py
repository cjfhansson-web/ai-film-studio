#!/usr/bin/env python3
"""Create a deterministic, clearly non-AI storyboard draft from verified video segments.
Usage: python3 tools/build_storyboard.py analysis/manifest.json --output analysis/storyboard.json
"""
import argparse
import json
from pathlib import Path

def validate_manifest(manifest):
    if manifest.get("schema_version")!="0.1": raise ValueError("Unsupported manifest schema")
    sources=manifest.get("sources")
    if not isinstance(sources,list) or not sources: raise ValueError("No video sources")
    seen=set()
    for source in sources:
        duration=source.get("duration_seconds")
        if not isinstance(duration,(int,float)) or duration<=0: raise ValueError("Invalid source duration")
        for seg in source.get("segments",[]):
            sid=seg.get("id")
            a,b=seg.get("start_seconds"),seg.get("end_seconds")
            if not isinstance(sid,str) or sid in seen: raise ValueError("Duplicate or missing segment ID")
            seen.add(sid)
            if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not (0<=a<b<=duration+0.01):
                raise ValueError("Segment outside source duration")
            if not isinstance(seg.get("thumbnail"),str) or not seg["thumbnail"]:
                raise ValueError("Missing thumbnail")
    if not seen: raise ValueError("No candidate segments")

def build(manifest,target=30.0):
    validate_manifest(manifest)
    if target<=0: raise ValueError("Target must be positive")
    sources=manifest["sources"]
    pools=[[dict(seg,source_id=source["id"],source_file=source["source_file"])
            for seg in source["segments"]] for source in sources]
    positions=[0]*len(pools)
    selected=[]
    remaining=target
    while remaining>0.001:
        progressed=False
        for i,pool in enumerate(pools):
            if positions[i]>=len(pool): continue
            seg=pool[positions[i]]
            positions[i]+=1
            length=min(seg["end_seconds"]-seg["start_seconds"],remaining)
            if length<=0: continue
            selected.append({"order":len(selected)+1,"source_id":seg["source_id"],
                "source_file":seg["source_file"],"segment_id":seg["id"],
                "source_in_seconds":seg["start_seconds"],
                "source_out_seconds":round(seg["start_seconds"]+length,3),
                "duration_seconds":round(length,3),
                "thumbnail":seg["thumbnail"],"thumbnail_time_seconds":seg["thumbnail_time_seconds"],
                "reason":"Technical candidate only; creative AI selection not performed",
                "grade_suggestion":None})
            remaining-=length
            progressed=True
            if remaining<=0.001: break
        if not progressed: break
    return {"schema_version":"0.1","type":"technical_storyboard_draft",
            "ai_selected":False,"requested_duration_seconds":target,
            "actual_duration_seconds":round(target-remaining,3),
            "incomplete":remaining>0.001,"shots":selected}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest",type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--duration",type=float,default=30.0)
    args=p.parse_args()
    data=json.loads(args.manifest.read_text(encoding="utf-8"))
    result=build(data,args.duration)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{len(result['shots'])} verified shots, {result['actual_duration_seconds']}s; AI selection: no")
if __name__=="__main__": main()
