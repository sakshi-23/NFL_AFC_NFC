try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import json
from bs4 import BeautifulSoup
from ScraperHelperFunctions import mapTeamNameToExtraInfo
import pdb

#functions for switcher
#i%5==1 D
def roundNum(player, row):
    if (row.contents == []) :
        player['round'] = "N/A"
    else:
        player['round'] = row.contents[0]
#i%5==2 D
def selNum(player, row):
    if (row.contents == []) :
        player['selNum'] = "N/A"
    else:
        player['selNum'] = row.contents[0]
#i%5==3 D
def name(player, row):
    #player's name because it's <a> tag and
    #I need to get text not the link
    href = row.contents[1].get('href')
    nameArr = href.split('/')
    urlProfile.append(href);
    player['forChecking'] = nameArr[2]
    names = row.contents[1].text.split()
    player['name'] = names[1] + ", " + names[0]
#i%5==4 D
def position(player, row):
    position = row.contents[0]
    if (position == 'OT'):
        position = 'T'
    if ('LB' in position):
        position = 'LB'
    if (position == 'SAF'):
        position = 'S'
    player['position'] = position
#i%5==0 D
def school(player, row):
    player['school'] = row.contents[0]
def status(player, row):
    player['status'] = row.contents[0]
def label(row, count):
    if (len(row.contents[0].strip()) < 1) :
        labelQS = 'N/A' + str(count)
    else:
        labelQS = row.contents[0]
    return labelQS.strip()
def statLabel(player, row, labelQS):
    if (row.contents is None or len(row.contents) < 1) :
        player[labelQS] = "N/A"
    else:
        player[labelQS] = row.contents[0]
# def team(player, row):
#     player['team'] = row.contents[0].text
def teamR(player, row):
    teamArr = row.contents[0].get('href').split('/')
    player['team'] = teamArr[2]
def playerName(player, row):
    nameArr = row.contents[0].get('href').split('/')
    player['forChecking'] = nameArr[2]
    player['name'] = row.contents[0].text

def isInDraft (drafts, player):
    teamDraft = (item for item in drafts if item['name'] == player['name'])
def scrapContents(rosterJson, drafts, evenOdd, table):
    i = 0
    for tr in table.findAll('tr',{'class':evenOdd}):
        for row in tr.findAll("td"):
            i+=1
            if (i%13==1):
                count = 0
                player = {}
                rosterJson.append(player)

            count += 1

            switchFunc = {
                1: position,
                2: selNum,
                3: playerName,
                4: status,
                5: label,
                6: statLabel,
                7: label,
                8: statLabel,
                9: label,
                10: statLabel,
                11: label,
                12: statLabel,
                0: teamR
            }

            if (i%13 >= 5):
                if ((i%13)%2 == 1):
                    labelQS = switchFunc[i%13](row, count)
                else:
                    switchFunc[i%13](player, row, labelQS)
            else:
                switchFunc[i%13](player, row)

            if (i%13 == 0):
                playerDraft = next((item for item in drafts if item['forChecking'] == player['forChecking']), None)
                if (playerDraft):
                    if (playerDraft['team'].replace(" ", "").lower() == player['team']):
                        playerDraft['status'] = player['status']
                    elif (playerDraft['status']=='N/A'):
                            playerDraft['status'] = 'OTHER_TEAM'

def rosterJsonAddAll(soupR, rosterJson, drafts):
    for table in soupR.findAll("table"):
        scrapContents(rosterJson, drafts, 'odd', table);
        scrapContents(rosterJson, drafts, 'even', table);

teamExtraInfos = mapTeamNameToExtraInfo()

#FOR other scraper
urlProfile = [];
#any way to get the urlList without having a soup first?
url = "http://www.nfl.com/draft/history/fulldraft?type=team"
page = urllib2.urlopen(url).read()
soup = BeautifulSoup(page, "html.parser")

#getting the url's for all nfl teams
urlBaseDrafts = "http://www.nfl.com/draft/history/fulldraft?teamId="
urlListDrafts = []
urlBaseRoster = "http://www.nfl.com/players/search?category=team&playerType=current&filter="
urlListRoster = []

#ComboBox!
for option in soup.findAll('option'):
    urlListDrafts.append(urlBaseDrafts+option['value']+"&type=team")
    urlListRoster.append(urlBaseRoster+option['value'])

#to-be json list-> would contain object format type of needed data
draftsJson = [];
rosterJson = [];
countName = 0;
# loop through urlList to gather all the data needed
for url2 in urlListDrafts:
    page2 = urllib2.urlopen(url2).read()
    soup2 = BeautifulSoup(page2, "html.parser")
    for table in soup2.findAll("table") [0:10]:#2014-2005
        tbody = table.find("tbody")
        # object that tells me which team, what year,
        # how many players were picked that year
        i = 0 #which column in the row is selected

        playerList=[]
        for row in tbody.findAll("td"):
            i+= 1

            if (i%5 == 1):
                player = {}
                title = table.find("tr", {'class':'thd1'})
                player['year'] = title.find("td").contents[0][:4]
                player['team'] = soup2.find('option', selected=True).getText();
                player['teamAbbr'] = teamExtraInfos[player['team']]["abbr"]
                player['division'] = teamExtraInfos[player['team']]["division"]
                player['status'] = 'N/A'
                draftsJson.append(player)

            swithcer = {
                1: roundNum,
                2: selNum,
                3: name,
                4: position,
                0: school
            }
            swithcer[i%5] (player, row)

for urlR in urlListRoster:
    pageR = urllib2.urlopen(urlR).read()
    soupR = BeautifulSoup(pageR, "html.parser")
    rosterJsonAddAll(soupR, rosterJson, draftsJson)
    if (soupR.findAll('a', {'title':'Go to page 2'}) != None):
        urlR = "http://www.nfl.com/players/search?category=team&playerType=current&d-447263-p=2&filter=" + urlR[-4:]
        pageR = urllib2.urlopen(urlR).read()
        soupR = BeautifulSoup(pageR, "html.parser")
        rosterJsonAddAll(soupR, rosterJson, draftsJson)

with open('combinedRosterDraft.json', 'w') as outfile:
    json.dump(draftsJson, outfile, ensure_ascii=False, indent=4)
# FOR other scraper
with open('playerprof.json', 'w') as outfile:
    json.dump(urlProfile, outfile, ensure_ascii=False, indent=4);
