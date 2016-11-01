# -*- coding: utf-8 -*-

import glob
import os

from pynlpl.formats import folia

from utils import docx_to_raw, create_sentences

CORRECTION_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/corrections.xml'
POS_TAGSET = 'https://raw.githubusercontent.com/mhkuu/french-learner-corpus/master/config/pos.xml'


def process_folder(directory):
    for filename in glob.glob(os.path.join(directory, '*.docx')):
        print filename

        # Retrieve raw text
        raw = docx_to_raw(filename)

        # Replace apostrophes
        raw = raw.replace(u"`", u"'")
        raw = raw.replace(u"’", u"'")

        # Create the XML output
        create_xml(os.path.splitext(os.path.basename(filename))[0] + '-final', raw)


def create_xml(filename, raw):
    # Start the XML and declare the tagsets
    doc = folia.Document(id=filename)
    doc.declare(folia.Correction,
                CORRECTION_TAGSET,
                annotatortype=folia.AnnotatorType.MANUAL)
    doc.declare(folia.SyntacticUnit,
                POS_TAGSET,
                annotatortype=folia.AnnotatorType.MANUAL)
    doc.declare(folia.PosAnnotation,
                POS_TAGSET,
                annotator='Stanford POS Tagger',
                annotatortype=folia.AnnotatorType.AUTO)

    # Add the text
    text = doc.append(folia.Text)
    for paragraph in raw.splitlines():
        par = paragraph.strip()
        if par:  # skip empty paragraphs
            p = text.add(folia.Paragraph)

            create_sentences(p, par)

    doc.save('out/{}.xml'.format(filename))


if __name__ == '__main__':
    for subdir, _, _ in os.walk('in'):
        process_folder(subdir)
