# -*- coding: utf-8 -*-
__author__ = 'Sun Sagong'

import pytest
from graph import Graph

testdata = [
            # src and dst are identical - not likely happen
            ("EXCHANGE_RATE_REQUEST KRAKEN BTC KRAKEN BTC", None, None),
            ("EXCHANGE_RATE_REQUEST KRAKEN USD KRAKEN USD", None, None),
            ("EXCHANGE_RATE_REQUEST GDAX BTC GDAX BTC",     None, None),
            ("EXCHANGE_RATE_REQUEST GDAX USD GDAX USD",     None, None),
            
            # different exchanges but same ccy pairs - no arbitrage opporunity
            ("EXCHANGE_RATE_REQUEST KRAKEN BTC GDAX BTC",   1.0,
             ['KRAKEN-BTC', 'GDAX-BTC']),
            ("EXCHANGE_RATE_REQUEST KRAKEN USD GDAX USD",   1.0,
             ['KRAKEN-USD', 'GDAX-USD']),
            ("EXCHANGE_RATE_REQUEST GDAX BTC KRAKEN BTC",   1.0,
             ['GDAX-BTC', 'KRAKEN-BTC']),
            ("EXCHANGE_RATE_REQUEST GDAX USD KRAKEN USD",   1.0,
             ['GDAX-USD', 'KRAKEN-USD']),

            # crypto ccy -> fiat - TenX's business case
            ("EXCHANGE_RATE_REQUEST KRAKEN BTC KRAKEN USD", 1001.0,
             ['KRAKEN-BTC', 'GDAX-BTC', 'GDAX-USD', 'KRAKEN-USD']),
            ("EXCHANGE_RATE_REQUEST KRAKEN BTC GDAX USD",   1001.0,
             ['KRAKEN-BTC', 'GDAX-BTC', 'GDAX-USD']),
            ("EXCHANGE_RATE_REQUEST GDAX BTC KRAKEN USD",   1001.0,
             ['GDAX-BTC', 'GDAX-USD', 'KRAKEN-USD']),
            ("EXCHANGE_RATE_REQUEST GDAX BTC GDAX USD",     1001.0,
             ['GDAX-BTC', 'GDAX-USD']),

            # fiat -> crypto ccy
            ("EXCHANGE_RATE_REQUEST KRAKEN USD KRAKEN BTC", 0.0009,
             ['KRAKEN-USD', 'KRAKEN-BTC']),
            ("EXCHANGE_RATE_REQUEST KRAKEN USD GDAX BTC",   0.0009,
             ['KRAKEN-USD', 'KRAKEN-BTC', 'GDAX-BTC']),            
            ("EXCHANGE_RATE_REQUEST GDAX USD KRAKEN BTC",   0.0009,
             ['GDAX-USD', 'KRAKEN-USD', 'KRAKEN-BTC']),
            ("EXCHANGE_RATE_REQUEST GDAX USD GDAX BTC",     0.0009,
             ['GDAX-USD', 'KRAKEN-USD', 'KRAKEN-BTC', 'GDAX-BTC']),
            
            # special case -requested node does not exist in the graph
            ("EXCHANGE_RATE_REQUEST AAAAA YYY BBBBB ZZZ",     None, None),
            
        ]


def initialize_graph(): 
    G = Graph()
    
    upds = []
    upds.append('2020-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009')
    upds.append('2020-11-01T09:43:23+00:00 GDAX BTC USD 1001.0 0.0008')
    
    for u in upds:
        G.update(u)
    
    return G

@pytest.mark.parametrize("req, rate_expected, path_expected", testdata)
def test_respond_cases(req, rate_expected, path_expected):
    G = initialize_graph()
        
    response, rate, path = G.respond(req)
    
    assert rate_expected == rate
    assert path_expected == path

@pytest.mark.respond
def test_respond_special_case_isolated_node():
    G = initialize_graph()

    # additional update to add isolated nodes
    G.update("2020-11-01T09:43:23+00:00 XXXXX AAA BBB 1000.0 0.001")
    
    request = 'EXCHANGE_RATE_REQUEST XXXXX AAA KRAKEN BTC'
    response, rate, path = G.respond(request)
    
    expected  = None
    rate_expected = None
    path_expected = None
    
    assert expected == response
    assert rate_expected == rate
    assert path_expected == path
    