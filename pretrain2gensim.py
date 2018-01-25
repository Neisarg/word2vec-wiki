if __name__ == '__main__':
    from gensim.models import KeyedVectors
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-w2v', required=True)
    argparser.add_argument('-output', required=True)
    argparser.add_argument('--binary', action='store_true')
    args = argparser.parse_args()
    print args
    # load pretrained model
    model = KeyedVectors.load_word2vec_format(args.w2v, binary=args.binary,
            unicode_errors='ignore')

    model.init_sims(replace=True)

    model.save(args.output)
