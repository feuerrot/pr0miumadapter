#!/usr/bin/env python
import websockets
import socket
import asyncio

config = {
	'ws_server': 'ws://miner.pr0gramm.com',
	'ws_port': '8044'
}

getshares = '{"type":"get_shares","params":{"user":"feuerrot"}}'

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

async def tcp_to_ws(reader, ws):
	print("tcp_to_ws")
	while True:
		print("tcp_to_ws while true")
		data = await reader.read(1024)
		try:
			data = data.decode('ascii').strip()
			print("tcp_to_ws got data")
			if not data:
				print("tcp_to_ws no data")
			else:
				await ws.send(data)
				print("tcp_to_ws sent data")
		except Exception as e:
			print(e)

async def ws_to_tcp(writer, ws):
	print("ws_to_tcp")
	while True:
		print("ws_to_tcp while true")
		data = await ws.recv()
		print("ws_to_tcp got data")
		writer.write(data.encode('ascii'))
		print("ws_to_tcp wrote data")
		await writer.drain()
		print("ws_to_tcp writer drain")

async def accept_client(client_reader, client_writer):
	print("accepted client")
	ws = await websockets.connect("{}:{}".format(config['ws_server'], config['ws_port']))
	print("ws connected")
	a = asyncio.ensure_future(tcp_to_ws(client_reader, ws))
	b = asyncio.ensure_future(ws_to_tcp(client_writer, ws))
	return (a,b)

def handle_client(client_reader, client_writer):
	print("got client")
	task = asyncio.ensure_future(accept_client(client_reader, client_writer))

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	f = asyncio.start_server(handle_client, host=None, port=1234)
	loop.run_until_complete(f)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
