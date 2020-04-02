from parsel import Selector
import requests as req
import re


campeonatos = {
    'paulista2019':'http://www.saopaulofc.net/equipe/temporada/campeonato-paulista-2019',
    'brasileiro2019':'http://www.saopaulofc.net/equipe/temporada/campeonato-brasileiro-2019',
    'paulista2020':'http://www.saopaulofc.net/equipe/temporada/campeonato-paulista-2020',
    'libertadores2020':'http://www.saopaulofc.net/equipe/temporada/copa-libertadores-2020'
}

RE_TAG  = '<[^>]*>'
SPLIT   = "(?!<(?:\(|\[)[^)\]]+),(?![^(\[]+(?:\)|\]))|(\s{1}e\s{1})|;"
PAREN   =   '\((.*)\)'

def __find_goals(str):
    first, second = str.split('<hgroup>')[1:]

    ft, ft_goals = first.split('<h4>')[-1].split('</h4>')
    ft = ft.strip()
    ft_goals = ft_goals.split('<p>')[-1].split('</p>')[0]

    st, st_goals = second.split('<h4>')[-1].split('</h4>')
    st = st.strip()
    st_goals = st_goals.split('<p>')[-1].split('</p>')[0]

    return [(ft, ft_goals), (st, st_goals)]

def scrap_game(id, date, place, url):
    # '{} - {} - {} - {}'.format(id, date, place, url)
    print(url)
    res     = req.get(url)
    html    = Selector(text=res.text)
    details = html.css('section.details')
    escals  = details[0:2]
    goals   = details[2]
    cards   = details[4]   
    money   = details[-1]

    team_0  = re.sub(RE_TAG, '', escals[0].xpath('hgroup')[0].xpath('h4').get()).strip()
    team_1  = re.sub(RE_TAG, '', escals[1].xpath('hgroup')[0].xpath('h4').get()).strip()

    spfc_escal  = re.sub(RE_TAG, '', escals[0 if team_0 == 'São Paulo' else 1].xpath('p').get()).strip()
    other_escal = re.sub(RE_TAG, '', escals[1 if team_0 == 'São Paulo' else 0].xpath('p').get()).strip()
    other_team  = team_1 if team_0 == 'São Paulo' else team_0
    
    (ft, ft_goals), (st, st_goals) = __find_goals(goals.get())

    spfc_goals  = ft_goals if ft == 'São Paulo' else st_goals
    other_goals = st_goals if ft == 'São Paulo' else ft_goals

    p = re.compile(PAREN)
    print(re.findall('\(([^)]+)\)', spfc_escal))
    # print(    spfc_escal[spfc_escal.find("(")+1:spfc_escal.rfind(")")])

    spfc_escal  = re.split(SPLIT, spfc_escal)
    spfc_escal  = [x for x in spfc_escal if x if x != ' e ']
    other_escal = re.split(SPLIT, other_escal)
    other_escal = [x for x in other_escal if x if x != ' e ']

    spfc    = { 'team': spfc_escal, 'goals': spfc_goals }
    other   = { 'team': other_escal, 'goals': other_goals }
    
    to_return = dict()
        
    to_return['id']     = id
    to_return['date']   = date
    to_return['place']  = place
    to_return['url']    = url
    to_return['spfc']   = spfc
    to_return['other']  = other
    return to_return


def scrap_campeonato(id, url):
    res     = req.get(url)
    html    = Selector(text=res.text)
    table   = html.css('table.jogos')[0]
    r_games = table.xpath('//tr[@height=49]')
    for game in r_games:
        cells   =  game.xpath('td')
        date    = re.sub(RE_TAG, '', cells[0].get())
        place   = re.sub(RE_TAG, '', cells[2].get())
        url     = 'http://www.saopaulofc.net' + cells[3].xpath('a')[0].attrib['href']
        game = scrap_game(id, date, place, url)
        # print(game)
        # break

def init_scrapping():

    for camp_id, camp_url in campeonatos.items():
        scrap_campeonato(camp_id, camp_url)
        # break


    return 1
