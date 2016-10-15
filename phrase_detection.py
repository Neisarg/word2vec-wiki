import logging
from gensim.models.word2vec import LineSentence
from gensim.models import Phrases
import os


def train():
    sents = LineSentence(args.sents)
    save_path = os.path.join(args.save_dir, save_model)
    print 'Save to:', save_path

    global bigram, trigram
    bigram = Phrases(sents, min_count=args.min_count, threshold=args.bi_threshold)
    bigram.save(save_model + '.bi')

    trigram = Phrases(bigram[sents], min_count=min_count,
                      threshold=args.tri_threshold)
    trigram.save(save_model + '.tri')


if __name__ == '__main__':
    import argparse
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-sents', required=True)
    argparser.add_argument('-save_dir',
            default='/data/home/cul226/word2vec-gensim/')
    argparser.add_argument('-save_model')
    argparser.add_argument('-min_count', type=int, default=20)
    argparser.add_argument('-bi_threshold', type=float, default=150.)
    argparser.add_argument('-tri_threshold', type=float, default=100.)
    args = argparser.parse_args()
    print args

    save_model = args.save_model if args.save_model else\
        'phrase_{}_{}_{}'.format(args.min_count, args.bi_threshold,
                                 args.tri_threshold)
    train()

