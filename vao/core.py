
from pathlib import Path
import bs4
from typing import List
import pandas as pd
import json
import Levenshtein as L
import seaborn as sns
import numpy as np
# harmaonized data hts hs product classification



class Context:
    seperator = '<sep>'
    text: str
    lines: List[str]
    line_count: int
    word_count: int
    char_count: int
    about: dict


    def __init__(self, lines =[], about={}) -> None:
        self.about = about

        if lines:
            self.lines = lines
            self.line_count = len(lines)

            self.text = self.seperator.join(lines)

            self.word_count = 0
            self.char_count = 0
            for line in lines:
                words = line.split(' ')
                self.word_count += len(words) 
                for word in words:
                    self.char_count += len(word)

            self.summary = self.generate_summary()

    def get_lines_as_df(self):
        return pd.DataFrame({'lines': self.lines})

    def generate_summary(self):
        lines_ = []
        words_ = []
        
        for line in self.lines:
            words = line.split(' ')
            for word in words:
                lines_.append(line)
                words_.append(word)
        

        df = pd.DataFrame({'line': lines_, 'word': words_})
        self.M = df

        avg_words_in_line = df.groupby('line').count().mean()['word']
        self.word_counts = sum(df.groupby('line').count().values.tolist(), [])

        avg_chars_in_line = pd.DataFrame({'sentence': df['line'].unique()})['sentence'].str.len().mean()
        word_frequency = df.groupby("word").count()['line']

        results = {
            'counts': {
                'char_count': self.char_count,
                'word_count': self.word_count,
                'line_count': self.line_count,
            },
            'avg': {
                'avg_words_in_line': avg_words_in_line,
                'avg_chars_in_line': avg_chars_in_line,
            },
            'word_frequency': word_frequency,
        }

        self.summary = results

        return results

    
    def get_correlation_matrix(self):
        cols = []
        for line1 in self.lines:
            rows = []
            for line2 in self.lines:
                rows.append(L.ratio(line1, line2))
            cols.append(rows)

        return pd.DataFrame(cols)

    def get_word_dict(self, frequency_map, vocab, limit=10):
        wdf = pd.DataFrame(frequency_map).reset_index()
        df = wdf if not vocab else wdf[wdf['word'].isin(vocab)] 
        return df.sort_values('line', ascending=False).head(limit).set_index('word')

    
    def filter_lines_on_correlation_threshold(self, threshold, max_length=-1):

        char_count = max_length+0.01 if max_length < 0 else self.summary['counts']['char_count']
        while (char_count > max_length):
            df = self.get_lines_as_df()
            correlation_df = self.get_correlation_matrix()
            mask = ~(correlation_df.mask(np.eye(len(correlation_df), dtype=bool)).abs() > threshold).any()
            lines = sum(df[mask].values.tolist(), [])
            char_count = Context(lines).summary['counts']['char_count']
            threshold -= 0.01

        return lines

    def filter_line_above_average_word_count(self):
        lines_df = pd.DataFrame(self.M.groupby('line').count()).reset_index()
        return lines_df[lines_df['word'] > self.summary['avg']['avg_words_in_line']]['line'].values


    def plot_word_dict_graph(self, vocab=[], limit=10):
        df = self.get_word_dict(self.summary['word_frequency'], vocab, limit=limit)
        df.plot.bar()

    
    def plot_line_correlations(self):
        sns.heatmap(self.get_correlation_matrix())


    def save(self, name):
        data = {
            'seperator': self.seperator,
            'lines': self.lines,
            'about': self.about
        }

        json.dump(data, Path(name).open('w'))

    @classmethod
    def load(cls, name):
        data = json.load(Path(name).open('r'))
        clss = cls(data['lines'])
        clss.seperator = data['seperator'],
        clss.about = data['about']
        return clss