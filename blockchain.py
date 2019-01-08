from datetime import datetime
import json
import hashlib
import calendar

class Blockchain():
    def __init__(self, current_node_url):
        self.obj = {
            "chain": [],
            "pending_bets": [],
            "network_nodes": [],
            "current_node_url": current_node_url
        }
        # Genesis block
        self.create_new_block(100, "0","0")
    
    def get_blockchain(self):
        return json.dumps(self.obj)

    def create_new_block(self, nonce, previous_hash, block_hash):
        d = datetime.utcnow()
        _obj = self.obj
        block = {
            "index": len(_obj["chain"]) + 1,
            "timestamp": calendar.timegm(d.utctimetuple()),
            "bets": _obj["pending_bets"], 
            "nonce": nonce,
            "hash": block_hash,
            "previous_block_hash": previous_hash
        }

        _obj["pending_bets"] = []
        _obj["chain"].append(block)

        return block

    def get_last_block(self):
        chain = self.obj["chain"]
        return chain[-1]

    def register_bet(self, player_name, match_id, team_one_score, team_two_score):
        bet = {
            "player": player_name,
            "match_id": match_id,
            "team_one": team_one_score, 
            "team_two": team_two_score
        }
        self.obj["pending_bets"].append(bet)
        return self.get_last_block()
    
    def hash_block(self, previous_hash, block_data, nonce):
        data_as_string = previous_hash + str(nonce) + json.dumps(block_data, separators=(',',':'))
        sha = hashlib.sha256(data_as_string.encode('utf-8')).hexdigest()
        return sha

    def proof_of_work(self, previous_hash, block_data):
        nonce = 0
        hashed_data = self.hash_block(previous_hash, block_data, nonce)
        while hashed_data[:4] != "0000":
            nonce = nonce + 1
            hashed_data = self.hash_block(previous_hash, block_data, nonce)
        
        return nonce

    def mine(self):
        last_block = self.get_last_block()
        previous_block_hash = last_block["hash"]
        block_data = {
            "bets": self.obj["pending_bets"],
            "index": last_block["index"] - 1
        }
        nonce = self.proof_of_work(previous_block_hash, block_data)
        block_hash = self.hash_block(previous_block_hash, block_data, nonce)
        new_block = self.create_new_block(nonce, previous_block_hash, block_hash)
        return new_block

    def receive_new_block(self, block):
        last_block = self.get_last_block()
        correct_hash = last_block["hash"] == block["previous_block_hash"]
        correct_index = last_block["index"] + 1 == block["index"]

        if correct_hash and correct_index:
            self.obj["chain"].append(block)
            self.obj["pending_bets"] = []
            return True
        
        return False

    def register_new_node(self, new_node):
        network_nodes = self.obj["network_nodes"]     
        if new_node != self.obj["current_node_url"] and not new_node in network_nodes:
            network_nodes.append(new_node)
        return network_nodes



    