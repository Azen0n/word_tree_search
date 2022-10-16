from __future__ import annotations
from dataclasses import dataclass, field

from nltk.stem.snowball import SnowballStemmer
from pymorphy2 import MorphAnalyzer

from datatypes import Article, Word


@dataclass
class Node:
    """Tree Node.
    
    * char — character, Node base.
    * parent — parent Node (None if root).
    * children — char-Node dictionary of Node children.
    * word — tree leaf with stemmed word.
    """
    char: str
    parent: Node = None
    children: dict[str, Node] = field(default_factory=dict)
    word: Word = None


@dataclass
class WordTree:
    """Word Tree with characters as nodes.
    
    * articles — list of articles.
    * root — root Node.
    """
    articles: list[Article]
    root: Node = field(init=False)
    _words: dict[str, Word] = field(init=False)
    
    def __post_init__(self):
        self.root = Node('')
        self._words = Word.words
        self.__build()

    def __build(self):
        """Build Word Tree."""
        stems = list(sorted(list(Word.words.keys())))
        for stem in stems:
            current_node = self.root
            for char in stem:
                if char in current_node.children:
                    current_node = current_node.children[char]
                else:
                    new_node = Node(char, current_node)
                    current_node.children[char] = new_node
                    current_node = new_node
            current_node.word = self._words[stem]
    
    def traverse(self):
        """Print Word Tree nodes and words at the leaves using keyboard."""
        current_node = self.root
        print(f'Children of root:')
        for child in current_node.children.keys():
            print(child, end='  ')
        print()
        char = input('Enter char (up, exit): ')
        while char != 'exit':
            try:
                if char == 'up':
                    current_node = current_node.parent
                else:
                    current_node = current_node.children[char]
                print(f'Children of "{current_node.char}":')
                for child in current_node.children.keys():
                    print(child, end='  ')
                print()
                if not current_node.children:
                    print(f'Word stem in this node:  {current_node.word.stem}')
                    current_node.word.print_articles()
                char = input('Enter char (up, exit): ')
            except KeyError:
                char = input('Not found. Enter char: ')

    def search(self, word: str):
        """Search for every form of word using Word Tree.
        
        Returns None, all results is printed in console.
        """
        stemmer = SnowballStemmer('russian')
        morph = MorphAnalyzer()
        part_of_speech = morph.parse(word)[0].tag.POS
        stem = stemmer.stem(word)
        current_node = self.root
        for char in stem:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                print('Not found.')
                return
        if current_node.word is not None:
            current_node.word.print_articles(part_of_speech)
        else:
            print('Not found.')
            return
