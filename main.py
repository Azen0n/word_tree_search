import re

import fitz
import nltk
from nltk.stem.snowball import SnowballStemmer

from datatypes import Article, Sentence
from tree import WordTree

stemmer = SnowballStemmer('russian')


def main():
    pdf_path = 'file.pdf'
    txt_path = 'file.txt'
    nltk.download('punkt')

    text = read_pdf(pdf_path, txt_path)
    articles = split_text_into_articles(text)
    tree = WordTree(articles)

    tree.traverse()

    search_input = input('Enter any form of word or phrase to search in tree.\n'
                         ' - exit to leave from search mode\n'
                         'Enter word or phrase: ')
    while search_input != 'exit':
        result = tree.search(search_input)
        print_search_result(search_input, result)
        search_input = input('Enter word or phrase (exit): ')


def read_pdf(path: str, save_txt_path: str = None) -> str:
    """Reads pdf with scholar articles and returns plain string.

    If save_txt_path passed, text is saved in said path.
    """
    with fitz.open(path) as document:
        text = ''
        for page in document:
            text += page.get_text()
    if save_txt_path:
        with open(save_txt_path, 'w', encoding='utf8') as f:
            f.write(text)
    return text


def print_search_result(search_input: str, result: list[Sentence]):
    """Prints list of sentences with highlighted words."""
    if not result:
        print('Not found.')
        return
    if ' ' in search_input:
        words = search_input.split(' ')
    else:
        words = [search_input]
    for i, sentence in enumerate(result):
        sentence_text = sentence.text
        pattern = [fr'{stemmer.stem(word)}[А-Яа-яA-Za-z]*' for word in words]
        sentence_text = highlight_sentence_text(' '.join(pattern), sentence_text)
        print(f'{i + 1}. {sentence_text}')


def highlight_sentence_text(pattern: str, sentence_text: str) -> str:
    """Highlights stem and word ending in sentence text with red color.

    Returns text of sentence.
    """
    return re.sub(fr'({pattern})', r'\033[31m\g<1>\033[0m', sentence_text)


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
