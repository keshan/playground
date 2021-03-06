# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
import icu


def makePhonemeSet(s):
    pat = []
    for phoneme in s.split():
        if len(phoneme) == 1:
            pat.append(phoneme)
        else:
            pat.append('{%s}' % phoneme)
    print ' '.join(pat).encode('utf-8')
    result = icu.UnicodeSet()
    result.applyPattern('[%s]' % ' '.join(pat))
    return result


def match(s, unicodeset):
    return icu.UnicodeSet.span(
        unicodeset, s, icu.USetSpanCondition.SPAN_CONTAINED) == len(s)


WHITELISTED_SPECIAL_RULES = [
    "{\.} [:^Letter:] → ;",
    "\\u200D → ;"
]

def check(path, graphemes, phonemes):
    prefixes = {}
    num_lines = 0
    for line in codecs.open(path, 'r', 'utf-8'):
        num_lines += 1
        line = line.strip()
        if not line or line[0] in ':#$':
            continue
        assert line[-1] == ';'
        if line in WHITELISTED_SPECIAL_RULES:
            continue
        line = line.replace('\\.', '.').replace("''", "")
        graph, arrow, phon = line[:-1].split()
        assert arrow == '→'
        if graph[:-1] in prefixes:
            error = ('%s:%d: %s hidden by %s, defined on line %d' %
                     (path, num_lines, graph, graph[:-1], prefixes[graph[:-1]]))
            print(error.encode('utf-8'))
        else:
            prefixes[graph] = num_lines
        if not match(graph, graphemes):
            print(('%s:%d: Unexpected graphemes in "%s"' %
                  (path, num_lines, line)).encode('utf-8'))
        if not match(phon, phonemes):
            print(('%s:%d: Unexpected phonemes in "%s"' %
                   (path, num_lines, line)).encode('utf-8'))

            
def regtest(translit_name, graphemes, phonemes):
    rules = codecs.open('%s.txt' % translit_name, 'r', 'utf-8').read()
    translit = icu.Transliterator.createFromRules(
        translit_name, rules, icu.UTransDirection.FORWARD)
    num_lines = 0
    path = 'test-%s.txt' % translit_name
    for line in codecs.open(path, 'r', 'utf-8'):
        num_lines += 1
        graph, expected_ipa = line.strip().split('\t')
        if not match(graph, graphemes):
            print(('%s:%d: Unexpected graphemes in "%s"' %
                  (path, num_lines, graph)).encode('utf-8'))
        if not match(expected_ipa, phonemes):
            print(('%s:%d: Unexpected phonemes in "%s"' %
                   (path, num_lines, expected_ipa)).encode('utf-8'))
        actual_ipa = translit.transliterate(graph)
        if actual_ipa != expected_ipa:
            print(('%s:%d: Expected "%s" but got "%s" for "%s"' %
                   (path, num_lines, expected_ipa, actual_ipa, graph)).encode('utf-8'))
