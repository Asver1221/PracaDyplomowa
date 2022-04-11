import os
import random

from flask import Blueprint, jsonify, request

from backend.models.blockchain import Blockchain
from backend.models.wallet import Wallet
from backend.models.transaction import Transaction
from backend.models.transaction_pool import TransactionPool
from backend.pubsub import PubSub

blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

BLOCKCHAIN = Blueprint('BLOCKCHAIN', __name__)

@BLOCKCHAIN.route('/', methods=['GET'])
def default_blockchain_route():
    return jsonify(blockchain.to_json())

@BLOCKCHAIN.route('/range', methods=['GET'])
# http://localhost:5000/blockchain/range?start=3&&end=6
def route_blockchain_range():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    return jsonify(blockchain.to_json()[::-1][start:end])

@BLOCKCHAIN.route('/length', methods=['GET'])
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

@BLOCKCHAIN.route('/mine')
def route_blockchain_mine():
    transaction_data = transaction_pool.transaction_data()
    transaction_data.append(Transaction.reward_transaction(wallet).to_json())
    blockchain.add_block(transaction_data)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.clear_blockchain_transactions(blockchain)

@BLOCKCHAIN.route('known-addresses', methods=['GET'])
def route_known_adresses():
    known_addresses = set()

    for block in blockchain.chain:
        for transaction in block.data:
            known_addresses.update(transaction['output'].keys())

    return jsonify(list(known_addresses))

if os.environ.get('SEED_DATA') == 'True':
    for i in range(10):
        blockchain.add_block([
            Transaction(Wallet(), Wallet().address, random.randint(5, 100)).to_json(),
            Transaction(Wallet(), Wallet().address, random.randint(5, 100)).to_json()
        ])
