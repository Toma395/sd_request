from flask import Flask, request, jsonify
import requests
import base64
from PIL import Image
from io import BytesIO
import os
import time
import traceback

app = Flask(__name__)

PROMPT_MAP = {
    "1": "highly detailed product, shopping mall background, close-up, QR code",
    "2": "medium range poster, short message, colorful layout",
    "3": "bold distant ad, minimal text, logo centered"
}

NPROMPT_MAP = {
    "1": "low quality, blurry",
    "2": "distorted, bad layout",
    "3": "tiny text, cluttered"
}

IMAGE_MAP = {
    "img1": "input_images/product1.jpg",
    "img2": "input_images/product2.jpg"
}

STABLE_DIFFUSION_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SIGNAGE_PC_URL = "http://172.17.10.74:5001/receive_image"

@app.route("/generate_ad", methods=["POST"])
def generate_ad():
    try:
        data = request.json
        prompt_id = data.get("prompt_id")
        image_id = data.get("image_id")

        # 入力バリデーション
        if prompt_id not in PROMPT_MAP:
            return jsonify({"error": "Invalid prompt_id"}), 400
        if image_id not in IMAGE_MAP:
            return jsonify({"error": "Invalid image_id"}), 400

        prompt = PROMPT_MAP[prompt_id]
        nprompt = NPROMPT_MAP.get(prompt_id, "")  # 存在しなければ空
        image_path = IMAGE_MAP[image_id]

        payload = {
            #"image_path": image_path,
            "prompt": prompt,
            "negative_prompt": nprompt,
            "seed": -1,
            "steps": 20,
            "width": 512,
            "height": 712,
            "save_images": False,
            "sample_name": "Euler a",
            "cfg_scale": 7.0,
            "batch_size": 1,
            "n_iter": 1,
            "restore_faces": False,
            "tiling": False,
            "enable_hr": False,
            "hr_scale": 2.0,
            "hr_upscaler": "Latent",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "webhook": None,
            "track_id": None
        }

        # 画像生成リクエスト
        response = requests.post(STABLE_DIFFUSION_URL, json=payload)
        if response.status_code != 200:
            return jsonify({"error": "Stable Diffusion API failed", "status_code": response.status_code}), 500

        result = response.json()
        if "images" not in result or not result["images"]:
            return jsonify({"error": "Image generation failed (no images)"}), 500

        # デコード & 保存
        image_data = base64.b64decode(result["images"][0])
        image = Image.open(BytesIO(image_data))

        filename = f"output_{int(time.time())}.png"
        output_path = os.path.join("outputs", filename)
        os.makedirs("outputs", exist_ok=True)
        image.save(output_path)

        # サイネージPCへ送信
        signage_response = requests.post(SIGNAGE_PC_URL, json={
            "filename": filename,
            "image_base64": result["images"][0]
        })

        if signage_response.status_code != 200:
            return jsonify({
                "status": "partial_success",
                "error": "Image generated but failed to send to signage",
                "filename": filename
            }), 502

        return jsonify({
            "status": "success",
            "send_status": signage_response.status_code,
            "filename": filename
        })

    except Exception as e:
        # ログ出力（サーバーログなどに表示）
        print("Error:", traceback.format_exc())
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)