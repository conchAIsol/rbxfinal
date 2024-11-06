from geckoterminal_api import AsyncGeckoTerminalAPI
import websockets
import aiohttp
from aiohttp import web
import asyncio

class CombinedServer:
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/', self.handle_http)
        self.app.router.add_get('/ws', self.handle_websocket)
        self.active_websockets = set()

    async def cleanup(self, app):
        for ws in self.active_websockets:
            await ws.close(code=WSCloseCode.GOING_AWAY, message="shutdown")
        self.active_websockets.clear()

    async def handle_http(self, request):
        return web.FileResponse('./index.html')
    
    async def handle_websocket(self, request):
        print('handling')
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.active_websockets.add(ws)


        try:
            async with aiohttp.ClientSession() as session:
                gt = AsyncGeckoTerminalAPI()

                mcap = await gt.network_token(network="solana", address="CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump", include="market_cap_usd")
                marketcap = mcap['data']['attributes']['market_cap_usd']
                marketcap_float = float(marketcap)

                finalmcap = (marketcap_float)
                print('marketcap:', str(finalmcap))
                await ws.send_str(str(finalmcap))
        finally:
            self.active_websockets.remove(ws)
            await ws.close()


        
                                                             
        


async def server():
    server = CombinedServer()
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

    print('server started')
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(server())
