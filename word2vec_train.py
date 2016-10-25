import logging
from gensim.models.word2vec import LineSentence
from gensim.models import Phrases
from gensim.models import Word2Vec
import os


def train():
    sents = LineSentence(args.sents)
    model = Word2Vec(sents, size=300, min_count=args.min_count,
                     sg=1, workers=args.nproc, iter=10, sample=1e-4)
    model.init_sims(replace=True)

    # save model
    model.save(os.path.join(args.save_dir, args.gensim_model))
    # save w2v
    model.save_word2vec_format(
            os.path.join(args.save_dir, args.w2v_model), binary=True)


if __name__ == '__main__':
    import argparse
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-sents', required=True)
    argparser.add_argument('-save_dir',
            default='/data/home/cul226/word2vec-gensim/')
    argparser.add_argument('-gensim_model', required=True)
    argparser.add_argument('-w2v_model', required=True)
    argparser.add_argument('-min_count', type=int, default=20)
    argparser.add_argument('-nproc', type=int, default=16)
    args = argparser.parse_args()
    print args
    train()
