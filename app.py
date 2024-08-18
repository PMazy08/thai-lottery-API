import re
from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests

app = FastAPI()

@app.get("/")
def say_hi():
    return {"Hello": "wassup"}

@app.get("/lotto/{day}/{month}/{year}")
# low >>> 30 ธันวาคม 2549

def get_lotto_results(day: str, month: str, year: str):
    url = f"https://news.sanook.com/lotto/check/{day}{month}{year}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

    soup = BeautifulSoup(html_content, "html.parser")
    lotto_sections = soup.find_all('div', class_='lottocheck__sec')

    if not lotto_sections:
        raise HTTPException(status_code=404, detail="Results not found")

    results = {
        "lotto_1": "",
        "side_prizes": [],
        "2back_number": "",
        "front_number": [],
        "back_number": [],
        "lotto_2": [],
        "lotto_3": [],
        "lotto_4": [],
        "lotto_5": []
    }

    patterns = {
        "lotto_1": re.compile(r"รางวัลที่ 1\s*รางวัลละ \d{1,3}(?:,\d{3})* บาท\s*(\d{6})"),
        "side_prizes": re.compile(r"รางวัลข้างเคียงรางวัลที่ 1\s*\d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*([\d\s]+)"),
        "2back_number": re.compile(r"เลขท้าย 2 ตัว\s*\d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*(\d{2})"),
        "front_number": re.compile(r"เลขหน้า 3 ตัว\s*\d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*(\d{3})\s*(\d{3})"),
        "back_number": re.compile(r"เลขท้าย 3 ตัว\s*\d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*((?:\d{3}\s*){1,4})"),
        "lotto_2": re.compile(r"รางวัลที่ 2\s*มี \d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*([\d\s]+)"),
        "lotto_3": re.compile(r"รางวัลที่ 3\s*มี \d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*([\d\s]+)"),
        "lotto_4": re.compile(r"รางวัลที่ 4\s*มี \d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*([\d\s]+)"),
        "lotto_5": re.compile(r"รางวัลที่ 5\s*มี \d+ รางวัลๆละ \d{1,3}(?:,\d{3})* บาท\s*([\d\s]+)")
    }

    for section in lotto_sections:
        text = section.get_text(separator='\n').strip()
        # print(f"Section Text:\n{text}\n") 

        for key, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                if key == "lotto_1":
                    results[key] = match.group(1).strip()
                elif key == "side_prizes":
                    results[key] = [prize.strip() for prize in match.group(1).split() if prize.strip()]
                elif key == "2back_number":
                    results[key] = match.group(1).strip()
                elif key == "front_number":
                    results[key] = [num.strip() for num in match.groups() if num.strip()]
                elif key == "back_number":
                    results[key] = [num.strip() for num in match.group(1).split() if num.strip()]
                else:
                    results[key] = [prize.strip() for prize in match.group(1).split() if prize.strip()]

    return results

