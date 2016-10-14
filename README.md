# word2vec-wiki
Generate word/phrase embedding using Wikipedia articles.

This is a documentation (**for my own reference**) on generating word/phrase embedding from Wikipedia articles.

### 1 - Download latest Wiki dump
This can be found at https://dumps.wikimedia.org/enwiki/. Specifically, we need `pages-articles.xml.bz2`.

### 2 - Extract plaintext from Wikitext
[WikiExtractor.py][extract] is used.

```
$ python WikiExtractor.py -l -ns 0 --no-templates -o [output_folder] --processes 16 pages-articles.xml.bz2
```
In the command above, `-l` preserves links; `-ns 0` only accepts Wikipedia pages in namespace 0, which are main articles rather than categories or other types.

[extract]: <https://github.com/attardi/wikiextractor>

### 3 - Prepare training corpus for word2vec tools
Extract sentences from Wikipedia pages into the following format: one sentence = one line; words already preprocessed and separated by whitespace.

```
python2.7 wiki2vec_corpus.py -h
usage: wiki2vec_corpus.py [-h] -folder FOLDER -output OUTPUT [-nproc NPROC]
                          [--add_wiki_title] [--debug]

optional arguments:
  -h, --help        show this help message and exit
  -folder FOLDER    path to Wikipedia extracted by WikiExtractor
  -output OUTPUT    output path
  -nproc NPROC      # processes
  --add_wiki_title  whether to export Wiki title in the sentence
  --debug
```

**Note**: when `--add_wiki_title` is set, Wikipeida title is preserved in addition to the anchor text.

Every Wikipedia link to an article within wiki is replaced by WIKI/{link}.
```
e.g:
[[ Barack Obama | B.O ]] is the president of [[USA]]
is transformed into:
    WIKI/Barack_Obama B.O is the president of WIKI/USA USA
```

