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


import os
import re
import urllib
import string
import HTMLParser
import multiprocessing
from nltk.tokenize import sent_tokenize, word_tokenize


def repl_html_tag(m):
    return ' ' + PLACEHOLDER + ' '


def accept_tokens(sent):
    wds = [wd for wd in word_tokenize(sent)
           if not args.no_punct or wd not in puncts]
    return wds


def extract_sents(wiki_doc, html_parser=None):
    results = []
    assert isinstance(wiki_doc, str)
    link_regex = '<a href="(.+?)">(.+?)</a>([a-zA-Z-]*)'
    if args.add_wiki_title:
        m = re.findall(link_regex, wiki_doc)
        wikis, anchors = [], []
        for match in m:
            try:
                # There are links to sites outside of Wikipedia
                # in the 2017.3 dump. The regex matching above will also
                # match these cases. Need to handle them separately.
                if re.match('^https?%3A', match[0]):
                    #match[0].startswith('http%3A'):
                    wikis.append('')
                    anchors.append(match[1] + match[2])
                else:
                    wiki = urllib.unquote(match[0])
                    wiki = urllib.unquote(wiki)     # to handle cases %2528, %2529
                    wiki = html_parser.unescape(wiki.decode('utf8'))
                    wiki = 'WIKI/' + wiki[0].upper() + wiki[1:].replace(' ', '_')
                    wikis.append(wiki)
                    anchors.append(match[1] + match[2])
            except:
                print(match[0])
        wiki_doc = re.sub(link_regex, repl_html_tag, wiki_doc)
    else:
        wiki_doc = re.sub('<[^>]*>', '', wiki_doc)

    wiki_idx = 0
    wiki_doc = wiki_doc.decode('utf8')
    for line in wiki_doc.split('\n'):
        sents = sent_tokenize(line)
        for sent in sents:
            wds = accept_tokens(sent)
            if args.add_wiki_title:
                for i, wd in enumerate(wds):
                    if wd == PLACEHOLDER:
                        anchor = anchors[wiki_idx]
                        anchor_split = word_tokenize(anchor.decode('utf8'))
                        if wikis[wiki_idx]:
                            if args.keep_anchor:
                                new_wd = wikis[wiki_idx] + ' ' + ' '.join(anchor_split)
                            else:
                                new_wd = wikis[wiki_idx]
                        else:
                            new_wd = ' '.join(anchor_split)
                        wds[i] = new_wd
                        wiki_idx += 1
            if len(wds) < MIN_SENT_LEN:
                continue
            sent = ' '.join(wds).encode('utf8')
            if args.lower:
                sent = sent.lower()
            results.append(sent)
    if args.add_wiki_title:
        assert(wiki_idx == len(wikis))
    return results


def process_files(queue, files):
    pid = multiprocessing.current_process().pid
    html_parser = HTMLParser.HTMLParser()

    output = os.path.join(
        output_folder, '{}.{}'.format(args.output_prefix, pid))
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
            text = text.strip()
            if len(text) == 0:
                continue

            sents = extract_sents(text, html_parser=html_parser)
            for sent in sents:
                assert isinstance(sent, str)
                out.write(sent + '\n')
        if k % 50 == 0:
            print 'pid:{}\t{}/{}'.format(pid, k, len(files))
        if args.debug:
            break
    queue.put(None)


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-folder', required=True,
        help='path to Wikipedia extracted by WikiExtractor')
    argparser.add_argument(
        '-output_folder', required=True, help='folder to save outpus')
    argparser.add_argument('-output_prefix', default='out', help='output prefix')
    argparser.add_argument('-nproc', type=int, default=1, help='# processes')
    argparser.add_argument('--add_wiki_title', action='store_true',
        help='whether to export Wiki title in the sentence')
    argparser.add_argument('--keep_anchor', action='store_true',
        help='if export wiki title, whether to keep anchor text')
    argparser.add_argument('--no_punct', action='store_true',
            help='whether to remove punctuations')
    argparser.add_argument('--lower', action='store_true',
            help='lower case')
    argparser.add_argument('--debug', action='store_true')
    args = argparser.parse_args()
    print args

    extract_folder = args.folder
    nproc = args.nproc
    output_folder = args.output_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    PLACEHOLDER = 'AKAPLACEHOLDER'
    MIN_SENT_LEN = 5
    puncts = set(string.punctuation)
    puncts.add('``')
    puncts.add("''")

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
