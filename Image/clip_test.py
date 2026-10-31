import torch, open_clip
from PIL import Image

model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
tokenizer = open_clip.get_tokenizer("ViT-B-32")

text_temp = tokenizer(["a photo that feels stark, distant and unwelcoming", "a photo that feels bright and welcoming"])
text_vibe = tokenizer(["a photo of a sad, lonely moment", "a photo of a happy, joyful moment"])
text_energy = tokenizer(["a photo of a peaceful and calm scene", "a photo of an energetic, lively scene"])

photos = ["test1.jpg", "test2.jpg", "test3.jpg", "test4.jpg", "test5.jpeg"]   # use your real file names

with torch.no_grad():
    temp_f = model.encode_text(text_temp)
    vibe_f = model.encode_text(text_vibe)
    energy_f = model.encode_text(text_energy)
    temp_f /= temp_f.norm(dim=-1, keepdim=True)
    vibe_f /= vibe_f.norm(dim=-1, keepdim=True)
    energy_f /= energy_f.norm(dim=-1, keepdim=True)

    for name in photos:
        image = preprocess(Image.open(name)).unsqueeze(0)
        img_f = model.encode_image(image)
        img_f /= img_f.norm(dim=-1, keepdim=True)

        prob_temp = (25 * img_f @ temp_f.T).softmax(dim=-1)
        prob_vibe = (25 * img_f @ vibe_f.T).softmax(dim=-1)
        prob_energy = (25 * img_f @ energy_f.T).softmax(dim=-1)

        print(f"{name:12}  warm {prob_temp[0,1]:.2f}   happy {prob_vibe[0,1]:.2f}   energetic {prob_energy[0,1]:.2f}")
