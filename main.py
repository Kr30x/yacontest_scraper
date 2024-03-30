import os, codecs, time
import gspread
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

def read_contests(PATH_TO_CONTESTS):
    contests = []
    with open(PATH_TO_CONTESTS) as f:
        for line in f.readlines():
            contests.append(line.strip())
    return contests


def auth(auth_link, username, password):
    driver.get(auth_link)
    auth_button = driver.find_element(By.CLASS_NAME, "link_access_login")
    auth_button.click()
    time.sleep(1)
    file = driver.page_source
    soup = BeautifulSoup(file, 'html.parser')
    input_elems = soup.find_all('input', class_='input__control')
    username_input_id = input_elems[0].get('id')
    password_input_id = input_elems[1].get('id')
    user_form = driver.find_element("id", username_input_id)
    pass_form = driver.find_element("id", password_input_id)
    submit_button = driver.find_element(By.CLASS_NAME, "button_theme_action")
    user_form.send_keys(username)
    pass_form.send_keys(password)
    submit_button.click()

def logout():
    logout_button = driver.find_element(By.CLASS_NAME, "button_theme_pseudo")
    logout_button.click()

def send_data(table, page_name, data):
    page = table.worksheet(page_name)
    page.update("E2", datetime.now().strftime("%H:%M:%S"))
    page.update([data.columns.values.tolist()] + data.values.tolist())


gc = gspread.service_account(filename="credits.json")
os.environ['PATH'] += r"C:\SeleniumDrivers"
driver = webdriver.Chrome()


def process_contest(idx, auth_link, group, table):
    standings_link = f"{auth_link[:-6]}" + "standings"
    driver.get(standings_link)
    end_search = False
    page_cnt = 1
    final_data = []
    final_surnames = set()
    tasks_num = 0
    def convert(a, tasks_num, contains_fine):
        a = a.split()
        try:
            place = int(a[0])
            surname = a[1] + a[2]
            name = a[3]
            patronimyc = ""
            if a[4] != '+' and a[4] != '-':
                patronimyc = a[4]
            scores = []
        except:
            return [-1, " ", " ", " ", [], -1]
        for i in range(len(a) - 3, -1, -1):
            if len(scores) < tasks_num:
                if a[i][0] == '+':
                    scores.append('+')
                elif a[i][0] == "-":
                    scores.append("-")
        if contains_fine:
            total = int((a[-2]))
        else:
            total = 0
        return [place, surname, name, patronimyc, scores, total]

    def analyse_page(page, final_surnames, final_data, group, tasks_num):
        soup = BeautifulSoup(page, 'html.parser')
        div_elements = soup.find_all('tr', class_='table__row')
        data_array = []
        participants = set()
        contains_fine = False
        for div in div_elements:
            if tasks_num == 0:
                tasks_num = div.get_text().count('/')
            if contains_fine == False and div.get_text(separator=" ").split().count('Штраф') > 0:
                contains_fine = True
            converted_participant = convert(div.get_text(strip=True, separator=" "), tasks_num, contains_fine)
            if converted_participant[1] not in participants:
                data_array.append(converted_participant)
                participants.add(converted_participant[1])
        if len(data_array) > 0:
            data_array.pop(0)
        for data in data_array:
            if data[1] in group and data[1] not in final_surnames:
                final_data.append(data)
                final_surnames.add(data[1])
        return final_surnames, final_data, tasks_num

    prev_final_result_size = -1
    while not end_search:
        prev_final_result_size = len(final_data)
        driver.get(f"{standings_link}?p={page_cnt}")
        final_surnames, final_data, tasks_num = analyse_page(driver.page_source, final_surnames, final_data, group, tasks_num)
        if prev_final_result_size == len(final_data):
            end_search = True
        page_cnt += 1

    columns = pd.DataFrame()
    places = [""] * 100
    surnames = [""] * 100
    names = [""] * 100
    patronymics = [""] * 100
    scores = [[""] * 100 for i in range(tasks_num)]
    totals = [""] * 100
    page_name = f"Дз{idx}"

    for i, data in enumerate(final_data):
        places[i] = data[0]
        surnames[i] = data[1]
        names[i] = data[2]
        patronymics[i] = data[3]
        for j in range(len(data[4])):
            scores[j][i] = data[4][j]
        totals[i] = data[5]
    columns['Место'] = places
    columns['Фамилия'] = surnames
    columns['Имя'] = names
    columns['Отчество'] = patronymics
    columns[' '] = [""] * 100
    columns['Баллы'] = totals
    columns['  '] = [""] * 100
    for i in range(tasks_num):
        columns[f'{i + 1}'] = scores[i]

    send_data(table=table, page_name=page_name, data=columns)
    return columns


def get_data(prefix):
    ans = dict()
    ans['contests'] = read_contests(f"{prefix}contests.txt")
    with open(f"{prefix}key.txt") as f:
        temp = f.readlines()
        ans['username'] = temp[0]
        ans['password'] = temp[1]
    ans['table'] = gc.open(f"{prefix}_generate")
    group = []
    with codecs.open(f'{prefix}.txt', "r", "utf_8_sig") as f:
        for line in f.readlines():
            group.append(line.split()[0])
    ans['group'] = group
    ans['auth_link'] = ans['contests'][0]
    return ans


# ALL INPUTS
groups_to_analyse = []

# Here starts the code


for group in groups_to_analyse:
    print(f"processing group {group}")
    group_data = get_data(group)
    auth(group_data['auth_link'], group_data['username'], group_data['password'])
    total_data = dict()
    for idx, contest in enumerate(group_data['contests']):
        feed = process_contest(idx + 1, contest, group_data['group'], group_data['table'])
        for i, item in enumerate(feed['Фамилия']):
            if item == "":
                continue
            else:
                if item != "" and item in total_data:
                    total_data[item] += feed['Баллы'][i]
                else:
                    total_data[item] = feed['Баллы'][i]
    total_data = sorted(total_data.items(), key=lambda x: x[1], reverse=True)
    place = [i for i in range(1, len(total_data) + 1)]
    surnames = []
    score = []
    for item in total_data:
        surnames.append(item[0])
        score.append(item[1])
    package = pd.DataFrame()
    package['Место'] = place
    package['Фамилия'] = surnames
    package['Баллы'] = score
    send_data(group_data['table'], "Общий зачет", package)
    logout()
