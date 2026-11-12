import torch, open_clip
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

SCENE_CONTEXT = 0.5
MAJOR_WEIGHT = 50
MINOR_WEIGHT = 25

model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
tokenizer = open_clip.get_tokenizer("ViT-B-32")

# decide if the image is inside or outside
context = tokenizer(["a photo of an indoor scene inside a room, with walls and a ceiling", "a photo of an outdoor scene with open sky, trees or a street"])

# the two "temperature" contexts. Is the photo outside and warm or inside and warm in a cozy way
text_temp1 = tokenizer(["a photo that is cold and stark, with blue and grey colours", "a photo that is warm and cozy, with soft colours and light"])
text_temp2 = tokenizer(["a photo that shows a cloudy, rainy day", "a photo that shows a clear, sunny day"])

# check for energy and and vibe of the scene 
text_vibe = tokenizer(["a photo of a sad, lonely moment", "a photo of a happy, joyful moment"])
text_energy = tokenizer(["a photo of a peaceful and calm scene", "a photo of an energetic, lively scene"])

with torch.no_grad():
    # encode each quality
    context_f = model.encode_text(context)
    temp1_f = model.encode_text(text_temp1)
    temp2_f = model.encode_text(text_temp2)
    vibe_f = model.encode_text(text_vibe)
    energy_f = model.encode_text(text_energy)

    # normalize
    context_f /= context_f.norm(dim=-1, keepdim=True)
    temp1_f /= temp1_f.norm(dim=-1, keepdim=True)
    temp2_f /= temp2_f.norm(dim=-1, keepdim=True)
    vibe_f /= vibe_f.norm(dim=-1, keepdim=True)
    energy_f /= energy_f.norm(dim=-1, keepdim=True)

def image_to_vector(path): 
    # {"warmth", "happiness", "energy", "outdoor"}, each 0–1
    with torch.no_grad():

        # create the probabilities
        image = preprocess(Image.open(path)).unsqueeze(0)
        img_f = model.encode_image(image)
        img_f /= img_f.norm(dim=-1, keepdim=True)

        prob_context = (MAJOR_WEIGHT * img_f @ context_f.T).softmax(dim=-1)
            
        if prob_context[0][1] >= SCENE_CONTEXT: 
            prob_temp = (MINOR_WEIGHT * img_f @ temp2_f.T).softmax(dim=-1)
        else:
            prob_temp = (MINOR_WEIGHT * img_f @ temp1_f.T).softmax(dim=-1)
            
        prob_vibe = (MINOR_WEIGHT * img_f @ vibe_f.T).softmax(dim=-1)
        prob_energy = (MINOR_WEIGHT * img_f @ energy_f.T).softmax(dim=-1)

        vibe_vector = {"warmth": prob_temp[0,1].item(), 
                       "happiness": prob_vibe[0,1].item(), 
                       "energy": prob_energy[0,1].item(),
                       "outdoor": prob_context[0,1].item()}
    
    return vibe_vector

if __name__ == "__main__":
    import sys
    from tkinter import Tk, filedialog

    # use a path from the command line if given, otherwise open a file picker
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Choose a photo",
                                          filetypes=[("Images", "*.jpg *.jpeg *.png *.heic *HEIC")])
        root.destroy()

    if not path:
        print("No file chosen.")
    else:
        result = image_to_vector(path)
        print(f"\n{path}")
        for name, score in result.items():
            print(f"  {name:8} {score:.2f}")
