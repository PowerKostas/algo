import pandas as pd
from sklearn import linear_model
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from csv import writer
from datetime import date
import time
from scipy.stats import poisson
import numpy

# Stats from FBref
# Database can get updated about 2 days after the matches (That's when xG stats are posted on FBref)
# Teams_Elo.csv should not have an empty row in the end while Bundesliga.csv should
# At the start of a new season: 
# 1.Change season variable
# 2.Update flashscore_dict with the name that promoted teams have on flashscore and with the name they have on FBref
# Be careful not to add relegation/promotion playoff matches, that happen at the end of a season

def league_differences(league_num):
    if league_num==0:
        league='Premier League'
        xpath_league_num=9 
        matchday_games=10 
        total_season_games=380 
        driver_get_link='https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures'
        flashscore_link='https://www.flashscore.com/football/england/premier-league/'
        site_struct_1='7'
        other_site_struct_1='6'
        site_struct_2='9'
        other_site_struct_2='8'
        flashscore_dict={'Aston Villa':'Aston Villa','Arsenal':'Arsenal','Tottenham':'Tottenham','Liverpool':'Liverpool','Brighton':'Brighton','Southampton':'Southampton','Everton':'Everton','Fulham':'Fulham','Newcastle':'Newcastle Utd','Bournemouth':'Bournemouth','Brentford':'Brentford','Crystal Palace':'Crystal Palace','Chelsea':'Chelsea','West Ham':'West Ham','Wolves':'Wolves','Manchester City':'Manchester City','Manchester Utd':'Manchester Utd','Leeds':'Leeds United','Leicester':'Leicester City','Nottingham':"Nott'ham Forest"}
    elif league_num==1:
        league='Bundesliga'
        xpath_league_num=20 
        matchday_games=9 
        total_season_games=306 
        driver_get_link='https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures'
        flashscore_link='https://www.flashscore.com/football/germany/bundesliga/'
        site_struct_1='6'
        other_site_struct_1='7'
        site_struct_2='8'
        other_site_struct_2='9'
        flashscore_dict={'RB Leipzig':'RB Leipzig','Wolfsburg':'Wolfsburg','Bayern Munich':'Bayern Munich','Augsburg':'Augsburg','Stuttgart':'Stuttgart','FC Koln':'Köln','Union Berlin':'Union Berlin','Bochum':'Bochum','Bayer Leverkusen':'Leverkusen','Freiburg':'Freiburg','B. Monchengladbach':"M'Gladbach",'Hoffenheim':'Hoffenheim','Dortmund':'Dortmund','Hertha Berlin':'Hertha BSC','Mainz':'Mainz 05','Eintracht Frankfurt':'Eint Frankfurt','Schalke':'Schalke 04','Werder Bremen':'Werder Bremen'}
    elif league_num==2:
        league='Serie A'
        xpath_league_num=11 
        matchday_games=10 
        total_season_games=380 
        driver_get_link='https://fbref.com/en/comps/11/schedule/Serie-A-Scores-and-Fixtures'
        flashscore_link='https://www.flashscore.com/football/italy/serie-a/'
        site_struct_1='6'
        other_site_struct_1='7'
        site_struct_2='8'
        other_site_struct_2='9'
        flashscore_dict={'Lecce':'Lecce','Napoli':'Napoli','Torino':'Torino','Inter':'Inter','AS Roma':'Roma','Empoli':'Empoli','AC Milan':'Milan','Lazio':'Lazio','Spezia':'Spezia','Sassuolo':'Sassuolo','Salernitana':'Salernitana','Cremonese':'Cremonese','Sampdoria':'Sampdoria','Monza':'Monza','Atalanta':'Atalanta','Fiorentina':'Fiorentina','Juventus':'Juventus','Bologna':'Bologna','Verona':'Hellas Verona','Udinese':'Udinese'}
    elif league_num==3:
        league='La Liga'
        xpath_league_num=12 
        matchday_games=10 
        total_season_games=380
        driver_get_link='https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures'
        flashscore_link='https://www.flashscore.com/football/spain/laliga/'
        site_struct_1='6'
        other_site_struct_1='7'
        site_struct_2='8'
        other_site_struct_2='9'
        flashscore_dict={'Ath Bilbao':'Athletic Club','Almeria':'Almería','Cadiz CF':'Cádiz','Villarreal':'Villarreal','Getafe':'Getafe','Valladolid':'Valladolid','Sevilla':'Sevilla','Atl. Madrid':'Atlético Madrid','Mallorca':'Mallorca','Barcelona':'Barcelona','Espanyol':'Espanyol','Valencia':'Valencia','Celta Vigo':'Celta Vigo','Betis':'Betis','Girona':'Girona','Real Sociedad':'Real Sociedad','Real Madrid':'Real Madrid','Osasuna':'Osasuna','Rayo Vallecano':'Rayo Vallecano','Elche':'Elche'}
    elif league_num==4:
        league='Ligue 1'
        xpath_league_num=13 
        matchday_games=10 
        total_season_games=380 
        driver_get_link='https://fbref.com/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures'
        flashscore_link='https://www.flashscore.com/football/france/ligue-1/'
        site_struct_1='6'
        other_site_struct_1='7'
        site_struct_2='8'
        other_site_struct_2='9'
        flashscore_dict={'Angers':'Angers','Marseille':'Marseille','Strasbourg':'Strasbourg','Rennes':'Rennes','Paris SG':'Paris S-G','Nice':'Nice','Lorient':'Lorient','Lille':'Lille','Troyes':'Troyes','Reims':'Reims','Auxerre':'Auxerre','Brest':'Brest','Toulouse':'Toulouse','Montpellier':'Montpellier','AC Ajaccio':'Ajaccio','Clermont':'Clermont Foot','Monaco':'Monaco','Nantes':'Nantes','Lens':'Lens','Lyon':'Lyon'}

    return league,xpath_league_num,league_num,matchday_games,total_season_games,driver_get_link,flashscore_link,site_struct_1,other_site_struct_1,site_struct_2,other_site_struct_2,flashscore_dict

def get_stats(last_date,today,driver_get_link,xpath_league_num,season):
    # Setup
    options=webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
    options.add_argument("--window-size=1600,900")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver=webdriver.Chrome(service=Service('C:/Users/Kostas/Downloads/new_chromedriver'),options=options)
    driver.maximize_window()
    action=webdriver.ActionChains(driver)
    driver.get(driver_get_link)

    try:
        time.sleep(1) # Always has to sleep before performing actions
        driver.find_element(By.XPATH,'//*[@id="qc-cmp2-ui"]/div[2]/div/button[3]').click() # Accepts cookies

        # Scrolls and clicks the share and export button and then clicks the modify button
        driver.execute_script('window.scrollBy(0,300)')
        time.sleep(1)
        share_export=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1_sh"]/div/ul/li[1]/span')
        action.move_to_element(share_export).perform()
        time.sleep(1)
        driver.find_element(By.XPATH,'//*[@id="share_on_sched_'+season+'_'+str(xpath_league_num)+'_1"]').click()

        # Removes excess matches
        extra_matches=0
        fix=0
        flag=False
        i=1
        while True:
            i+=1
            extra_matches+=1
            try:
                # Removes future games (Have to do this weird scrolling method)
                if driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/td[2]/a').text>=today:
                    x_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/th/button[2]')
                    driver.execute_script("arguments[0].scrollIntoView();",x_button)
                    time.sleep(1)
                    driver.execute_script('window.scrollBy(0,-300)')
                    time.sleep(1)
                    x_button.click()
                    driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/th/button[1]').click()
                    extra_matches-=1
                    fix+=1
                    break
                # Removes already documented games or games where xGoals hasn't been added by the website
                elif driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/td[2]/a').text<=last_date or driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/td[5]').text=='' or driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/td[7]').text=='':
                    x_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/th/button[1]')
                    driver.execute_script("arguments[0].scrollIntoView();",x_button)
                    time.sleep(1)
                    driver.execute_script('window.scrollBy(0,-300)')
                    time.sleep(1)
                    x_button.click()
                    extra_matches-=1
                    fix+=1
                    break_point=0
                else:
                    updated_till=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/td[2]/a').text
                    flag=True
                    break_point=0
            # Removes blank row 
            except NoSuchElementException:
                x_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr['+str(i-fix)+']/th/button[1]')
                driver.execute_script("arguments[0].scrollIntoView();",x_button)
                time.sleep(1)
                driver.execute_script('window.scrollBy(0,-300)')
                time.sleep(1)
                x_button.click()
                extra_matches-=1
                fix+=1
                break_point+=1
                if break_point==4: # If there are 4 blank rows in a row it means that we are at the end of the page (no other games)
                    break

        # Scrolls and removes useless columns (date,time,etc...)
        x_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr[1]/td[1]/button[1]')
        driver.execute_script("arguments[0].scrollIntoView();",x_button)
        time.sleep(1)
        driver.execute_script('window.scrollBy(0,-300)')
        time.sleep(1)
        for i in range(4):
            x_button.click()
            x_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr[1]/td[1]/button[1]')
        driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1"]/tbody/tr[1]/td[5]/button[2]').click()

        # Scrolls to share and export, gets table as cvs and saves it in the variable
        hover_button=driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1_sh"]/div/ul/li[1]/span')
        action.move_to_element(hover_button).perform()
        driver.find_element(By.XPATH,'//*[@id="sched_'+season+'_'+str(xpath_league_num)+'_1_sh"]/div/ul/li[1]/div/ul/li[3]/button').click()
        table=driver.find_element(By.XPATH,'//*[@id="csv_sched_'+season+'_'+str(xpath_league_num)+'_1"]').text
        driver.quit()
    except NoSuchElementException:
        return 'NaN',False,'NaN',0,True
    if not flag:
        updated_till='NaN'

    return table,flag,updated_till,extra_matches,False

def csv_format_stats(table,league):
    # Removes useless information remaining on the table
    table=table[107:]
    table=[table.replace('–',',')]

    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv','a',encoding='utf-8',newline='') as file: # Appends new matches to the csv file
        writer_object=writer(file)
        writer_object.writerow(table) 

    # Removes useless information remaining on the csv file
    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv') as file: 
        result=file.read()
        new_result=result.replace('"','')

    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv','w') as file:
        file.write(new_result)

def xG_Elo_System(actual_outcome_xG,pointer_home,pointer_away,xG_elo_ratings,xG_hfa):
    temp_expected_outcome_home=1/(1+10**((xG_elo_ratings[pointer_away]-xG_elo_ratings[pointer_home])/400))
    xG_hfa=float(xG_hfa)+(20*(actual_outcome_xG-temp_expected_outcome_home))*0.075-((20*(actual_outcome_xG-temp_expected_outcome_home))*0.075)/1.5

    expected_outcome_home=1/(1+10**((xG_elo_ratings[pointer_away]-xG_hfa-xG_elo_ratings[pointer_home])/400))
    xG_elo_ratings[pointer_home]=xG_elo_ratings[pointer_home]+20*(actual_outcome_xG-expected_outcome_home)
    xG_elo_ratings[pointer_away]=xG_elo_ratings[pointer_away]-20*(actual_outcome_xG-expected_outcome_home)
        
    return xG_elo_ratings,xG_hfa

def MarWin_Elo_System(actual_outcome_win,pointer_home,pointer_away,marwin_elo_ratings,marwin_hfa,scaling_factor,scaling_pointer):
    temp_expected_outcome_home=1/(1+10**((marwin_elo_ratings[pointer_away]-marwin_elo_ratings[pointer_home])/400))
    marwin_hfa=float(marwin_hfa)+(20*(actual_outcome_win-temp_expected_outcome_home))*0.075-((20*(actual_outcome_win-temp_expected_outcome_home))*0.075)/1.5

    expected_outcome_home=1/(1+10**((marwin_elo_ratings[pointer_away]-marwin_hfa-marwin_elo_ratings[pointer_home])/400))
    marwin_elo_ratings[pointer_home]=marwin_elo_ratings[pointer_home]+20*scaling_factor[scaling_pointer]*(actual_outcome_win-expected_outcome_home)
    marwin_elo_ratings[pointer_away]=marwin_elo_ratings[pointer_away]-20*scaling_factor[scaling_pointer]*(actual_outcome_win-expected_outcome_home)

    return marwin_elo_ratings,marwin_hfa

def assign_elo(start,end,count,teams_data,xG_hfa,marwin_hfa,league,total_season_games,matchday_games):
    print('\nCalculating '+league+' elos...')
    data=pd.read_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv')

    #Initializing variables to calculate elos (we are doing the temp stuff to get rid of useless information)
    temp_teams=teams_data.loc[:,'name']
    teams=[]
    for i in range(len(temp_teams)):
        teams.append(temp_teams[i])

    temp_xG_elo_ratings=teams_data.loc[:,'xG_elo']
    xG_elo_ratings=[]
    for i in range(len(temp_xG_elo_ratings)):
        xG_elo_ratings.append(temp_xG_elo_ratings[i])
    
    temp_marwin_elo_ratings=teams_data.loc[:,'marwin_elo']
    marwin_elo_ratings=[]
    for i in range(len(temp_marwin_elo_ratings)):
        marwin_elo_ratings.append(temp_marwin_elo_ratings[i]) 

    temp_average_elo_ratings=teams_data.loc[:,'average_elo']
    average_elo_ratings=[]
    for i in range(len(temp_average_elo_ratings)):
        average_elo_ratings.append(temp_average_elo_ratings[i])     

    scaling_factor=[1,1,1.51,1.85,2.11,2.32,2.49,2.64,2.77,2.88,2.99] # Used to give extra elo in margin wins

    # Iterates for every match in the database
    # Gives stats from the database to the functions so they can calculate teams elo's
    for i in range(starting_lenght+extra_matches-1):
        # Determining  results
        if data.loc[i,'G_H']>data.loc[i,'G_A']:
            actual_outcome_win=1
        elif data.loc[i,'G_H']<data.loc[i,'G_A']:
            actual_outcome_win=0
        else:
            actual_outcome_win=0.5

        if data.loc[i,'xG_H']-float(data.loc[i,'xG_A'])>=1:
            actual_outcome_xG=1
        elif data.loc[i,'xG_H']-float(data.loc[i,'xG_A'])<=-1:
            actual_outcome_xG=0
        else:
            actual_outcome_xG=0.5

        scaling_pointer=abs(int(data.loc[i,'G_H'])-int(data.loc[i,'G_A']))
        home_team=data.loc[i,'Home']
        away_team=data.loc[i,'Away']

        # Relegation System
        # Adds promoted teams to the database and resets relegated teams elo, incase they get promoted again
        if i>=int(start) and i<=int(end): # Start and end is the index, in the Bundesliga.csv/Premier League.csv..., of the first 9/10... matches in a season
            new_team_home=True
            new_team_away=True
            count=int(count)+1
            in_league=[False]*len(teams) # Everybody starts as not in the league at the start of every season
            # Reads information of In_League.txt
            if count!=1: 
                with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/In_League.txt') as file: 
                    line=file.readlines()
                    for j in range(len(line)):
                        if line[j]=='True\n':
                            in_league[j]=line[j][:4]
                        else:
                            in_league[j]=line[j][:5]

            for j in range(len(teams)):
                if home_team==teams[j]: # If team of current iteration is found in the database it means that it's not a new team and it's still in the league
                    new_team_home=False
                    in_league[j]=True
                if away_team==teams[j]:
                    new_team_away=False
                    in_league[j]=True

            # Incase it finds a new team it adds it in the database
            if new_team_home:
                teams.append(home_team)
                xG_elo_ratings.append(900)
                marwin_elo_ratings.append(900)
                average_elo_ratings.append(900)
                in_league.append(True)
                with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv','a',encoding='utf-8',newline='') as file:
                    file.write('\n'+home_team+',900,900,900')
            if new_team_away:
                teams.append(away_team)
                xG_elo_ratings.append(900)
                marwin_elo_ratings.append(900)
                average_elo_ratings.append(900)
                in_league.append(True)
                with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv','a',encoding='utf-8',newline='') as file:
                    file.write('\n'+away_team+',900,900,900')     

            # Every new team of the season has been added at this point, so we move start and end to index the next season
            if count==matchday_games:
                start=int(start)+total_season_games
                end=int(end)+total_season_games
                count=0
                # Resets elo of relegated teams, incase they get promoted again, so to have it ready
                for j in range(len(teams)): 
                    if in_league[j]==False:
                        xG_elo_ratings[j]=900
                        marwin_elo_ratings[j]=900
                        average_elo_ratings[j]=900

            # Have to write it in a txt file incase the matches of the first matchday dont finish in the same day and I have to retrieve the in_league information a second time
            with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/In_League.txt','w') as file:
                for j in range(len(in_league)):
                    if j==0:
                        file.write(str(in_league[j]))
                    else:
                        file.write('\n'+str(in_league[j]))

        flag_1,flag_2=False,False
        for j in range(len(teams)):
            if home_team==teams[j]:
                pointer_home=j
                flag_1=True
            if away_team==teams[j]:
                pointer_away=j
                flag_2=True
            if flag_1==True and flag_2==True:
                break
        
        # Elo assignment before match
        average_elo_ratings[pointer_home]=(xG_elo_ratings[pointer_home]+marwin_elo_ratings[pointer_home])/2
        data.loc[i,'H_ELO']=average_elo_ratings[pointer_home]
        data.to_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv', index=False)
        average_elo_ratings[pointer_away]=(xG_elo_ratings[pointer_away]+marwin_elo_ratings[pointer_away])/2
        data.loc[i,'A_ELO']=average_elo_ratings[pointer_away]
        data.to_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv', index=False)

        # Calls elo calculation functions
        xG_elo_ratings,xG_hfa=xG_Elo_System(actual_outcome_xG,pointer_home,pointer_away,xG_elo_ratings,xG_hfa)
        marwin_elo_ratings,marwin_hfa=MarWin_Elo_System(actual_outcome_win,pointer_home,pointer_away,marwin_elo_ratings,marwin_hfa,scaling_factor,scaling_pointer)

    # Updating Teams_Elo.csv and Start-End-Count.txt at the end of the loop
    teams_data=pd.read_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv')
    teams_data['xG_elo']=xG_elo_ratings
    teams_data.to_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv',index=False)
    teams_data['marwin_elo']=marwin_elo_ratings
    teams_data.to_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv',index=False)
    teams_data['average_elo']=(teams_data['xG_elo']+teams_data['marwin_elo'])/2
    teams_data.to_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv',index=False)
    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Start-End-Count-xG_hfa-marwin_hfa.txt','w') as file:
        file.write(str(start)+'\n'+str(end)+'\n'+str(count)+'\n'+str(xG_hfa)+'\n'+str(marwin_hfa))

    # Removes new line at the end of the Teams_Elo.csv
    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv') as file:
        content=file.read().rstrip('\n')
    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv','w') as file:
        file.write(content)
        file.truncate()  

def get_odds(flashscore_link,site_struct_1,other_site_struct_1,site_struct_2,other_site_struct_2,league):
    # Setup
    options=webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
    options.add_argument("--window-size=1600,900")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver=webdriver.Chrome(service=Service('C:/Users/Kostas/Downloads/new_chromedriver.exe'),options=options)
    driver.maximize_window()

    print("\nCollecting "+league+"'s odds...")
    match_count=2
    actual_match_count=-1 # This is the actual one because it accounts for skipped matches
    stop_flag=False
    flashscore_home_names=[]
    flashscore_away_names=[]
    home_odds=[]
    draw_odds=[]
    away_odds=[]
    over_odds=[]
    under_odds=[]
    yes_btts_odds=[]
    no_btts_odds=[]
    driver.get(flashscore_link)
    time.sleep(1)
    while True: # For every match
        swap_flag=False
        skip_flag=False
        # Scrolls to the match
        while True:
            try:
                # Gets the time and filters out finished and live matches because the format is (before | hours:minutes and live | LIVE)
                if driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/main/div[4]/div[2]/div[1]/section[1]/div/div[2]/div['+str(match_count)+']/div[2]').text[2]==':':
                    driver.execute_script("arguments[0].scrollIntoView();",driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/main/div[4]/div[2]/div[1]/section[1]/div/div[2]/div['+str(match_count)+']/div[2]'))
                    time.sleep(1)
                    driver.execute_script('window.scrollBy(0,-300)')
                else:
                    skip_flag=True
                break
            except IndexError: # Filters out live matches that have not passed the 10th minute, eg it says the game is at minute 2' so it has no [2] character
                skip_flag=True
                break
            except NoSuchElementException: # Stops when it can't find any other matches
                stop_flag=True
                break
        if stop_flag:
            break
        elif skip_flag:
            match_count+=1
            continue
    
        # Clicks the button to get the odds
        while True:
            try:
                time.sleep(1)
                driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/main/div[4]/div[2]/div[1]/section[1]/div/div[2]/div['+str(match_count)+']/div[2]').click()
                break
            except NoSuchElementException:
                pass
        
        # Gets the names of the teams
        while True:
            try:
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[1]) # It changes focus to the popup tab
                flashscore_home_names.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div[5]/div[2]/div[3]/div[2]/a').text)
                flashscore_away_names.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div[5]/div[4]/div[3]/div[1]/a').text)
                break
            except NoSuchElementException:
                pass

        # Clicks odds
        while True:
            try:
                time.sleep(1)
                driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_1+']/div/a[2]').click()
                break
            except NoSuchElementException: # Sometimes a match has a different site structure than expected, that's why we change it
                time.sleep(1)
                driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+other_site_struct_1+']/div/a[2]').click()
                swap_flag=True
                temp=site_struct_2
                site_struct_2=other_site_struct_2
                other_site_struct_2=temp
                break

        # Gets 1x2 odds
        while True:
            try:
                time.sleep(1)
                home_odds.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div/div[2]/div/a[1]/span').text)
                draw_odds.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div/div[2]/div/a[2]/span').text)
                away_odds.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div/div[2]/div/a[3]/span').text)
                break
            except NoSuchElementException:
                pass

        # Clicks Over/Under odds 
        while True:
            try:
                time.sleep(1)
                driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[1]/div/a[3]').click()
                break
            except NoSuchElementException: # Sometimes it has a different XPATH
                pass

        over_odds.append(['NaN','NaN','NaN'])
        under_odds.append(['NaN','NaN','NaN'])
        actual_match_count+=1
        # Gets Over/Under odds
        while True:
            try:
                time.sleep(1)
                count=2
                index=0
                for num in range(20): # Random number to be sure it will get through everything 
                    try:
                        # The if is there to avoid getting asian handicaps and instances where there are only odds for the over or for the under
                        if driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div['+str(count)+']/div[2]/div/span').text[2]=='5' and (driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div['+str(count)+']/div[2]/div/a[1]/span').text!='' and driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div['+str(count)+']/div[2]/div/a[2]/span').text!=''):
                            over_odds[actual_match_count][index]=driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div['+str(count)+']/div[2]/div/a[1]/span').text
                            under_odds[actual_match_count][index]=driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div['+str(count)+']/div[2]/div/a[2]/span').text
                            index+=1
                        count+=1
                    except IndexError: # To avoid crashes when handling asian handicaps like 3,4 where they dont have a [2]
                        count+=1
                break
            except NoSuchElementException: # Stops when it can't find any other odds
                break

        # Clicks BTTS odds 
        while True:
            try:
                time.sleep(1)
                driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[1]/div/a[10]').click()
                break
            except NoSuchElementException:
                pass

        # Gets BTTS odds
        while True:
            try:
                time.sleep(1)
                yes_btts_odds.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div/div[2]/div/a[1]/span').text)
                no_btts_odds.append(driver.find_element(By.XPATH,'/html/body/div[1]/div/div['+site_struct_2+']/div[3]/div/div[2]/div/a[2]/span').text)
                break
            except NoSuchElementException:
                pass
        
        match_count+=1
        if swap_flag:
            temp=site_struct_2
            site_struct_2=other_site_struct_2
            other_site_struct_2=temp
        driver.close()
        driver.switch_to.window(driver.window_handles[0]) # It changes focus to the original tab
    driver.quit()

    return flashscore_home_names,flashscore_away_names,home_odds,draw_odds,away_odds,over_odds,under_odds,yes_btts_odds,no_btts_odds

def streak_bonus_calculator(all_form,history_form,home_form,away_form,home_history_form,away_history_form,k):
    # Only did it for the 1x2 market because I don't think streaks affect the goal and btts markets
    home_away_streak=1
    all_streak=1
    home_away_history_streak=1
    history_streak=1
    win_streak=True
    lose_streak=True
    for n in range(len(all_form)): # Number of games we keep track of
        # These can be put here because they are the same for both teams
        if all_form[n]>=0.0291666666666667: # If it's a win
            outcome_history=(all_form[n]-0.0291666666666667)/0.0291666666666667 # Gets the expected win probabilities that were used for that match
            # Reset the loss streak
            if lose_streak:
                lose_streak=False
                all_streak=1
                win_streak=True
            all_streak+=(0.0291666666666667+0.0291666666666667*outcome_history) # Bonus the average win
        elif all_form[n]<0.0291666666666667 and all_form[n]>0.0041666666666667: # If it's a draw
            outcome_history=(all_form[n]-0.0083333333333333)/0.0166666666666667 # Gets the expected draw probabilities that were used for that match
            all_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672 # If it's a 50-50 match the result is zero, if the reversed expected outcome<0.25 it's a negative bonus of an average win, if the reversed expected outcome>0.75 it's a positive bonus of an average win (in general if outcome>0.50, the result will be positive, if outcome<0.50 the result will be negative)
        else: # If it's a loss
            outcome_history=all_form[n]/0.0041666666666667 # Gets the expected loss probabilities that were used for that match
            # Reset the win streak
            if win_streak:
                win_streak=False
                all_streak=1
                lose_streak=True
            all_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history)) # Negative bonus the average win (1-outcome_history=reversing the already reversed expected outcome because if a team a small change to win they shoud lose small points, same goes other way around [big change=big points])
    
    win_streak=True
    lose_streak=True
    for n in range(len(history_form)):
        if history_form[n]>=0.0291666666666667: 
            outcome_history=(history_form[n]-0.0291666666666667)/0.0291666666666667
            if lose_streak:
                lose_streak=False
                history_streak=1
                win_streak=True
            history_streak+=(0.0291666666666667+0.0291666666666667*outcome_history)
        elif history_form[n]<0.0291666666666667 and history_form[n]>0.0041666666666667:
            outcome_history=(history_form[n]-0.0083333333333333)/0.0166666666666667
            history_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672
        else: 
            outcome_history=history_form[n]/0.0041666666666667
            if win_streak:
                win_streak=False
                history_streak=1
                lose_streak=True
            history_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history))

    win_streak=True
    lose_streak=True
    # For the home team
    if k==0: 
        for n in range(len(home_form)):
            if home_form[n]>=0.0291666666666667:
                outcome_history=(home_form[n]-0.0291666666666667)/0.0291666666666667
                if lose_streak:
                    lose_streak=False
                    home_away_streak=1
                    win_streak=True
                home_away_streak+=(0.0291666666666667+0.0291666666666667*outcome_history)
            elif home_form[n]<0.0291666666666667 and home_form[n]>.0041666666666667:
                outcome_history=(home_form[n]-0.0083333333333333)/0.0166666666666667
                home_away_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672
            else:
                outcome_history=home_form[n]/0.0041666666666667
                if win_streak:
                    win_streak=False
                    home_away_streak=1
                    lose_streak=True
                home_away_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history))

        win_streak=True
        lose_streak=True
        for n in range(len(home_history_form)):
            if home_history_form[n]>=0.0291666666666667: 
                outcome_history=(home_history_form[n]-0.0291666666666667)/0.0291666666666667
                if lose_streak:
                    lose_streak=False
                    home_away_history_streak=1
                    win_streak=True
                home_away_history_streak+=(0.0291666666666667+0.0291666666666667*outcome_history)
            elif home_history_form[n]<0.0291666666666667 and home_history_form[n]>0.0041666666666667:
                outcome_history=(home_history_form[n]-0.0083333333333333)/0.0166666666666667
                home_away_history_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672
            else: 
                outcome_history=home_history_form[n]/0.0041666666666667
                if win_streak:
                    win_streak=False
                    home_away_history_streak=1
                    lose_streak=True
                home_away_history_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history))
    # For the away team
    else: 
        win_streak=True
        lose_streak=True
        for n in range(len(away_form)):
            if away_form[n]>=0.0291666666666667: 
                outcome_history=(away_form[n]-0.0291666666666667)/0.0291666666666667
                if lose_streak:
                    lose_streak=False
                    home_away_streak=1
                    win_streak=True
                home_away_streak+=(0.0291666666666667+0.0291666666666667*outcome_history)
            elif away_form[n]<0.0291666666666667 and away_form[n]>0.0041666666666667:
                outcome_history=(away_form[n]-0.0083333333333333)/0.0166666666666667
                home_away_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672
            else:
                outcome_history=away_form[n]/0.0041666666666667
                if win_streak:
                    win_streak=False
                    home_away_streak=1
                    lose_streak=True
                home_away_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history))

        for n in range(len(away_history_form)):
            if away_history_form[n]>=0.0291666666666667: 
                outcome_history=(away_history_form[n]-0.0291666666666667)/0.0291666666666667
                if lose_streak:
                    lose_streak=False
                    home_away_history_streak=1
                    win_streak=True
                home_away_history_streak+=(0.0291666666666667+0.0291666666666667*outcome_history)
            elif away_history_form[n]<0.0291666666666667 and away_history_form[n]>0.0041666666666667:
                outcome_history=(away_history_form[n]-0.0083333333333333)/0.0166666666666667
                home_away_history_streak+=(outcome_history*0.10208333333333344)-0.05104166666666672
            else: 
                outcome_history=away_history_form[n]/0.0041666666666667
                if win_streak:
                    win_streak=False
                    home_away_history_streak=1
                    lose_streak=True
                home_away_history_streak-=(0.0291666666666667+0.0291666666666667*(1-outcome_history))

    return all_streak,history_streak,home_away_streak,home_away_history_streak

def form_calculator(translated_home_names,translated_away_names,i):
    # Calculates a form number for each team in the upcoming matches to then multiply to adjust the expected goals I have predicted
    home_form=[]
    away_form=[]
    all_form=[]
    home_history_form=[]
    away_history_form=[]
    history_form=[]
    home_goal_form=[]
    away_goal_form=[]
    all_goal_form=[]
    home_history_goal_form=[]
    away_history_goal_form=[]
    history_goal_form=[]
    home_btts_form=[]
    away_btts_form=[]
    all_btts_form=[]
    home_history_btts_form=[]
    away_history_btts_form=[]
    history_btts_form=[]
    form_teams=[translated_home_names,translated_away_names]
    goal_sum=0
    btts_sum=0

    # How I came up with the numbers:
    # 1x2 numbers: Starting form number is 0.5, the minimum form number (all losses) I want is 0.7, so I divided the 0.2 difference by the 24 matches and made some adjustments to make the system more punishing to losses and more rewarding to wins
    # So if a team losses all of the 24 matches their form number would be around 0.7 (*Further explanation of the calculations is in the next star)
    # The average form number (all draws) is 1 and the maximum form number (all wins) is 1.3, the process is all the same
    # Goal and btts numbers: Starting form numbers for both is 0.5 and the average is 1, we go through each game in the database and find the average amount of goals and btts happenings and then multiply it by the 24 matches, then we divide that number by the 0.5 difference between the starting and average form number, the result will be the number added for each goal/btts happening
    # So if a team scores the average amount of goals (or btts happenings) in the 24 matches their form number would be 1
    for m in range(len(data)): # Goes through each game in the database
        goal_sum+=data.loc[m,'G_H']+data.loc[m,'G_A']
        if data.loc[m,'G_H']>=1 and data.loc[m,'G_A']>=1:
            btts_sum+=1

    goal_average=0.5/((goal_sum/(len(data)-1))*24)
    btts_average=0.5/(btts_sum/len(data)*24)

    for k in range(2): # For each team in that match
        for j in range(len(data)): # Goes through each game in the database, but collects the most 6 recent results to determine the form number
            home_elo=data.loc[j,'H_ELO']
            away_elo=data.loc[j,'A_ELO']
            if data.loc[j,'Home']==form_teams[k][i]: # Finds if the team we are searching for is playing at home
                outcome=1/(1+10**((home_elo+hfa-away_elo)/400))
                # 1x2 Market
                if data.loc[j,'G_H']>data.loc[j,'G_A']:
                    home_form.append(0.0291666666666667+0.0291666666666667*outcome)
                    all_form.append(0.0291666666666667+0.0291666666666667*outcome)
                elif data.loc[j,'G_H']==data.loc[j,'G_A']:
                    home_form.append(0.0083333333333333+0.0166666666666667*outcome) # (*The number we are looking for is 0.0166666666666667, if it's a fair match [eg:1000 elo for both teams] the outcome variable would be equal to 0.5, so the result would be 0.0166666666666667 [if the home team is higher elo they would get less points and if they're lower elo they would get more])
                    all_form.append(0.0083333333333333+0.0166666666666667*outcome)  # (*For the win we have doubled the first number to be more rewarding for wins and for the loss we have removed the first number and halved the second one to make it more punishing for losses)
                else:
                    home_form.append(0.0041666666666667*outcome)
                    all_form.append(0.0041666666666667*outcome)
                # BTTS Market
                if data.loc[j,'G_H']>=1 and data.loc[j,'G_A']>=1:
                    home_btts_form.append(btts_average)
                    all_btts_form.append(btts_average)
                else:
                    home_btts_form.append(0)
                    all_btts_form.append(0)
                # Goal Market
                home_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
                all_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
            elif data.loc[j,'Away']==form_teams[k][i]: # Finds if the team we are searching for is playing away
                outcome=1/(1+10**((away_elo-hfa-home_elo)/400))
                # 1x2 Market
                if data.loc[j,'G_A']>data.loc[j,'G_H']:
                    away_form.append(0.0291666666666667+0.0291666666666667*outcome)
                    all_form.append(0.0291666666666667+0.0291666666666667*outcome)
                elif data.loc[j,'G_A']==data.loc[j,'G_H']:
                    away_form.append(0.0083333333333333+0.0166666666666667*outcome)
                    all_form.append(0.0083333333333333+0.0166666666666667*outcome)
                else:
                    away_form.append(0.0041666666666667*outcome)
                    all_form.append(0.0041666666666667*outcome)
                # BTTS Market
                if data.loc[j,'G_H']>=1 and data.loc[j,'G_A']>=1:
                    away_btts_form.append(btts_average)
                    all_btts_form.append(btts_average)
                else:
                    away_btts_form.append(0)
                    all_btts_form.append(0)
                # Goal Market
                away_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
                all_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
            if data.loc[j,'Home']==form_teams[k][i] and data.loc[j,'Away']==form_teams[k-1][i]: # Finds if the team we are searching for is playing at home and it's opponent away, to figure out their H2H
                outcome=1/(1+10**((home_elo+hfa-away_elo)/400))
                # 1x2 Market
                if data.loc[j,'G_H']>data.loc[j,'G_A']:
                    home_history_form.append(0.0291666666666667+0.0291666666666667*outcome)
                    history_form.append(0.0291666666666667+0.0291666666666667*outcome)
                elif data.loc[j,'G_H']==data.loc[j,'G_A']:
                    home_history_form.append(0.0083333333333333+0.0166666666666667*outcome)
                    history_form.append(0.0083333333333333+0.0166666666666667*outcome)
                else:
                    home_history_form.append(0.0041666666666667*outcome)
                    history_form.append(0.0041666666666667*outcome)
                # BTTS Market
                if data.loc[j,'G_H']>=1 and data.loc[j,'G_A']>=1:
                    home_history_btts_form.append(btts_average)
                    history_btts_form.append(btts_average)
                else:
                    home_history_btts_form.append(0)
                    history_btts_form.append(0)
                # Goal Market
                home_history_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
                history_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
            elif data.loc[j,'Away']==form_teams[k][i] and data.loc[j,'Home']==form_teams[k-1][i]: # Finds if the team we are searching for is playing away and it's opponent home
                outcome=1/(1+10**((away_elo-hfa-home_elo)/400))
                # 1x2 Market
                if data.loc[j,'G_A']>data.loc[j,'G_H']:
                    away_history_form.append(0.0291666666666667+0.0291666666666667*outcome)
                    history_form.append(0.0291666666666667+0.0291666666666667*outcome)
                elif data.loc[j,'G_A']==data.loc[j,'G_H']:
                    away_history_form.append(0.0083333333333333+0.0166666666666667*outcome)
                    history_form.append(0.0083333333333333+0.0166666666666667*outcome)
                else:
                    away_history_form.append(0.0041666666666667*outcome)
                    history_form.append(0.0041666666666667*outcome)
                # BTTS Market
                if data.loc[j,'G_H']>=1 and data.loc[j,'G_A']>=1:
                    away_history_btts_form.append(btts_average)
                    history_btts_form.append(btts_average)
                else:
                    away_history_btts_form.append(0)
                    history_btts_form.append(0)
                # Goal Market
                away_history_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))
                history_goal_form.append(goal_average*(data.loc[j,'G_H']+data.loc[j,'G_A']))

            # LIFO to keep the last 6 results
            # 1x2 Market
            if len(home_form)==7:
                home_form.pop(0)
            if len(away_form)==7:
                away_form.pop(0)
            if len(all_form)==7:
                all_form.pop(0)
            if len(home_history_form)==7:
                home_history_form.pop(0)
            if len(away_history_form)==7:
                away_history_form.pop(0)
            if len(history_form)==7:
                history_form.pop(0)
            # Goal Market
            if len(home_goal_form)==7:
                home_goal_form.pop(0)
            if len(away_goal_form)==7:
                away_goal_form.pop(0)
            if len(all_goal_form)==7:
                all_goal_form.pop(0)
            if len(home_history_goal_form)==7:
                home_history_goal_form.pop(0)
            if len(away_history_goal_form)==7:
                away_history_goal_form.pop(0)
            if len(history_goal_form)==7:
                history_goal_form.pop(0)
            # BTTS Market
            if len(home_btts_form)==7:
                home_btts_form.pop(0)
            if len(away_btts_form)==7:
                away_btts_form.pop(0)
            if len(all_btts_form)==7:
                all_btts_form.pop(0)
            if len(home_history_btts_form)==7:
                home_history_btts_form.pop(0)
            if len(away_history_btts_form)==7:
                away_history_btts_form.pop(0)
            if len(history_btts_form)==7:
                history_btts_form.pop(0)

        # Streak bonus calculator
        all_streak,history_streak,home_away_streak,home_away_history_streak=streak_bonus_calculator(all_form,history_form,home_form,away_form,home_history_form,away_history_form,k)

        # If a team hasn't played at least 6 games for each type, it adds the needed draws to their slate
        # 1x2 Market
        if len(home_form)<6:
            home_form=[sum(home_form)+(6-len(home_form))*0.0166666666666667]
        if len(away_form)<6:
            away_form=[sum(away_form)+(6-len(away_form))*0.0166666666666667]
        if len(all_form)<6:
            all_form=[sum(all_form)+(6-len(all_form))*0.0166666666666667]
        if len(home_history_form)<6:
            home_history_form=[sum(home_history_form)+(6-len(home_history_form))*0.0166666666666667]
        if len(away_history_form)<6:
            away_history_form=[sum(away_history_form)+(6-len(away_history_form))*0.0166666666666667]
        if len(history_form)<6:
            history_form=[sum(history_form)+(6-len(history_form))*0.0166666666666667]
        # Goal Market
        if len(home_goal_form)<6:
            home_goal_form=[sum(home_goal_form)+(6-len(home_goal_form))*0.0208333333333333]
        if len(away_goal_form)<6:
            away_goal_form=[sum(away_goal_form)+(6-len(away_goal_form))*0.0208333333333333]
        if len(all_goal_form)<6:
            all_goal_form=[sum(all_goal_form)+(6-len(all_goal_form))*0.0208333333333333]
        if len(home_history_goal_form)<6:
            home_history_goal_form=[sum(home_history_goal_form)+(6-len(home_history_goal_form))*0.0208333333333333]
        if len(away_history_goal_form)<6:
            away_history_goal_form=[sum(away_history_goal_form)+(6-len(away_history_goal_form))*0.0208333333333333]
        if len(history_goal_form)<6:
            history_goal_form=[sum(history_goal_form)+(6-len(history_goal_form))*0.0208333333333333]
        # BTTS Market
        if len(home_btts_form)<6:
            home_btts_form=[sum(home_btts_form)+(6-len(home_btts_form))*(btts_average/2)]
        if len(away_btts_form)<6:
            away_btts_form=[sum(away_btts_form)+(6-len(away_btts_form))*(btts_average/2)]
        if len(all_btts_form)<6:
            all_btts_form=[sum(all_btts_form)+(6-len(all_btts_form))*(btts_average/2)]
        if len(home_history_btts_form)<6:
            home_history_btts_form=[sum(home_history_btts_form)+(6-len(home_history_btts_form))*(btts_average/2)]
        if len(away_history_btts_form)<6:
            away_history_btts_form=[sum(away_history_btts_form)+(6-len(away_history_btts_form))*(btts_average/2)]
        if len(history_btts_form)<6:
            history_btts_form=[sum(history_btts_form)+(6-len(history_btts_form))*(btts_average/2)]

        # Figures out total forms for the match
        if k==0:
            home_total_form=sum(home_form)*home_away_streak+sum(all_form)*all_streak+sum(home_history_form)*home_away_history_streak+sum(history_form)*history_streak+0.5
            home_total_goal_form=sum(home_goal_form)+sum(all_goal_form)+sum(home_history_goal_form)+sum(history_goal_form)+0.5
            home_total_btts_form=sum(home_btts_form)+sum(all_btts_form)+sum(home_history_btts_form)+sum(history_btts_form)+0.5
        else:
            away_total_form=sum(away_form)*home_away_streak+sum(all_form)*all_streak+sum(away_history_form)*home_away_history_streak+sum(history_form)*history_streak+0.5
            away_total_goal_form=sum(away_goal_form)+sum(all_goal_form)+sum(away_history_goal_form)+sum(history_goal_form)+0.5
            away_total_btts_form=sum(away_btts_form)+sum(all_btts_form)+sum(away_history_btts_form)+sum(history_btts_form)+0.5

        # Clears the slate for the away team
        # 1x2 Market
        home_form.clear()
        away_form.clear()
        all_form.clear()
        home_history_form.clear()
        away_history_form.clear()
        history_form.clear()
        # Goal Market
        home_goal_form.clear()
        away_goal_form.clear()
        all_goal_form.clear()
        home_history_goal_form.clear()
        away_history_goal_form.clear()
        history_goal_form.clear()
        # BTTS Market
        home_btts_form.clear()
        away_btts_form.clear()
        all_btts_form.clear()
        home_history_btts_form.clear()
        away_history_btts_form.clear()
        history_btts_form.clear()

    return home_total_form,away_total_form,home_total_goal_form,away_total_goal_form,home_total_btts_form,away_total_btts_form

def find_ev(i):
    # Finds the index of teams in the Teams_Elo.csv file
    pointer_home=[]
    pointer_away=[]
    for j in range(len(translated_home_names)):
        flag_1=False
        flag_2=False
        for k in range(len(teams)):
            if translated_home_names[j]==teams[k]:
                pointer_home.append(k)
                flag_1=True
            if translated_away_names[j]==teams[k]:
                pointer_away.append(k)
                flag_2=True
            if flag_1 and flag_2:
                break

    # Linear regression
    line_home_goals=linear_model.LinearRegression()
    line_home_goals.fit(data[['H_ELO','A_ELO']].values,data.G_H)
    line_away_goals=linear_model.LinearRegression()
    line_away_goals.fit(data[['H_ELO','A_ELO']].values,data.G_A)

    # Finds the expected goals for each team in the upcoming matches and adjusts the results to their recent form
    home_1x2=line_home_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*home_total_form
    away_1x2=line_away_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*away_total_form
    home_goals=line_home_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*home_total_goal_form
    away_goals=line_away_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*away_total_goal_form
    home_btts=line_home_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*home_total_btts_form
    away_btts=line_away_goals.predict([[average_elo[pointer_home[i]],average_elo[pointer_away[i]]]])*away_total_btts_form

    # Uses poisson's distribution to translate expected goals to win probabilities,goals scored,etc... Source: https://www.thepunterspage.com/poisson-distribution-betting/
    home_win_my_odds=0
    away_win_my_odds=0
    draw_my_odds=0
    under_my_odds=[0,0,0]
    yes_btts_my_odds=0
    # Poisson's distrubution for 1x2 market
    for home in range(11):
        for away in range(11):
            probability=poisson.pmf(k=home,mu=home_1x2)*poisson.pmf(k=away,mu=away_1x2)
            if home>away:
                home_win_my_odds+=probability
            elif away>home:
                away_win_my_odds+=probability
            else:
                draw_my_odds+=probability

    # Poisson's distrubution over market
    for home in range(11):
        for away in range(11):
            probability=poisson.pmf(k=home,mu=home_goals)*poisson.pmf(k=away,mu=away_goals)
            if home+away<1.5:
                under_my_odds[0]+=probability
            if home+away<2.5:
                under_my_odds[1]+=probability
            if home+away<3.5:
                under_my_odds[2]+=probability

    # Poisson's distrubtion for btts market
    for home in range(11):
        for away in range(11):
            probability=poisson.pmf(k=home,mu=home_btts)*poisson.pmf(k=away,mu=away_btts)
            if home>=1 and away>=1:
                yes_btts_my_odds+=probability

    # Calculates expected value (ev) to find profitable bets
    ev_home=numpy.round(home_win_my_odds*(10*float(home_odds[i])-10)-((draw_my_odds+away_win_my_odds)*10),2)
    ev_draw=numpy.round(draw_my_odds*(10*float(draw_odds[i])-10)-((home_win_my_odds+away_win_my_odds)*10),2)
    ev_away=numpy.round(away_win_my_odds*(10*float(away_odds[i])-10)-((home_win_my_odds+draw_my_odds)*10),2)
    ev_under=[]
    ev_over=[]

    for j in range(len(under_odds[i])):
        if under_odds[i][j]!='NaN':
            ev_over.append(numpy.round((1-under_my_odds[j])*(10*float(over_odds[i][j])-10)-(under_my_odds[j]*10),2))
            ev_under.append(numpy.round(under_my_odds[j]*(10*float(under_odds[i][j])-10)-((1-under_my_odds[j])*10),2))
    # This is just for the printing part later
    over_index=str(ev_over.index(max(ev_over))+1)
    under_index=str(ev_under.index(max(ev_under))+1)

    ev_yes_btts=numpy.round(yes_btts_my_odds*(10*float(yes_btts_odds[i])-10)-((1-float(yes_btts_my_odds))*10),2)
    ev_no_btts=numpy.round((1-yes_btts_my_odds)*(10*float(no_btts_odds[i])-10)-(float(yes_btts_my_odds)*10),2)

    return ev_home,ev_draw,ev_away,ev_over,ev_under,ev_yes_btts,ev_no_btts,over_index,under_index

def find_potd(ev_home,ev_draw,ev_away,ev_over,ev_under,ev_yes_btts,ev_no_btts,potd_max,message,potd_teams):
    if ev_home>potd_max:
        potd_max=ev_home
        message='[Home]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_draw>potd_max:
        potd_max=ev_draw
        message='[Draw]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_away>potd_max:
        potd_max=ev_away
        message='[Away]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_over>potd_max:
        potd_max=ev_over
        message='[Over:'+over_index+'.5]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_under>potd_max:
        potd_max=ev_under
        message='[Under:'+under_index+'.5]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_yes_btts>potd_max:
        potd_max=ev_yes_btts
        message='[BTTS Yes]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]
    if ev_no_btts>potd_max:
        potd_max=ev_no_btts
        message='[BTTS No]'
        potd_teams=translated_home_names[i]+' vs '+translated_away_names[i]

    return potd_max,message,potd_teams

season='2022-2023'

league_num=0
attempt=0
potd_max=-10 # 10=Random small number
message=''
potd_teams=''
potd_flag=False
while True:
    league,xpath_league_num,league_num,matchday_games,total_season_games,driver_get_link,flashscore_link,site_struct_1,other_site_struct_1,site_struct_2,other_site_struct_2,flashscore_dict=league_differences(league_num)
        
    with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Start-End-Count-xG_hfa-marwin_hfa.txt','r') as file: # Gets information needed for later
        lines=file.readlines()
        start=lines[0][:len(lines[0])-1]
        end=lines[1][:len(lines[1])-1]
        count=lines[2][:len(lines[2])-1]
        xG_hfa=lines[3][:len(lines[3])-1]
        marwin_hfa=lines[4]
    hfa=(float(xG_hfa)+float(marwin_hfa))/2

    data=pd.read_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv')
    teams_data=pd.read_csv('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Teams_Elo.csv')

    if attempt==0:
        print('Do you want to:\n(a) Update the database and get predictions (b) Get predictions')
        question_flag=False 
        while question_flag==False:
            choice=input('\nChoose the appropriate letter: ')
            if choice=='a' or choice=='b':
                question_flag=True

    if choice=='a':
        print('\nLoading '+league+' stats...')
        with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/'+league+'.csv') as file: # Used for later
            starting_lenght=len(file.readlines())

        today=str(date.today())
        with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Updated_Till.txt') as file: # last_date shows the when the last match on the database happened
            other_line=file.readlines()
            last_date=other_line[-1]

        table,flag,updated_till,extra_matches,error=get_stats(last_date,today,driver_get_link,xpath_league_num,season)
        if not error:    
            league_num+=1
            if flag: # Flag checks if any new games have to be added
                with open('C:/Users/Kostas/Desktop/Coding/Codes/Algo/Algo [OLD]/'+league+'/Updated_Till.txt','w') as file: # Keeps date of when the last game on the database happened
                    file.write(updated_till)
                csv_format_stats(table,league)
                assign_elo(start,end,count,teams_data,xG_hfa,marwin_hfa,league,total_season_games,matchday_games)
            else:
                print('\nEverything is up to date!')
        else:
            print('\nError. Trying again...')
        attempt+=1
        
        if league_num==5: # If it has updated all the leagues, it stops
            print('\nSuccess!')
            # Now it will start the prediction phase
            league_num=0
            choice='b' 
            continue

    elif choice=='b':
        # Gets odds
        flashscore_home_names,flashscore_away_names,home_odds,draw_odds,away_odds,over_odds,under_odds,yes_btts_odds,no_btts_odds=get_odds(flashscore_link,site_struct_1,other_site_struct_1,site_struct_2,other_site_struct_2,league)

        # Gathering information need for later, from Teams_Elos.csv (temp has to be added to remove useless information)
        temp_teams=teams_data.loc[:,'name']
        teams=[]
        for i in range(len(temp_teams)):
            teams.append(temp_teams[i])
        
        temp_average_elo=teams_data.loc[:,'average_elo']
        average_elo=[]
        for i in range(len(temp_average_elo)):
            average_elo.append(temp_average_elo[i])
    
        # Translates team's names from flashscore to correspond them with the data in Teams_Elo.csv
        translated_home_names=[]
        translated_away_names=[]
        for i in range(len(flashscore_home_names)):
            translated_home_names.append(flashscore_dict[flashscore_home_names[i]])
            translated_away_names.append(flashscore_dict[flashscore_away_names[i]])
        
        if len(flashscore_home_names)>0: # If there is atleast 1 match
            potd_flag=True
            for i in range(len(translated_home_names)): # For each upcoming match
                # Calculates form
                home_total_form,away_total_form,home_total_goal_form,away_total_goal_form,home_total_btts_form,away_total_btts_form=form_calculator(translated_home_names,translated_away_names,i)
                
                # Finds ev of each market for each match
                ev_home,ev_draw,ev_away,ev_over,ev_under,ev_yes_btts,ev_no_btts,over_index,under_index=find_ev(i)
        
                # Prints results            
                print('\n',translated_home_names[i]+':',ev_home,'Draw:',ev_draw,translated_away_names[i]+':',ev_away,'Over '+over_index+'.5:',max(ev_over),'Under '+under_index+'.5:',max(ev_under),'BTTS Yes:',ev_yes_btts,'BTTS No:',ev_no_btts) 

                # Checks if this match has the best ev pick so far, in order to eventually find the max ev pick of the day to print (Have to pass message and potd_teams to have something to return in the function, incase it doesn't go in the if statements)
                potd_max,message,potd_teams=find_potd(ev_home,ev_draw,ev_away,max(ev_over),max(ev_under),ev_yes_btts,ev_no_btts,potd_max,message,potd_teams)
        else:
            print('\nNo matches available...')

        # Goes to next league's predictions
        attempt+=1
        league_num+=1

        # If it has made predictions for all the leagues, it stops
        if league_num==5:
            print('\nSuccess!')
            break

# Prints pick of the day
if potd_flag: # If there is atleast one game today
    print('\nPOTD:',potd_teams,message,potd_max)

# Waits until user input to close the program
end=input('\nType anything to close the program... ')