import datetime

from bs4 import BeautifulSoup
from sparknlp.base import *
from sparknlp.annotator import *


def get_company(text:str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    name = soup.find("div", {"class":"page-h1"}).findChild("span").get_text()
    return name

def get_contents(text:str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    contents = soup.select('div.page-list-right')[0].text
    return contents

def get_cols(text:str, col:str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    page_list = soup.find('div', {"class": "page-list-right"})
    children = page_list.findChildren()
    for child in children:
        el = child.select('p')
        for e in el:
            find = e.find('strong')
            print(find)
            print(type(find))
            if find is not None and col in find.text:
                print(col)
                print(type(find.text))
                return find.parent.contents[-1].text
    return ''