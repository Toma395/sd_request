import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
import os
import matplotlib.pyplot as plt
import pandas as pd

url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

payload = {
    "prompt": "a fantasy castle on a hill, sunset, high detail",
    "steps": 20,
    "width": 512,
    "height": 512,
    "save_images": False
}

#output_dir = "./outputs/all_images"
output_dir = "./outputs/custom_forder"
os.makedirs(output_dir, exist_ok=True)

times = []
num_trials = 100

for i in range(num_trials):
    print(f"🌀 {i+1} 回目の生成中...")

    start_time = time.time()
    response = requests.post(url, json=payload)

    try:
        r = response.json()
        if "images" in r:
            image = Image.open(BytesIO(base64.b64decode(r['images'][0])))
            image.save(os.path.join(output_dir, f"output_{i+1:03}.png"))
        else:
            print(f"❌ {i+1} 回目: 'images' キーが見つかりません")
    except Exception as e:
        print(f"❌ {i+1} 回目: JSONまたは画像処理エラー: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    times.append(elapsed_time)

# CSVに保存
df = pd.DataFrame(times, columns=["generation_time"])
df.to_csv("generation_time_with_save.csv", index_label="trial")
print("📁 保存完了: generation_time_with_save.csv")

# 箱ひげ図
plt.figure(figsize=(8, 6))
plt.boxplot(times, vert=True)
plt.title("画像生成 + 保存時間の箱ひげ図")
plt.ylabel("所要時間（秒）")
plt.grid(True)
plt.tight_layout()
plt.show()
