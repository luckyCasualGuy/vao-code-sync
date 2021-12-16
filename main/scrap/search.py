

class GoogleSearchURL:
    def __init__(self, search_string: str) -> None:
        search_string = str(search_string)
        self.string = f"https://www.google.com/search?q={'+'.join(search_string.split(' '))}"

    def __repr__(self) -> str:
        return self.string