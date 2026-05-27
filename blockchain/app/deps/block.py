from datetime import datetime
import hashlib

class Block:

    def __init__(self, data=None, previous_hash="", index=0, timestamp = None, hash_value=None):
        self.data = dict(sorted(data.items())) or {}
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.previous_hash = previous_hash
        self.index = index
        self.hash_value = hash_value or self.calculate_hash()
        
    def calculate_hash(self):
        block_string = f"{self.previous_hash}{self.timestamp}{self.data}{self.index}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            "data": self.data,
            "previous_hash": self.previous_hash,
            "index": self.index,
            "timestamp": self.timestamp,
            "hash_value": self.hash_value
        }
    

    @classmethod
    def from_json(cls, json_data):
        return cls(
            data = json_data["data"],
            previous_hash = json_data["previous_hash"],
            index = json_data["index"],
            timestamp = json_data["timestamp"],
            hash_value = json_data["hash_value"]
        )
