# Videoanalys 2.0 – lokal pilot

Detta är ett **tekniskt första steg**, inte AI-baserat kreativt urval. Programmet läser lokala videofiler, hittar sannolika scenbyten med FFmpeg, delar upp långa scener i kortare kandidater och extraherar en mittbild per delsekvens.

## Körning
Kräver Python 3.9+ samt `ffmpeg` och `ffprobe` på PATH.

```bash
python3 -m unittest discover -s tests -p 'test_video_segments.py'
python3 tools/analyze_video.py --output ./analysis ./video1.mp4 ./video2.mov ./video3.mp4
```

Resultat: `analysis/manifest.json` och `analysis/clipNN_segmentNNN.jpg`. Originalfilmer ändras inte. Ingen data skickas till molnet. Kör endast på filer som du har rätt att behandla.

Manifestet innehåller källfil, teknisk metadata, scengränser, tidsintervall och thumbnail för varje kandidat. **Det väljer inte ännu de bästa sekvenserna, förstår inte ljud och skapar inte en 30-sekundersfilm.** En mittbild är en första approximation, inte ett kvalitetsgranskat representativt bildval.

Nästa steg: kvalitetspoängsätt flera frames per segment, utvärdera med testfilmer och anslut AI-rankning mot briefen. Därefter privat molnuppladdning och visuellt klippbord.

Begränsningar: scenidentifiering är heuristisk, kan missa långsamma scenbyten eller felidentifiera kraftig rörelse. Högupplösta videor kan ta tid att analysera. Ingen användarautentisering eller molnlagring är aktiverad.
