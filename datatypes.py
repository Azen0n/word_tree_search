from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypedDict
import re
import time

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.snowball import SnowballStemmer


class Words(TypedDict):
    """Singleton's internal word dictionary of word stem-class instance."""
    stem: str
    cls: Word


class WordSingleton(type):
    """Splitting sentences in words results in creating new object for 
    each word. This kind of singleton will return existing word with 
    new form-sentence record in it or create new word if it doesn't exist.
    """
    _words: Words = {}
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
        cls._words[stem]._count += 1


class WordFormSentence(TypedDict):
    """Word base is word stem, all other word forms kept in 
    form-sentences dictionary.
    """
    word_form: str
    sentences: list[Sentence]


@dataclass
class Word(metaclass=WordSingleton):
    """Word.
    
    * text — word base.
    * forms — dictionary with word forms and list of sentences 
    with these forms.
    * count — number of occurences of all forms with this base
    (across all articles).
    """
    _stem: str
    forms: WordFormSentence = field(init=False)
    _count: str = 0
    
    def __init__(self, stem: str, word_form: str, sentence: Sentence):
        """:param stem: word base (stemmed using nltk 
        SnowballStemmer).
        :param word_form: any form with base stem.
        :param sentence: Sentence object with this word form.
        """
        self._stem = stem
        self.forms = {word_form: [sentence]}
        self._count += 1
    
    def __str__(self) -> str:
        return self._stem
    
    @property
    def text(self) -> str:
        return self._stem
    
    @property
    def count(self) -> int:
        return self._count


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
        self.text = re.sub('рис\.\s?\d\.?', '', self.text)

    def __split_into_sentences(self):
        """Split article text into sentences."""
        sentences = sent_tokenize(self.text)
        for sentence in sentences:
            self.sentences.append(Sentence(self, sentence))

    def __log(self, time: float):
        print(f'Article completed: {self.title} ({time:.2f}s)')
        print(f'Number of sentences: {len(self.sentences)}')
        word_count = 0
        for sentence in self.sentences:
            word_count += len(sentence.words)
        print(f'Number of unique words: {word_count}\n')
