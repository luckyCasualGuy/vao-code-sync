from pathlib import Path
import bs4
import json


IGNORE = ['script', 'img', 'table', 'button', 'i', 'noscript', 'style', 'form', 'meta']


class RawHtmlContent:
    def __init__(self, content, meta={}) -> None:
        self.content = content
        self.meta = meta

    def save(self, name):
        save_content = {
            'content': self.content,
            'meta': self.meta
        }

        json.dump(save_content, Path(name).open('w'))

    @classmethod
    def load(cls, name):
        loaded = json.load(Path(name).open('r'))
        return cls(loaded['content'], loaded['meta'])


class Body:
    def __init__(self, content, ignore=[]) -> None:
        self.soup = bs4.BeautifulSoup(content, 'html.parser')
        self.body = self.soup.body

        if ignore:
            if self.body: self.body = self.ignore(self.body, ignore)

    @staticmethod
    def ignore(body, tags=[]):
        new_body = body
        if tags:
            for tag in tags:
                for t in new_body.find_all(tag):
                    if t: t.decompose()
        return new_body

    def extract_lines(self, word_thresh = 2):
        lines = []
        def recursive_extract(tag):

            if isinstance(tag, bs4.element.Tag):
                for t in tag.children:
                    recursive_extract(t)
            else:
                text = tag.text
                if len(text.split(' ')) > word_thresh:
                    lines.append(text)

        if self.body: recursive_extract(self.body)

        return lines
