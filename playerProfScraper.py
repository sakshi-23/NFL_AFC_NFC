import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from bs4 import BeautifulSoup
from ScraperHelperFunctions import mapTeamNameToExtraInfo

teamExtraInfos = mapTeamNameToExtraInfo()

with open('playerprof.json') as data_file:
    playerProfile = json.load(data_file);
def assignKeyP(key, i):
    print (player['name']);
    if player[key] is not None:
        player[player[key][i].text]=player[key][i+1].strip().replace(": ","");
urlBase = "http://www.nfl.com";
urlArr = [];
for urlRest in playerProfile:
    urlArr.append(urlBase+urlRest);

urlArr = urlArr[500:1000]#[1000:1500]
profiles=[];
keyNames=['hwa', 'birth', 'college', 'exp', 'hs'];

for url in urlArr:
# if True:
#     url = "http://www.nfl.com/player/tylerdavis/2555563/profile"
    page = urllib2.urlopen(url).read();
    soup = BeautifulSoup(page, "html.parser");
    player={};
    player['picture'] = soup.find("div", {"class":"player-photo"}).find("img").get('src');
    player['name'] = soup.find("span", {"class":"player-name"}).contents[0].strip();
    if soup.find("span", {"class": "player-number"}) is not None:
        player['number'] = soup.find("span", {"class": "player-number"}).contents[0].strip();
    if soup.find("p", {"class": "player-team-links"}) is not None:
        player['team'] = soup.find("p", {"class": "player-team-links"}).find("a").getText();

    i=0;
    for paragraph in soup.find("div", {"class":"player-info"}).findAll("p"):
        if i > 1:
            if (i-2) != 0 or len(paragraph.contents) > 2:
                player[keyNames[i-2]] = paragraph.contents;
        i+=1;
    #TAKES care of Height, Weight, Age
    if 'hwa' in player:
        for j in range(1, len(player['hwa']), 2):
            assignKeyP('hwa', j);
        player.pop('hwa');
    for k in range(1,len(keyNames)):
        if keyNames[k] in player:
            index =1;
            if len(player[keyNames[k]]) <3:
                index = 0;
            assignKeyP(keyNames[k], index);
            player.pop(keyNames[k]);
    # for quickStat in soup.findAll()
    if soup.find("p", {"class":"player-quick-stat-item-header"}) is not None:
        # firstStatKey = soup.find("p", {"class":"player-quick-stat-item-header"}).text;
        # firstStatValue = soup.find("p", {"class":"player-quick-stat-item-body"}).text;
        stats=[];
        # stats.append({firstStatKey:firstStatValue});
        for wrapStat in soup.findAll("div", {"class":"player-quick-stat-item"}):
            statKey = wrapStat.find("p", {"class":"player-quick-stat-item-header"}).text;
            print (statKey)
            statValue = wrapStat.find("p", {"class":"player-quick-stat-item-body"}).text;
            stats.append({statKey:statValue});
        player['stats'] = stats;
    profiles.append(player);

with open('playerProfile2.json', 'w') as outfile:
    json.dump(profiles, outfile, ensure_ascii=False, indent=4);
