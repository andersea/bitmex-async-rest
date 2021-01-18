from base64 import b64encode
import math
from uuid import uuid4

import anyio
import asks
import orjson

from . import __version__ as VERSION

from .auth import APIKeyAuthWithExpires

class BitMEXRestApi:
    def __init__(self, network, api_key=None, api_secret=None, timeout=7):
        if network not in ('mainnet', 'testnet'):
            raise ValueError('network argument must be either \'mainnet\' or \'testnet\'')

        self.api_key = api_key
        self.api_secret = api_secret
        self._throttle_delay_until = 0

        # Prepare HTTPS session
        self.session = asks.Session(
            base_location='https://www.bitmex.com' if network == 'mainnet' else 'https://testnet.bitmex.com',
            endpoint='/api/v1',
            headers={
                'user-agent': 'bitmex-trio-rest-api-' + VERSION,
                'content-type': 'application/json',
                'accept': 'application/json',
            },
            connections=2)

        self.timeout = timeout

    async def instrument(self, symbol, filter=None, start=0, count=100, reverse=False, start_time=None, end_time=None):
        query = {
            'symbol': symbol,
            'start': start,
            'count': count,
        }
        if reverse:
            query['reverse'] = 'true'
        if filter:
            query['filter'] = orjson.dumps(filter).decode('utf8')
        if start_time:
            query['startTime'] = start_time
        if end_time:
            query['endTime'] = end_time
        return await self._request(path='/instrument', query=query, verb='GET')

    async def instrument_active(self):
        return await self._request(path='/instrument/active')
    
    async def execution(self, symbol=None, filter=None, start=0, count=100, reverse=False, start_time=None, end_time=None):
        query = {
            'start': start,
            'count': count,
        }
        if symbol:
            query['symbol'] = symbol
        if filter:
            query['filter'] = orjson.dumps(filter).decode('utf8')
        if reverse:
            query['reverse'] = 'true'
        if start_time:
            query['startTime'] = start_time
        if end_time:
            query['endTime'] = end_time

        return await self._request(path='/execution', query=query, verb='GET')

    async def trade_history(self, symbol, filter=None, start=0, count=100, reverse=False, start_time=None, end_time=None):
        query = {
            'symbol': symbol,
            'start': start,
            'count': count,
        }
        if filter:
            query['filter'] = orjson.dumps(filter).decode('utf8')
        if reverse:
            query['reverse'] = 'true'
        if start_time:
            query['startTime'] = start_time
        if end_time:
            query['endTime'] = end_time

        return await self._request(path='/execution/tradeHistory', query=query, verb='GET')

    async def funding(self, symbol=None, start=0, count=100, reverse=False, start_time=None, end_time=None):
        query = {
            'start': start,
            'count': count,
        }
        if symbol:
            query['symbol'] = symbol
        if reverse:
            query['reverse'] = 'true'
        if start_time:
            query['startTime'] = start_time
        if end_time:
            query['endTime'] = end_time

        return await self._request(path='/funding', query=query, verb='GET')

    async def open_orders(self, symbol):
        query = {
            'symbol': symbol,
            'filter': orjson.dumps({'open': True}).decode('utf8')
        }
        return await self._request(path='/order', query=query, verb='GET')

    async def order(self, symbol, quantity, *, price=None, side=None, order_type=None, exec_inst=None, post_only=False, orderid_prefix='', text=None):
        query = {
            'symbol': symbol,
            'orderQty': quantity
        }
        if price is not None:
            query['price'] = price
        if side is not None:
            query['side'] = side
        if order_type is not None:
            query['ordType'] = order_type
        if exec_inst is not None:
            query['execInst'] = exec_inst
        elif post_only:
            query['execInst'] = 'ParticipateDoNotInitiate'
        if orderid_prefix:
            query['clOrdID'] = orderid_prefix + '-' + b64encode(uuid4().bytes).decode('utf8').rstrip('=\n')
        else:
            query['clOrdID'] = b64encode(uuid4().bytes).decode('utf8').rstrip('=\n')
        if text is not None:
            query['text'] = text
        return await self._request(path='/order', postdict=query, verb='POST')

    async def order_bulk_amend(self, orders):
        return await self._request(path='/order/bulk', postdict={'orders': orders}, verb='PUT')

    async def order_bulk_create(self, orders, orderid_prefix='', post_only=False):
        for order in orders:
            orderid = b64encode(uuid4().bytes).decode('utf8').rstrip('=\n')
            if orderid_prefix:
                orderid = orderid_prefix + '-' + orderid
            order['clOrdID'] = orderid
            if post_only:
                order['execInst'] = 'ParticipateDoNotInitiate'
        return await self._request(path='/order/bulk', postdict={'orders': orders}, verb='POST')

    async def order_delete(self, order):
        return await self._request(path='/order', postdict=order, verb='DELETE')

    async def order_delete_bulk(self, orders):
        return await self._request(path='/order', postdict={'orderID': [o['orderID'] for o in orders]}, verb='DELETE')

    async def order_cancel_all_after(self, milliseconds):
        """Cancel all open orders after timeout. Dead mans switch."""
        return await self._request(path='/order/cancelAllAfter', postdict={'timeout': milliseconds}, verb='POST')

    async def position(self, symbol):
        pos = await self._request(
            path='/position',
            query={'filter': orjson.dumps({'symbol': symbol}).decode('utf8')}
        )
        if not pos:
            # No position found; stub it
            return {'avgCostPrice': 0, 'avgEntryPrice': 0, 'currentQty': 0, 'symbol': symbol, '_stub': True}
        return pos[0]

    async def trade_bucketed(
            self,
            symbol, bin_size, start=0, count=500, *,
            partial=False, reverse=False,
            start_time=None, end_time=None
        ):
        query = {
            'symbol': symbol,
            'binSize': bin_size,
            'start': start,
            'count': count,
        }
        if partial:
            query['partial'] = 'true'
        if reverse:
            query['reverse'] = 'true'
        if start_time is not None:
            query['startTime'] = start_time
        if end_time is not None:
            query['endTime'] = end_time

        return await self._request(path='/trade/bucketed', query=query)

    async def user_wallet_history(self, count=1000, start=0):
        return await self._request(path='/user/walletHistory', query={
            'currency': 'XBt',
            'start': start,
            'count': count,
        })

    async def _request(self, *, path, query=None, postdict=None, timeout=None, verb=None):
        """Send a request to BitMEX Servers."""
        if timeout is None:
            timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        # Auth: API Key/Secret
        auth = None
        if self.api_key is not None and self.api_secret is not None:
            auth = APIKeyAuthWithExpires(self.api_key, self.api_secret)

        await self._throttle()
        response = await self.session.request(verb, path=path, connection_timeout=timeout, json=postdict, auth=auth, params=query)
        await self._set_throttle(response)
        # Make non-200s throw
        response.raise_for_status()
        return response.json()
    
    async def _set_throttle(self, response):
        remaining = int(response.headers['x-ratelimit-remaining'])
        if remaining == 0:
            self._throttle_delay_until = await anyio.current_time() + 5
        else:
            self._throttle_delay_until = await anyio.current_time() + max(0, math.sqrt(10/remaining) - 0.2 * remaining)

    async def _throttle(self):
        await anyio.sleep(max(0, self._throttle_delay_until - await anyio.current_time()))
