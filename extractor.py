from dotenv import load_dotenv
import os
import json
import re
import cv2
from paddleocr import PaddleOCR

from llama_client import call_llm

load_dotenv()

# -------------------------------
# Initialize OCR
# -------------------------------
ocr = PaddleOCR(use_angle_cls=True, lang="en")

# -------------------------------
# Helper: Clean text
# -------------------------------
def clean_text_list(text_list):
    cleaned = []
    for t in text_list:
        t = t.strip()
        t = t.replace("-", "")   # fix phone like -919949590688
        cleaned.append(t)
    return cleaned

# -------------------------------
# Fallback Regex Extraction
# -------------------------------
def fallback_extract(text):

    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\s]{8,}", text)

    return {
        "Name": "",
        "Email": email[0] if email else "",
        "Phone": phone[0] if phone else "",
        "Designation": "",
        "Organization": ""
    }

# -------------------------------
# LLM Extraction
# -------------------------------
def extract_with_qwen(text_list):

    text_list = clean_text_list(text_list)
    text = "\n".join(text_list)

    prompt = f"""
Extract the following fields from the visiting card text.

STRICT RULES:
- Return ONLY valid JSON
- Do not add explanations
- Do not add extra text

Fields:
Name
Email
Phone
Designation
Organization

JSON format:

{{
 "Name": "",
 "Email": "",
 "Phone": "",
 "Designation": "",
 "Organization": ""
}}

Text:
{text}
"""

    try:
        response = call_llm(prompt)

        if not response:
            print("⚠ Empty LLM response → using fallback")
            return fallback_extract(text)

        # Extract JSON safely
        json_match = re.search(r"\{.*\}", response, re.DOTALL)

        if json_match:
            json_text = json_match.group()
            return json.loads(json_text)
        else:
            print("⚠ JSON not found → fallback")
            return fallback_extract(text)

    except Exception as e:
        print("⚠ LLM failed:", e)
        return fallback_extract(text)

# -------------------------------
# MAIN FUNCTION
# -------------------------------
def extract_contact_details(image_path):

    img = cv2.imread(image_path)

    if img is None:
        print("❌ Could not read image:", image_path)
        return None

    results = ocr.ocr(img)

    if not results or not results[0]:
        print("⚠ No text detected")
        return None

    text_list = [line[1][0] for line in results[0]]

    print("OCR Text:", text_list)

    data = extract_with_qwen(text_list)

    return data