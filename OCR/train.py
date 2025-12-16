from transformers import TrOCRProcessor, VisionEncoderDecoderModel, Trainer, TrainingArguments
from datasets import load_dataset
from PIL import Image
import torch
from pathlib import Path

# Chargement du modèle et du processor
model_name = "microsoft/trocr-base-printed"
processor = TrOCRProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

# Gestion robuste des chemins
current_file = Path(__file__).resolve()
main_path = current_file.parent.parent  # si ton script est dans un sous-dossier "OCR"
path_dataset = main_path / "dataset.json"

# Chargement du dataset JSON
dataset = load_dataset("json", data_files={"train": str(path_dataset)})["train"]

# Prétraitement des exemples
def preprocess(example):
    image_rel_path = example["image"].lstrip("/\\")  # supprime / ou \ en début
    image_path = (main_path / image_rel_path).resolve()
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.squeeze()
    labels = processor.tokenizer(
        example["captcha"],
        return_tensors="pt",
        padding="max_length",
        max_length=64,
        truncation=True
    ).input_ids.squeeze()
    return {"pixel_values": pixel_values, "labels": labels}



dataset = dataset.map(preprocess, remove_columns=dataset.column_names)
dataset.set_format(type="torch", columns=["pixel_values", "labels"])

# Config du modèle
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.eos_token_id
model.config.max_length = 64
model.config.vocab_size = model.config.decoder.vocab_size

# Arguments d'entraînement
training_args = TrainingArguments(
    output_dir=str(main_path / "trocr-finetuned"),
    per_device_train_batch_size=8,      
    num_train_epochs=5,
    learning_rate=4e-5,                
    logging_steps=50,
    save_strategy="epoch",
    save_total_limit=2,             
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

# Sauvegarde finale du modèle et du processor dans le dossier nommé output
save_path = main_path / "trocr-finetuned"
model.save_pretrained(save_path)   
processor.save_pretrained(save_path)