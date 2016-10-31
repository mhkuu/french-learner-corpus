# -*- coding: utf-8 -*-

import glob
import os

from bs4 import BeautifulSoup, element
from pynlpl.formats import folia

# from utils import SENTENCE_SPLITTER, STANFORD_TAGGER

CORRECTION_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/corrections.xml'
POS_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/pos.xml'


def get_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def process_folder(directory):
    for filename in glob.glob(os.path.join(directory, '*.txt')):
        print filename

        soup = BeautifulSoup(open(filename), 'html.parser')
        [x.extract() for x in soup.find_all(['voc', 'mor', 'synt', 'pht', 'ph_pause', 'unclear'])]
        [x.decompose() for x in soup.find_all(['int'])]
        for x in soup.find_all('global'):
            if x.has_attr('sequence'):
                x.name = 'paragraph'

        # Create the XML output
        create_xml(get_basename(filename), soup)


def create_xml(filename, soup):
    # Start the XML and declare the tagsets
    doc = folia.Document(id=filename)
    doc.declare(folia.PosAnnotation,
                POS_TAGSET,
                annotator='Stanford POS Tagger',
                annotatortype=folia.AnnotatorType.AUTO)

    # Add the text
    text = doc.append(folia.Text)
    for paragraph in soup.find_all('paragraph'):
        p = text.add(folia.Paragraph)

        # Split paragraphs into sentences
        for sentence in paragraph.find_all('sp'):
            s = p.append(folia.Sentence)

            # Tokenize and tag sentences using the Stanford POS tagger
            contents = ' '.join(sentence.contents)

            #tagged_words = STANFORD_TAGGER.tag([sentence])
            for word in contents.split():
                w = s.append(folia.Word, word)
            #    w.add(folia.PosAnnotation, cls=tag)

    doc.save('out/{}.xml'.format(filename))

if __name__ == '__main__':
    for subdir, _, _ in os.walk('in'):
        process_folder(subdir)
