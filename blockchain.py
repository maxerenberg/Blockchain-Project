# CUTC Case Competition: Multi-Party Aggregation on the Blockchain
# this project was adapted from the following articles written by Gerald Nash:
# https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b
# https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d

import hashlib
import datetime
import json
from flask import Flask
from flask import request 

class Block:
    def __init__(self, index, timestamp, data, prev_hash, proof, hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data 
        self.prev_hash = prev_hash 
        self.proof = proof
        self.hash = hash

def genesis_block():
    return Block(0, datetime.datetime.now(), [], '0', 0, '0')

def create_tx(id, date, desc, debit, credit):  # can add a digital signature if desired
    return json.dumps({'id':id, 'date':date, 'description':desc, 
                       'debit':debit, 'credit':credit})

def next_block(last_block, data, proof, hash):
    return Block(last_block.index + 1, datetime.datetime.now(), 
                 data, last_block.hash, proof, hash)

blockchain = [genesis_block()]
node = Flask(__name__)
node_tx = []
zeros = '00' # can add more as desired
peer_nodes = []

def proof_of_work(data):
    inc = 1
    sha = hashlib.sha256()
    sha.update((data + str(inc)).encode('utf-8'))
    while not sha.hexdigest().startswith(zeros):
        inc += 1
        sha.update((data + str(inc)).encode('utf-8'))
    return (inc, sha.hexdigest())
    
miner_address = 'miner-address'

@node.route('/mine', methods=['GET'])
def mine():
    # can add a reward to the miner for finding the proof; not needed here
    txn_lst = node_tx.copy()
    del node_tx[:]
    last_block = blockchain[len(blockchain)-1]
    result = proof_of_work(str(txn_lst) + last_block.prev_hash)
    proof = result[0]
    hash = result[1]
    mined_block = next_block(last_block, txn_lst, proof, hash)
    blockchain.append(mined_block)
    return json.dumps({'index':mined_block.index,
                       'timestamp':str(mined_block.timestamp),
                       'data':txn_lst,
                       'hash':hash})

def find_new_chains():
    other_chains = []
    for node_url in peer_nodes: # need to know the peer nodes beforehand
        chain = requests.get(node_url + '/blocks').content
        chain = json.loads(chain)
        other_chains.append(chain)
    return other_chains

def consensus():
    global blockchain
    other_chains = find_new_chains()
    longest = blockchain
    for chain in other_chains:
        if len(chain) > len(longest):
            longest = chain            
    blockchain = longest

@node.route('/txion', methods=['POST'])
def transaction():
    if request.method == 'POST':
        new_txion = request.get_json()
        node_tx.append(new_txion)
        print(new_txion)
        return 'Transaction successfully submitted.'

@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain = blockchain.copy()
    for i in range(len(chain)):
        block = {'index':chain[i].index,
                 'timestamp':str(chain[i].timestamp),
                 'data':chain[i].data,
                 'hash':chain[i].hash}
        chain[i] = block
    return json.dumps(chain)
      
node.run()
