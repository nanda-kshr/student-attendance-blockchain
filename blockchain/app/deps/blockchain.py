from app.deps.block import Block
import json

class BlockChain:
    def __init__(self):
        self.chain = []
        self.index = 0

    def add_data(self, data):
        self.index += 1
        if self.chain:
            b = Block(data.copy(), self.chain[-1].hash_value, self.index)
            self.is_block_valid(b)
        else:
            b = Block(data.copy(), "0", self.index)
        self.chain.append(b)
        self.save_chain()

    def is_block_valid(self, b: Block):
        if self.chain:
            if b.previous_hash != self.chain[-1].hash_value:
                raise Exception("INVALID CHAIN LINK")
            if b.hash_value != b.calculate_hash():
                raise Exception("INVALID BLOCK hash_value")
        
        print("Block is Validated Successfully")
        
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].hash_value != self.chain[i].calculate_hash():
                raise Exception("INVALID CHAIN")
            if self.chain[i].previous_hash != self.chain[i-1].hash_value:
                raise Exception("INVALID CHAIN LINK")
        
        print("Chain is Validated Successfully")
            
    def break_the_chain(self):
        if len(self.chain) > 1:
            self.chain[1].data = "wrong data"
    
    def save_chain(self):
        with open("chain.json", 'w') as file:
            json.dump([i.to_dict() for i in self.chain ] , file)

    def initalize(self):
        try:
            with open("chain.json", "r") as blockchain_data_file:
                blockchain_data = json.load(blockchain_data_file)
            chain = []

            for i in blockchain_data:
                block = Block.from_json(i)
                chain.append(block)
                self.is_chain_valid()
            self.index = chain[-1].index
            self.chain = chain
        except Exception as e:
            print("File not found. Started a fresh BlockChain")




def test(b):
    data = {
        "StudentId": 0,
        "Name": "Ammu"
    }
    b.add_data(data)
    data["StudentId"] += 1
    b.add_data(data)
    data["StudentId"] += 1
    b.add_data(data)
    data["StudentId"] += 1
    # b.break_the_chain()
    b.add_data(data)
    data["StudentId"] += 1
    b.is_chain_valid()


