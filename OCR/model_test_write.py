import os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

main_path = "./"
print("main_path :", main_path)

processor = TrOCRProcessor.from_pretrained(main_path+"/trocr-finetuned")
model = VisionEncoderDecoderModel.from_pretrained(main_path+"/trocr-finetuned")

image_files = [f for f in os.listdir(main_path+"/img") if f.endswith(('.png', '.jpg', '.jpeg'))]

for image_file in image_files:
    image_path = os.path.join(main_path, "img", image_file)
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f"Texte prédit pour l'image {image_file} : {text}")

#Modifier le nom de l'image ci-dessous...
# image = Image.open(main_path+"/img/ruvmWa.png").convert("RGB")
# pixel_values = processor(images=image, return_tensors="pt").pixel_values
# generated_ids = model.generate(pixel_values)
# text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
# print("Texte prédit :", text)

#boucle for pour tester les 10 premiers captchas
###
#for i in range(10):
#    if i != 0 :
#        image = Image.open(main_path+"/img/captcha_"+str(i)+".png").convert("RGB")
#        pixel_values = processor(images=image, return_tensors="pt").pixel_values
#       generated_ids = model.generate(pixel_values)
#        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#        print("Texte prédit pour le captcha", i, " :", text)
#