import sys
import requests
import json
from flask import Flask, request, Response
from blockchain import Blockchain

app = Flask(__name__)
 
app_port = sys.argv[1]
current_node_url = "http://localhost:"+app_port
b = Blockchain(current_node_url)

@app.route('/blockchain')
def get_blockchain():
    return Response(b.get_blockchain(), status=200, content_type="application/json")

@app.route('/bet', methods=['POST'])
def register_bet():
    payload = request.get_json(force=True)
    b.register_bet(payload["playername"], payload["matchid"], payload["teamonescore"], payload["teamtwoscore"])
    return "Bet created and broadcast successfully."

@app.route('/bet/broadcast', methods=['POST'])
def register_and_broadcast_bet():
    payload = request.get_json(force=True)
    b.register_bet(payload["playername"], payload["matchid"], payload["teamonescore"], payload["teamtwoscore"])    
    network_nodes = b.obj["network_nodes"]
    # send new node to all other nodes
    for i in range(len(network_nodes)):
        network_node = network_nodes[i]
        payload_to_post = json.dumps(payload)
        requests.post(network_node+"/bet", data=payload_to_post)

    return "Bet created and broadcast successfully."


@app.route('/receive-new-block', methods=['POST'])
def receive_new_block():
    payload = request.get_json(force=True)
    new_block = payload["new_block"]
    result = b.receive_new_block(new_block)
    if result:
        return "New block received and accepted."
    return "New block rejected."

@app.route('/mine')
def mine():
    new_block = b.mine()
    network_nodes = b.obj["network_nodes"]
    # send new node to all other nodes
    for i in range(len(network_nodes)):
        network_node = network_nodes[i]
        payload_to_post = json.dumps({"new_block": new_block})
        requests.post(network_node+"/receive-new-block", data=payload_to_post)

    return "New block mined and broadcast successfully."

@app.route('/register-node', methods=['POST'])
def register_node():
    payload = request.get_json(force=True)
    b.register_new_node(payload["newnodeurl"])
    return "New node registered successfully successfully."

@app.route('/register-and-broadcast-node', methods=['POST'])
def register_and_broadcast_node():
    payload = request.get_json(force=True)
    new_node_url = payload["newnodeurl"]
    network_nodes = b.register_new_node(new_node_url)

    # send new node to all other nodes
    for i in range(len(network_nodes)):
        network_node = network_nodes[i]
        payload_to_post = json.dumps({ "newnodeurl": new_node_url })
        requests.post(network_node+"/register-node", data=payload_to_post)
    
    # send all nodes to new node
    payload_to_post = json.dumps({ "all_network_nodes": network_nodes + [current_node_url] })
    requests.post(new_node_url+"/register-nodes-bulk", data=payload_to_post)

    return "New node registered successfully successfully."

@app.route('/register-nodes-bulk', methods=['POST'])
def register_nodes_bulk():
    request_payload = request.get_json(force=True)
    all_network_nodes = request_payload["all_network_nodes"]
    print(request_payload)
    for i in range(len(all_network_nodes)):
        network_node = all_network_nodes[i]
        b.register_new_node(network_node)

    return "Bulk registration successful."

if __name__ == '__main__':   
    app.run(port=app_port)