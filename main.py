#!/usr/bin/env python
import websockets
import socket
import asyncio

config = {
	'ws_server': 'ws://miner.pr0gramm.com',
	'ws_port': '8044'
}

getshares = '{"type":"get_shares","params":{"user":"feuerrot"}}'

def proxy_tcp_to_ws(input):
	print("PROXY TCP -> WS")
	return input

def proxy_ws_to_tcp(input):
	print("PROXY WS -> TCP")
	return input

async def tcp_to_ws(reader, ws):
	while True:
		data = await reader.read(1024)
		try:
			if data:
				data = data.decode('ascii').strip()
			else:
				return
			if data:
				await ws.send(proxy_tcp_to_ws(data))
		except Exception as e:
			print(e)
			return

async def ws_to_tcp(writer, ws):
	while True:
		data = await ws.recv()
		try:
			if data:
				data = proxy_ws_to_tcp(data)
				data = data.encode('ascii')
				writer.write(data)
				await writer.drain()
			else:
				return
		except Exception as e:
			print(e)
			return

async def accept_client(client_reader, client_writer):
	print("accepted client: {}".format(client_writer.get_extra_info('peername')))
	ws = await websockets.connect("{}:{}".format(config['ws_server'], config['ws_port']))
	a = asyncio.ensure_future(tcp_to_ws(client_reader, ws))
	b = asyncio.ensure_future(ws_to_tcp(client_writer, ws))

def handle_client(client_reader, client_writer):
	print("got client")
	asyncio.ensure_future(accept_client(client_reader, client_writer))

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	f = asyncio.start_server(handle_client, host=None, port=1234)
	loop.run_until_complete(f)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
