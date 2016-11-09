import os

from nltk.data import load
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import StanfordTokenizer

from pattern.fr import parse, lemma

from pynlpl.formats import folia

from docx import Document

# open the sentence detector, add some missing abbreviations
SENTENCE_SPLITTER = load('tokenizers/punkt/french.pickle')
for abbrev in ['al', 'vs', 'vol', 'no', 'pp', u'\u00E9d', u'r\u00E9d', 'red']:
    SENTENCE_SPLITTER._params.abbrev_types.add(abbrev)


class MyStanfordPOSTagger(StanfordPOSTagger):
    """
    Extends the StanfordPosTagger with a custom command that calls the FrenchTokenizerFactory.
    """

    @property
    def _cmd(self):
        return ['edu.stanford.nlp.tagger.maxent.MaxentTagger',
                '-model', self._stanford_model, '-textFile',
                self._input_file_path, '-tokenizerFactory',
                'edu.stanford.nlp.international.french.process.FrenchTokenizer$FrenchTokenizerFactory',
                '-outputFormatOptions', 'keepEmptySentences']

os.environ['CLASSPATH'] = 'C:\stanford-postagger'
os.environ['JAVAHOME'] = 'C:\Program Files (x86)\Java\jre1.8.0_111'
STANFORD_TAGGER = MyStanfordPOSTagger(os.path.join('C:\stanford-postagger', 'models', 'french.tagger'))
STANFORD_TOKENIZER = StanfordTokenizer()


def docx_to_raw(filename):
    """Converts a .docx-file to raw text"""
    doc = Document(filename)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    # Return the text with one newline under each paragraph
    return '\n'.join(text)


def create_sentences(paragraph, text, tagger='stanford'):
    sentences = []

    # Split paragraphs into sentences using the PunktTokenizer
    for sentence in SENTENCE_SPLITTER.tokenize(text):
        s = paragraph.add(folia.Sentence)

        # Tokenize and tag sentences using the Stanford POS tagger or Pattern's tagger
        if tagger == 'stanford':
            tagged_words = STANFORD_TAGGER.tag([sentence])
        elif tagger == 'pattern':
            tagged_words = parse(sentence, chunks=False).split()
            tagged_words = sum(tagged_words, [])
        else:
            raise ValueError('Unknown tagger')

        for word, tag in tagged_words:
            w = s.add(folia.Word, word)
            w.add(folia.PosAnnotation, cls=tag)
            if tagger == 'pattern':
                w.add(folia.LemmaAnnotation, cls=lemma(word))

        sentences.append(s)

    return sentences

