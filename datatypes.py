from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re
import time

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from pymorphy2 import MorphAnalyzer

STOPWORDS = set(stopwords.words('russian')
                ).union(set(stopwords.words('english')))


class WordSingleton(type):
    """Splitting sentences in words results in creating new object for 
    each word. This kind of singleton will return existing word with 
    new form-sentence record in it or create new word if it doesn't exist.
    """
    _words: dict[str, Word] = {}

    def __call__(cls, stem: str, word_form: str, sentence: Sentence):
        if stem in cls._words:
            cls.__append_form_and_sentence(stem, word_form, sentence)
        else:
            cls._words[stem] = super(
                WordSingleton, cls).__call__(stem, word_form, sentence)
        return cls._words[stem]

    def __append_form_and_sentence(cls, stem: str, word_form: str,
                                   sentence: Sentence):
        if word_form in cls._words[stem].forms:
            cls._words[stem].forms[word_form].append(sentence)
        else:
            cls._words[stem].forms[word_form] = [sentence]
        cls._words[stem].count += 1

    @property
    def words(self):
        return self._words


class PartOfSpeech(Enum):
    """pymorphy2 parts of speech abbreviations."""
    NOUN = 'noun'
    ADJF = 'full form adjective'
    ADJS = 'short form adjective'
    ADVB = 'adverb'
    COMP = 'comparative'
    CONJ = 'conjunction'
    GRND = 'gerund'
    INFN = 'infinitive'
    INTJ = 'interjection'
    PRCL = 'particle'
    PRED = 'predicative'
    PREP = 'preposition'
    VERB = 'verb'
    PRTS = 'short form participle'
    PRTF = 'full form participle'
    NUMR = 'numeral'
    NPRO = 'noun-pronoun'


@dataclass
class Word(metaclass=WordSingleton):
    """Word.

    * text — word base.
    * forms — dictionary with word forms and list of sentences
    with these forms.
    * count — number of occurrences of all forms with this base
    (across all articles).
    """
    stem: str
    forms: dict[str, list[Sentence]] = field(init=False)
    count: int = 0

    def __init__(self, stem: str, word_form: str, sentence: Sentence):
        """:param stem: word base (stemmed using nltk
        SnowballStemmer).
        :param word_form: any form with base stem.
        :param sentence: Sentence object with this word form.
        """
        self.stem = stem
        self.forms = {word_form: [sentence]}
        self.count += 1

    def __str__(self) -> str:
        return self.stem

    @property
    def articles(self) -> dict[Article, dict[str, list[Sentence]]]:
        """Returns dict of Articles with this word stem and all its forms
        and corresponding sentences.
        """
        articles = {}
        for form in self.forms:
            sentences = self.forms[form]
            for sentence in sentences:
                article = sentence.article
                if article not in articles:
                    articles[article] = {form: [sentence]}
                else:
                    if form in articles[article]:
                        if sentence not in articles[article][form]:
                            articles[article][form].append(sentence)
                    else:
                        articles[article][form] = [sentence]
        return articles

    def print_articles(self, part_of_speech: str = None):
        """Prints all articles, forms and sentences, where word of 
        part_of_speech occurs.
        
        If part_of_speech is None, prints all articles, forms and 
        sentences with this word.
        """
        if part_of_speech is not None:
            try:
                part_of_speech = PartOfSpeech[part_of_speech]
                self.__print_filtered_articles(part_of_speech)
                return
            except KeyError:
                print(f'Part of speech "{part_of_speech}" not found.')
                print('Printing all articles.')
        self.__print_all_articles()

    def __print_filtered_articles(self, part_of_speech: PartOfSpeech):
        """Prints articles, forms and sentences, where word of 
        part_of_speech occurs.
        """
        morph = MorphAnalyzer()
        filtered_forms = [form for form in self.forms.keys() if morph.parse(
            form)[0].tag.POS == part_of_speech.name]
        for article in self.articles:
            article_forms = [form for form in self.articles[article]
                             if form in filtered_forms]
            if article_forms:
                self.__print_article_info(article)
                self.__print_article_forms(article, forms=article_forms)

    def __print_all_articles(self):
        """Prints all articles, forms and sentences with this word."""
        for article in self.articles:
            self.__print_article_info(article)
            self.__print_article_forms(
                article,
                forms=list(self.articles[article].keys()))

    def __print_article_info(self, article: Article):
        """Prints single article title and authors."""
        print(f'Article "{article.title}"')
        print(f'Authors: ', end='')
        for author in article.authors:
            print(f'{author}', end=' ')
        print()

    def __print_article_forms(self, article: Article, forms: list[str]):
        """Prints forms of word present in article."""
        for form in forms:
            print(f'\n - {form}:')
            for i, sentence in enumerate(self.articles[article][form]):
                print(f'\t{i + 1}. {sentence.text}')
        print()


@dataclass
class Sentence:
    """Sentence.
    
    * article — Article object with this sentence.
    * text — preprocessed sentence string.
    * words — list of words in this sentence.
    """
    article: Article
    text: str
    words: list[Word] = field(default_factory=list)

    def __post_init__(self):
        self.__sentence_preprocessing()
        self.__split_sentence_into_words()

    def __sentence_preprocessing(self):
        """Remove special characters and extra whitespaces from sentence."""
        self.text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', self.text)
        self.text = re.sub(r'\s+', ' ', self.text)
        self.text = self.text.strip()

    def __split_sentence_into_words(self):
        """Split sentence into list of word stems."""
        words = word_tokenize(self.text)
        words = [word for word in words if word not in STOPWORDS]
        stemmer = SnowballStemmer('russian')
        for word in words:
            word = Word(stemmer.stem(word), word, self)
            if word not in self.words:
                self.words.append(word)


@dataclass
class Article:
    """Article.
    
    * authors — list of author names of article in format 'И.О. Фамилия'
    * title — article title (ALL CAPS).
    * text — preprocessed article text.
    * sentences — list of sentences in this article.
    """
    authors: list[str]
    title: str
    text: str
    sentences: list[Sentence] = field(default_factory=list)

    def __post_init__(self):
        start_time = time.time()
        self.__flatten_article_title()
        self.__text_preprocessing()
        self.__split_into_sentences()
        end_time = time.time()
        self.__log(end_time - start_time)

    def __hash__(self) -> int:
        return hash((self.title, tuple(self.authors)))

    def __flatten_article_title(self):
        """Remove newline characters and repeating whitespaces from 
        article titles.
        """
        self.title = re.sub(r'\n', '', self.title)
        self.title = re.sub(r'\s{2,}', ' ', self.title)
        self.title = self.title.strip()

    def __text_preprocessing(self):
        """Remove newline characters and 'рис. #' references."""
        self.text = self.text.lower()
        self.text = re.sub('\n', '', self.text)
        self.text = re.sub(r'рис\.\s?\d\.?', '', self.text)

    def __split_into_sentences(self):
        """Split article text into sentences."""
        sentences = sent_tokenize(self.text)
        for sentence in sentences:
            self.sentences.append(Sentence(self, sentence))

    def __log(self, processing_time: float):
        print(f'Article completed: {self.title} ({processing_time:.2f}s)')
        print(f'Number of sentences: {len(self.sentences)}')
        word_count = 0
        for sentence in self.sentences:
            word_count += len(sentence.words)
        print(f'Number of words after preprocessing: {word_count}\n')
