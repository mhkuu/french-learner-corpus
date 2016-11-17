# -*- coding: utf-8 -*-

import glob
import os

from bs4 import BeautifulSoup
from pynlpl.formats import folia

from utils import create_sentences

CORRECTION_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/corrections.xml'
POS_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/pos.xml'


def get_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def process_folder(directory):
    for filename in glob.glob(os.path.join(directory, '*.txt')):
        print filename

        with open(filename, 'r') as f:
            contents = f.read()
            # Rename the global tags with a sequence attribute
            contents = contents.replace('<global sequence=', '</paragraph><paragraph sequence=')

            soup = BeautifulSoup(contents, 'html.parser')

            # Remove/unwrap unwanted tags
            [x.decompose() for x in soup.find_all(['int', 'contour_fall', 'contour_rise'])]
            [x.unwrap() for x in soup.find_all(['voc', 'mor', 'synt', 'pht', 'ph_pause', 'ph_long', 'unclear', 'prag', 'into', 'ii'])]

            # Create the XML output
            create_xml(get_basename(filename), soup)


def create_xml(filename, soup):
    # Start the XML and declare the tagsets
    doc = folia.Document(id=filename)
    doc.declare(folia.PosAnnotation,
                POS_TAGSET,
                annotator='Stanford POS Tagger',
                annotatortype=folia.AnnotatorType.AUTO)

    text = doc.append(folia.Text)

    # Add the metadata
    for metadata in soup.find_all('global'):
        for key, value in metadata.attrs.items():
            text.add(folia.Feature, subset=key, cls=value)

    # Add the text
    for paragraph in soup.find_all('paragraph'):
        p = text.add(folia.Paragraph)

        # Split paragraphs into sentences
        for sentence in paragraph.find_all('sp'):
            # Fetch the contents
            try:
                contents = ' '.join(sentence.contents)
            except TypeError:
                print sentence.contents

            # Create the FoLiA sentences
            sentences = create_sentences(p, contents, 'stanford')

            # Add speaker data
            for s in sentences:
                s.add(folia.Feature, subset='speaker', cls=sentence['who'])

    doc.save('out/{}.xml'.format(filename))

if __name__ == '__main__':
    for subdir, _, _ in os.walk('in'):
        process_folder(subdir)
