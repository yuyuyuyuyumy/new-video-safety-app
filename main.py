import os
import glob
import shutil
import ffmpeg
import whisper
from transformers import pipeline
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Models...")
whisper_model = whisper.load_model("tiny")
image_classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")

def split_video(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, "audio.wav")
    try:
        ffmpeg.input(video_path).output(audio_path, ac=1, ar=16000).run(overwrite_output=True, quiet=True)
    except:
        audio_path = None
    
    frame_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    ffmpeg.input(video_path).filter('fps', fps=1).output(frame_pattern).run(overwrite_output=True, quiet=True)
    frame_paths = sorted(glob.glob(os.path.join(output_dir, "frame_*.jpg")))
    return audio_path, frame_paths

@app.post("/analyze")
@app.post("/")
async def analyze_video(file: UploadFile = File(...)):
    temp_dir = "temp_data"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    video_path = os.path.join(temp_dir, file.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_path, frame_paths = split_video(video_path, temp_dir)

    audio_res = {"text": "", "flagged": False, "words": []}
    if audio_path and os.path.exists(audio_path):
        stt = whisper_model.transcribe(audio_path)
        text = stt.get("text", "")
        ng_list = ["殺す", "暴力", "爆破", "詐欺", "攻撃", "危険"]
        detected = [w for w in ng_list if w in text]
        audio_res = {"text": text, "flagged": len(detected) > 0, "words": detected}

    visual_res = []
    has_visual_danger = False
    for idx, frame_p in enumerate(frame_paths[:30]):
        img = Image.open(frame_p)
        preds = image_classifier(img)
        nsfw_score = next((p['score'] for p in preds if p['label'].lower() == 'nsfw'), 0)
        is_unsafe = nsfw_score > 0.6
        if is_unsafe:
            has_visual_danger = True
        visual_res.append({"sec": idx, "score": round(nsfw_score * 100, 1), "is_unsafe": is_unsafe})

    return {
        "is_safe": not (audio_res["flagged"] or has_visual_danger),
        "audio": audio_res,
        "visual": visual_res
    }
