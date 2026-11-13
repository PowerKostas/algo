import psycopg2
import pandas as pd
import datetime

number=['9','20','11','12','13']
comp=['Premier-League','Bundesliga','Serie-A','La-Liga','Ligue-1']
seasons=['2017-2018','2018-2019','2019-2020','2020-2021','2021-2022','2022-2023','2023-2024']

def initiate():
	conn=psycopg2.connect(host='localhost', database='algo',port=5432, user='parstoukas', password='111111')
	cur=conn.cursor()

	current_season='2023-2024'
	for i in range(len(comp)):
		formatted_comp=comp[i].replace('-','').lower()

		cur.execute("""
		DROP SCHEMA IF EXISTS """+formatted_comp+""" CASCADE;
		CREATE SCHEMA """+formatted_comp+""";
		""")

		for j in range(len(seasons)):
			formatted_seasons=seasons[j].replace('-','')
			df=pd.read_html('https://fbref.com/en/comps/'+number[i]+'/'+seasons[j]+'/schedule/'+seasons[j]+'-'+comp[i]+'-Scores-and-Fixtures',attrs={'class':'stats_table sortable min_width'})
			df=df[0]
			df=df.dropna(how='all').reset_index(drop=True)

			cur.execute("""					
			CREATE TABLE """+formatted_comp+""".t"""+formatted_seasons+""" (
				home VARCHAR(50),
				xgh FLOAT NOT NULL,
				gh INTEGER NOT NULL,
				ga INTEGER NOT NULL,
				xga FLOAT NOT NULL,
				away VARCHAR(50),
				date DATE,

				PRIMARY KEY (home,away,date)
			);    
						
			""")

			if seasons[j]!=current_season:
				for k in range(len(df)):
					if pd.isna(df['Notes'][k]):
						cur.execute("""INSERT INTO """+formatted_comp+""".t"""+formatted_seasons+""" (home,xgh,gh,ga,xga,away,date) VALUES (%s,%s,%s,%s,%s,%s,%s); """, 
						(df['Home'][k],df['xG'][k],df['Score'][k][0:df['Score'][k].find('–')],
						df['Score'][k][df['Score'][k].find('–')+1:],df['xG.1'][k],df['Away'][k],df['Date'][k]))

			else:
				ignore_postponed_k=0 

				for k in range(len(df)):
					if not pd.isna(df['xG'][k]) and not pd.isna(df['Score'][k]) and not pd.isna(df['xG.1'][k]):
						cur.execute("""INSERT INTO """+formatted_comp+""".t"""+formatted_seasons+""" (home,xgh,gh,ga,xga,away,date) VALUES (%s,%s,%s,%s,%s,%s,%s); """, 
						(df['Home'][k],df['xG'][k],df['Score'][k][0:df['Score'][k].find('–')],
						df['Score'][k][df['Score'][k].find('–')+1:],df['xG.1'][k],df['Away'][k],df['Date'][k]))
						ignore_postponed_k+=1

					elif pd.isna(df['Notes'][k]):
						cur.execute("""
						CREATE TABLE """+formatted_comp+""".nextmatch (
							nextmatchdate DATE,
							nextmatchindex INTEGER
						);
							
						INSERT INTO """+formatted_comp+""".nextmatch (nextmatchdate,nextmatchindex) VALUES (%s,%s); """, (df['Date'][k],ignore_postponed_k))

						break


	conn.commit()
	cur.close()
	conn.close()

#initiate()


def update():
	conn=psycopg2.connect(host='localhost', database='algo',port=5432, user='parstoukas', password='111111')
	cur=conn.cursor()

	today_date=datetime.date.today()
	for i in range(len(comp)):
		formatted_comp=comp[i].replace('-','').lower()
		cur.execute("""SELECT * FROM """+formatted_comp+""".nextmatch""")
		rows=cur.fetchall()
		next_match_date=rows[0][0]
		next_match_index=rows[0][1]

		print('\nStarting',comp[i],today_date,next_match_date,next_match_index)
		if today_date>next_match_date:
			print('\n','In',comp[i],'\n')

			df=pd.read_html('https://fbref.com/en/comps/'+number[i]+'/schedule/'+comp[i]+'-Scores-and-Fixtures',attrs={'class':'stats_table sortable min_width'})
			df=df[0]
			df=df.dropna(how='all').reset_index(drop=True)

			formatted_last_season=seasons[-1].replace('-','')
			for j in range(next_match_index,len(df)):
				print(df['Home'][j],df['Away'][j])

				if not pd.isna(df['xG'][j]) and not pd.isna(df['Score'][j]) and not pd.isna(df['xG.1'][j]):
					if datetime.datetime.strptime(df['Date'][j],'%Y-%m-%d').date()>=next_match_date:
						print('Inserted',df['Home'][j],df['Away'][j])

						cur.execute("""INSERT INTO """+formatted_comp+""".t"""+formatted_last_season+""" (home,xgh,gh,ga,xga,away,date) VALUES (%s,%s,%s,%s,%s,%s,%s); """, 
						(df['Home'][j],df['xG'][j],df['Score'][j][0:df['Score'][j].find('–')],
						df['Score'][j][df['Score'][j].find('–')+1:],df['xG.1'][j],df['Away'][j],df['Date'][j]))

				elif pd.isna(df['Notes'][j]):
					print('Stopped',df['Home'][j],df['Away'][j])

					cur.execute("""DELETE FROM """+formatted_comp+""".nextmatch WHERE nextmatchindex="""+str(next_match_index)+""";
					INSERT INTO """+formatted_comp+""".nextmatch (nextmatchdate,nextmatchindex) VALUES (%s,%s); """, (df['Date'][j],j))
					break


	conn.commit()
	cur.close()
	conn.close()

update()
