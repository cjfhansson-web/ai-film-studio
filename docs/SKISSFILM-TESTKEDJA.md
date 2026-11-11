# Provkedja – hackig skissfilm

**Status:** Utvecklingskod på separat gren. Inga AI-anrop, ingen molnuppladdning och ingen Resolve-export ännu.

## Steg 1: scenkandidater
```bash
python3 tools/analyze_video.py --output analysis video1.mp4 video2.mp4 video3.mp4
```

## Steg 2: en bild per sekund
```bash
python3 tools/sample_frames.py analysis/manifest.json --output analysis/frames --interval 1
```
Detta skapar JPEG-bilder samt `analysis/frames/sampled-manifest.json`. Bilderna är knutna till källtidskoder. För snabbare rörelse kan `--interval 0.25` användas för fyra bilder per sekund. Adaptivt urval är ännu inte implementerat.

## Steg 3: skapa och kontrollera kreativ klippplan
Exempel på JSON-struktur finns i `examples/storyboard-v02.example.json`. En framtida AI-integration ska skapa planen med verkliga segment-ID:n från sampled-manifest.

```bash
python3 tools/validate_creative_plan.py storyboard.json analysis/frames/sampled-manifest.json
```

## Steg 4: spela upp skissen
Öppna `storyboard-preview.html` lokalt. Välj storyboard-JSON och välj sedan alla motsvarande JPEG-bilder från `analysis/frames`. Välj variant och tryck Spela. Den lokala prototypen laddar inte upp filerna. Varje stillbild hålls tills nästa tidskod i den valda sekvensen.

**Begränsning:** Den nuvarande spelaren använder filval från användaren och kan inte själv generera AI-regi, automatiskt hämta bilder från filsystemet eller rendera en videofil. Den visade tidslinjen är en förhandsvisning.

## Testning
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
Dessa testfall har lagts till men är inte verifierade i GitHub CI. Verifiera på Mac med riktiga videoklipp före vidare integration.

## Nästa leverans
1. En AI-endpoint som får en samplad bildsekvens + metadata och returnerar validerade, kreativa klippbeslut.
2. Tydlig märkning av saknade scener, samt referensbildsgenerering när bildtjänsten är ansluten.
3. Ett integrerat gränssnitt för idé, uppladdning, analys, uppspelning och återkoppling.
4. Export till Resolve först efter format- och importtest.
