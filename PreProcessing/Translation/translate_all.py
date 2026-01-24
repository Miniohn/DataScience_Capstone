import os
import requests

API_KEY = "API_KEY"
url = f"https://translation.googleapis.com/language/translate/v2?key={API_KEY}"

input_folder = "input_txts"
output_folder = "output_txts"

os.makedirs(output_folder, exist_ok=True)

def translate_line(text: str) -> str:
    if not text.strip():
        return ""

    payload = {
        "q": text,
        "source": "fa",
        "target": "en",
        "format": "text",
    }
    res = requests.post(url, data=payload)

    # 1) HTTP 상태 코드 확인
    if res.status_code != 200:
        print("HTTP 오류 코드:", res.status_code)
        print("응답 내용:", res.text)
        raise Exception("Translation API HTTP error")

    # 2) JSON 파싱
    data = res.json()

    # 3) API 자체 에러 확인
    if "error" in data:
        print("Google Translation API 에러:", data["error"])
        raise Exception("Translation API returned an error")

    # 4) 정상 데이터인지 확인
    if "data" not in data or "translations" not in data["data"]:
        print("예상과 다른 응답 형식:", data)
        raise Exception("Unexpected response format")

    return data["data"]["translations"][0]["translatedText"]


def translate_file(input_path, output_path):
    print(f"번역 시작: {input_path} → {output_path}")
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            translated = translate_line(line.strip("\n"))
            fout.write(translated + "\n")
    print(f"완료: {output_path}")

def main():
    files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    print(f"총 {len(files)}개 파일 번역 시작\n")

    for filename in files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename.replace(".txt", "_en.txt"))
        translate_file(input_path, output_path)

    print("\n모든 파일 번역 완료!")

if __name__ == "__main__":
    main()
