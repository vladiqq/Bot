import re
import os.path
import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse
from sqlighter import SQL

db = SQL('mytelegrambd123')


class KH:
    host = 'https://www.sportinform.com.ua/'
    url = 'https://www.sportinform.com.ua/tournaments/110/'
    lastkey = ""

    def __init__(self, lastk):
        self.lastkey = lastk
        print(self.lastkey['lastkey'], type(self.lastkey))

    def search_news(self):
        """Поиск новостей"""
        r = requests.get(self.url)
        html = BS(r.content, 'html.parser')

        new = []
        items = html.select('.illustr > a ')
        for i in items:
            key2 = re.match(r'\/tournaments\/110\/news\/(\d+)', i['href'])
            key = key2.group(1)
            if self.lastkey['lastkey'] < int(key):
                new.append(i['href'])
        #   key=""

        return new

    def parse_news(self, uri):
        """Датали новых новостей"""
        link = self.host + uri
        r = requests.get(link)
        html = BS(r.content, 'html.parser')
        # parse poster image url
        key = re.match(r'\/tournaments\/110\/news\/(\d+)', uri).group(1)

        poster = re.findall(r'http://www.sportinform.com.ua/files/news/\w+-\w+-\w+.\w+',
                            str(html.select('.news-header > .photo')))
        if poster.__len__() == 0:
            poster = re.findall(r'http://www.sportinform.com.ua/files/news/\w+-\w.\w+',
                                str(html.select('.news-header > .photo')))
        ne = str(html.select('h1')[0].text)
        if ne.startswith('Расписание'):
            db.add_schedule(link)

        info = {
            "id": key,
            "title": html.select('h1')[0].text,
            "link": link,
            "image": poster[0],
        }
        poster.clear()

        return info

    def show_schedule(team, link):
        """Вывод расписания"""
        r = requests.get(link)
        html = BS(r.content, 'html.parser')
        cd = html.select('p')
        gd1 = str(cd).split(r'<p><span style="font-size: medium;"><br />')
        gd1 = str(gd1).split(r'</span></p>, <p><span style="font-size: medium;">')
        location = []
        game = []

        for gd in gd1[1:-1]:  # Поиск команды в рассписании
            d = re.findall(str(team).upper(), str(gd))
            b = re.findall(str(team).title(), str(gd))
            if b or d:
                gd = re.split("<br/>.r.n", str(gd))
                location.append(gd[1][:-4])  # список с полями
                for i in gd:
                    z = re.findall(str(team).upper(), str(i))
                    y = re.findall(str(team).title(), str(i))  # поиск команды на этом поле
                    if z or y:
                        print(i)
                        q = i[5:-2]
                        print(q)
                        if q.startswith('t'):
                            q = q[1:]
                            q = re.sub(r'\\t', ' --> ', q)  # замена хуйни
                            game.append(q)  # список с играми

                        else:
                            q = re.sub(r'\\t', ' --> ', q)  # замена хуйни
                            game.append(q)  # список с играми
        if game.__len__() == 0:
            info = ""
        else:
            info = {
                'location': location,
                'game': game,
            }
        return info

    def download_image(self, url):
        """Загрузка картинки"""
        r = requests.get(url, allow_redirects=True)

        a = urlparse(url)
        filename = os.path.basename(a.path)
        open(filename, 'wb').write(r.content)

        return filename

    def update_lastkey(self, new_key):
        """Обновление id последней новости"""
        self.lastkey = int(new_key)

        return db.update_lastkey(new_key)

    def delete_photo(self):
        a = "/home/ubuntu/Deploy/"
        for file in os.listdir(a):
            if file.endswith(".jpg"):
                os.remove(a + file)
