#!/usr/bin/env python3
"""Sample source footage as a timed flipbook, without cloud or AI calls."""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

def sample_times(start,end,interval=1.0):
    if not all(math.isfinite(v) for v in (start,end,interval)) or start<0 or end<=start or interval<=0:
        raise ValueError("Invalid sampling interval")
    times=[]
    i=0
    while start+i*interval<end-0.0001:
        times.append(round(start+i*interval,3))
        i+=1
    return times

def sample(manifest,folder,interval=1.0):
    folder.mkdir(parents=True,exist_ok=True)
    for source in manifest["sources"]:
        path=Path(source["source_file"])
        if not path.is_file():raise FileNotFoundError(path)
        source["sampled_frames"]=[]
        for seg in source["segments"]:
            frames=[]
            for idx,t in enumerate(sample_times(seg["start_seconds"],seg["end_seconds"],interval)):
                name=f"{source['id']}_{seg['id']}_{idx:04d}.jpg"
                dest=folder/name
                subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
                    "-ss",str(t),"-i",str(path),"-frames:v","1","-vf","scale=480:-2",
                    "-q:v","3",str(dest)],check=True,capture_output=True)
                frames.append({"time_seconds":t,"image":name})
            seg["still_frames"]=frames
            source["sampled_frames"].extend(frames)
    manifest["sampling_interval_seconds"]=interval
    manifest["frame_sampling_status"]="complete"
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--interval",type=float,default=1.0)
    args=p.parse_args()
    if not shutil.which("ffmpeg"):p.error("ffmpeg missing")
    data=json.loads(args.manifest.read_text(encoding="utf-8"))
    result=sample(data,args.output,args.interval)
    (args.output/"sampled-manifest.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Saved",sum(len(s["sampled_frames"]) for s in result["sources"]),"sampled frames")
if __name__=="__main__":main()
