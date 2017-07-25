#!/usr/bin/env python
import websockets
import socket
import asyncio
import json
import traceback
import time

config = {
	'ws_server': 'ws://miner.pr0gramm.com',
	'ws_port': '8044',
	'user': 'feuerrot'
}

def proxy_tcp_to_ws(input):
	try:
		j = json.loads(input)
		if j['method'] == 'submit':
			return '{{"type":"submit","params":{{"user":"feuerrot","job_id":"{}","nonce":"{}","result":"{}"}}}}'.format(j['params']['job_id'], j['params']['nonce'], j['params']['result'])
			print("TCP2WS: submit job {} nonce {}".format(j['params']['job_id'], j['params']['nonce']))
	except Exception as e:
		print("proxy_tcp_to_ws()")
		print(e)

async def tcp_to_ws(reader, ws):
	while True:
		data = await reader.read(1024)
		try:
			if data:
				data = data.decode('ascii').strip()
				#print("TCP2WS: {}".format(data))
				data = proxy_tcp_to_ws(data)
				if data == None:
					continue
				#data += '\n'
				#print("TCP2WS: {}".format(data))
				await ws.send(data)
			else:
				return
		except Exception as e:
			print("tcp_to_ws()")
			traceback.print_exc()
			return

def proxy_ws_to_tcp(input, state):
	try:
		j = json.loads(input)
		if j['type'] == 'job':
			rtn = {
				'jsonrpc': '2.0',
				'method': 'job',
				'params': {
					'blob': j['params']['blob'],
					'job_id': j['params']['job_id'],
					'target': j['params']['target']
				}
			}
			print('WS2TCP: new job: {}'.format(rtn['params']['job_id']))
		elif j['type'] == 'job_accepted':
			print('WS2TCP: job accepted - {}'.format(j['params']['shares']))
			rtn = {
				"id": 1,
				"jsonrpc": "2.0",
				"error": None,
				"result": {
					"status": "OK"
				}
			}
		else:
			rtn = None
		if rtn != None:
			return json.dumps(rtn).replace(' ',''), state
		else:
			return None, state
	except Exception as e:
		print("proxy_ws_to_tcp()")
		print(e)

async def ws_to_tcp(writer, ws):
	state = {
		'login': False,
	}
	while True:
		data = await ws.recv()
		try:
			if data:
				#print("WS2TCP: {}".format(data))
				(data, state) = proxy_ws_to_tcp(data, state)
				if data == None:
					continue
				data += '\n'
				#print("WS2TCP: {}".format(data))
				data = data.encode('ascii')
				writer.write(data)
				await writer.drain()
			else:
				return
		except Exception as e:
			print("ws_to_tcp()")
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
