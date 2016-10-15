import logging
from gensim.models.word2vec import LineSentence
from gensim.models import Phrases
import os


def train():
    sents = LineSentence(args.sents)

    global bigram, trigram
    bi_path = os.path.join(args.save_dir, bi_model)
    print 'Bigram: ', bi_path
    if os.path.exists(bi_path):
        bigram = Phrases.load(bi_path)
    else:
        bigram = Phrases(sents, min_count=args.min_count, threshold=args.bi_threshold)
        bigram.save(bi_path)

    tri_path = os.path.join(args.save_dir, bi_model + '_' + tri_model)
    print 'Trigram: ', tri_path
    trigram = Phrases(bigram[sents], min_count=args.min_count,
                      threshold=args.tri_threshold)
    trigram.save(tri_path)


if __name__ == '__main__':
    import argparse
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-sents', required=True)
    argparser.add_argument('-save_dir',
            default='/data/home/cul226/word2vec-gensim/')
    argparser.add_argument('-bi_model')
    argparser.add_argument('-tri_model')
    argparser.add_argument('-min_count', type=int, default=20)
    argparser.add_argument('-bi_threshold', type=int, default=150)
    argparser.add_argument('-tri_threshold', type=int, default=100)
    args = argparser.parse_args()
    print args

    bi_model = args.bi_model if args.bi_model else\
        'bigram_{}_{}'.format(args.min_count, args.bi_threshold)
    tri_model = args.tri_model if args.tri_model else\
        'trigram_{}_{}'.format(args.min_count, args.tri_threshold)
    train()

