import random
import bs4
import re

USER_AGENTS = [
    'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)


class Body:
    def __init__(self, content: bytes, skip_tags=None):
        self.soup = bs4.BeautifulSoup(content, 'html.parser').body

        if skip_tags:
            for tag in skip_tags:
                for t in self.soup.find_all(tag):
                    t.decompose()

    def extract_text(self, join=None):
        texts = []
        def recursive_extract(tag):
            if not isinstance(tag, bs4.element.Tag):
                texts.append(tag.text)
                return

            for t in tag.children:
                recursive_extract(t)
        recursive_extract(self.soup)

        if join: texts = join.join(texts)
        return texts


class CleanText:
    remove_tokens = ['\n', '\t', '\r', '©', '™', '®', '\xa0', '  ', '°', '(', ')']

    def __init__(self, text) -> None:
        if isinstance(text, str):
            self.text = self.clean(text)

        if isinstance(text, list):
            texts = []
            for t in text:
                t = self.clean(t)
                if t: texts.append(t)
            self.text = texts
    
    @staticmethod
    def clean(text):
        replace_dict = {token: '' for token in CleanText.remove_tokens}
        text = CleanText.replace_multiple(replace_dict, text)       
        text = CleanText.split_titled(text)
        return ' '.join([word for word in text.split(' ') if word])
        
    @staticmethod
    def replace_multiple(replace_dict, text):
        replace = dict((re.escape(k), v) for k, v in replace_dict.items()) 
        pattern = re.compile("|".join(replace.keys()))
        return pattern.sub(lambda m: replace[re.escape(m.group(0))], text)

    @staticmethod    
    def split_titled(text: str):
        clean_text = []
        for word in text.split(' '):
            if not word.isupper() and not word.isnumeric() and not word.islower():
                words = list(filter(None, re.split("([A-Z][^A-Z]*)", word)))
                cleaned_words = []
                for w in words:
                    if not w[-1].isalnum() and w[-1] not in '.,?!%':
                        w = w[:-1]
                    
                    if w: cleaned_words.append(w)
                word = ' '.join(cleaned_words)
            clean_text.append(word)

        return ' '.join(clean_text)