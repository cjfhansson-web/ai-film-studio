// AI Film Studio — protected prototype API
// Configure OPENAI_API_KEY and STUDIO_ACCESS_TOKEN as Cloudflare Secrets.
// Do not put secret values in this public repository.
const ORIGIN = "https://cjfhansson-web.github.io";
const MODEL = "gpt-4.1-mini";
function reply(data, status = 200, origin = "") {
  const headers = {"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"};
  if (origin === ORIGIN) { headers["Access-Control-Allow-Origin"] = ORIGIN; headers["Vary"] = "Origin"; }
  return new Response(JSON.stringify(data), {status, headers});
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    if (request.method === "GET" && url.pathname === "/health")
      return reply({ok:true,service:"AI Film Studio",mode:"prototype"},200,origin);
    if (request.method === "OPTIONS") {
      if (origin !== ORIGIN) return reply({error:"Forbidden"},403);
      return new Response(null,{status:204,headers:{
        "Access-Control-Allow-Origin":ORIGIN,
        "Access-Control-Allow-Methods":"POST, OPTIONS",
        "Access-Control-Allow-Headers":"Content-Type, Authorization",
        "Access-Control-Max-Age":"600","Vary":"Origin"}});
    }
    if (request.method !== "POST" || url.pathname !== "/analyze")
      return reply({error:"Not found"},404,origin);
    if (origin !== ORIGIN) return reply({error:"Forbidden origin"},403);
    if (!env.OPENAI_API_KEY || !env.STUDIO_ACCESS_TOKEN)
      return reply({error:"Server secrets missing"},503,origin);
    if (request.headers.get("Authorization") !== "Bearer " + env.STUDIO_ACCESS_TOKEN)
      return reply({error:"Unauthorized"},401,origin);
    if (Number(request.headers.get("Content-Length")) > 1200000)
      return reply({error:"Request too large"},413,origin);
    let body;
    try {
      const raw = await request.text();
      if (new TextEncoder().encode(raw).length > 1200000) return reply({error:"Request too large"},413,origin);
      body = JSON.parse(raw);
    } catch { return reply({error:"Invalid JSON"},400,origin); }
    const frames = body?.images;
    if (!Array.isArray(frames) || frames.length < 1 || frames.length > 8 ||
      !frames.every(f => typeof f?.filename === "string" && f.filename.length <= 120 &&
        Number.isFinite(f.timeSeconds) && f.timeSeconds >= 0 &&
        typeof f.dataUrl === "string" && f.dataUrl.length <= 160000 &&
        /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(f.dataUrl)))
      return reply({error:"Provide 1–8 small JPEG/PNG/WebP stills with filename and timeSeconds"},400,origin);
    const brief = String(body.brief || "").slice(0,1000);
    const instructions = "Du är en erfaren filmregissör och klippdramaturg. Ge tre tydligt olika visuella storyboardförslag på svenska. Beskriv idé, ton, tempo och scener. Referera endast till exakta filnamn och tidsstämplar från underlaget. Påstå inte att du har sett rörelse eller hört ljud: du har bara stillbilder. Returnera enbart JSON med nyckeln concepts, en array med tre objekt. Varje objekt ska ha title, idea, mood, pacing och scenes (array med filename, timeSeconds, purpose, editSuggestion).";
    const content = [{type:"text",text:instructions+"\nÖnskemål: "+brief+"\nReferenser: "+JSON.stringify(frames.map(f=>({filename:f.filename,timeSeconds:f.timeSeconds})))},
      ...frames.map(f=>({type:"image_url",image_url:{url:f.dataUrl,detail:"low"}}))];
    let upstream;
    try {
      upstream = await fetch("https://api.openai.com/v1/chat/completions",{
        method:"POST",
        headers:{"Authorization":"Bearer "+env.OPENAI_API_KEY,"Content-Type":"application/json"},
        body:JSON.stringify({model:MODEL,messages:[{role:"user",content}],response_format:{type:"json_object"},max_completion_tokens:2200})
      });
    } catch { return reply({error:"AI unavailable"},502,origin); }
    if (!upstream.ok) return reply({error:"AI request failed",status:upstream.status},502,origin);
    try {
      const data = await upstream.json();
      const parsed = JSON.parse(data.choices?.[0]?.message?.content || "{}");
      if (!Array.isArray(parsed.concepts)) throw Error("Invalid response");
      return reply({concepts:parsed.concepts,usage:data.usage || null},200,origin);
    } catch { return reply({error:"Could not parse AI response"},502,origin); }
  }
};
