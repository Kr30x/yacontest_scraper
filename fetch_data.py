import requests
from bs4 import BeautifulSoup

url = "http://wiki.cs.hse.ru/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D1%8B_%D0%B8_%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D1%8B_%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85_2_2023/24"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", class_="wikitable")
rows = table.find_all("tr")

# Пройти по каждой строке и найти ссылки внутри
hrefs = []
for row in rows:
    links = row.find_all("a")
    for link in links:
        href = link.get("href")
        hrefs.append(href)
with open('228contests.txt', 'w') as f:
    for line in hrefs:
        f.writelines(line + '/enter/' + '\n')