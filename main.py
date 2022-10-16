import re

import fitz
import nltk
from pymorphy2 import MorphAnalyzer

from datatypes import Article
from tree import WordTree


def main():
    pdf_path = 'file.pdf'
    txt_path = 'file.txt'
    nltk.download('punkt')
    morph = MorphAnalyzer()
    
    text = read_pdf(pdf_path, txt_path)
    articles = split_text_into_articles(text)
    tree = WordTree(articles)
    
    tree.traverse()
    
    word = input('Enter any form of word to search in tree.\n'
                 ' - exit to leave from search mode\n'
                 'Enter word: ')
    while word != 'exit':
        result = tree.search(word)

        if result is not None:
            part_of_speech = morph.parse(word)[0].tag.POS
            result.print_articles(part_of_speech)
        else:
            print('Not found.')

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
                         (?:Аннотация\.?:?)    # counts as first sentence
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
