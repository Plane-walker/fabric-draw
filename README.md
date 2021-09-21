# fabric-draw
## Data transmission format
```json 
{
  "groups": {
    "orderer.test.com": {
      "nodes": ["peer0.org1.test.com"], 
      "blockchains": ["channel-1"]
    }, 
    "org1.test.com": {
      "nodes": {
        "leader_peers": ["peer0.org1.test.com"], 
        "anchor_peers": ["peer0.org2.test.com"],
        "committing_peers": [],
        "endorsing_peers":[],
      }
      "blockchains": ["channel-1"]
    }
  },
  "nodes": {
    "peer0.org1.test.com": {
      "address": {"host": "1.1.1.1", "port": "7054", "sk": "123adawdada"},
      "bootstrap": ["peer1.org1.test.com"],
      "type": ["leader_peer", "anchor_peer", "committing_peer"]
    }
  },
  "blockchains": {
    "channel-1": {
      "name": "TwoOrgsChannel"
    }
  }
}
```
