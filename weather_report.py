import sys
import argparse
sys.path.append("Image")
sys.path.append("Song")

# import our original modules
from image_scorer import image_to_vector
from context import get_context, apply_context

def photo_to_vector(path): 
    photo_vector = image_to_vector(path)
    context = get_context(path)
    return apply_context(photo_vector, context)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Report: photo -> vibe vector")
    parser.add_argument("photo", help="path to a photo (.jpg/.png/.heic)")
    parser.add_argument("--minutes", type=float, default=45, help="playlist length (used once songs are connected)")
    args = parser.parse_args()

    result = photo_to_vector(args.photo)

    print(f"\n{args.photo}")
    for key, value in result.items():
        print(f"  {key:9} {value:.2f}")