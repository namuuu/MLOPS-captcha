from fastapi import FastAPI, File, UploadFile
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import io
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def mon_script_traitement(image_bytes):
    """
    C'est ici que vous placez votre logique de script Python.
    Exemple: Ouvrir l'image et récupérer ses dimensions.
    """
    image = Image.open(io.BytesIO(image_bytes))
    # Exemple de traitement : on récupère la taille et le format
    # Vous pourrirez ici faire de l'OCR, du ML, du redimensionnement, etc.
    largeur, hauteur = image.size
    format_img = image.format
    
    return {
        "message": "Analyse de l'image terminée",
        "largeur": largeur,
        "hauteur": hauteur,
        "format": format_img
    }

def monOcr(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    main_path = __file__.replace("api\\", "").replace("api-server.py", "")

    processor = TrOCRProcessor.from_pretrained(main_path+"/trocr-finetuned")
    model = VisionEncoderDecoderModel.from_pretrained(main_path+"/trocr-finetuned")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return{
        "Text_predit": text
    }


@app.post("/analyser-image/")
async def create_upload_file(file: UploadFile = File(...)):
    # 1. Lire le contenu du fichier uploadé
    contents = await file.read()
    
    # 2. Exécuter votre script python sur ce contenu
    resultat = mon_script_traitement(contents)
    
    # 3. Renvoyer le résultat en JSON
    return resultat

@app.post("/analyser-ocr/")
async def create_upload_file(file: UploadFile = File(...)):
    # 1. Lire le contenu du fichier uploadé
    contents = await file.read()
    
    # 2. Exécuter votre script python sur ce contenu
    resultat = monOcr(contents)
    
    # 3. Renvoyer le résultat en JSON
    return resultat