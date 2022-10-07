import re

import fitz
import nltk

from datatypes import Article
from tree import WordTree


def main():
    txt_path = 'file.txt'
    nltk.download('punkt')
    
    with open(txt_path, encoding='utf8') as f:
        text = f.read()
    articles = split_text_into_articles(text)
    tree = WordTree(articles)
    
    tree.traverse()
    
    word = input('Enter word (exit): ')
    while word != 'exit':
        tree.search(word)
        word = input('Enter word (exit): ')


def read_pdf(path: str, save_txt_path: str = None) -> str:
    with fitz.open(path) as document:
        text = ''
        for page in document:
            text += page.get_text()
    if save_txt_path:
        with open(save_txt_path, 'w', encoding='utf8') as f:
            f.write(text)
    return text


def split_text_into_articles(text: str) -> list[Article]:
    """Returns list of Article objects, consisting of
    list of authors, title and main text without 'СПИСОК ЛИТЕРАТУРЫ'.
    """
    pattern = re.compile(r"""(?:\d+\s?)\n   # page number (ignored)
                         ((?:.+\n){1,5})    # authors and their universities
                         (?:УДК:?\s+[\d]+\.?[\d]+.+\n)  # УДК (ignored)
                         ((?:.+\n){1,5}(?=Аннотация))   # article title
                         (?:Аннотация\.?\:?)    # counts as first sentence
                                                # so ignored
                         """, re.X)
    authors_pattern = r'[А-ЯA-Z]\. ?[А-ЯA-Z]\.? [А-Яа-я]+'
    splitted_text = re.split(pattern, text)
    articles = []
    try:
        for i in range(1, len(splitted_text), 3):
            authors = re.findall(authors_pattern, splitted_text[i])
            title = splitted_text[i + 1]
            raw_text = re.split('СПИСОК ЛИТЕРАТУРЫ', splitted_text[i + 2])[0]
            articles.append(Article(authors, title, raw_text))
    except IndexError:
        raise IndexError('Wrong split occurred. Adjust regex pattern.')
    return articles
    

if __name__ == '__main__':
    main()
