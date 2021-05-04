
from urllib.request import urlopen
import sqlite3

from bs4 import BeautifulSoup
import ssl
import textwrap


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('urls.db')
cur = conn.cursor()


def createTable():
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS urls(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, summary TEXT)''')


# clearing Table
# def clearTable():
#     cur.execute('DELETE * FROM urls')

# Make the single line out put look like a paragraph
def makePara(text):
    dedented_out = textwrap.dedent(text).strip()
    return textwrap.fill(dedented_out, width=100)


# return a summary paragraph text
def paragraph(url):
    html = urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    para = soup.find_all('p')
    text_para = []
    for i in para:
        #    print(i.text)
        text_para.append(i.text)
    # print(text_para)
    cor = 0
    index = -1
    out = 'Article not found'
    for k in text_para:
        index = index + 1
        if len(k) < 15:
            continue
        elif "Coordinates" in k and cor == 0:
            cor = 1
            continue
        elif "may refer to:" in k:
            continue
        else:
            out = k
            updatedatabase(url, out)
            break

    return makePara(out)


def CheckDb(url):
    cur.execute('''SELECT count(*) FROM urls WHERE url=?''', (url,))
    return cur.fetchone()[0]


def updatedatabase(url, para):
    cur.execute('''INSERT OR IGNORE INTO urls (url,summary) VALUES (?,?)''', (url, para))
    conn.commit()
    #print('Commited')


def fetchFromDb(url):
    cur.execute('''SELECT summary FROM urls WHERE  (url = ?)''', (url,))
    return makePara(cur.fetchone()[0])


# A wikipedia url fr a certain topic can be simply made by adding the topic to the end of 'https://en.wikipedia.org' and replacing any white spaces with '_'
def search(txt):
    txt = txt.replace(" ", "_")
    url = 'https://en.wikipedia.org/wiki/' + txt
    if CheckDb(url) == 0:
        print("No such article in the data base, Fetching from wikipedia...\n")
        text_data = paragraph(url)
    else:
        print("Article exists in the data base\n")
        text_data = fetchFromDb(url)
    return text_data


createTable()

while True:
    print("type \"exit()\" to exit")
    topic = input("Search wiki for : ")
    try:
        if topic == 'exit()':
            print('program ended')
            break
        print(search(str(topic)))
        print('\n')
    except:
        print('An error Occurred')
