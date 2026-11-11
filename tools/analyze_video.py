#!/usr/bin/env python3
"""Local video segmentation pilot. Requires ffmpeg and ffprobe on PATH.
No uploads, AI calls, or changes to original videos.
Usage: python3 tools/analyze_video.py --output ./analysis video1.mp4 video2.mov
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)

def probe(path):
    data=json.loads(run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=index,codec_type,width,height,avg_frame_rate",
        "-of","json",str(path)]).stdout)
    duration=float(data.get("format",{}).get("duration",0))
    if duration<=0: raise ValueError("Missing or invalid duration: "+str(path))
    streams=data.get("streams",[])
    if not any(s.get("codec_type")=="video" for s in streams):
        raise ValueError("No video stream: "+str(path))
    return {"duration":round(duration,3),"streams":streams}

def scene_times(path,duration,threshold=0.30):
    cmd=["ffmpeg","-hide_banner","-nostdin","-i",str(path),"-an",
         "-vf",f"select=gt(scene\\,{threshold}),showinfo",
         "-f","null","-"]
    result=subprocess.run(cmd,capture_output=True,text=True)
    if result.returncode!=0: raise RuntimeError("Scene detection failed: "+result.stderr[-700:])
    times=[]
    for line in result.stderr.splitlines():
        if "showinfo" in line:
            m=re.search(r"pts_time:\s*([0-9.]+)",line)
            if m:
                t=float(m.group(1))
                if 0<t<duration: times.append(t)
    return sorted(set(times))

def segments(duration,cuts,max_length=6.0,min_length=0.65):
    """Return non-overlapping intervals, retaining short final tails by merging."""
    boundaries=[0.0]+[t for t in cuts if 0<t<duration]+[duration]
    boundaries=sorted(set(boundaries))
    chunks=[]
    for start,end in zip(boundaries,boundaries[1:]):
        while end-start>max_length:
            chunks.append((start,start+max_length))
            start+=max_length
        if end>start: chunks.append((start,end))
    merged=[]
    for start,end in chunks:
        if merged and end-start<min_length:
            prev,_=merged[-1];merged[-1]=(prev,end)
        elif merged and start-merged[-1][1]<0.001 and merged[-1][1]-merged[-1][0]<min_length:
            prev,_=merged[-1];merged[-1]=(prev,end)
        else: merged.append((start,end))
    return [(round(a,3),round(b,3)) for a,b in merged if b>a]

def thumbnail(path,at,destination):
    run(["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
         "-ss",str(at),"-i",str(path),"-frames:v","1","-vf",
         "scale=480:-2","-q:v","3",str(destination)])

def analyze(paths,out,threshold,max_length):
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for i,path in enumerate(paths,1):
        if not path.is_file(): raise FileNotFoundError(path)
        info=probe(path)
        cuts=scene_times(path,info["duration"],threshold)
        intervals=segments(info["duration"],cuts,max_length)
        clips=[]
        for j,(start,end) in enumerate(intervals,1):
            thumb=out/f"clip{i:02d}_segment{j:03d}.jpg"
            thumbnail(path,(start+end)/2,thumb)
            clips.append({"id":f"clip{i:02d}-s{j:03d}","start_seconds":start,
                          "end_seconds":end,"duration_seconds":round(end-start,3),
                          "thumbnail":thumb.name,"thumbnail_time_seconds":round((start+end)/2,3)})
        results.append({"id":f"clip{i:02d}","source_file":str(path.resolve()),
                        "duration_seconds":info["duration"],"streams":info["streams"],
                        "scene_cuts_seconds":[round(t,3) for t in cuts],"segments":clips})
    manifest={"schema_version":"0.1","analysis_type":"technical_scene_candidates",
              "ai_analyzed":False,"sources":results}
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos",nargs="+",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--threshold",type=float,default=0.30)
    parser.add_argument("--max-length",type=float,default=6.0)
    args=parser.parse_args()
    if not 0<args.threshold<1 or args.max_length<=0: parser.error("Invalid threshold or max-length")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        parser.error("ffmpeg and ffprobe must be installed")
    manifest=analyze(args.videos,args.output,args.threshold,args.max_length)
    print(f"Analyzed {len(manifest['sources'])} videos; results in {args.output}")

if __name__=="__main__": main()
