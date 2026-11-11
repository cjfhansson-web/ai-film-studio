# AI-regissören: första körbara pilot

**Status:** AI-anropskod implementerad men ännu inte körd mot OpenAI eller riktiga videor. Kör endast på utvecklingsgrenen. Den befintliga webbsidan på main påverkas inte.

## Förutsättningar
Mac eller annan dator med Python 3, ffmpeg och ffprobe. OpenAI API-nyckel med aktiv fakturering. API-anrop kostar pengar; ingen nyckel får läggas i GitHub eller i HTML.

## Kör lokalt
```bash
python3 tools/analyze_video.py --output analysis film1.mp4 film2.mp4 film3.mp4
python3 tools/sample_frames.py analysis/manifest.json --output analysis/frames --interval 1
```
Skriv din kreativa idé och filmbrief i `brief.txt`. Därefter:
```bash
export OPENAI_API_KEY='DIN_API_NYCKEL'
python3 tools/ai_director.py analysis/frames/sampled-manifest.json \
  --frames analysis/frames --brief brief.txt --output analysis/ai-storyboard.json --max-images 24
```
**Sekretess:** Enbart utvalda JPEG-stillbilder och manifestmetadata skickas till AI-tjänsten i denna pilot, inte originalvideofilerna. Manifestet innehåller inga lokala sökvägar i API-anropet. Tänk på att bildinnehållet kan vara känsligt.

**Budget:** `--max-images` begränsar hur många bilder som skickas; kostnaden beror också på bildinnehåll, textlängd och modell. Standard är 24 stillbilder, maximalt 64. Detta är ett initialt bildurval, inte ännu adaptiv analys.

Om AI returnerar ogiltiga segment eller tidsintervall stoppas processen och ingen ny storyboard sparas. Systemet försöker inte automatiskt rätta en ogiltig plan i denna version.

## Förhandsgranskning
Öppna `storyboard-preview.html` och välj `analysis/ai-storyboard.json` samt samtliga JPEG-filer från `analysis/frames`. Välj variant och spela upp. Förslag till nya scener visas som platshållare med fotograferingsbrief och AI-videoprompt; referensbilder genereras ännu inte.

## Kända begränsningar
- Denna pilot är ett **lokalt kommandoradsflöde**, inte en ansluten webbtjänst.
- Bildsamplingen ger inte ljudanalys eller full rörelseförståelse.
- En genererad storyboard är inte automatiskt en bra film: mänsklig granskning krävs.
- Modellen kan misslyckas med JSON-krav eller kreativa krav; då stoppas resultatet.
- Ingen automatisk bildgenerering, molnuppladdning eller verifierad Resolve-export ännu.
- Inga faktiska API-anrop eller videobaserade integrationstester har utförts här.

## Nästa
Provkör med tre korta egna filmer, dokumentera fel och kostnad. Lägg därefter till korrigeringsloop, bildgenerering för föreslagna scener och ett gemensamt webbaserat arbetsflöde.
