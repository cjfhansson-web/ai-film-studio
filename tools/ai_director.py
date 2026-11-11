#!/usr/bin/env python3
"""Opt-in AI director pilot. Sends sampled JPEG frames to OpenAI; no original videos uploaded.
Requires OPENAI_API_KEY. Output is checked against the real manifest before saving.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from validate_creative_plan import validate

API="https://api.openai.com/v1/chat/completions"
def collect(manifest,folder,max_images=24):
    frames=[]
    for src in manifest.get("sources",[]):
        for seg in src.get("segments",[]):
            for fr in seg.get("still_frames",[]):
                path=folder/Path(fr["image"]).name
                if path.is_file():
                    frames.append((src["id"],seg["id"],fr["time_seconds"],path))
    if not frames:raise ValueError("No sampled frames found")
    # Evenly distribute the visual budget across all source frames.
    if len(frames)>max_images:
        indices=[round(i*(len(frames)-1)/(max_images-1)) for i in range(max_images)]
        frames=[frames[i] for i in indices]
    return frames

def request_plan(brief,manifest,frames,model="gpt-4.1-mini"):
    key=os.environ.get("OPENAI_API_KEY")
    if not key:raise RuntimeError("OPENAI_API_KEY not set")
    source_data=[{"id":s["id"],"duration_seconds":s["duration_seconds"],
        "segments":[{"id":g["id"],"start_seconds":g["start_seconds"],
            "end_seconds":g["end_seconds"],"still_frames":g.get("still_frames",[])}
            for g in s.get("segments",[])]} for s in manifest["sources"]]
    instructions=("You are a creative film director and editor. Return JSON only, with schema_version='0.2', "
        "project and variants. Produce two genuinely distinct edit variants: A uses ONLY real source shots; "
        "B may include pickup or generated placeholders ONLY when creatively justified. "
        "Every source shot must reference a real source_id and segment_id, with in/out inside its segment; "
        "timeline_duration_seconds must equal out minus in. Include still_frames copied from the "
        "corresponding sampled segment, ideally frames within the selected in/out. "
        "Each shot needs id, kind, narrative_role, creative_reason, timeline_duration_seconds and treatment "
        "with crop_aspect_ratio, look_name and Swedish resolve_instructions. "
        "For pickup/generated shots add cinematography_brief in Swedish, generation_prompt in English, "
        "reference_image_status='not_generated', reference_image=null. "
        "The image samples are sparse: do not claim to have heard audio or seen continuous movement. "
        "Aim for the requested duration if sufficient footage is available; never fabricate sources. "
        "Use Swedish for concepts and explanations. JSON object only.")
    parts=[{"type":"text","text":"CREATIVE BRIEF:\n"+brief+"\nVERIFIED SOURCES:\n"+json.dumps(source_data,ensure_ascii=False)}]
    for sid,seg,t,path in frames:
        parts.append({"type":"text","text":f"Frame: source_id={sid}, segment_id={seg}, time_seconds={t}"})
        parts.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+base64.b64encode(path.read_bytes()).decode(),"detail":"low"}})
    payload={"model":model,"temperature":0.8,"response_format":{"type":"json_object"},
        "messages":[{"role":"system","content":instructions},{"role":"user","content":parts}]}
    req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={
        "Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=120) as response:
        data=json.load(response)
    return json.loads(data["choices"][0]["message"]["content"])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest",type=Path)
    p.add_argument("--frames",type=Path,required=True)
    p.add_argument("--brief",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--max-images",type=int,default=24)
    p.add_argument("--model",default="gpt-4.1-mini")
    a=p.parse_args()
    if not 2<=a.max_images<=64:p.error("--max-images must be 2..64")
    manifest=json.loads(a.manifest.read_text(encoding="utf-8"))
    brief=a.brief.read_text(encoding="utf-8").strip()
    if not brief:p.error("Creative brief is empty")
    frames=collect(manifest,a.frames,a.max_images)
    print(f"Sending {len(frames)} stills (not video files) to AI model {a.model}",file=sys.stderr)
    try:
        plan=request_plan(brief,manifest,frames,a.model)
        errors=validate(plan,manifest)
        if errors:raise ValueError("AI edit plan rejected:\n"+"\n".join(errors))
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
        print("Validated creative edit plan:",a.output)
    except (urllib.error.HTTPError,urllib.error.URLError,ValueError,KeyError) as e:
        print("AI analysis failed; no storyboard saved:",str(e),file=sys.stderr)
        raise SystemExit(1)
if __name__=="__main__":main()
