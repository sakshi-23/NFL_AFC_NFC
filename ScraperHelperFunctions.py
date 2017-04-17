try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from bs4 import BeautifulSoup
import csv
import json
import pdb

"""
Function to create dictionary mapping from NFL team names to their corresponding abbreviations
"""
def mapTeamNameToExtraInfo():
    team_url = "http://www.nfl.com/teams"
    page = urllib2.urlopen(team_url).read()
    soup = BeautifulSoup(page, "html.parser")
    teamGrid = soup.find("div", {"id": "col1"})
    afc = teamGrid.find("div", {"class": "col-one"})
    nfc = teamGrid.find("div", {"class": "col-two"})

    afcTeams = afc.findAll("div", {"class": "title"})
    nfcTeams = nfc.findAll("div", {"class": "title"})

    teamExtraInfos = {}
    for iTeam in xrange(len(afcTeams)): # afc and nfc have same number of teams
        afcName, afcAbbr = _getTeamNameAbbr(afcTeams[iTeam])
        nfcName, nfcAbbr = _getTeamNameAbbr(nfcTeams[iTeam])

        afcExtraInfo = {"abbr": afcAbbr, "division": "AFC"}
        nfcExtraInfo = {"abbr": nfcAbbr, "division": "NFC"}

        teamExtraInfos[afcName] = afcExtraInfo
        teamExtraInfos[nfcName] = nfcExtraInfo
    return teamExtraInfos

def _getTeamNameAbbr(teamGroup):
    teamUrl = teamGroup.find("a").get("href")
    teamName = teamGroup.contents[0].text
    teamAbbr = teamUrl.split("=")[1]
    return teamName, teamAbbr

def mergeCombinedDraftsWithScores(scoreCsv, draftJson):
    newDraft = []
    missingNames = []
    with open(scoreCsv) as scoreF:
        reader = csv.reader(scoreF)
        nameToScores = _csvToDict(reader)
    with open(draftJson) as draftF:
        drafts = json.load(draftF)

    for draft in drafts:
        names = draft["name"].split(", ")
        firstLastName = names[1] + " " + names[0]
        if firstLastName in nameToScores:
            scores = nameToScores[firstLastName]
        else:
            missingNames.append(firstLastName + "\n")

        # For merging to dictionaries
        scoreDraft = draft.copy()
        scoreDraft.update(scores)

        newDraft.append(scoreDraft)

    with open("draftScores.json", "w") as outfile:
        json.dump(newDraft, outfile, ensure_ascii=False, indent=4)

    with open("missingNames3.txt", "w") as outfile:
        outfile.writelines(missingNames)

def _csvToDict(reader):
    titleFields = reader.next()
    nameToScores = {}
    for row in reader:
        scores = {}
        for i in range(len(row)):
            if (i != 1):
                scores[titleFields[i]] = row[i]

        nameToScores[row[1]] = scores

    return nameToScores

def main():
    mergeCombinedDraftsWithScores('Metrics.csv', 'combinedRosterDraft.json')

main()
