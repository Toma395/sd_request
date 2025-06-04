import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
import os

url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

payload = {
    "prompt": "a fantasy castle on a hill, sunset, high detail",
    "steps": 20,
    "width": 512,
    "height": 512,
    "save_images": False
}

# 処理時間の計測開始
start_time = time.time()
response = requests.post(url, json=payload)
r = response.json()

# レスポンスの中身を表示
print("Response JSON:", json.dumps(r, indent=2))

# 'images' キーが存在するかチェック
if "images" in r:
    os.makedirs("./outputs/custom_folder", exist_ok=True)
    image = Image.open(BytesIO(base64.b64decode(r['images'][0])))
    image.save("./outputs/custom_folder/output.png")
    print("✅ 画像を保存しました")
else:
    print("❌ 'images' キーが含まれていません。エラー発生かも")

# 時間計測終了（保存完了時点）
end_time = time.time()
elapsed_time = end_time - start_time

print(f"⏱ リクエスト～保存までの所要時間: {elapsed_time:.2f} 秒")
