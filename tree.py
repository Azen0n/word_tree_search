from __future__ import annotations
from dataclasses import dataclass, field

from datatypes import Article, Word, Words


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
    _words: Words = field(init=False)
    
    def __post_init__(self):
        self.root = Node('')
        self._words = Word._words
        self.__build()
        
    
    def __build(self):
        """Build Word Tree."""
        stems = list(sorted(list(Word._words.keys())))
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
                    print((f'Children not found. Word stem in this node:'
                           f'{current_node.word.text}'))
                char = input('Enter char (up, exit): ')
            except:
                char = input('Not found. Try again: ')
