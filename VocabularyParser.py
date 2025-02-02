from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import csv

# На 03.02.2025 есть проблема с сертами WH.
# False отключает обязательную проверку, но делает соединение уязвимым для MITM-атак.
verify_wh = False

TYPE_MAPPING = {
    "существительное": "n",
    "глагол": "v",
    "прилагательное": "adj",
    "наречие": "adv"
}

def PrintError(message):
    print(f"[!] {message}")

def PrintWarning(message):
    print(f"[?] {message}")

def ReadTargets(path: str) -> list[str]:
    result = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            for url in file.read().splitlines():
                number = url.strip().split('/')[-1]
                result.append(number)
    except Exception as e:
        PrintError(e)
    return result

def GetToken() -> str | None:
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.vocabulary.com',
        'priority': 'u=1, i',
        'referer': 'https://www.vocabulary.com/',
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }
    try:
        response = requests.post('https://api.vocabulary.com/1.0/auth/token', headers=headers)
        if not response.ok:
            PrintWarning(f"Невалидный HTTP-код ({response.status_code}) с API авторизации vocabulary.com")
            return None
        return response.json()['access_token']
    except Exception as e:
        PrintError(e)
    return None

def GetWordsList(token: str, id: str) -> list:
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU',
        'authorization': f'Bearer {token}',
        'origin': 'https://www.vocabulary.com',
        'priority': 'u=1, i',
        'referer': 'https://www.vocabulary.com/',
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'x-time-zone': 'Asia/Yekaterinburg',
    }
    try:
        response = requests.get(
            f'https://api.vocabulary.com/1.0/lists/{id}',
            headers=headers
        )

        if not response.ok:
            PrintWarning(f"HTTP Error ({response.status_code}) for id [{id}]")
            return None

        result = []
        for word in response.json()['wordlist']['words']:
            result.append(word['word'])
        return result
    except Exception as e:
        PrintError(e)
    return None

def FetchWord(word):
    headers = {
        'Accept-Language': 'ru-RU',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        response = requests.get(
            f'https://wooordhunt.ru/word/{word}',
            headers=headers,
            verify=verify_wh
        )

        if not response.ok:
            PrintWarning(f"HTTP Error ({response.status_code}) for word [{word}]")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        british_source = soup.find("span", class_="transcription")
        translation_source = soup.find("div", class_="t_inline_en")
        forms_div = soup.find_all("h4", class_="pos_item")

        if not british_source:
            PrintWarning(f"Транскрипция не найдена для слова: ({word})")
            return None

        transcription = british_source.text[1:].strip()
        word_types = []
        for item in forms_div:
            text = item.text.lower()
            for rus_name, short_name in TYPE_MAPPING.items():
                if rus_name in text:
                    word_types.append(short_name)
                    break

        type_str = f"({', '.join(word_types)})" if word_types else ""
        if not translation_source:
            PrintWarning(f"Перевод не найден для слова: ({word})")
            return None

        translation = translation_source.get_text(strip=True)
        return [
            f"{word} {transcription} {type_str}",
            translation
        ]
    except Exception as e:
        PrintError(e)
    return None

def EntryPoint() -> None:
    targetsPath = "Targets.txt"
    resultPath = "Result.csv"

    targets = ReadTargets(targetsPath)
    if len(targets) == 0:
        PrintError(f"В файле ({targetsPath}) нет корректных урлов!")
        return

    token = GetToken()
    if token is None:
        PrintError("Не удалось получить токен для (api.vocabulary.com)!")
        return

    try:
        with open(resultPath, "w", encoding="utf8", newline='') as file:
            writter = csv.DictWriter(file, fieldnames=["Word", "Translation"])
            writter.writeheader()
            for url in tqdm(targets):
                for word in GetWordsList(token, url):
                    if result := FetchWord(word):
                        writter.writerow({"Word": result[0], "Translation": result[1]})
    except Exception as e:
        PrintError(e)

if __name__ == "__main__":
    EntryPoint()