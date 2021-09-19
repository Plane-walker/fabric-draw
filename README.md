# fabric-draw
## Data transmission format
{
  "groups": {
    "orderer.test.com": {
        "peers": ["peer0.org1.test.com"], 
        "blockchains": ["channel-1"]
    }, 
    "org1.test.com": {
        "leader_peers": ["peer0.org1.test.com","peer0.org2.test.com"], 
        "anchor_peers": [],
        "committing_peer": [],
        "endorsing_peers":[]
    }
  },
  "peers": {
    "peer0.org1.test.com": {
      "address": {"host": "1.1.1.1", "port": "7054", "sk": ""},
      "bootstrap": ["peer1.org1.test.com"],
      "type": "peer"
    }
  },
  "blockchains": {
    "channel-1": {
      "name": "first_channel"
    }
  }
}
