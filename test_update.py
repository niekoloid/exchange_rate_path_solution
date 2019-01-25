# -*- coding: utf-8 -*-
__author__ = 'Sun Sagong'

import pytest
from datetime import datetime
from graph import Graph

@pytest.mark.update
def test_update_case1():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')

    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
        
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD']
    
    assert edges ==     {'KRAKEN-BTC': ['KRAKEN-USD'], \
                         'KRAKEN-USD': ['KRAKEN-BTC']}
    
    assert weights == {('KRAKEN-BTC', 'KRAKEN-USD'): 1000.0, \
                       ('KRAKEN-USD', 'KRAKEN-BTC'): 0.0009}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD': datetime(2017, 11, 1, 9, 42, 23)}

@pytest.mark.update
def test_update_case2():
    G = Graph()
    
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')

    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['GDAX-BTC', 'GDAX-USD']
    
    assert edges ==     {'GDAX-BTC': ['GDAX-USD'], \
                         'GDAX-USD': ['GDAX-BTC']}
    
    assert weights == {('GDAX-BTC', 'GDAX-USD'): 1001.0, \
                       ('GDAX-USD', 'GDAX-BTC'): 0.0008}
    
    assert last_updates == {'GDAX-BTC->GDAX-USD': datetime(2017, 11, 1, 9, 43, 23)}
    
@pytest.mark.update
def test_update_case3_combined():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')

    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1000.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.0009, \
                       ('GDAX-BTC',     'GDAX-USD'):    1001.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.0008, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2017, 11, 1, 9, 42, 23), \
                              'GDAX-BTC->GDAX-USD':     datetime(2017, 11, 1, 9, 43, 23)}
    
@pytest.mark.update
def test_update_case4_older_updates_existing_pairs():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    
    G.update('2017-11-01T00:00:00+00:00 GDAX BTC USD 9999.0 0.1111')
    G.update('2017-11-01T00:11:11+00:00 KRAKEN BTC USD 1111.0 0.9999')

    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1000.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.0009, \
                       ('GDAX-BTC',     'GDAX-USD'):    1001.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.0008, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2017, 11, 1, 9, 42, 23), \
                              'GDAX-BTC->GDAX-USD':     datetime(2017, 11, 1, 9, 43, 23)}
    
@pytest.mark.update
def test_update_case5_newer_updates_existing_pairs():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    
    G.update('2017-11-01T11:11:11+00:00 GDAX BTC USD 9999.0 0.1111')
    G.update('2017-11-01T22:22:22+00:00 KRAKEN BTC USD 1111.0 0.9999')

    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1111.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.9999, \
                       ('GDAX-BTC',     'GDAX-USD'):    9999.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.1111, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2017, 11, 1, 22, 22, 22), \
                              'GDAX-BTC->GDAX-USD':     datetime(2017, 11, 1, 11, 11, 11)}
    
@pytest.mark.update
def test_update_case6_timezone_adjustment():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    
    G.update('2222-11-01T09:42:23-08:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2222-11-01T09:42:23+08:00 GDAX BTC USD 1001.0 0.0008')
    
    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1000.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.0009, \
                       ('GDAX-BTC',     'GDAX-USD'):    1001.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.0008, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2222, 11, 1, 1, 42, 23), \
                              'GDAX-BTC->GDAX-USD':     datetime(2222, 11, 1, 17, 42, 23)}

@pytest.mark.update
def test_update_case7_isolated_full_pairs():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    G.update('2017-11-01T09:44:23+00:00 XXXXX AAA BBB 9999.0 0.1111')
    
    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD', \
                         'XXXXX-AAA', 'XXXXX-BBB']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD'],\
                         'XXXXX-AAA':   ['XXXXX-BBB'],\
                         'XXXXX-BBB':   ['XXXXX-AAA']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1000.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.0009, \
                       ('GDAX-BTC',     'GDAX-USD'):    1001.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.0008, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0,\
                       ('XXXXX-AAA',    'XXXXX-BBB'):   9999.0,\
                       ('XXXXX-BBB',    'XXXXX-AAA'):   0.1111,}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2017, 11, 1, 9, 42, 23), \
                            'GDAX-BTC->GDAX-USD':       datetime(2017, 11, 1, 9, 43, 23),\
                            'XXXXX-AAA->XXXXX-BBB':     datetime(2017, 11, 1, 9, 44, 23)}
    
@pytest.mark.update
def test_update_case8_isolated_half_pair():
    G = Graph()
    
    G.update('2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    G.update('2017-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    G.update('2017-11-01T09:44:23+00:00 XXXXX BTC ZZZ 9999.0 0.1111')
    
    nodes = G.nodes
    edges = dict(G.edges)
    weights = G.weights
    last_updates = G.last_updates
    
    assert nodes ==     ['KRAKEN-BTC', 'KRAKEN-USD', 'GDAX-BTC', 'GDAX-USD', \
                         'XXXXX-BTC', 'XXXXX-ZZZ']
    
    assert edges ==     {'KRAKEN-BTC':  ['KRAKEN-USD', 'GDAX-BTC', 'XXXXX-BTC'], \
                         'KRAKEN-USD':  ['KRAKEN-BTC', 'GDAX-USD'], \
                         'GDAX-BTC':    ['GDAX-USD', 'KRAKEN-BTC', 'XXXXX-BTC'], \
                         'GDAX-USD':    ['GDAX-BTC', 'KRAKEN-USD'],\
                         'XXXXX-BTC':   ['XXXXX-ZZZ', 'KRAKEN-BTC', 'GDAX-BTC'],\
                         'XXXXX-ZZZ':   ['XXXXX-BTC']}
    
    assert weights == {('KRAKEN-BTC',   'KRAKEN-USD'):  1000.0, \
                       ('KRAKEN-USD',   'KRAKEN-BTC'):  0.0009, \
                       ('GDAX-BTC',     'GDAX-USD'):    1001.0, \
                       ('GDAX-USD',     'GDAX-BTC'):    0.0008, \
                       ('GDAX-USD',     'KRAKEN-USD'):  1.0, \
                       ('KRAKEN-USD',   'GDAX-USD'):    1.0, \
                       ('KRAKEN-BTC',   'GDAX-BTC'):    1.0, \
                       ('GDAX-BTC',     'KRAKEN-BTC'):  1.0,\
                       ('XXXXX-BTC',    'XXXXX-ZZZ'):   9999.0,\
                       ('XXXXX-ZZZ',    'XXXXX-BTC'):   0.1111,\
                       ('XXXXX-BTC',    'KRAKEN-BTC'):  1.0,\
                       ('KRAKEN-BTC',   'XXXXX-BTC'):   1.0,\
                       ('XXXXX-BTC',    'GDAX-BTC'):    1.0,\
                       ('GDAX-BTC',   'XXXXX-BTC'):     1.0}
    
    assert last_updates == {'KRAKEN-BTC->KRAKEN-USD':   datetime(2017, 11, 1, 9, 42, 23), \
                            'GDAX-BTC->GDAX-USD':       datetime(2017, 11, 1, 9, 43, 23),\
                            'XXXXX-BTC->XXXXX-ZZZ':     datetime(2017, 11, 1, 9, 44, 23)}