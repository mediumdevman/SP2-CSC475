# Shared Interfaces

How the components talk to each other. If you change a function's inputs or outputs, update this file and tell the group.

---

## Shared conventions

**Vibe vector:** every scorer returns a dict with the same three keys, each a float in `[0, 1]` (the image scorer also returns `outdoor`, which is removed by the context module before matching):

```python
{"warmth": 0.0–1.0, "happiness": 0.0–1.0, "energy": 0.0–1.0}
```

| Key | 0 means | 1 means |
|---|---|---|
| `warmth` | cold, grey, stark | sunny, warm, cozy |
| `happiness` | sad, lonely | happy, joyful |
| `energy` | calm, peaceful | energetic, lively |

**Song record:** how one song is passed between components (e.g. into the playlist builder):

```python
{
    "song_id": int,
    "path": str,            # audio file path
    "title": str,
    "artist": str,
    "duration_sec": float,
    "vector": {"warmth": ..., "happiness": ..., "energy": ...},
}
```

---

## C1: Image scorer (Jackson, `Image/image_scorer.py`, exists)

```python
image_to_vector(path: str) -> dict
# {"warmth", "happiness", "energy", "outdoor"}, each 0–1
```

- Loads CLIP (ViT-B/32, LAION-2B) once at import.
- An indoor/outdoor check decides which warmth prompts are used.
    - For indoor photos, colour-based prompts determine the image's warmth score. For outdoor photos we use prompts that try to match the weather to the warmth of a photo: snow vs. sun, cloud vs. clear, etc.
- `outdoor` is the outdoor probability. It is stored in the vector for the context module (C2), even though it won't translate to plotting the image in 3D space.

## C2: Context module (Jackson, not built yet)

```python
get_context(path: str) -> dict
# {"datetime": datetime | None, "lat": float | None, "lon": float | None,
#  "temp_c": float | None, "precip_mm": float | None, "cloud_cover": float | None}

apply_context(vector: dict, context: dict) -> dict
# returns the 3-axis vibe vector {"warmth", "happiness", "energy"}; "outdoor" is dropped here
```

- `get_context` reads EXIF (time + GPS) and calls Open-Meteo. Any value it can't get is `None`, and it never raises.
- If a photo has no location data stored, we use the CLIP analysis as the final and only score.
- If a photo does have location data, we use an equation to figure out how the location data changes the score. If it's a cozy, warm inside photo, but location data returns that it is -3 outside, the warmth score will be increased by a multiplier. We use the outdoor probability that is stored in the vector for this.
- Blend with CLIP's warmth score. Helps where photos that are warm visually can be even warmer if geolocationally we know the exact temperature of the moment.

## C3: librosa feature extractor (`Librosa/extract_features.py`, exists)

```python
extract_features(path: str) -> dict
# {"file", "tempo_bpm", "loudness_db", "onset_rate", "brightness_hz",
#  "low_mid_ratio", "noisiness", "mode", "mode_strength"}
```

- Raw features, not a vibe vector. C5 turns these into a vector.
- Running the script on a folder writes `features.csv`.

## C4/C5: CLAP scorer and song model (Brooklynn)

```python
song_to_vector(audio_path: str) -> dict   # vibe vector (CLAP zero-shot), exists
predict_song_vector(features: dict, clap_embedding=None) -> dict   # vibe vector (Systems B/C), not built yet
```


## C6: Library and playlist builder (Jaiya, not built yet)

```python
load_library(system: str = "A_clap_zeroshot") -> list[dict]   # list of song records
build_playlist(photo_vector: dict, minutes: float, songs: list[dict]) -> list[dict]
write_m3u(playlist: list[dict], out_path: str) -> str          # returns the file path
```

- `build_playlist` ranks songs by distance to the photo vector and adds the closest until the total is within ±3 min of `minutes`.
- **[DECIDE]** Distance: Euclidean, or weighted per axis?
- **[DECIDE]** Flow rules (no back-to-back artist, smooth energy changes): now, or later (D8)?

---

## Main pipeline (Jackson, `weather_report.py`, not built yet)

```bash
python weather_report.py photo.jpg --minutes 45
```

1. `vector = image_to_vector(photo)`
2. `context = get_context(photo)`; `vector = apply_context(vector, context)`
3. `songs = load_library()`
4. `playlist = build_playlist(vector, minutes, songs)`
5. `write_m3u(playlist, "playlist.m3u")`, then print the playlist
