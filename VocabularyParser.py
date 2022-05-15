from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import init, Fore
import requests
import csv

def PrintError(message):
    print(f"\n\t[{Fore.RED}!{Fore.WHITE}] {message}")

def PrintWarning(message):
    print(f"\n\t[{Fore.YELLOW}?{Fore.WHITE}] {message}")

def main():
    # Open Targets.txt
    urls = []
    try:
        # Default: 'r'
        file = open("Targets.txt")
        
        # Remove '\n' and spaces
        lines = file.read().splitlines()

        # Place all lines in array
        for i in lines:
            urls.append(i)

        # Free memory
        file.close()
    except:
        PrintError("Reading error: Targets.txt")
        return

    # Open Result.csv
    try:
        # Write, using UTF-8
        file = open("Result.csv", "w", encoding = "utf8", newline = '')

        # [Word] [Translation]
        writter = csv.DictWriter(file, fieldnames = ["Word", "Translation"])

        # Prepare headers
        writter.writeheader()
        
        # URLs iteration
        for url in urls:
            # Prepare words (using SOUP)
            words = GetWords(url)
            if words != False:
                # Using progressbar
                print(f"# Url {Fore.YELLOW}[{url}]{Fore.WHITE} started, progress: ")
                for i in tqdm(words):
                    # Get word details (buffer[0] - info, buffer[1] - translation) or False
                    buffer = FetchWord(i)
                    
                    # If finded via WooordHunt
                    if buffer != False:
                        # Write into .csv
                        writter.writerow({ "Word": buffer[0], "Translation": buffer[1] })
    except:
        PrintError("Reading error: Result.csv")

    PrintWarning("Well done!")
    # Free memory
    file.close()

# Print a word type (ex: (n, v) or (n)
def PrintWordType(wordType, currentLen, maxLen):
    if currentLen < maxLen:
        return wordType + ", "
    else:
        return wordType

def FetchWord(word):
    # Try to get HTML source
    try:
        # Using WooordHunt
        request = requests.get("http://wooordhunt.ru/word/" + word)
    except:
        PrintError("Requests module error!")
        return False

    # Try to using SOUP
    try:
        soup = BeautifulSoup(request.text, "html.parser")
    except:
        PrintError("BeautifulSoup module error!")
        return False

    result = [ word, "" ]

    # Find a british transcription
    britishDiv = soup.find("div", { "id" : "uk_tr_sound" })
    britishSource = soup.find("span", class_ = "transcription")
    try:
        result[0] += " " + britishSource.text[1:] + " ("
    except:
        PrintWarning(f"British transcription not found, word [{word}]")
        return False

    # Forms
    formsDiv = soup.find_all("h4", class_ = "pos_item")
    maxLen = len(formsDiv)
    currentLen = 0

    # Print a word type
    for i in formsDiv:
        currentLen += 1
        buffer = i.text
        if "существительное" in buffer:
            result[0] += PrintWordType("n", currentLen, maxLen)
        if "глагол" in buffer:
            result[0] += PrintWordType("v", currentLen, maxLen)
        if "прилагательное" in buffer:
            result[0] += PrintWordType("adj", currentLen, maxLen)
        if "наречие" in buffer:
            result[0] += PrintWordType("adv", currentLen, maxLen)

    result[0] = result[0] + ")"

    # Translation
    translationDiv = soup.find("div", { "id" : "content_in_russian" })
    translationSource = soup.find("div", class_ = "t_inline_en")
    try:
        result[1] = translationSource.text
    except:
        PrintWarning(f"Translation not found, word [{word}]")
        return False

    return result

def GetWords(url):
    # Try to get HTML source
    try:
        request = requests.get(url)
    except:
        PrintError("Requests module error!")
        return False

    # Try to using SOUP
    try:
        soup = BeautifulSoup(request.text, "html.parser")
    except:
        PrintError("BeautifulSoup module error!")
        return False

    # Find all "word" class
    words = soup.find_all("a", class_ = "word")

    # Prepare result
    result = []
    for i in words:
        result.append(i.text[1:])
    return result

# Entry Point
if __name__ == "__main__":
    main()
