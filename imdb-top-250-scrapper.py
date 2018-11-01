# -*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
import re
import csv

yearRegex = r"\((\d{4})\)"
castRegex= r"^(.*)\s\(dir.\),\s(.*)"

IMDB_TOP_250_URL = 'https://www.imdb.com/chart/top'

def convert(url):
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(resp, 'lxml')
    return soup
    
def startScrapping():
    dataset = []
    soup = convert(IMDB_TOP_250_URL)
    rows = soup.find_all('tr')
#    soup.findChild()
    for row in rows:
        movieInfo = {};
        titles = row.find_all('td', { 'class': 'titleColumn' })
        ratings = row.find_all('td', { 'class': 'ratingColumn imdbRating' })
        for row in titles:
            movieInfo['rank'] = row.getText().strip().split('\n')[0]
            movieInfo['title'] = row.getText().strip().split('\n')[1].strip()
            movieInfo['year'] = re.match(yearRegex, row.getText().strip().split('\n')[2], re.MULTILINE).group(1)
            anchorTag = row.findChild('a')
            movieInfo['link'] = 'https://www.imdb.com' + anchorTag.get('href')
            movieInfo['linkMeta'] = anchorTag.get('title')
            movieInfo['director'] = re.match(castRegex, anchorTag.get('title'), re.MULTILINE).group(1) 
            movieInfo['starring'] = re.match(castRegex, anchorTag.get('title'), re.MULTILINE).group(2)
            
        for row in ratings:
            movieInfo['score'] = row.getText().strip().split('\n')[0]
        dataset.append(movieInfo)
        
    for item in dataset:
        print('Crawling ', item.get('title'))
        if item.get('link'):
            try:
                soupLink = convert(item.get('link'))
                subtexts = soupLink.find('div', { 'class': 'subtext' })
                item['rating'] = null if not subtexts.getText().split()[0] else subtexts.getText().split()[0]
                item['duration'] = null if not subtexts.getText().split()[2] + subtexts.getText().split()[3] else subtexts.getText().split()[2] + subtexts.getText().split()[3]
                item['genre'] = null if not subtexts.getText().split()[5] else subtexts.getText().split()[5]
                item['metadate'] = subtexts.getText().split()
                
                summary_text = soupLink.find_all('div', { 'class': 'summary_text' })
                credit_summary_item = soupLink.find_all('div', { 'class': 'credit_summary_item' })
                item['summarytext'] = summary_text[0].getText().strip()
                item['creditsInfo'] = credit_summary_item
                
                storyline = soupLink.find('div', { 'id': 'titleStoryLine'})
                storyText = storyline.findChild('div', { 'class': 'inline canwrap' }).findChild('p').findChild('span').getText()
                item['storyline'] = storyText
            except:
                print('Error')
            
    keys = dataset[1].keys()
    with open('imdb-top-250.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dataset)
        
def init():
    startScrapping()
        
#soupLink = convert('https://www.imdb.com/title/tt0071562/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=e31d89dd-322d-4646-8962-327b42fe94b1&pf_rd_r=Q5MBEKKFJAP35E591Z17&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_3')
#storyline = soupLink.find_all('div', { 'class': 'subtext' })
##storyText = storyline.findChild('div', { 'class': 'inline canwrap' }).findChild('p').findChild('span').getText()
#print(storyline)
init()