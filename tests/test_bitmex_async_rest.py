import pytest

from bitmex_async_rest import BitMEXRestApi

@pytest.fixture
def testnet():
    return BitMEXRestApi('testnet')

async def test_throttle(testnet: BitMEXRestApi):
    for i in range(120):
        funding = await testnet.funding(count=1)
    assert i == 119