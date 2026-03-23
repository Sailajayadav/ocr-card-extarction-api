import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN_ROUTER")
)

def call_llm(prompt: str):
    try:
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "You are a JSON generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=256
        )

        return completion.choices[0].message.content

    except Exception as e:
        print("HF Router Error:", str(e))
        return None