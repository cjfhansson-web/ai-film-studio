# AI Film Studio 2.0 — verifierad teknisk nulägesgranskning
Datum: 2026-11-11
Status: Planering; inga produktionsändringar.

## Verifierat i GitHub
- `index.html`: befintligt lokalt video-filval och stillbilds-/storyboardflöde. Ingen nätverksuppladdning eller anrop till backend identifierat.
- `creative-lab.html`: regelbaserad brief och konceptvisning. Ingen faktisk videobaserad AI-analys.
- `worker.js`: POST `/analyze` accepterar 1–8 små bild-data-URL:er och brief; anropar bildförståelsemodell för koncept i JSON. Inga videoobjekt, ljudspår, segment eller rendering.
- `wrangler.toml`: Worker-konfiguration; inga lagringsbindningar eller köer deklarerade.
- `README.md`: endast projektnamn.

## Målfunktion, första vertikala snitt
Tre originalfilmer → privat uppladdning → scen-/shot-segmentering och analys → utvalda tidsintervall med representativa stillbilder → visuellt klippbord för cirka 30 sekunder.

## Föreslagen arkitektur (ännu ej implementerad)
1. Webbläsaren får kortlivade uppladdningsbehörigheter från en autentiserad API-tjänst; stora filer laddas direkt till privat objektlagring med återupptagbar överföring.
2. Backend skapar asynkrona analysjobb; media-worker kör FFmpeg/ffprobe, extraherar metadata, scener, nyckelrutor, ljudindikatorer och kandidattidsintervall.
3. AI bedömer kandidater mot briefen och föreslår flera redigeringsvarianter. Alla referenser ska valideras mot verkliga fil-ID:n, tidsintervall och varaktigheter.
4. Webbklippbord visar faktiska extraherade thumbnails, källklipp, in/ut, längd, föreslagen grading och skäl till valet.
5. Senare: proxy-rendering av lågupplöst provfilm samt export av redigerbar tidslinje till DaVinci Resolve (testa XML-format med gratisversionen).

## Viktiga beslut före molnaktivering
- Autentisering: nuvarande delade bearer-token är inte lämplig som permanent publik användarautentisering.
- Dataskydd: privat lagring, tidsbegränsade länkar, radering och retention.
- Kostnader: kvoter för storlek, total videotid, AI-tokens, analysjobb och rendering.
- Filformat: börja med H.264/H.265 i MP4/MOV, verifiera iPhone/Sony-filer.
- Tidsbas: frame rate och timebase måste lagras för korrekta klipp och Resolve-exporter.
- Kvalitet: thumbnail ska väljas inom varje vald delsekvens, inte enbart som omslagsbild för hela filen.

## Acceptanskriterier för första milstolpen
- Tre uppladdade videoklipp kan analyseras utan att originalfiler ändras.
- Systemet visar verifierade delsekvenser med fil-ID, start, slut och representativ thumbnail.
- Ett cirka 30 sekunders klippbord använder enbart existerande delsekvenser.
- AI kan motivera urval och erbjuda alternativ.
- Fel och kostnadsgränser visas begripligt; ingen tyst förlust av filer.
- Befintlig `index.html` på main förblir orörd under utvecklingen.

## Testplan
Enhetstester för tidskod, segmentgränser och JSON-validering; integrationstester för uppladdning/analys och radering; mobiltest i Safari; separat verifiering av faktiskt driftsatt Cloudflare- och GitHub Pages-version.

## Genomförandeordning
A. Definiera datakontrakt för klipp, segment, analysjobb och klippbord.
B. Bygg testbart lokalt analysflöde på exempelvideo innan extern molnlagring aktiveras.
C. Integrera säker uppladdning, asynkrona jobb och privat lagring.
D. Koppla AI-rankning till verkliga segment och bygg visuellt klippbord.
E. Först därefter proxy-rendering och Resolve-export.

Ingen videoanalys, uppladdning eller renderingsfunktion är implementerad genom detta dokument.
