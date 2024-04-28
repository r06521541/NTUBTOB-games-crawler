from datetime import datetime, timezone, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from game import Game


local_timezone = timezone(timedelta(hours=8))  # 台北時間（UTC+08:00）

def get_games_from_schedules(url, my_team_name):

    # 不開頁面、禁用GPU加速等等
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu") 
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    my_team_value = ''

    select_team = Select(driver.find_element(By.NAME, 'team'))
    for team_element in select_team.options:
        if my_team_name in team_element.text:
            my_team_value = team_element.get_attribute("value")
    if not my_team_value:
        return []
    select_team.select_by_value(my_team_value)  # 選擇傳入的球隊

    total_games = []
    select_year = Select(driver.find_element(By.CSS_SELECTOR, "[ng-model='ssearch.year']"))
    for year_element in select_year.options:
        year_value = year_element.get_attribute("value")
        year = int(year_value)
        if abs(datetime.now().year - year) > 1:
            continue;
        select_year.select_by_visible_text(year_value)  # 選擇傳入的年份
        
        select_season = Select(driver.find_element(By.CSS_SELECTOR, "[ng-model='ssearch.half']"))    
        for season_element in select_season.options:
            season_value = season_element.get_attribute("value")
            season = int(season_value)
            select_season.select_by_visible_text(season_element.text)  # 選擇傳入的季度

            games = find_games(driver.page_source, year, season)
            total_games = total_games + games
    driver.quit()

    total_games.sort(key=lambda x: x.start_datetime)    
    return total_games

def find_games(html_text, year, season):
    games = []
    
    soup = BeautifulSoup(html_text, "html.parser")
    gameElements = soup.find_all('tr')
    for gameElement in gameElements:    
        tds = gameElement.findChildren("td")    
        if (len(tds) >= 6):

            start_datetime, duration = date_string_to_datetime(tds[0].text, tds[1].text)
            location = tds[2].text.replace(" ", "").replace("棒球場", "")
            away_team = tds[3].text.replace(" ", "").replace("校友", "")
            home_team = tds[4].text.replace(" ", "").replace("校友", "")

            games.append(Game(year, season, start_datetime, duration, location, home_team, away_team))
    return games

def date_string_to_datetime(date_string, time_string):
    # 將日期字串轉換為日期物件
    date_object = datetime.strptime(date_string, "%Y-%m-%d")

    # 從時間字串中取得開始和結束時間的時間物件
    start_time_object = datetime.strptime(time_string.split(" - ")[0], "%H%M")
    end_time_object = datetime.strptime(time_string.split(" - ")[1], "%H%M")

    # 合併日期和開始時間
    start_datetime = datetime.combine(date_object.date(), start_time_object.time())

    # 合併日期和結束時間
    end_datetime = datetime.combine(date_object.date(), end_time_object.time())
    
    duration = int((end_datetime - start_datetime).total_seconds() / 60)

    start_datetime = start_datetime.replace(tzinfo=local_timezone)
    return start_datetime, duration