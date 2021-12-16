from main.scrap.core import CleanText, Body
from collections import Counter
from difflib import get_close_matches
from pandas import DataFrame


HEADER3M = {'User-Agent': "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}


class CleanText3M(CleanText):
    def __init__(self, text) -> None:
        super().__init__(text)


class Links3M:
    link3m_start = "https://www.3m"

    def __init__(self, body: Body) -> None:
        counter = 0
        links3m = []
        for a in body.soup.find_all('a'):
            href = a['href']
            index = href.find(self.link3m_start)
            if index > 0:
                link = '/'.join(href[index:].split('/')[:-1]) + '/'
                links3m.append((link))
                counter += 1

        self.links = links3m
        self.__length = counter

    def __len__(self): return self.__length

    def __iter__(self):
        for link in self.links:
            yield link

    def __next__(self):
        return next(self.__iter__())

    def __getitem__(self, index):
        return self.links[index]



class SearchScore3M:
    def __init__(self, text: str, search: str, sentnce_limit=None) -> None:
        lower_text = text.lower()
        lower_text_replaced = CleanText3M.replace_multiple({'.': '', ',': ''}, lower_text)
        splits = lower_text_replaced.split(' ')
        
        search_words = search.lower().split(' ')
        result = {}
        for word in search_words:
            matches = get_close_matches(word, splits)
            if matches:
                match_counter = Counter(matches)
                result[word] = list(match_counter.keys())
            else: result[word] = []

        self.keywords = result

        result = {key: {k: [] for k in self.keywords[key]} for key in self.keywords.keys()}
        for sentence in lower_text.split('. '):
            for word in self.keywords.keys():
                keys = self.keywords[word]
                for key in keys:
                    if sentence.__contains__(key):
                        result[word][key].append(sentence)
        self.sentences = result

        W = []
        K = []
        S = []
        for word, word_value in self.sentences.items():
            for key, key_sentences in word_value.items():
                SM = sentnce_limit if sentnce_limit else -1
                for sentence in key_sentences:
                    if not SM: break
                    W.append(word)
                    K.append(key)
                    S.append(sentence)
                    SM -= 1

        self.M = DataFrame({'search word': W, 'close match': K, 'sentence': S})
        self.matrix = DataFrame(self.M.groupby(['search word', 'close match', 'sentence']).count())
        