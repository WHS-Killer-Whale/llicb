from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import socket
import requests
from geoip2.database import Reader
import time
import requests
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import matplotlib

# URL에서 IP 주소를 가져오기
def get_ip_from_url(url):
    try:
        ip_address = socket.gethostbyname(url)
        return ip_address
    except Exception as e:
        print(f"Error: {e}")
        return None


# IP 주소를 사용하여 국가 찾기
def get_country_from_ip(ip_address):
    try:
        reader = Reader('GeoLite2-Country.mmdb')  # MaxMind GeoLite2 데이터베이스 파일
        response = reader.country(ip_address)
        return response.country.name
    except Exception as e:
        print(f"Error: {e}")
        return None


def append_to_csv(filename, data):
    # CSV 파일을 추가 모드로 열기
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 데이터를 순회하며 한 줄씩 추가
        writer.writerows(data)

def load_companies_from_csv(filename):
    companies_in_csv = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                companies_in_csv.add(row[0])  # 가정: 첫 번째 열이 회사명
    except FileNotFoundError:
        # 파일이 없을 경우 빈 세트 반환
        return companies_in_csv
    return companies_in_csv

# CSV 파일에 없는 기업들만 담긴 새로운 리스트 생성
def get_unique_companies(csv_filename, current_list):
    existing_companies = load_companies_from_csv(csv_filename)
    unique_companies = [company for company in current_list if company[0] not in existing_companies]
    return unique_companies



def csv_to_list(filename):
    data_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                data_list.append(row)
    except FileNotFoundError:
        print(f"{filename} The file does not exist.")
    return data_list

def save_string_to_txt(file_name, string_data):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(string_data)



def add_header_to_csv(filename):

    data_list = csv_to_list(filename)

    first_row = data_list[0] if data_list else []

    expected_header = ['company name', 'country', 'description', 'sector']
    if first_row != expected_header:
        data_list.insert(0, expected_header)


    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)
    
def main():
    gpt_api_key = input("gpt_api_key : \n")
    while True:
        use_telegram = input("To send the result via Telegram, enter 'n' if you do not want to use 'y' Telegram : \n").lower()
        if use_telegram == 'y':
            telegram_api_key = input("telegram_api_key : \n")
            chat_id = input("telegram_chat_id : \n")
            break
        elif use_telegram == 'n':
            telegram_api_key = ""
            chat_id = ""
            break
        else:
            print("You entered it incorrectly. Please enter it again. \n")


    
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
    chrome_options.add_argument("--headless") # 이 옵션을 적용하면 크롬창 안보여요 

    driver = webdriver.Chrome(options=chrome_options)
# 첫 요청으로 쿠키를 획득
    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion"
    driver.get(url)
# 바로 파싱하면 페이지 특성상 찾을 수 없기에 먼저 릭사이트 내 다른 페이지로 이동
    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion/conditions"
    driver.get(url)
# 피해자를 나열한 페이지로 다시 이동
    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion"
    driver.get(url)
    time.sleep(5)
    sendMessage = ''
    sendMessage += 'Lockbit Victim List and gpt opnion\n\n'
# 빈 배열 선언
    name_country_list = []

    add_header_to_csv('companies_info.csv')
# 피해자 명단을 파싱
    for i in range(1,11):
        url = driver.find_element("xpath", '/html/body/div[3]/div[1]/div/a['+str(i)+']/div[1]/div/div/div[1]').text   
        name_country_list.append([])
        ip_address = get_ip_from_url(url)
        country = get_country_from_ip(ip_address)
        company_name = url[:url.find('.')]
        if company_name == "co" :
            tmp = url[url.find('.')+1:]
            company_name = tmp[:tmp.find('.')]
        name_country_list[i-1].append(company_name)
        if country == None :
            name_country_list[i-1].append("typo")
        else :
            name_country_list[i-1].append(country)
        description = driver.find_element("xpath", '/html/body/div[3]/div[1]/div/a['+str(i)+']/div[2]/div').text  
        name_country_list[i-1].append(description)
            
    driver.quit()
    name_country_list = get_unique_companies('companies_info.csv', name_country_list)

      
# 가난해서 3개만 출력
# 꼭 레포에 올릴때 api키 먼저 지우고 입력받고 돌아가게 수정하기
    sectors_name = ""
    for i in range(0,len(name_country_list)):
        if len(name_country_list[i][2]) > 10 or not("https://" in name_country_list[i][2]) :
            json_message = "Do you know about a company called "+str(name_country_list[i][0])+ " that is supposed to operate in the country of "+str(name_country_list[i][1])+"?" + "Part of the description of the entity is as follows. "+ "'"+ str(name_country_list[i][2])+ "'. "+ "Answer in words, not sentences. For example, if it's manufacturing, it's manufacturing, and if it's service, it's service. If you don't know, answer 'null'."
            response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {gpt_api_key}"},
            json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": json_message}]},
            )
            sectors = response.json()["choices"][0]["message"]["content"]
            name_country_list[i].append(sectors)
        else :
            json_message = "Do you know about a company called "+str(name_country_list[i][0])+ " that is supposed to operate in the country of "+str(name_country_list[i][1])+"? " + "Answer in words, not sentences. For example, if it's manufacturing, it's manufacturing, and if it's service, it's service. If you don't know, answer 'null'."
            response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {gpt_api_key}"},
            json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": json_message}]},
            )
            sectors = response.json()["choices"][0]["message"]["content"]
            name_country_list[i].append(sectors)
                


    sectors_list =[]
    country_list = []
    companies_list = csv_to_list('companies_info.csv')
    
    for i in range(0, len(companies_list)) :
        if companies_list[i][1] == "typo" :
            if companies_list[i][3].lower() == "null" :
                sendMessage += "회사 명 : " + companies_list[i][0] + ", 회사 이름에 오타가 있거나 서버가 닫혀있습니다. \n"
            else :
                sendMessage += "회사 명 : " + companies_list[i][0] + ", 회사 이름에 오타가 있거나 서버가 닫혀있지만 업종을 추정 하였습니다. 추정 업종 : " + companies_list[i][3] + "\n" 
        else : 
            sectors = companies_list[i][3]
            if sectors.lower() != "null" :
                sendMessage += "회사 명 : " + companies_list[i][0] + ", 추정 국가 : " + companies_list[i][1] + ", 추정 업종 : " + sectors +"\n"
            else :
                sendMessage += "회사 명 : " + companies_list[i][0] + ", 추정 국가 : " + companies_list[i][1] + ", 추정 업종 : gpt에서 추정 업종을 찾을 수 없습니다. \n"
            
                

    for i in range(0, len(companies_list)) :
        if companies_list[i][1] != "typo" :
            country_list.append(companies_list[i][1])
            if companies_list[i][3].lower() != "null" :
                sectors_list.append(companies_list[i][3])
                sectors_name += companies_list[i][3] + ", "
    
    
    

    append_to_csv('companies_info.csv', name_country_list)
    
    sectors_name += "Instead of grouping the industry into sub-categories like the list above, group the common parts into major categories, produce statistics, and explain them within 3 sentences including the statistics."
    response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {gpt_api_key}"},
    json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": sectors_name}]},
    )
    statistics = response.json()["choices"][0]["message"]["content"] 

    sendMessage += "GPT4's opinion : " + statistics + "\n"


    bigSectors = str(sectors_list) + " The Python list above lists the industries of the companies. Convert the values to the corresponding one of the eight large industries listed below. (Technology, healthcare, finance, manufacturing, retail, energy, real estate, transportation, Leisure, Food, Media, Education) Your answer should be sent in the form of ['technology', 'healthcare', ... ,'energy'] without any other words."

    response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {gpt_api_key}"},
    json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": bigSectors}]},
    )
    industry_list = ast.literal_eval(response.json()["choices"][0]["message"]["content"])

    # 리스트를 pandas Series로 변환
    industry_series = pd.Series(industry_list)

    # 각 산업 분야별 빈도수 계산
    industry_counts = industry_series.value_counts()
    
    # 그래프 그리기
    matplotlib.use('Agg')
    plt.figure(figsize=(10,6))
    sns.barplot(x=industry_counts.index, y=industry_counts.values, alpha=0.8)
    plt.title('Frequency by industry sector')
    plt.ylabel('frequency', fontsize=12)
    plt.xlabel('industry sector', fontsize=12)
    plt.xticks(rotation=90)

    # 그래프를 이미지 파일로 저장
    plt.savefig("industry_counts.png", dpi=300, bbox_inches='tight')




    country_series = pd.Series(country_list)

    # 각 산업 분야별 빈도수 계산
    country_counts = country_series.value_counts()

    # 그래프 그리기
    plt.figure(figsize=(10,6))
    sns.barplot(x=country_counts.index, y=country_counts.values, alpha=0.8)
    plt.title('Frequency by country')
    plt.ylabel('frequency', fontsize=12)
    plt.xlabel('country', fontsize=12)
    plt.xticks(rotation=90)

    # 그래프를 이미지 파일로 저장
    plt.savefig("country_counts.png", dpi=300, bbox_inches='tight')
    


    
    get_update_api = f"http://api.telegram.org/bot{telegram_api_key}/getUpdates"

    send_message_api = f"https://api.telegram.org/bot{telegram_api_key}/sendMessage"
    send_document_api = f"https://api.telegram.org/bot{telegram_api_key}/sendDocument"

    def send_message(text):
                    response = requests.post(
                                    url = send_message_api, data = {"chat_id": chat_id, "text": text}
                    )
                    

    def send_document(text, filepath):
                    response = requests.post(
                                    url = send_document_api,
                                    data = {"chat_id": chat_id, "caption": text},
                                    files = {"document": open(filepath, "rb")},
                    )
    # 글자수 4096까지 제한이여서 그냥 아래와 같이 코드를 짬
    if use_telegram == "y":
        if len(sendMessage) > 4090 :
            save_string_to_txt('message.txt', sendMessage)
            send_document( "글자수 제한이 넘어가서 txt파일로 전송합니다.", './message.txt')
        else :
            send_message( sendMessage )
        send_document( "csv file", './companies_info.csv' )
        send_document( "industry graph image", './industry_counts.png' )
        send_document( "country graph image", './country_counts.png' )
    elif use_telegram == "n":
        save_string_to_txt('message.txt', sendMessage)

  
if __name__ == '__main__':
    
    main()
