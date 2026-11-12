import laion_clap
#import numpy as np
import torch
#import librosa
import os
import contextlib

TEMPERATURE = 20

with open(os.devnull, "w") as devnull:
    with contextlib.redirect_stdout(devnull):
        model = laion_clap.CLAP_Module(enable_fusion=False)
        model.load_ckpt() #pretrained checkpoint
#music_audioset_epoch_15_esc_90.14.pt is for music specifically, check default against this eventually

#zero-shot scoring

prompts = {
    "energy": {
        "low": "A slow, mellow and low-energy song.",
        "high": "An energetic, stimulating and fast-paced song."
    },
    "happy": {
        "low": "A sad and melancholic song.",
        "high": "A happy and cheerful song."
    },
    "warmth": {
        "low": "A cold and distant song.",
        "high": "A warm and comforting song."
    }
}

text_embeds = {}

with torch.no_grad():
    for cat in prompts:
        text_embeds[cat] = model.get_text_embedding([prompts[cat]["low"], prompts[cat]["high"]], use_tensor=True)

        # Normalize
        text_embeds[cat] = torch.nn.functional.normalize(text_embeds[cat], dim=-1)


#prompts_embed = [energy_embed, happy_embed, warm_embed]

def song_to_vector(audio_path, text_embeds):

  with torch.no_grad():
    audio_embed = model.get_audio_embedding_from_filelist([audio_path], use_tensor=True)
    audio_embed = torch.nn.functional.normalize(audio_embed, dim=-1)

    vibe_vector = {}

    for cat in text_embeds:
      similarities = audio_embed @ text_embeds[cat].T

      # Similarity to low and high prompts
      low_sim = similarities[0, 0]
      high_sim = similarities[0, 1]

      probabilities = torch.softmax(torch.stack([low_sim, high_sim])*TEMPERATURE, dim=0)

      vibe_vector[cat] = probabilities[1].item()

  return vibe_vector

if __name__ == "__main__":
  import sys

  if len(sys.argv) > 1:
      path = sys.argv[1]
  else:
      path = input("Enter song file path: ")

  if not path:
      print("No song selected.")
  else:
      result = song_to_vector(path, text_embeds)

      print(f"\n{path}")
      for cat, score in result.items():
          print(f"  {cat:8} {score:.2f}")