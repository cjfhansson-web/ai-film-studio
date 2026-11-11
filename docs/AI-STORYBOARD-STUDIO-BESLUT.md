# Beslut: AI Storyboard Studio – kreativ produktmodell (2026-11-11)

## Grundprincip
Utgå från användarens **egen idé och egna originalfilmer**. AI ska inte bara beskriva tänkbara klipp, utan föreslå flera konkreta redigeringsversioner med verkliga källintervall, ordning, rytm och bildbehandling. Första versionen spelar upp en **hackig skissfilm** byggd på stillbilder. Full videoanalys och videorendering är en senare version.

## Flöde
1. Användaren beskriver idé, syfte, målgrupp och önskad känsla och väljer egna videofiler.
2. Systemet extraherar adaptivt stillbilder ur materialet. Grundnivå ca 1 bild/s, tätare kring scenbyten eller svårtolkad rörelse. Varje bild knyts till källfil, källtidskod och teknisk metadata.
3. AI analyserar bildsekvenserna, upptäcker visuella samband och föreslår minst två alternativa filmidéer, inklusive en version som endast använder befintligt material.
4. AI skapar en faktisk edit decision list (EDL): ordning, in/ut, klipplängder, skäl, tempo, visuella övergångar och föreslagen behandling.
5. Skissfilmen spelas upp på en 30 fps-tidslinje där en stillbild typiskt hålls i 30 bildrutor. Kortare/längre hålltid kan användas för rytm. Förhandsvisningen ska kunna spela hela den föreslagna klippningen, inte bara visa en statisk kontaktkarta.
6. AI får identifiera **saknat material** och lägga in tydligt märkta platshållarscener. Dessa ska aldrig framställas som användarens befintliga footage. Varje saknad scen får en separat, AI-genererad *referensbild* (vid faktisk generering), en fotograferingsbrief och en videogenereringsprompt.
7. Användaren kan välja att filma scenen, generera videon externt eller avstå. Vid senare uppladdning ersätts platshållaren med verkligt källmaterial utan att övrig klippning försvinner.
8. Export: visuell behandlingsplan samt maskinläsbar edit plan; därefter verifierad Resolve-kompatibel XML/EDL-export med verkliga mediareferenser. Stöd för transform, crop, övergångar och grading måste testas i Resolve; inga löften om avancerad grading via XML.

## Tre explicita shot-typer
- `source`: verifierat originalklipp; kräver source_id, source_in_seconds, source_out_seconds och referens till samplade bilder.
- `pickup`: nyinspelning föreslås; kräver creative_reason, reference_image (om genererad), cinematography_brief, generation_prompt, duration_seconds.
- `generated`: AI-video föreslås; samma produktionsinformation, men intended_production='ai_video'. En genererad referensbild är **inte** färdig video.

## Per-shot-regi
- Klippning: position, duration, transition, pacing, narrative_role.
- Bildbehandling: crop_aspect_ratio, normalized_crop_rect, position, zoom, look_name, color_temperature_intent, contrast_intent, saturation_intent.
- Praktisk instruktion: `resolve_instructions` på svenska, med tydlig skillnad mellan kreativa riktvärden och exakt stödda Resolve-kommandon.
- Saknade scener: syfte, varför originalmaterialet inte räcker, alternativ utan nyinspelning, referensbild, kameravinkel, objektivkänsla, kamerarörelse, ljus, färg, rekvisita, tidslängd och prompt.

## Krav på AI
- Får bara referera till källintervall som finns i analysmanifestet.
- Ska föreslå minst en version utan nyproducerade scener och kan ge en ambitiös version med föreslagna kompletteringar.
- Ska skilja mellan vad den faktiskt kan observera i stillbilder och vad den antar om rörelse/ljud.
- Ska kunna begära tätare sampling innan den väljer kritiska klipppunkter.
- Ska ge kreativt motiverade beslut, inte generiska listor med taggar.
- Ingen referensbild får utges för att vara en stillbild från användarens original.

## MVP-acceptans
- En verklig källfil ger samplade stillbilder med spårbara tidskoder.
- AI:s edit plan kan valideras maskinellt och visas som uppspelbar skissfilm.
- Minst en platshållarscen kan visas i samma tidslinje, tydligt märkt och med båda produktionsinstruktionerna.
- Det går att exportera planens JSON utan att tappa källkopplingar eller instruktioner.
- Befintliga `index.html` på main lämnas orörd.
