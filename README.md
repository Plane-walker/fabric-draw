# fabric-draw
## Data transmission format
```json 
{
  "groups": {
    "orderer.test.com": {
      "nodes": {
	    "ca": "ca.orderer.test.com",
	    "orderer": ["peer0.org1.test.com"]
	  },
      "blockchains": "fabric-1"
    }, 
    "org1.test.com": {
      "nodes": {
        "ca": "ca.org1.test.com",
        "leader_peers": ["peer0.org1.test.com"], 
        "anchor_peers": ["peer0.org2.test.com"],
        "committing_peers": [],
        "endorsing_peers":[]
      },
	  "blockchains": "fabric-1",
    "channel": ["channel-1"]
    }
  },
  "nodes": {
    "peer0.org1.test.com": {
      "name": "peer0",
      "org_name": "org1",
      "address": {"host": "1.1.1.1", "port": "7054", "sk": "123adawdada"},
      "bootstrap": ["peer1.org1.test.com"],
      "type": ["leader_peer", "anchor_peer", "committing_peer"]
    },
    "ca.org1.test.com": {
      "name": "ca",
      "org_name": "org1",
      "address": {"host": "1.1.1.1", "port": "7054", "sk": "123adawdada"},
      "type": ["ca_peer"]
    }
  },
  "blockchains": {
    "fabric-1": {
      "channel-1": {
        "name": "TwoOrgsChannel"
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
