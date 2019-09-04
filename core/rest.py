from flask_restful import Resource, reqparse
import core.config as config
import requests
import json

def satoshis(amount):
	return int(amount) / pow(10, 12)

class Node(object):
	@classmethod
	def getinfo(cls):
		try:
			return requests.get(config.endpoint + '/getinfo', timeout=2).json()
		except Exception:
			return None

	@classmethod
	def json_rpc(cls, method, params):
		try:
			payload = {
					'jsonrpc': '2.0',
					'id': config.rid,
					'method': method,
					'params': params
				}

			data = requests.post(config.endpoint + '/json_rpc', data=json.dumps(payload), timeout=2).json()
			if 'error' in data:
				return None
			
			return data['result']

		except Exception:
			return None

class GetInfo(Resource):
	def get(self):
		result = {'error': None, 'data': {}}
		data = Node.getinfo()

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'supply': float(data['already_generated_coins']),
				'hashrate': int(data['difficulty'] / 240),
				'min_fee': float(data['readable_tx_fee']),
				'reward': satoshis(data['last_block_reward']),
				'difficulty': data['difficulty'],
				'height': data['height'],
				'hash': data['top_block_hash'],
				'tx_count': data['tx_count'],
				'mempool': data['tx_pool_size']
			}

		return result

class BlockByHeight(Resource):
	def get(self, height):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('getblockheaderbyheight', {'height': height})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'height': data['block_header']['height'],
				'hash': data['block_header']['hash'],
				'reward': satoshis(data['block_header']['reward']),
				'prev_hash': data['block_header']['prev_hash'],
				'difficulty': data['block_header']['difficulty'],
				'orphan': data['block_header']['orphan_status'],
				'timestamp': data['block_header']['timestamp'],
				'nonce': data['block_header']['nonce'],
				'version': data['block_header']['major_version']
			}

		return result

class BlocksRange(Resource):
	def get(self, height):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('f_blocks_list_json', {'height': height})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'blocks': []
			}

			for block in data['blocks']:
				result['data']['blocks'].append({
						'height': block['height'],
						'hash': block['hash'],
						'difficulty': block['difficulty'],
						'size': block['cumul_size'],
						'min_fee': satoshis(block['min_tx_fee']),
						'timestamp': block['timestamp'],
						'tx_count': block['tx_count']
					})

		return result

class BlockHeader(Resource):
	def get(self, bhash):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('getblockheaderbyhash', {'hash': bhash})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'height': data['block_header']['height'],
				'hash': data['block_header']['hash'],
				'reward': satoshis(data['block_header']['reward']),
				'prev_hash': data['block_header']['prev_hash'],
				'difficulty': data['block_header']['difficulty'],
				'orphan': data['block_header']['orphan_status'],
				'timestamp': data['block_header']['timestamp'],
				'nonce': data['block_header']['nonce'],
				'version': data['block_header']['major_version']
			}

		return result

class BlockByHash(Resource):
	def get(self, bhash):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('f_block_json', {'hash': bhash})
		
		parser = reqparse.RequestParser()
		parser.add_argument('offset', type=int, default=0)
		args = parser.parse_args()

		if args['offset'] > 50:
			args['offset'] = 50

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'height': data['block']['height'],
				'hash': data['block']['hash'],
				'reward': satoshis(data['block']['baseReward']),
				'fees': satoshis(data['block']['totalFeeAmount']),
				'size': data['block']['blockSize'],
				'difficulty': data['block']['difficulty'],
				'version': data['block']['major_version'],
				'nonce': data['block']['nonce'],
				'orphan': data['block']['orphan_status'],
				'prev_hash': data['block']['prev_hash'],
				'timestamp': data['block']['timestamp'],
				'tx_count': len(data['block']['transactions']),
				'transactions': []
			}

			for transaction in data['block']['transactions'][args['offset']:args['offset'] + 10]:
				result['data']['transactions'].append({
						'hash': transaction['hash'],
						'size': transaction['size'],
						'amount': satoshis(transaction['amount_out']),
						'fee': satoshis(transaction['fee'])
					})

		return result

class TransactionInfo(Resource):
	def get(self, thash):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('k_transaction_details_by_hash', {'hash': thash})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'block': data['transaction']['blockHash'],
				'height': data['transaction']['blockIndex'],
				'hash': data['transaction']['hash'],
				'timestamp': data['transaction']['timestamp'],
				'unlock_time': data['transaction']['unlockTime'],
				'size': data['transaction']['size'],
				'mempool': not data['transaction']['inBlockchain'],
				'fee': satoshis(data['transaction']['fee']),
				'inputs_amount': satoshis(data['transaction']['totalInputsAmount']),
				'outputs_amount': satoshis(data['transaction']['totalOutputsAmount']),
				'coinbase': data['transaction']['totalInputsAmount'] == 0,
				'payment_id': data['transaction']['paymentId'],
				'signatures': data['transaction']['signatures'],
				'inputs': data['transaction']['inputs'],
				'outputs': data['transaction']['outputs'],
				'mixin': data['transaction']['mixin'],
				'public_key': data['transaction']['extra']['publicKey'],
				'nonce': data['transaction']['extra']['nonce'],
				'raw': data['transaction']['extra']['raw']
			}

		return result

class TransactionInfoPaymentId(Resource):
	def get(self, payid):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('k_transactions_by_payment_id', {'payment_id': payid})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'transactions': []
			}

			for transaction in data['transactions']:
				result['data']['transactions'].append({
						'hash': transaction['hash'],
						'size': transaction['size'],
						'amount': satoshis(transaction['amount_out']),
						'fee': satoshis(transaction['fee'])
					})

		return result

class MempoolInfo(Resource):
	def get(self):
		result = {'error': None, 'data': {}}
		data = Node.json_rpc('f_mempool_json', {})

		if data is None:
			result['error'] = 'Request failed'
		else:
			result['data'] = {
				'mempool': []
			}

			for transaction in data['mempool']:
				result['data']['mempool'].append({
						'hash': transaction['hash'],
						'size': transaction['size'],
						'amount': satoshis(transaction['amount_out']),
						'fee': satoshis(transaction['fee']),
						'received': transaction['receiveTime']
					})

		return result
