# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 18:34:00 2018

@author: karma
"""
from utils import load_processed_corpus, tageojeol_to_tuple
from hangle import decompose, compose, moum_begin, moum_end, jaum_begin, jaum_end, kor_begin, kor_end
import glob

def is_all_complete_hangle(eojeol):
    for char in eojeol:
        if not (kor_begin <= ord(char) <= kor_end):
            return False
    return True

def to_lr(e, w, t):
    tag = t[0][0]
    i = 0
    for i_, ti in enumerate(t):
        if t[0][0] == 'N' and ti[0] == 'V':
            break
        if t[0][0] == 'V' and (ti == 'ETN' and len(w[i_]) == 1 and jaum_begin <= ord(w[i_][0]) <= jaum_end):
            tag = 'N'
            break
        if not (ti[0] == 'N' or ti == 'XSN' or ti[:2] == 'VV' or ti[:2] == 'VA' or ti == 'XR'):
            break
        i = i_
    lw = e[:len(''.join(w[:i+1]))]
    r = e[len(lw):]
    
    # 아빤 = 아빠/N + ㄴ/J
    # 갈꺼야 = 가/V + ㄹ/E + 꺼야/E
    if (t[i][0] == 'N' or t[i][0] == 'V') and (jaum_begin <= ord(w[i+1][0]) <= jaum_end):
        last_l = decompose(lw[-1])
        l0 = lw[:-1] + compose(last_l[0], last_l[1], ' ')
        return lw, r, tag, l0

    # 가? = 가/V + ㅏ/E + ?/S
    # 먹었어 = 먹/V + 었어/E
    return lw, r, tag.replace('X','N'), ''.join(w[:i+1])

def is_compound_noun(t):
    if len(t) <= 1:
        return False
    n_count = len([ti for ti in t if ti[0] == 'N' or ti == 'XSN'])
    if len(t) == n_count:
        return True
    if n_count <= 1:
        return False
    if t[0][0] == 'N' and [-1][0] == 'N':
        return True
        
def print_tolr(args):
    print('L=%s, R=%s, tag=%s, L(원형)=%s' % args)
    
refinement_corpus = glob.glob('../refinement/*')

with open('../db/lrdb.csv', 'w', encoding='utf-8') as f:
    f.write('%s\n' % '\t'.join(['eojeol', 'l', 'r', 'tag', 'lstemmed']))
    for fname in refinement_corpus:
        texts, texttags = load_processed_corpus(fname)
        for text, tag in zip(texts, texttags):
            for eojeol, eojeoltag in zip(text.split(), tag.split()):
                if not is_all_complete_hangle(eojeol):
                    continue
                    
                try:
                    w, t = tageojeol_to_tuple(eojeoltag)
                except:
                    continue
                
                if len(t) <= 1:
                    continue
                if (t[0][0] != 'N' and t[0][0] != 'V'):
                    continue
                if is_compound_noun(t):
                    continue

                try:
                    l, r, y, l0 = to_lr(eojeol, w, t)
                    f.write('%s\n' % '\t'.join([eojeol, l, r, y, l0]))
                except:
                    continue