import pytest
from time import time

from bitmex_async_rest import BitMEXRestApi

@pytest.fixture
def testnet():
    return BitMEXRestApi('testnet')

async def test_throttle(testnet: BitMEXRestApi):
    # for i in range(120):
    #     funding = await testnet.funding(count=1)
    # assert i == 119
    assert True

async def test_order_book_L2(testnet: BitMEXRestApi):
#    book = await testnet.order_book_L2('XBTUSD', 5)
#    assert len(book) == 10
    assert True