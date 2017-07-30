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
	'defaultuser': 'feuerrot',
	'sharespersecond': 20
}

class Sync():
	def __init__(self):
		self.user = None
		self.login = False
		self.queue = asyncio.Queue()

def sharestostring(input):
	try:
		shares = int(input)
		seconds = shares / config['sharespersecond']
		days = int(seconds/(60*60*24))
		hours = (seconds - days*24*60*60)/60/60
		return "{} shares - {} days {:.2f} hours".format(shares, days, hours)
	except:
		return "{} shares".format(input)

async def proxy_tcp_to_ws(input, sync):
	try:
		j = json.loads(input)
		if j['id']:
			await sync.queue.put(j['id'])
		if j['method'] == 'login':
			if not j['params']['login'] == 'x':
				sync.user = j['params']['login']
		elif j['method'] == 'submit':
			rtn = {
				'type': 'submit',
				'params': {
					'user': sync.user or config['defaultuser'],
					'job_id': j['params']['job_id'],
					'nonce': j['params']['nonce'],
					'result': j['params']['result']
				}
			}
			print("T2W: submit job {} nonce {}".format(j['params']['job_id'], j['params']['nonce']))
			return json.dumps(rtn)
		return None
	except Exception as e:
		print("proxy_tcp_to_ws()")
		traceback.print_exc()

async def tcp_to_ws(reader, ws, sync):
	while True:
		data = await reader.read(1024)
		try:
			if data:
				data = data.decode('ascii').strip()
				#print("T2W: {}".format(data))
				data = await proxy_tcp_to_ws(data, sync)
				if data == None:
					continue
				#data += '\n'
				#print("T2W: {}".format(data))
				await ws.send(data)
			else:
				return
		except Exception as e:
			print("tcp_to_ws()")
			traceback.print_exc()
			return

async def proxy_ws_to_tcp(input, sync):
	try:
		j = json.loads(input)
		if j['type'] == 'job':
			if sync.login:
				rtn = {
					'jsonrpc': '2.0',
					'method': 'job',
					'params': {
						'blob': j['params']['blob'],
						'job_id': j['params']['job_id'],
						'target': j['params']['target']
					}
				}
			else:
				_id = await sync.queue.get()
				rtn = {
					'id': _id,
					'jsonrpc': '2.0',
					'error': None,
					'result': {
						'status': 'ok',
						'id': '000000000000000',
						'job': {
							'blob': j['params']['blob'],
							'job_id': j['params']['job_id'],
							'target': j['params']['target']
						}
					}
				}
				sync.login = True
			print('W2T: new job: {}'.format(j['params']['job_id']))
		elif j['type'] == 'job_accepted':
			print('W2T: job accepted - {}'.format(sharestostring(j['params']['shares'])))
			rtn = {
				"id": await sync.queue.get(),
				"jsonrpc": "2.0",
				"error": None,
				"result": {
					"status": "OK"
				}
			}
		else:
			return None
		return json.dumps(rtn).replace(' ','')
		
	except Exception as e:
		print("proxy_ws_to_tcp()")
		traceback.print_exc()

async def ws_to_tcp(writer, ws, sync):
	while True:
		data = await ws.recv()
		try:
			if data:
				#print("W2T: {}".format(data))
				data = await proxy_ws_to_tcp(data, sync)
				if data == None:
					continue
				data += '\n'
				#print("W2T: {}".format(data))
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
	sync = Sync()
	asyncio.ensure_future(tcp_to_ws(client_reader, ws, sync))
	asyncio.ensure_future(ws_to_tcp(client_writer, ws, sync))

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
