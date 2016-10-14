'''
The script will prepare the Wikipedia corpus in a format that can be processed
by word2vec tools.

If "add_wiki_title" is set:
Every Wikipedia link to an article within wiki is replaced by:
    WIKI/{link}

e.g:
[[ Barack Obama | B.O ]] is the president of [[USA]]

is transformed into:

    WIKI/Barack_Obama B.O is the president of WIKI/USA USA

Before running this script, we should use WikiExtractor to extract plaintext
from the original Wikipedia xml dump.
'''
import argparse
import os
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import multiprocessing
import urllib
import string


def repl_html_tag(m):
    word = m.group(1)
    return ' {} {}'.format(PLACEHOLDER,  word)


def get_wikis(sent):
    m = re.findall('<a href="(.+?)">.+?</a>', sent)
    ret = []
    for link in m:
        link = urllib.unquote(link)
        ret.append('WIKI/' + link[0].upper() + link[1:].replace(' ', '_'))
    return ret


def process_files(queue, files):
    pid = multiprocessing.current_process().pid
    output = '{}.{}'.format(args.output, pid)
    out = open(output, 'w')
    for k, f in enumerate(files):
        content = open(f).read()
        m = re.findall(('<doc id="(.+?)" url="(.+?)" title="(.+?)">\n'
                       '(.+?)</doc>'), content, re.S)
        for d in m:
            text = d[3]
            idx = text.find('\n\n')
            if idx != -1:
                text = text[idx+2:]
            text = text.strip().decode('utf8')
            if len(text) == 0:
                continue
            for line in text.split('\n'):
                sents = sent_tokenize(line)
                for sent in sents:
                    if args.add_wiki_title:
                        wikis = get_wikis(sent)
                        sent_no_html = re.sub('<a href=".+?">(.+?)</a>',
                                repl_html_tag,
                                sent.encode('utf8')).decode('utf8')
                    else:
                        sent_no_html = re.sub('<[^>]*>', '', sent)
                    wds = [wd for wd in word_tokenize(sent_no_html)
                            if wd not in punkts]
                    if len(wds) < MIN_SENT_LEN:
                        continue
                    if args.add_wiki_title:
                        wiki_idx = 0
                        for i, wd in enumerate(wds):
                            if wd == PLACEHOLDER:
                                wds[i] = wikis[wiki_idx]
                                wiki_idx += 1
                        assert(wiki_idx == len(wikis))
                    out.write(' '.join(wds).encode('utf8') + '\n')
        if k % 50 == 0:
            print 'pid:{}\t{}/{}'.format(pid, k, len(files))
        if args.debug:
            break
    queue.put(None)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-folder', required=True, help='path to Wikipedia
            extracted by WikiExtractor')
    argparser.add_argument('-output', required=True, help='output path')
    argparser.add_argument('-nproc', type=int, default=1, help='# processes')
    argparser.add_argument('--add_wiki_title', action='store_true',
                           help='whether to export Wiki title in the sentence')
    argparser.add_argument('--debug', action='store_true')
    args = argparser.parse_args()
    print args

    extract_folder = args.folder
    nproc = args.nproc

    PLACEHOLDER = 'AKAPLACEHOLDER'
    MIN_SENT_LEN = 5
    punkts = set(string.punctuation)
    punkts.add('``')
    punkts.add("''")

    cnt = 0
    fs = []
    for root, dirs, files in os.walk(extract_folder):
        for f in files:
            fs.append(os.path.join(root, f))
    print 'total {} files'.format(len(fs))
    arg_list = [[] for i in xrange(nproc)]
    for k, f in enumerate(fs):
        arg_list[k % nproc].append(f)

    queue = multiprocessing.Queue()
    procs = []
    for i in xrange(nproc):
        p = multiprocessing.Process(target=process_files, 
                                    args=(queue, arg_list[i]))
        procs.append(p)
        p.start()

    finished = 0
    while finished < nproc:
        r = queue.get()
        if r is None:
            finished += 1

    for p in procs:
        p.join()

