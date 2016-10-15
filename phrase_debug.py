from gensim.models.word2vec import LineSentence
from gensim.models import Phrases


if __name__ == '__main__':
    import os
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-save_dir',
            default='/data/home/cul226/word2vec-gensim/')
    argparser.add_argument('-model', required=True)
    args = argparser.parse_args()

    sents = LineSentence('/data/home/cul226/wiki2vec/no_title/wiki_sents')
    bigram = Phrases.load(os.path.join(args.save_dir, args.model))

    cnt = 0
    with open(os.path.join(args.save_dir, args.model + '.tsv'), 'w') as f:
        for phrase, score in bigram.export_phrases(sents):
            f.write('{0}\t{1}\n'.format(phrase, score))
            if cnt % 10000 == 0:
                print cnt
            cnt += 1

