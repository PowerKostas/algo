import requests 
from bs4 import BeautifulSoup
import pandas as pd
import math
import numpy as np
import csv

def elo_calc(i):
    home_xresult=1/(1+pow(10,(team_elo[df['Away'][i]]-(team_elo[df['Home'][i]]+0))/400))
    away_xresult=1-home_xresult

    k=16
    #if i<=5:
        #k=20
    
    if df['Score'][i][0]>df['Score'][i][2]:
        home_elo_change=k*(1-home_xresult)
        away_elo_change=k*(0-away_xresult)

    elif df['Score'][i][0]==df['Score'][i][2]:
        home_elo_change=k*(0.5-home_xresult)
        away_elo_change=k*(0.5-away_xresult)
    
    else:
        home_elo_change=k*(0-home_xresult)
        away_elo_change=k*(1-away_xresult)
    
    team_elo[df['Home'][i]]+=home_elo_change
    team_elo[df['Away'][i]]+=away_elo_change

    return team_elo

def xg_elo_calc(i):
    home_xresult=1/(1+pow(10,(team_elo[df['Away'][i]]-(team_elo[df['Home'][i]]+0))/400))
    away_xresult=1-home_xresult

    k=16
    #if i<=5:
        #k=20
    
    if abs(df['xG'][i]-df['xG.1'][i])<1:
        home_elo_change=k*(0.5-home_xresult)
        away_elo_change=k*(0.5-away_xresult)

    elif df['xG'][i]>df['xG.1'][i]:
        home_elo_change=k*(1-home_xresult)
        away_elo_change=k*(0-away_xresult)
    
    else:
        home_elo_change=k*(0-home_xresult)
        away_elo_change=k*(1-away_xresult)
    
    team_elo[df['Home'][i]]+=home_elo_change
    team_elo[df['Away'][i]]+=away_elo_change

    return team_elo

def initiate_teams(starting_elo):
    for i in range(len(df)): 
        if not pd.isna(df['xG'][i]) and not pd.isna(df['Score'][i]) and not pd.isna(df['xG.1'][i]): # To avoid playoff games
            if df['Home'][i] not in team_elo:
                team_elo[df['Home'][i]]=starting_elo
            if df['Away'][i] not in team_elo:
                team_elo[df['Away'][i]]=starting_elo

    return team_elo

def sort_dict():
    teams=list(team_elo)
    elos=list(team_elo.values())

    for i in range(len(elos)):
        swapped=False
        for j in range(len(elos)-i-1):
            if elos[j]<elos[j+1]:
                temp=elos[j]
                elos[j]=elos[j+1]
                elos[j+1]=temp

                temp=teams[j]
                teams[j]=teams[j+1]
                teams[j+1]=temp
                swapped=True
        
        if not swapped:
            break

    return teams,elos
    

# League specific info
number=['9','20']
comp=['Premier-League','Bundesliga']
csv_name=['E0','D1']
starting_row=[24,23]
converter=[{'Manchester City':'Man City',"Nott'ham Forest":"Nott'm Forest",'Luton Town':'Luton','Sheffield Utd':'Sheffield United','Newcastle Utd':'Newcastle','Manchester Utd':'Man United'},{"M'Gladbach":"M'gladbach",'Köln':'FC Koln','Mainz 05':'Mainz','Eint Frankfurt':'Ein Frankfurt','Darmstadt 98':'Darmstadt'}]


# Initiates and calculates elo for all previous seasons
seasons=['2017-2018','2018-2019','2019-2020','2020-2021','2021-2022','2022-2023']
for i in range(2):
    team_elo={}
    for j in range(len(seasons)):
        df=pd.read_html('https://fbref.com/en/comps/'+number[i]+'/'+seasons[j]+'/schedule/'+seasons[j]+'-'+comp[i]+'-Scores-and-Fixtures',attrs={'class':'stats_table sortable min_width'})
        df=df[0]

        if seasons[j]=='2017-2018': # Maybe bad
            team_elo=initiate_teams(1000)
        else:
            team_elo=initiate_teams(950)

        for k in range(len(df)):
            if not pd.isna(df['xG'][k]) and not pd.isna(df['Score'][k]) and not pd.isna(df['xG.1'][k]):
                team_elo=elo_calc(k)
            elif not pd.isna(df['Wk'][k]) and pd.isna(df['Notes'][k]): # It needs to stop in the first not yet played game, first condition to not stop in the blank rows of the database, second condition to not stop if the notes say an old match was postponed
                break

        # Sort and show
        #teams,elos=sort_dict()

        #print('\n\n')
        #for k in range(len(team_elo)):
            #print(str(k+1)+'.',teams[k],elos[k])


    # Initiates and calculates elo for this season and also gets the actual results and the custom results based on my elos
    def make_prediction(team_elo):
        team_elo=initiate_teams(950) 

        my_results=[]
        results=[]
        fb_ref_teams=[[],[]]
        temp_elo=[[],[]]
        for k in range(len(df)):
            if not pd.isna(df['Score'][k]):
                if abs(team_elo[df['Home'][k]]-team_elo[df['Away'][k]])<=30:
                    my_results.append(1)
                elif team_elo[df['Home'][k]]>team_elo[df['Away'][k]]:
                    my_results.append(0)
                else:
                    my_results.append(2)

                if df['Score'][k][0]>df['Score'][k][2]:
                    results.append(0)
                elif df['Score'][k][0]==df['Score'][k][2]:
                    results.append(1)
                else:
                    results.append(2)

                temp_elo[0].append(team_elo[df['Home'][k]])
                temp_elo[1].append(team_elo[df['Away'][k]])

                fb_ref_teams[0].append(df['Home'][k])
                fb_ref_teams[1].append(df['Away'][k])

                team_elo=elo_calc(k)

            elif not pd.isna(df['Wk'][k]) and pd.isna(df['Notes'][k]):
                break

        # Sort and show
        teams,elos=sort_dict()

        print('\n')
        for k in range(len(team_elo)):
            print(str(k+1)+'.',teams[k],elos[k])


        # Gets FootballData.uk odds and team order
        odds=[[],[],[]]
        football_data_teams=[[],[]]
        with open('C:/Users/Kostas/Desktop/'+csv_name[i]+'.csv') as file:
            csv_reader=csv.reader(file,delimiter=',')
            line_count=0

            for row in csv_reader:
                if line_count==0:
                    line_count+=1
                    continue

                odds[0].append(row[starting_row[i]]) 
                odds[1].append(row[starting_row[i]+1])
                odds[2].append(row[starting_row[i]+2])
                football_data_teams[0].append(row[3])
                football_data_teams[1].append(row[4])

        # Finds profit
        count=0
        correct=0
        money=0
        for k in range(len(my_results)): # For all games
            # Matches names from FBref to FootballData
            if fb_ref_teams[0][k] in converter[i]:
                home_fb_ref_name=converter[i][fb_ref_teams[0][k]]
            else:
                home_fb_ref_name=fb_ref_teams[0][k]
                
            if fb_ref_teams[1][k] in converter[i]:
                away_fb_ref_name=converter[i][fb_ref_teams[1][k]]
            else:
                away_fb_ref_name=fb_ref_teams[1][k]

            for l in range(len(my_results)): # Until it finds the matched names from FBref to FootballData
                if home_fb_ref_name==football_data_teams[0][l] and away_fb_ref_name==football_data_teams[1][l]:
                    count+=1
                    money-=10
                    
                    if my_results[k]==results[k]:
                        correct+=1
                        money+=10*float(odds[my_results[k]][l])
                    #print(home_fb_ref_name,away_fb_ref_name,football_data_teams[0][l],football_data_teams[1][l],temp_elo[0][k],temp_elo[1][k],my_results[k],results[k],odds[my_results[k]][l],money) 
                    
                    break

        print(count,correct,correct/count,'\n')
        print(money,'\n')

    season='2023-2024'
    df=pd.read_html('https://fbref.com/en/comps/'+number[i]+'/'+season+'/schedule/'+season+'-'+comp[i]+'-Scores-and-Fixtures', attrs={'class':'stats_table sortable min_width'})
    df=df[0]

    make_prediction(team_elo)
