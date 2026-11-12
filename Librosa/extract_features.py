"""
Weather Report - librosa feature extractor.
 
Extracts low-level acoustic features from audio files so they can be stored in
the song database and used as inputs.

"""

from __future__ import annotations
 
import argparse
import csv
import logging
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
 
import numpy as np
import librosa


# Settings

SR = 22050            # sample rate everything is resampled to
HOP = 512             # hop length (samples) for frame-based features
N_MFCC = 13           # number of MFCCs (timbre)
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff", ".aif"}
 
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

""" Return (mode, mode_strength)
mode: 1 = major, 0 = minor.
mode_strength: best major-key match minus best minor-key match (> 0 leans major / brighter, < 0 leans minor / darker).
"""
def major_minor(chroma_mean):

    with np.errstate(invalid="ignore", divide="ignore"):
        major = max(np.corrcoef(chroma_mean, np.roll(MAJOR_PROFILE, k))[0, 1] for k in range(12))
        minor = max(np.corrcoef(chroma_mean, np.roll(MINOR_PROFILE, k))[0, 1] for k in range(12))
    major, minor = np.nan_to_num(major), np.nan_to_num(minor)   # silent audio -> 0
    return int(major >= minor), float(major - minor)
 
def extract_features(path):
    """Extract features for one sog and return them as a dict"""
    
    y, sr = librosa.load(str(path), sr=SR, mono=True)

    if not np.any(y):
        raise ValueError("audio is empty or silent")

    S = np.abs(librosa.stft(y)) # frequency x time frames

    freqs = librosa.fft_frequencies(sr=sr) # the frequency (Hz) of each row of S

    #ENERGY
    
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_bpm = float(np.atleast_1d(tempo)[0])                 # can be off by x2
    loudness_db = float(librosa.amplitude_to_db(librosa.feature.rms(y=y)[0]).mean())
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_rate = len(onsets) / (len(y) / sr)                   # note/hit onsets per second
    
    #WARMTH
    brightness = float(librosa.feature.spectral_centroid(S=S, sr=sr).mean())    # Hz; lower = warmer
    low_mid = (freqs >= 100) & (freqs <= 800)
    power = S ** 2  
    low_mid_ratio = float(power[low_mid].sum() / power.sum())  # share of energy in the 100-800 Hz "body"
    noisiness = float(librosa.feature.spectral_flatness(S=S).mean())            # 0 tonal ... 1 noise/distortion

 
    #HAPPY
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    mode, mode_strength = major_minor(chroma)
    
    return {
        "file": Path(path).name,
        "tempo_bpm": tempo_bpm,             # energy, happy
        "loudness_db": loudness_db,         # energy
        "onset_rate": onset_rate,           # energy
        "brightness_hz": brightness,        # warmth (low), energy/happy (high)
        "low_mid_ratio": low_mid_ratio,     # warmth
        "noisiness": noisiness,             # warmth (low)
        "mode": mode,                       # happy
        "mode_strength": mode_strength,     # happy
    }



def main():
    folder = Path(sys.argv[1])                     # e.g. python extract_features.py music/
    songs = sorted(f for f in folder.iterdir() if f.suffix.lower() in AUDIO_EXTS)
    rows = [extract_features(song) for song in songs]
 
    with open("features.csv", "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
 
 
if __name__ == "__main__":
    main()
 