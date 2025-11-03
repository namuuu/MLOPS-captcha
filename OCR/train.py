from transformers import TrOCRProcessor, VisionEncoderDecoderModel, Trainer, TrainingArguments
from datasets import load_dataset
from PIL import Image
import torch

#Chargement du modèle et le processor
model_name = "microsoft/trocr-base-printed" # car les lettres écrites sont écrite à l'ordinateur (police)
processor = TrOCRProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

# chemins
path_dataset = __file__.replace("train.py", "dataset.json").replace("OCR\\", "")
main_path = __file__.replace("train.py", "").replace("OCR\\", "")

# Chargement du dataset (fichier JSON du type [{image:"path", captcha:"text"}])
dataset = load_dataset("json", data_files={"train": path_dataset})["train"]

# pré-traitement 
def preprocess(example):
    image = Image.open(main_path + example["image"]).convert("RGB")
    # -> pixel_values: Tensor shape [3, H, W]
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.squeeze()
    # -> labels: Tensor shape [seq_len]
    labels = processor.tokenizer(example["captcha"], return_tensors="pt", padding="max_length", max_length=64, truncation=True).input_ids.squeeze()
    return {
        "pixel_values": pixel_values,
        "labels": labels
    }

# map + type forcé
dataset = dataset.map(preprocess, remove_columns=dataset.column_names)
dataset.set_format(type="torch", columns=["pixel_values", "labels"])

# Config du modèle
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.eos_token_id
model.config.max_length = 64
model.config.vocab_size = model.config.decoder.vocab_size

# Entraînement
training_args = TrainingArguments(
    output_dir="./trocr-finetuned",
    per_device_train_batch_size=4,
    num_train_epochs=5,
    logging_steps=50,
    save_strategy="no",
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

# Sauvegarde du modèle
model.save_pretrained(main_path+"/trocr-finetuned")
processor.save_pretrained(main_path+"/trocr-finetuned")
