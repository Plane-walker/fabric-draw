# fabric-draw
## Data transmission format
```json 
{
  "groups": {
    "orderer.test.com": {
      "name": "orderer",
      "nodes": {
	    "ca": "ca.orderer.test.com",
	    "orderer": ["orderer0.orderer.test.com", "orderer1.orderer.test.com", "orderer2.orderer.test.com"]
	  },
      "blockchains": "fabric-1"
    }, 
    "org0.test.com": {
      "name": "org0",
      "nodes": {
        "ca": "ca.org0.test.com",
        "leader_peers": ["peer0.org0.test.com"], 
        "anchor_peers": ["peer0.org0.test.com"],
        "committing_peers": ["peer0.org0.test.com"],
        "endorsing_peers": ["peer0.org0.test.com"]
      },
	  "blockchains": "fabric-1",
    "channel": ["channel-1"]
    },
    "org1.test.com": {
      "name": "org1",
      "nodes": {
        "ca": "ca.org1.test.com",
        "leader_peers": ["peer0.org1.test.com"], 
        "anchor_peers": ["peer0.org1.test.com"],
        "committing_peers": ["peer0.org1.test.com"],
        "endorsing_peers": ["peer0.org1.test.com"]
      },
	  "blockchains": "fabric-1",
    "channel": ["channel-1"]
    },
    "org2.test.com": {
      "name": "org2",
      "nodes": {
        "ca": "ca.org2.test.com",
        "leader_peers": ["peer0.org2.test.com"], 
        "anchor_peers": ["peer0.org2.test.com"],
        "committing_peers": ["peer0.org2.test.com"],
        "endorsing_peers": ["peer0.org2.test.com"]
      },
	  "blockchains": "fabric-1",
    "channel": ["channel-1"]
    }
  },
  "nodes": {
    "ca.orderer.test.com": {
      "name": "ca",
      "address": {"host": "10.134.66.131", "port": "7054", "sk": ""},
      "type": ["ca"]
    },
    "orderer0.orderer.test.com": {
      "name": "orderer0",
      "address": {"host": "10.134.66.131", "port": "7050", "sk": ""},
      "type": ["orderer"]
    },
    "orderer1.orderer.test.com": {
      "name": "orderer1",
      "address": {"host": "10.134.119.134", "port": "7050", "sk": ""},
      "type": ["orderer"]
    },
    "orderer2.orderer.test.com": {
      "name": "orderer2",
      "address": {"host": "", "port": "7050", "sk": ""},
      "type": ["orderer"]
    },
    "ca.org0.test.com": {
      "name": "ca",
      "address": {"host": "10.134.66.131", "port": "7054", "sk": ""},
      "type": ["ca"]
    },
    "peer0.org0.test.com": {
      "name": "peer0",
      "address": {"host": "10.134.66.131", "port": "7051", "sk": ""},
      "bootstrap": ["127.0.0.1:7051"],
      "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
    },
    "ca.org1.test.com": {
      "name": "ca",
      "address": {"host": "10.134.119.134", "port": "7054", "sk": ""},
      "type": ["ca"]
    },
    "peer0.org1.test.com": {
      "name": "peer0",
      "address": {"host": "10.134.119.134", "port": "7051", "sk": ""},
      "bootstrap": ["127.0.0.1:7051"],
      "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
    },
    "ca.org2.test.com": {
      "name": "ca",
      "address": {"host": "", "port": "7054", "sk": ""},
      "type": ["ca"]
    },
    "peer0.org2.test.com": {
      "name": "peer0",
      "address": {"host": "", "port": "7051", "sk": ""},
      "bootstrap": ["127.0.0.1:7051"],
      "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
    },
  },
  "blockchains": {
    "fabric-1": {
      "channel-1": {
        "name": "FabricDraw"
      }
    }
  }
}
```

## atomic steps
### create org
### create peer
### docker compose
### mkdir
### build env
### edit host
### configtxgen
### docker swarm
