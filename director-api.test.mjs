import test from 'node:test';
import assert from 'node:assert/strict';
import {checkDirectorInput,checkDirectorPlan,generateDirectorPlan} from './director-api.mjs';
const frame={image:'frame0.jpg',time_seconds:0};
const source={id:'clip01',segments:[{id:'clip01-s001',start_seconds:0,end_seconds:3,still_frames:[frame]}]};
const shot={kind:'source',source_id:'clip01',segment_id:'clip01-s001',source_in_seconds:0,source_out_seconds:2,timeline_duration_seconds:2,still_frames:[frame]};
const body={brief:'Resglädje utan berättarröst',sources:[source],images:[{source_id:'clip01',segment_id:'clip01-s001',image:'frame0.jpg',time_seconds:0,dataUrl:'data:image/jpeg;base64,YQ=='}]};
const plan={variants:[{id:'A',shots:[shot]},{id:'B',shots:[shot]}]};
test('valid request and plan',()=>{assert.equal(checkDirectorInput(body),null);assert.equal(checkDirectorPlan(plan,[source]),null)});
test('reject fabricated frame',()=>{assert.match(checkDirectorPlan({variants:[{shots:[{...shot,still_frames:[{image:'fake.jpg',time_seconds:0}]}]},{shots:[shot]}]},[source]),/Invented/)});
test('reject missing source-only variant',()=>{const extra={kind:'pickup',timeline_duration_seconds:2,creative_reason:'Bridge',cinematography_brief:'Wide',generation_prompt:'Wide'};assert.match(checkDirectorPlan({variants:[{shots:[extra]},{shots:[extra]}]},[source]),/source-only/)});
test('reject image not in source manifest',()=>{assert.match(checkDirectorInput({...body,images:[{...body.images[0],image:'fake.jpg'}]}),/not in manifest/)});
test('AI plan passes mocked upstream response and never needs live API',async()=>{
  const mock=async()=>({ok:true,json:async()=>({choices:[{message:{content:JSON.stringify(plan)}}],usage:{total_tokens:5}})});
  const result=await generateDirectorPlan(body,'fake-test-key',mock);
  assert.equal(result.status,200);assert.equal(result.plan.variants.length,2);
});
test('invalid AI response is rejected',async()=>{
  const mock=async()=>({ok:true,json:async()=>({choices:[{message:{content:'{}'}}]})});
  assert.equal((await generateDirectorPlan(body,'fake-test-key',mock)).status,422);
});
