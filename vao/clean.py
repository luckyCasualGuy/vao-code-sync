
class CleanLines:
    remove = ['\n', '\r', '\t', '\xa0', '..', '...', '©', '™', '  ']
    separator = '. '
    line_separator = separator

    def __init__(self, lines, 
    lower=False, unique=True,
    remove=[], add_to_remove=[],
    inner_split=True) -> None:

        if remove: self.remove = remove
        if add_to_remove: self.remove.extend(add_to_remove)
        if not inner_split: self.line_separator = '<><><><><><><><><><><>'

        cleaned = []
        for line in lines:
            for t in self.remove:
                line = line.replace(t, '')

            if line:
                if lower: line = line.lower()
                for l in line.split(self.line_separator):
                    cleaned.append(l.strip())

        if unique: cleaned = list(set(cleaned))
        self.lines = cleaned

    @staticmethod
    def match_vocab(lines, vocab, mode='split', lower=True):
        matching = []

        if mode == 'split':
            for line in lines:
                for word in line.split(' '):
                    if word in vocab:
                        matching.append(line)
                        break

        if mode == 'ssplit':
            splits = []
            for word in vocab:
                splits.extend(word.split(' '))
            vocab = splits

            for line in lines:
                for word in line.split(' '):
                    if word in vocab:
                        matching.append(line)
                        break
            
            matching = list(set(matching))

        elif mode == 'contain':
            for line in lines:
                for word in vocab:
                    if line.__contains__(word):
                        matching.append(line)
            matching = list(set(matching))

        return matching

    def __call__(self):
        return self.lines