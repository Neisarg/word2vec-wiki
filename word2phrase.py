import logging
from gensim.models.word2vec import LineSentence
from gensim.models import Phrases
import os


if __name__ == '__main__':
    import argparse
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-sents', required=True)
    argparser.add_argument('-save_dir',
            default='/data/home/cul226/word2vec-gensim/')
    argparser.add_argument('-bi_model', default='bigram_20_100')
    argparser.add_argument('-tri_model')
    args = argparser.parse_args()
    print args

    sents = LineSentence(args.sents)

    bi_path = os.path.join(args.save_dir, args.bi_model)
    print 'Bigram: ', bi_path
    bigram = Phrases.load(bi_path)
    output = args.sents + '.phrase'

    cnt = 0
    with open(output, 'w') as out:
        for sent in bigram[sents]:
            cnt += 1
            out.write(' '.join(sent).encode('utf8') + '\n')
            if cnt % 10000 == 0:
                print cnt

