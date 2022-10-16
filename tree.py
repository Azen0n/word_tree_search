from __future__ import annotations
from dataclasses import dataclass, field

from nltk.stem.snowball import SnowballStemmer

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
        print('Enter char from list to traverse over tree.\n'
              ' - up to move to parent node\n'
              ' - exit to leave from traverse mode')
        self.__print_node_children(current_node)
        char = input('Enter char: ')
        while char != 'exit':
            if char == 'up':
                if current_node.parent is None:
                    print('At root node.')
                else:
                    current_node = current_node.parent
            elif char in current_node.children:
                current_node = current_node.children[char]
                self.__print_node_children(current_node)
                if not current_node.children:
                    print(f'Word stem in this node: {current_node.word.stem}')
                    current_node.word.print_articles()
                char = input('Enter char (up, exit): ')
            else:
                print('Not found.')
                char = input('Enter char (up, exit): ')
        print()

    def __print_node_children(self, node: Node):
        """Prints characters of node children."""
        print(f'Children of "{node.char}":')
        for child in node.children.keys():
            print(child, end='  ')
        print()

    def search(self, word: str) -> Word | None:
        """Search for every form of word using Word Tree.
        
        Returns Word or None if not found.
        """
        stemmer = SnowballStemmer('russian')
        stem = stemmer.stem(word)
        current_node = self.root
        for char in stem:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                return None
        return current_node.word
