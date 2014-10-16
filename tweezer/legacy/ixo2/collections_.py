#!/usr/bin/env python
#-*- coding: utf-8 -*-

from collections import Mapping
from itertools import chain


###############################################################################
## Code from [StackOveflow](http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys)

same = lambda x:x  # identity function
add = lambda a,b:a+b
_tuple = lambda x:(x,)  # python actually has coercion, avoid it like so

def flatten_dictionary(dictionary, keyReducer=add, keyLift=_tuple, init=()):

    # semi-lazy: goes through all dicts but lazy over all keys
    # reduction is done in a fold-left manner, i.e. final key will be
    #     r((...r((r((r((init,k1)),k2)),k3))...kn))
    # >>> x = {
    #     'a':1,
    #     'b':2,
    #     'c':{
    #         'aa':11,
    #         'bb':22,
    #         'cc':{
    #             'aaa':111
    #         }
    #     }
    # }
    # >>> flattenDict(x)
    # {('c', 'aa'): 11, ('c', 'bb'): 22, ('b',): 2, ('a',): 1, ('c', 'cc', 'aaa'): 111}

    # >>> {'_'.join(k):v for k,v in flattenDict(x).items()}
    # {'a': 1, 'b': 2, 'c_aa': 11, 'c_bb': 22, 'c_cc_aaa': 111}

    # >>> flattenDict(x, keyReducer=lambda a,b:hash((a,b))%10000)
    # {9775: 22, 980: 2, 5717: 1, 2539: 111, 6229: 11}

    def _flattenIter(pairs, _keyAccum=init):
        atoms = ((k,v) for k,v in pairs if not isinstance(v, Mapping))
        submaps = ((k,v) for k,v in pairs if isinstance(v, Mapping))
        def compress(k):
            return keyReducer(_keyAccum, keyLift(k))
        return chain(
            (
                (compress(k),v) for k,v in atoms
            ),
            *[
                _flattenIter(submap.items(), compress(k))
                for k,submap in submaps
            ]
        )
    return dict(_flattenIter(dictionary.items()))
