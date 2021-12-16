from os import stat
import re
from typing import List
from pathlib import Path
import json

class Context:
    ENDLINEREG = r"[\.?!:;]+"

    label = None
    char_count = None
    line_count = None
    word_count = None
    context = None
    line_position_map = None
    lines = None
    detail = None

    def __init__(self, text = '', label='context', details=None) -> None:
        self.__init_context(text)
        self.label = label
        self.details = details


    def __init_context(self, text):
        self.context = text

        char_count = len(text)
        self.char_count = char_count
        
        lines = self.get_lines(text)
        self.lines = lines
        line_count = len(lines)
        self.line_count = line_count

        word_count = len(self.get_words(text))
        self.word_count = word_count

        start = 0
        position_map = []
        for line in lines:
            line_length = len(line)
            end = start+line_length
            position_map.append((start, end))
            start = end + 1 # 1 for next and 1 for ' ' while joining to get context

        self.line_position_map = position_map

    def summary(self):
        return {'char count': self.char_count, 'word count': self.word_count, 'line_count': self.line_count}

    class PathNotDir(Exception): pass
    def save(self, path: str, name = ''):
        path = Path(path)
        if not path.is_dir():
            raise self.PathNotDir(f'{path} is not a dir')

        json_raw = {
            'label': self.label,
            'char_count': self.char_count,
            'line_count': self.line_count,
            'word_count': self.word_count,
            'context': self.context,
            'position_map': self.line_position_map,
            'lines': self.lines,
            'details': self.details
        }

        label = name if name else self.label
        with (path / f'{label}.json').open('w') as f:
            json.dump(json_raw, f)


    class PathNotFile(Exception): pass
    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.is_file():
            raise cls.PathNotFile(f'{path} is not a file')

        with path.open('r') as f:
            json_raw = json.load(f)

        c = cls()
        c.label = json_raw['label']
        c.char_count = json_raw['char_count']
        c.line_count = json_raw['line_count']
        c.word_count = json_raw['word_count']
        c.context = json_raw['context']
        c.line_position_map = json_raw['position_map']
        c.lines = json_raw['lines']
        c.details = json_raw['details'] if 'details' in json_raw else {}
        
        return c

    def get_lines(self, text) -> List[str]:
        return re.split(self.ENDLINEREG, text)


    def get_words(self, sentence) -> List[str]:
        return sentence.split(' ') if sentence else []


    def __repr__(self):
        return f"Context:{self.label}[len:{self.char_count}]"


    def __str__(self):
        return self.__repr__()