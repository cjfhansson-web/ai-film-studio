// Independent AI edit-plan API candidate. NOT wired to deployed worker.js.
// Run unit tests before integrating into the existing protected Cloudflare Worker.
const MAX_BYTES=1_200_000;
export function checkDirectorInput(body) {
  if (!body || typeof body!=="object" || Array.isArray(body)) return "Invalid request";
  if (typeof body.brief!=="string" || !body.brief.trim() || body.brief.length>2000) return "Invalid brief";
  if (!Array.isArray(body.sources) || body.sources.length<1 || body.sources.length>8) return "Provide 1-8 sources";
  const seen=new Set(), segments=new Set();
  for(const src of body.sources){
    if(typeof src.id!=="string" || !/^[a-zA-Z0-9_-]{1,50}$/.test(src.id) || seen.has(src.id)) return "Invalid source ID";
    seen.add(src.id);
    if(!Array.isArray(src.segments) || !src.segments.length || src.segments.length>200) return "Invalid segments";
    for(const seg of src.segments){
      if(typeof seg.id!=="string" || !/^[a-zA-Z0-9_-]{1,70}$/.test(seg.id)) return "Invalid segment ID";
      const key=src.id+":"+seg.id;
      if(segments.has(key)) return "Duplicate segment";
      segments.add(key);
      if(!Number.isFinite(seg.start_seconds)||!Number.isFinite(seg.end_seconds)||seg.start_seconds<0||seg.end_seconds<=seg.start_seconds) return "Invalid segment times";
      if(!Array.isArray(seg.still_frames)||seg.still_frames.length>300) return "Invalid segment frames";
      for(const frame of seg.still_frames){
        if(typeof frame.image!=="string" || !/^[a-zA-Z0-9_.-]{1,150}$/.test(frame.image) || !Number.isFinite(frame.time_seconds) ||
           frame.time_seconds<seg.start_seconds-0.001||frame.time_seconds>seg.end_seconds+0.001) return "Invalid frame metadata";
      }
    }
  }
  if(!Array.isArray(body.images)||body.images.length<1||body.images.length>8) return "Provide 1-8 still images";
  for(const im of body.images){
    if(!seen.has(im.source_id)||!segments.has(im.source_id+":"+im.segment_id)) return "Unknown image source";
    const seg=body.sources.find(s=>s.id===im.source_id).segments.find(s=>s.id===im.segment_id);
    if(!seg.still_frames.some(f=>f.image===im.image && f.time_seconds===im.time_seconds)) return "Image not in manifest";
    if(typeof im.dataUrl!=="string" || im.dataUrl.length>160000 ||
       !/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(im.dataUrl)) return "Invalid image data";
  }
  return null;
}
export function checkDirectorPlan(plan,sources) {
  if(!plan || !Array.isArray(plan.variants)||plan.variants.length<2||plan.variants.length>5) return "At least two variants required";
  const segments=new Map();
  for(const s of sources)for(const g of s.segments)segments.set(s.id+":"+g.id,g);
  let sourceOnly=false;
  for(const v of plan.variants){
    if(!Array.isArray(v.shots)||!v.shots.length||v.shots.length>80) return "Invalid shots";
    let allSource=true;
    for(const shot of v.shots){
      if(!Number.isFinite(shot.timeline_duration_seconds)||shot.timeline_duration_seconds<=0) return "Invalid duration";
      if(shot.kind==="source"){
        const seg=segments.get(shot.source_id+":"+shot.segment_id);
        if(!seg || !Number.isFinite(shot.source_in_seconds)||!Number.isFinite(shot.source_out_seconds) ||
          shot.source_in_seconds<seg.start_seconds-0.001 || shot.source_out_seconds>seg.end_seconds+0.001 ||
          shot.source_out_seconds<=shot.source_in_seconds ||
          Math.abs((shot.source_out_seconds-shot.source_in_seconds)-shot.timeline_duration_seconds)>.05) return "Invalid source interval";
        if(!Array.isArray(shot.still_frames)||!shot.still_frames.length) return "Missing source frames";
        for(const frame of shot.still_frames){
          if(!seg.still_frames.some(f=>f.image===frame.image&&f.time_seconds===frame.time_seconds) ||
             frame.time_seconds<shot.source_in_seconds-0.001 || frame.time_seconds>shot.source_out_seconds+0.001) return "Invented or out-of-range frame";
        }
      }else if(shot.kind==="pickup"||shot.kind==="generated"){
        allSource=false;
        if(!shot.creative_reason||!shot.cinematography_brief||!shot.generation_prompt) return "Missing proposed-scene brief";
      }else return "Invalid shot kind";
    }
    if(allSource)sourceOnly=true;
  }
  return sourceOnly?null:"One source-only variant required";
}
export async function generateDirectorPlan(body,apiKey,fetchImpl=fetch) {
  const err=checkDirectorInput(body);
  if(err) return {status:400,error:err};
  if(!apiKey) return {status:503,error:"Server AI key missing"};
  const system="You are an imaginative film director. Return only a JSON object with variants: at least two distinct edits, one using only real source shots. Use only exact source IDs, segment IDs, image names and timestamps from the supplied manifest. Source in/out must be within the segment and shot duration must match. Every source shot must include a nonempty still_frames list from the manifest inside the chosen interval. Proposed pickup/generated scenes need creative_reason, cinematography_brief and generation_prompt; mark any reference image as not_generated. Explain musical rhythm, edit decisions, crop and look in Swedish. No narration unless explicitly requested. Never claim to have heard audio or observed motion between stills.";
  const content=[{type:"text",text:"BRIEF: "+body.brief+"\nVERIFIED MANIFEST: "+JSON.stringify(body.sources)},
    ...body.images.flatMap(i=>[{type:"text",text:i.source_id+"/"+i.segment_id+" @ "+i.time_seconds},
      {type:"image_url",image_url:{url:i.dataUrl,detail:"low"}}])];
  let response;
  try{
    response=await fetchImpl("https://api.openai.com/v1/chat/completions",{
      method:"POST",headers:{"Authorization":"Bearer "+apiKey,"Content-Type":"application/json"},
      body:JSON.stringify({model:"gpt-4.1-mini",response_format:{type:"json_object"},
        messages:[{role:"system",content:system},{role:"user",content}],max_completion_tokens:5000})
    });
    if(!response.ok) return {status:502,error:"AI upstream error",upstreamStatus:response.status};
    const result=await response.json();
    const plan=JSON.parse(result.choices?.[0]?.message?.content||"{}");
    const invalid=checkDirectorPlan(plan,body.sources);
    if(invalid)return {status:422,error:"AI output rejected: "+invalid};
    return {status:200,plan,usage:result.usage||null};
  }catch{return {status:502,error:"AI response unavailable or invalid"};}
}
