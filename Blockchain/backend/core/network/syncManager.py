from Blockchain.backend.core.network.connection import Node
from Blockchain.backend.core.database.database import BlockChainDB

class syncManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def spin_up_server(self):
        self.server = Node(self.host, self.port)
        self.server.start_server()
        print("Server started")
        print(f"[LISTENTING] at {self.host}:{self.port}")

    def start_download(self, port):
        lastBlock = BlockChainDB().last_block()

        if not lastBlock:
            lastBlockHeader = '00008364315921ba08f474ce57c5662c415ed343a8bdda20d54b0ba80efa688c'
        else:
            lastBlockHeader = lastBlock['blockHeader']['blockHash']
        
        startBlock = bytes.fromhex(lastBlockHeader)

