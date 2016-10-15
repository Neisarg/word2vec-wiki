from gensim.models.word2vec import LineSentence
from gensim.models import Phrases


if __name__ == '__main__':
    sents = LineSentence('/data/home/cul226/wiki2vec/no_title/wiki_sents')
    bigram = Phrases.load('/data/home/cul226/word2vec-gensim/phrase.bi')

    cnt = 0
    with open('/data/home/cul226/word2vec-gensim/score.tsv', 'w') as f:
        for phrase, score in bigram.export_phrases(sents):
            f.write('{0}\t{1}\n'.format(phrase, score))
            if cnt % 10000 == 0:
                print cnt
            cnt += 1

