import base64
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_products_from_image(image_bytes: bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Ini adalah struk belanja. "
                            "Tugas kamu HANYA:\n"
                            "- Ambil NAMA PRODUK saja\n"
                            "- Abaikan harga, tanggal, toko\n"
                            "- Kembalikan dalam bentuk LIST JSON\n\n"
                            "Contoh output:\n"
                            "[\"Indomie Goreng\", \"Aqua 600ml\"]"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
