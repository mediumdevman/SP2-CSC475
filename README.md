# Weather Report: Context-Aware Playlist Generation from Photos

**Team:** Jackson MacNeil · Brooklynn Nelson · Jaiya Chauhan
| **Design / Requirements Specification**

---

## 1. Project Summary

The user uploads a photo of their surroundings and chooses a playlist length. *Weather Report* builds a playlist of about that length whose mood and energy match the scene.

- **Image side.** CLIP [1] scores the photo against text prompts. Photo metadata and a weather API add context: time of day, location, temperature, and rain.
- **Music side.** librosa [3] extracts objective features from each song (tempo, loudness, key/mode, timbre). Our own model, trained on songs we hand-label, predicts subjective qualities from those features plus pretrained CLAP [4, 5] audio embeddings.
- **Matching.** Photos and songs are scored on the same six dimensions, the *Weather Report*: energy, happiness, chillness, coolness, warmth, and danceability. We pick the closest-matching songs that add up to the requested length.

**Scope decisions:**
- We originally wanted to try and make something that is similar to Spotify's LLark [2] model, however, we have decided to not train our model in the same way. This is because LLark was trained on data sets with millions of entries. For  "Our own model", we want to create a small model trained on top of pretrained embeddings such as CLAP [4, 5].
- Also, Spotify no longer gives new apps audio features or preview clips, and Development Mode is restricted. We analyse our own audio (personal files, FMA [11], MTG-Jamendo [10]). Spotify export is a stretch goal; .m3u playlist files are the guaranteed output.

**Core experiment:** we compare three ways of scoring songs against held-out human ratings:
- **A.** CLAP zero-shot (no training)
- **B.** Our model using librosa features only
- **C.** Our model using librosa features + CLAP embedding

**Language and tools:** Python 3.11 throughout, using `open_clip`, `laion_clap`, `librosa`, `scikit-learn`, SQLite, Open-Meteo (weather), `Pillow` (EXIF). UI Language/Framework TBD (possibly Gradio)

---

## 2. Deliverables by Tier

**Basic** = every component works on its own. **Expected** = all components connected into a complete but unpolished system. **Advanced** = tested, evaluated, and polished.

### Basic: six components, two per person

| # | Component | Owner |
|---|---|---|
| C1 | CLIP image scorer: photo → Weather Report Scoring System | Jackson |
| C2 | Context module: EXIF + weather → Additonal Rating Information | Jackson |
| C3 | librosa feature extractor: audio → adjusted rating scale | Jaiya |
| C4 | Labelling protocol + tool + hand-labelled seed set (~100 songs) | Brooklynn (tool/protocol); everyone labels |
| C5 | Song vibe model + CLAP scoring: features → Weather Report | Brooklynn |
| C6 | Song database + playlist assembler: vibe vector + minutes → song list | Jaiya |

### Expected: complete end-to-end system

| # | Deliverable | Owner |
|---|---|---|
| E1 | One command: `python weather_report.py photo.jpg --minutes 45` → playlist | Jackson |
| E2 | Library of 300+ songs analysed and scored in the database | Jaiya |
| E3 | Baseline comparison of systems A, B, C | Brooklynn |
| E4 | Local UI interface + `.m3u` export | Jaiya |
| E5 | Mid-project progress report (README update) | Everyone |

### Advanced: tested and polished

| # | Deliverable | Owner |
|---|---|---|
| A1 | Fully Tested System Hosted on a Website | Everyone |
| A2 | Model Compairson/Listening Test with Friends/Participants | Everyone |
| A3 | Direct Spotify/Apple Music/Streaming Service API call to generate playlists | Everyone |


**Workload balance:** each person owns 2 basic components, 1–2 expected deliverables, and 1 advanced deliverable, and everyone labels songs and writes the paper. Brooklynn's ML experience goes where it matters most: the labelling design and the model.

---

## 3. Timeline (Oct 13 – Nov 30, 2026)

| Milestone | Dates | Jackson | Brooklynn | Jaiya | Milestone |
|---|---|---|---|---|---|
| 1 | Week of Nov 2nd | (C1) CLIP setup, prompt lists, (C2) EXIF information handler, (C4) hand lablled songs | (C4) Labelling protocol, pick seed songs, CLAP (C5) Embedding | (C3) librosa analyzer, (C6) SQLite schema, | Basic deliverables are working |
| 2 | Week of Nov 16th | Connect CLIP image scorer to python cmd line and SQLite Databse | Start training model on our hand labbled data set | Connect librosa analyzer to set of hand labbled samples | Basic Interface |
| 3 | Final Date TBD | Polish CLIP promtping & user uploads | Continue to train out Model | Refine librosa/Our Model alogrithms | Project in final state, explore Advanced Outcomes (time permitting) |


---

## 4. Personal Objectives

## Jackson MacNeil

* **Deliverables**
  * D1 (basic): run CLIP locally and compute similarity between a photo and a list of text prompts
  * D2 (basic): design prompt sets for all six dimensions and output a normalised 0–1 weather report per photo
  * D3 (basic): define the shared interfaces (function inputs/outputs) between all six components
  * D4 (basic): build a stub pipeline that runs end to end on fake data
  * D5 (expected): build a 30–50 photo test set rated by the team and report the correlation between CLIP scores and human ratings
  * D6 (expected): add weather and time-of-day context (EXIF + Open-Meteo) to the vibe vector, with fallbacks for photos without EXIF data
  * D7 (expected): connect the real components into a single command that turns a photo + length into a playlist
  * D8 (advanced): compare prompt strategies (single prompt vs prompt ensembles) and 2 CLIP model sizes on accuracy and speed
  * D9 (advanced): run the study with 8–10 participants, test for significant differences between systems, and measure whether context improves ratings

## Brooklynn Nelson

* **Deliverables**
  * D1 (basic): write a labelling protocol defining rating scale for each dimension, with example songs, share with Jack/Jiaya so they can label a set of songs too. 
  * D2 (basic): build a labelling tool that plays a clip and saves ratings to the database
  * D3 (basic): compute CLAP zero-shot prompt scores and 512-number embeddings for every song
  * D5 (expected): select a ~100-song seed set covering the full range of tempo, mood, and style, and coordinate labelling by all 3 members
  * D6 (expected): Let our model rate the songs and then compare with group to make sure our model is operating as expected
  * D7 (expected): compare systems A (zero-shot), B (librosa), and C (librosa + CLAP) with to decide which is the best trained model for our porject
  * D8 (expected): compare at least 3 model types (ridge, random forest, small MLP) and report the most important features per dimension
  * D9 (advanced): Train model on a lage, legally sourced, data set. Compare model to findings in the LLark [2] model. 

## Jaiya Chauhan

* **Deliverables**
  * D1 (basic): extract tempo, loudness, key/mode, spectral features, MFCCs, and duration with librosa
  * D2 (basic): design the SQLite schema and store features for the seed set
  * D3 (basic): rank songs by cosine similarity to the photo's vibe vector
  * D4 (basic): select songs whose total length is within ±3 minutes of the target and export as `.m3u`
  * D5 (expected): validate tempo against hand-tapped BPM for 20 songs and report common errors (half/double tempo)
  * D6 (expected): process a 300+ song library
  * D7 (expected): build a UI interface for photo upload, length selection, and playlist display
  * D8 (expected): improve playlist flow (no back-to-back repeat artists, smooth energy changes)
  * D9 (advanced): deploy a web app and, if the API allows, export playlists to Spotify

---

## 5. Related Work

Music emotion research usually models emotion in Russell's valence–arousal space [12]. Reviews [13, 14, 20] link audio features such as tempo, mode, and timbre to perceived emotion. DEAM [9] provides labelled data, and librosa [3] and Essentia [17] are standard MIR toolkits building on classic content-based analysis [16, 19].

CLIP [1] and its audio counterparts CLAP [4, 5] and MuLan [6] learn shared embedding spaces between media and text, which enables zero-shot scoring with text prompts. LLark [2] connects music encoders to a large language model, an approach too large for our scope but a key inspiration.

The closest prior work is emotion-based image–music matching [7, 8], which maps both modalities into valence–arousal space. We add interpretable custom dimensions and environmental context. Context-aware music recommendation, including location, time, and weather, is surveyed in [15]. Playlist generation and evaluation are surveyed in [18].

---

## 6. References

1. A. Radford et al., "Learning Transferable Visual Models From Natural Language Supervision," *Proc. ICML*, 2021.
2. J. Gardner, S. Durand, D. Stoller, R. Bittner, "LLark: A Multimodal Instruction-Following Language Model for Music," *Proc. ICML*, 2024.
3. B. McFee et al., "librosa: Audio and Music Signal Analysis in Python," *Proc. SciPy*, 2015.
4. B. Elizalde, S. Deshmukh, M. Al Ismail, H. Wang, "CLAP: Learning Audio Concepts from Natural Language Supervision," *Proc. ICASSP*, 2023.
5. Y. Wu et al., "Large-Scale Contrastive Language-Audio Pretraining with Feature Fusion and Keyword-to-Caption Augmentation," *Proc. ICASSP*, 2023.
6. Q. Huang et al., "MuLan: A Joint Embedding of Music Audio and Natural Language," *Proc. ISMIR*, 2022.
7. S. Zhao et al., "Emotion-Based End-to-End Matching Between Image and Music in Valence-Arousal Space," *Proc. ACM Multimedia*, 2020.
8. S. Choi, K. W. Kim, M. Kang, "MMVA: Multimodal Matching Based on Valence and Arousal across Images, Music, and Musical Captions," arXiv:2501.01094, 2025.
9. A. Aljanaki, Y.-H. Yang, M. Soleymani, "Developing a Benchmark for Emotional Analysis of Music," *PLOS ONE*, 2017.
10. D. Bogdanov et al., "The MTG-Jamendo Dataset for Automatic Music Tagging," *ICML Workshop on Machine Learning for Music Discovery*, 2019.
11. M. Defferrard, K. Benzi, P. Vandergheynst, X. Bresson, "FMA: A Dataset for Music Analysis," *Proc. ISMIR*, 2017.
12. J. A. Russell, "A Circumplex Model of Affect," *Journal of Personality and Social Psychology*, 39(6), 1980.
13. Y. E. Kim et al., "Music Emotion Recognition: A State of the Art Review," *Proc. ISMIR*, 2010.
14. Y.-H. Yang, H. H. Chen, "Machine Recognition of Music Emotion: A Review," *ACM Trans. Intelligent Systems and Technology*, 3(3), 2012.
15. M. Kaminskas, F. Ricci, "Contextual Music Information Retrieval and Recommendation: State of the Art and Challenges," *Computer Science Review*, 6(2–3), 2012.
16. G. Tzanetakis, P. Cook, "Musical Genre Classification of Audio Signals," *IEEE Trans. Speech and Audio Processing*, 10(5), 2002.
17. D. Bogdanov et al., "Essentia: An Audio Analysis Library for Music Information Retrieval," *Proc. ISMIR*, 2013.
18. G. Bonnin, D. Jannach, "Automated Generation of Music Playlists: Survey and Experiments," *ACM Computing Surveys*, 47(2), 2014.
19. D. P. W. Ellis, "Beat Tracking by Dynamic Programming," *Journal of New Music Research*, 36(1), 2007.
20. R. Panda, R. Malheiro, R. P. Paiva, "Audio Features for Music Emotion Recognition: A Survey," *IEEE Trans. Affective Computing*, 2023.

Additional references (MERT, musicnn, recommender-systems surveys, context studies) are listed in [DESIGN_DETAILS.md](DESIGN_DETAILS.md).
