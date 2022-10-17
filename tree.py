from __future__ import annotations
from dataclasses import dataclass, field

from nltk.stem.snowball import SnowballStemmer

from datatypes import Article, Sentence, Word

stemmer = SnowballStemmer('russian')


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

    def search(self, word: str) -> list[Sentence]:
        """Search for every form of word using Word Tree.

        Returns list of sentences with this word.
        """
        if ' ' in word:
            return self.__search_by_phrase(word)
        stem = stemmer.stem(word)
        current_node = self.root
        for char in stem:
            if char in current_node.children:
                current_node = current_node.children[char]
            else:
                return []
        if current_node.word is None:
            return []
        sentences = []
        for form in current_node.word.forms:
            for sentence in current_node.word.forms[form]:
                sentences.append(sentence)
        return sentences

    def __search_by_phrase(self, phrase: str) -> list[Sentence]:
        """Search for every form of words in phrase using Word Tree.

        Return list of sentences with this phrase.
        """
        words = phrase.split(' ')
        result: list[set[Sentence]] = []
        for word in words:
            sentences = self.search(word)
            if not sentences:
                return []
            result.append(set(sentences))
        sentences_with_all_words = result[0].intersection(*result[1:])

        sentences = []
        for sentence in sentences_with_all_words:
            if self.__is_next_to_each_other(words, sentence):
                sentences.append(sentence)
        return sentences

    def __is_next_to_each_other(self, words: list[str],
                                sentence: Sentence) -> bool:
        """Returns True if words stand next to each other in sentence."""
        stems = [stemmer.stem(word) for word in words]
        sentence_words = sentence.text.split(' ')
        sentence_stems = [stemmer.stem(word) for word in sentence_words]

        for i in range(len(sentence_stems) - len(stems) + 1):
            if stems == sentence_stems[i:i + len(stems)]:
                return True
        return False
