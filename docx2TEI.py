# -*- coding: utf-8 -*-

from datetime import date
import glob
import os
import re
from string import Template
import sys

import lxml.etree as etree

from utils import docx_to_raw, SENTENCE_SPLITTER, STANFORD_TAGGER, STANFORD_TOKENIZER


def process_folder(directory):
    print os.path.join(directory, '*.docx')
    for filename in glob.glob(os.path.join(directory, '*.docx')):

        raw = docx_to_raw(filename)

        # move guillemets back before the dot instead of after it
        raw = re.sub(u'\.[ \u00A0]*(\u00BB)', '\g<1>.', raw)
        # move year references before the end of the sentence
        raw = re.sub(u'\.[ \u00A0]*(\[[0-9]+\])', ' \g<1>.', raw)
        # replace right single quotation marks with normal apostrophes
        raw = raw.replace(u'\u2019', '\'')

        name = os.path.splitext(os.path.basename(filename))[0].decode(sys.getfilesystemencoding())
        print name

        xml = create_xml(name, raw)

        # write to output
        with open('out/' + name + '.xml', 'wb') as out:
            # open the XML template
            with open('template.xml', 'rb') as templ:
                template = Template(templ.read())
                today = date.today()
                output = template.substitute(title='test', year=today.year, date=today, sub=xml)
                out.write(output)


def create_xml(name, raw):
    # start the XML
    body = etree.Element('body')
    div = etree.Element('div')
    div.set('type', 'text')
    div.set('id', name)
    # TODO: mark headers?!
    # add paragraphs and sentences to the XML-format (with div as root)
    sentencenr = 1
    for i, paragraph in enumerate(raw.splitlines(), start=1):
        par = paragraph.strip()
        if par:  # skip empty paragraphs
            p = etree.Element('p')
            p.set('id', str(i))

            for j, sentence in enumerate(SENTENCE_SPLITTER.tokenize(par), start=1):
                s = etree.Element('s')
                s.set('n', str(i) + '.' + str(j))
                print sentence

                words = STANFORD_TOKENIZER.tokenize(sentence)
                tagged_words = STANFORD_TAGGER.tag(words)
                for k, (word, tag) in enumerate(tagged_words, start=1):
                    w = etree.Element('w')
                    w.text = word
                    w.set('id', str(i) + '.' + str(j) + '.' + str(k))
                    w.set('pos', tag)
                    s.append(w)

                p.append(s)

            div.append(p)
    body.append(div)
    xml = etree.tostring(body, pretty_print=True)
    return xml


if __name__ == '__main__':
    for subdir, _, _ in os.walk('in'):
        process_folder(subdir)
