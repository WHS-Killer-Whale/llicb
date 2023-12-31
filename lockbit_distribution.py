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


def get_ip_from_url(url):
    try:
        ip_address = socket.gethostbyname(url)
        return ip_address
    except Exception as e:
        print(f"Error: {e}")
        return None



def get_country_from_ip(ip_address):
    try:
        reader = Reader('GeoLite2-Country.mmdb')  
        response = reader.country(ip_address)
        return response.country.name
    except Exception as e:
        print(f"Error: {e}")
        return None


def append_to_csv(filename, data):

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerows(data)

def load_companies_from_csv(filename):
    companies_in_csv = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                companies_in_csv.add(row[0])  
    except FileNotFoundError:

        return companies_in_csv
    return companies_in_csv


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

def remove_existing_header(filename):
    data_list = csv_to_list(filename)

    first_row = data_list[0] if data_list else []


    expected_header = ['company name', 'country', 'description', 'sector']
    if first_row == expected_header:
        data_list.pop(0)

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)


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

    while True:
        try:
            comp_num = int(input("Enter the number of affected companies to obtain information (based on the order posted on the leak site). Please enter a number greater than or equal to 10  : \n"))
            if comp_num > 9 :
                break
        except ValueError:
            print("This is not an integer. Please enter it again.")
    
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
    chrome_options.add_argument("--headless") 

    driver = webdriver.Chrome(options=chrome_options)

    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion"
    driver.get(url)

    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion/conditions"
    driver.get(url)

    url = "http://lockbitaptc2iq4atewz2ise62q63wfktyrl4qtwuk5qax262kgtzjqd.onion"
    driver.get(url)
    time.sleep(5)
    sendMessage = ''
    sendMessage += 'Lockbit Victim List and gpt opnion\n\n'

    name_country_list = []
    
    remove_existing_header('companies_info.csv')
    for i in range(1,comp_num+1):
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

      

    sectors_name = ""
    for i in range(0,len(name_country_list)):
        if len(name_country_list[i][2]) > 10 or not("https://" in name_country_list[i][2]) :
            json_message = "Do you know about a company called "+str(name_country_list[i][0])+ " that is supposed to operate in the country of "+str(name_country_list[i][1])+"?" + "Part of the description of the entity is as follows. "+ "'"+ str(name_country_list[i][2])+ "'. "+ "Answer in words, not sentences. For example, if it's manufacturing, it's manufacturing, and if it's education, it's education.  If you don't know, answer 'null'."
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
                sendMessage += "company name : " + companies_list[i][0] + ", There is a typo in the company name or the server is closed. \n\n"
            else :
                sendMessage += "company name : " + companies_list[i][0] + ", There is a typo in the company name or the server is closed, but we estimated the industry. business type : " + companies_list[i][3] + "\n\n" 
        else : 
            sectors = companies_list[i][3]
            if sectors.lower() != "null" :
                sendMessage += "company name : " + companies_list[i][0] + ", country : " + companies_list[i][1] + ", business type : " + sectors +"\n\n"
            else :
                sendMessage += "company name : " + companies_list[i][0] + ", country : " + companies_list[i][1] + ", business type : Estimated industry not found in gpt. \n\n"
            
                

    for i in range(0, len(companies_list)) :
        if companies_list[i][1] != "typo" :
            country_list.append(companies_list[i][1])
            if companies_list[i][3].lower() != "null" :
                sectors_list.append(companies_list[i][3])
                
    
    
    

    append_to_csv('companies_info.csv', name_country_list)
    


    bigSectors = str(sectors_list) + " The Python list above lists the industries of the companies. Convert the values to the corresponding one of the thirteen large industries listed below. (Technology, healthcare, finance, manufacturing, retail, energy, real estate, transportation, Leisure, Food, Media, Education, Services) Your answer should be sent in the form of ['technology', 'healthcare', ... ,'energy'] without any other words. I'll convert your returned response to 'ast.literal_val' into a list and use it on Python, so make sure to send it in the form of ['Technology', 'Healthcare', ... , 'Energy'."

    response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {gpt_api_key}"},
    json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": bigSectors}]},
    )

    industry_list = ast.literal_eval(response.json()["choices"][0]["message"]["content"])
    

    
    for i in range(0,len(industry_list)) :
        sectors_name += industry_list[i] + ", "
        sectors_name += "',' We continue to list 13 industry group names. These listed names are the industry groups of ransomware victims. So count the number of each industry group and describe the characteristics of the number in 3 sentences."
    response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {gpt_api_key}"},
    json={"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": sectors_name}]},
    )
    statistics = response.json()["choices"][0]["message"]["content"] 

    sendMessage += "GPT4's opinion : " + statistics + "\n"

    
    industry_series = pd.Series(industry_list)


    industry_counts = industry_series.value_counts()
    

    matplotlib.use('Agg')
    plt.figure(figsize=(10,6))
    sns.barplot(x=industry_counts.index, y=industry_counts.values, alpha=0.8)
    plt.title('Frequency by industry sector')
    plt.ylabel('frequency', fontsize=12)
    plt.xlabel('industry sector', fontsize=12)
    plt.xticks(rotation=90)


    plt.savefig("industry_counts.png", dpi=300, bbox_inches='tight')




    country_series = pd.Series(country_list)


    country_counts = country_series.value_counts()


    plt.figure(figsize=(10,6))
    sns.barplot(x=country_counts.index, y=country_counts.values, alpha=0.8)
    plt.title('Frequency by country')
    plt.ylabel('frequency', fontsize=12)
    plt.xlabel('country', fontsize=12)
    plt.xticks(rotation=90)


    plt.savefig("country_counts.png", dpi=300, bbox_inches='tight')
    

    add_header_to_csv('companies_info.csv')
    
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

    if use_telegram == "y":
        if len(sendMessage) > 4090 :
            save_string_to_txt('message.txt', sendMessage)
            send_document( "The character limit has been exceeded and is sent to the txt file.", './message.txt')
        else :
            send_message( sendMessage )
        send_document( "csv file", './companies_info.csv' )
        send_document( "industry graph image", './industry_counts.png' )
        send_document( "country graph image", './country_counts.png' )
    elif use_telegram == "n":
        save_string_to_txt('message.txt', sendMessage)

  
if __name__ == '__main__':
    
    main()
