### Badly designed and overcomplicated
![Python Zen](https://i.imgur.com/PCcABJd.png "I like it though, I did great")

### PDF structure
Article has authors, title and main body. Split is based on this regular expression:
```python
(?:\d+\s?)\n   # page number (ignored)
((?:.+\n){1,5})    # authors and their universities
(?:УДК:?\s+[\d]+\.?[\d]+.+\n)  # УДК (ignored)
((?:.+\n){1,5}(?=Аннотация))   # article title
(?:Аннотация\.?:?)    # counts as first sentence so ignored
```
Each article usually look like this:
```
<end of previous article>
70 

И.О. Фамилия, И.О. Фамилия 
Университет, город 
УДК XXX.XXX 
MULTILINE 
TITLE 
OF THE 
ARTICLE 
Аннотация. <article main body> 
```

### Example of search result
![Search by phrase 'программный код'](https://i.imgur.com/p4uF30P.png "It's ugly in PS for some reason")

### Dependencies
```
pip install -r requirements.txt
```
Before running `main.py` move PDF with scholar articles in root directory and rename it to `file.pdf`.
