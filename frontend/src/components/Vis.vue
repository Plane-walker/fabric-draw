<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="info">
      <b-navbar-brand href="#">FabricDraw</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-button v-b-toggle.sidebar-variant size="sm" class="my-2 my-sm-0">Global Ope</b-button>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-button size="sm" class="my-2 my-sm-0 mx-sm-2" v-on:click="download()">Download File</b-button>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-button size="sm" class="my-2 my-sm-0 mx-sm-2" v-on:click="exportNet()">Export</b-button>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-form-file
            v-model="netFile"
            :state="Boolean(netFile)"
            placeholder="Choose a file or drop it here..."
            drop-placeholder="Drop file here..."
            size="sm"
          ></b-form-file>
        </b-navbar-nav>
        <b-navbar-nav>
          <b-button size="sm" class="my-2 my-sm-0 mx-sm-2" v-on:click="importNet()">Import</b-button>
        </b-navbar-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-form>
            <b-form-input size="sm" class="mr-sm-2" placeholder="Enter node label" autocomplete="off" v-model="searchNodeName"></b-form-input>
            <b-button size="sm" class="my-2 my-sm-0" v-on:click="searchNode()" type="submit">Search</b-button>
          </b-nav-form>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <b-sidebar id="sidebar-variant" title="Global Ope" bg-variant="light" shadow>
      <div class="px-3 py-2">
        <div class="my-2">
          <div v-b-toggle.collapse-1>
            <b-icon icon="plus-circle-fill" aria-hidden="true"></b-icon>
            Add Org
          </div>
          <b-collapse id="collapse-1" variant="light" class="mt-2">
            <b-card>
              <b-row class="my-1">
                <b-form-input v-model="org.domain" size="sm" class="mr-sm-2" placeholder="Enter base domain name"></b-form-input>
              </b-row>
              <b-row class="my-1">
                <b-form-input v-model="org.name" size="sm" class="mr-sm-2" placeholder="Enter org name"></b-form-input>
              </b-row>
              <b-row class="my-1">
                <b-form-input v-model="org.firstPeerName" size="sm" class="mr-sm-2" placeholder="Enter first peer name"></b-form-input>
              </b-row>
              <b-row class="my-1">
                <b-button size="sm" class="my-2 my-sm-0" v-on:click="newOrg()">Add</b-button>
              </b-row>
            </b-card>
          </b-collapse>
        </div>

        <div class="my-2">
          <div v-b-toggle.collapse-2>
            <b-icon icon="plus-circle-fill" aria-hidden="true"></b-icon>
            Add Orderer
          </div>
          <b-collapse id="collapse-2" variant="light" class="mt-2">
            <b-card>
              <b-row class="my-1">
                <b-form-input v-model="orderer.name" size="sm" class="mr-sm-2" placeholder="Enter orderer name"></b-form-input>
              </b-row>
              <b-row class="my-1">
                <b-button size="sm" class="my-2 my-sm-0" v-on:click="newOrderer()">Add</b-button>
              </b-row>
            </b-card>
          </b-collapse>
        </div>
      </div>
    </b-sidebar>
    <div id="visualization" class="vis-container m-auto"></div>
    <b-collapse id="collapse-3" v-model="visible" class="my-2">
      <b-card>
        <b-row class="my-1">
          <b-col md="1" offset-md="1">
            Change Domain: 
          </b-col>
          <b-col md="3">
            <b-form-input size="sm" v-model="peer.domain"></b-form-input>
          </b-col>
          <b-col md="1">
            <b-button size="sm" class="my-2 my-sm-0" v-on:click="changeDomain()">Chnage</b-button>
          </b-col>
        </b-row>
        <b-row class="my-1" v-if="showAddPeer">
          <b-col md="1" offset-md="1">
            New Peer: 
          </b-col>
          <b-col md="3">
            <b-form-input size="sm" v-model="peer.name" placeholder="Enter peer name"></b-form-input>
          </b-col>
          <b-col md="1">
            <b-button size="sm" class="my-2 my-sm-0" v-on:click="newPeer()">Add</b-button>
          </b-col>
        </b-row>
      </b-card>
    </b-collapse>
  </div>
</template>

<script>

export default {
  name: 'Vis',
  data () {
    return {
      peerIndex: 4,
      orgIndex: 2, 
      org: {
        domain: "test.com",
        name: "",
        firstPeerName: "",
        caName: "ca",
      },
      peer: {
        domain: "",
        name: "",
        parentPeer: "",
        orgIndex: "",
      },
      orderer: {
        name: "",
      },
      orgs: {
        0: {
          domain: "test.com",
          name: "orderer",
          CAID: 0,
          CAName: "ca",
          peerName: {
            1: "orderer",
          },
        },
        1: {
          domain: "test.com",
          name: "org1",
          CAID: 2,
          CAName: "ca",
          peerName: {
            3: "peer0",
          }
        }
      },
      nodes: {},
      edges: {},
      visible: false,
      showAddPeer: true,
      searchNodeName: "",
      netFile: null,
    }
  },
  methods: {
    newOrg() {
      this.orgs[this.orgIndex] = {
        domain: this.org.domain,
        name: this.org.name,
        CAID: this.peerIndex,
        CAName: this.org.caName,
        peerName: {}
      }
      this.nodes.add({
        id: this.peerIndex, 
        label: this.org.caName + '.' + this.org.name + '.' + this.org.domain,
        group: this.orgIndex,
      })
      this.peerIndex++
      this.addPeer(this.orgIndex, this.org.firstPeerName, [this.peerIndex - 1, 1])
      this.orgIndex++
      this.org.name = ""
      this.org.firstPeerName = ""
    },
    addPeer(org, name, parentPeers) {
      this.orgs[org]["peerName"][this.peerIndex] = name
      let peerLabel = ""
      if (org != 0) {
        peerLabel = name + '.' + this.orgs[org]["name"] + '.' + this.orgs[org]["domain"]
      } else {
        peerLabel = name + '.' + this.orgs[org]["domain"]
      }
      
      this.nodes.add({
        id: this.peerIndex, 
        label: peerLabel,
        group: org
      })
      for (let index = 0; index < parentPeers.length; index++) {
        this.edges.add({from: this.peerIndex, to: parentPeers[index]})
      }
      this.peerIndex++
    },
    newPeer() {
      this.addPeer(this.peer.orgIndex, this.peer.name, [this.peer.parentPeer])
      this.peer['name'] = ""
    },
    newOrderer() {
      this.addPeer(0, this.orderer.name, Object.keys(this.orgs[0]["peerName"]))
      this.orderer['name'] = ""
    },
    changeDomain() {
      this.orgs[this.peer.orgIndex]["domain"] = this.peer.domain
      let peerID = Object.keys(this.orgs[this.peer.orgIndex]["peerName"])
      if (this.peer.orgIndex == 0) {
        this.nodes.updateOnly({
          id: this.orgs[this.peer.orgIndex]["CAID"], 
          label: this.orgs[this.peer.orgIndex]["CAName"] + "." + this.peer.domain,
        })
        for (let index = 0; index < peerID.length; index++) {
          this.nodes.updateOnly({
            id: parseInt(peerID[index]), 
            label: this.orgs[this.peer.orgIndex]["peerName"][peerID[index]] + "." + this.peer.domain,
          })
        }
      } else {
        this.nodes.updateOnly({
          id: this.orgs[this.peer.orgIndex]["CAID"], 
          label: this.orgs[this.peer.orgIndex]["CAName"] + "." + this.orgs[this.peer.orgIndex]["name"] + "." + this.peer.domain,
        })
        for (let index = 0; index < peerID.length; index++) {
          this.nodes.updateOnly({
            id: parseInt(peerID[index]), 
            label: this.orgs[this.peer.orgIndex]["peerName"][peerID[index]] + "." + this.orgs[this.peer.orgIndex]["name"] + "." + this.peer.domain,
          })
        }
      }
    },
    selectShow(that, nodeID) {
      if (that.orgs[that.nodes.get(nodeID)['group']]["CAID"] != nodeID) {
        that.visible = true
        that.showAddPeer = true
        that.peer.parentPeer = nodeID
        that.peer.orgIndex = that.nodes.get(nodeID)['group']
        that.peer.domain = that.orgs[that.peer.orgIndex]["domain"]
        if (that.nodes.get(nodeID)['group'] == 0) {
          that.showAddPeer = false
        }
      }
      else {
        that.visible = false
      }
    },
    download() {
      let that = this
      this.$axios({
        method: 'POST',
        url: '/download',
        data: {
          jsonContent: JSON.stringify(that.orgs),
        },
        responseType: 'blob'
      })
      .then(response => {
        let link = document.createElement("a")
        link.href = window.URL.createObjectURL(new Blob([response.data]))
        link.target = "_blank"
        link.download = "fabricDraw.zip"
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      })
    },
    searchNode() {
      let that = this
      let items = this.nodes.get({
        filter: function (item) {
          return item.label == that.searchNodeName;
        }
      })
      if (items.length == 0) {
        return
      }
      this.network.selectNodes([items[0]['id']])
      that.selectShow(this, items[0]['id'])
    },
    exportNet() {
      let data = {
        orgs: this.orgs,
        nodes: this.nodes.get(),
        edges: this.edges.get(),
      }
      data = JSON.stringify(data)
      let link = document.createElement("a")
      link.href = window.URL.createObjectURL(new Blob([data], { type: "text/json" }))
      link.target = "_blank"
      link.download = "netjson.json"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      console.log(this.nodes.get())
    },
    importNet() {
      let that = this
      var reader = new FileReader()
      reader.readAsText(this.netFile)
      reader.onload = function (evt) {
          var fileString = evt.target.result
          let netData = JSON.parse(fileString)
          that.orgs = netData["orgs"]
          that.nodes.clear()
          that.edges.clear()
          that.nodes.add(netData["nodes"])
          that.edges.add(netData["edges"])
          console.log(netData["orgs"])
      }
    },
    create () {
      let visnetwork = this.$visnetwork
      let visdata = this.$visdata
      this.nodes = new visdata.DataSet([
        {
          id: 0, 
          label: "ca.test.com",
          group: 0,
        },
        {
          id: 1, 
          label: "orderer.test.com",
          group: 0,
        },
        {
          id: 2, 
          label: "ca.org1.test.com",
          group: 1,
        },
        {
          id: 3, 
          label: "peer0.org1.test.com",
          group: 1,
        },
      ])
      this.edges = new visdata.DataSet([
        {
          from: 1,
          to: 0,
        },
        {
          from: 3,
          to: 2,
        },
        {
          from: 3,
          to: 1,
        },
      ])
      var container = document.querySelector('#visualization')
      var data = {
          nodes: this.nodes,
          edges: this.edges
      }
      var options = {
        nodes: {
          shape: "dot",
          size: 16,
          font: {
            size: 16,
          },
          borderWidth: 2,
          shadow: true,
        },
        edges: {
          width: 2,
          shadow: true,
        },
      }
      this.network = new visnetwork.Network(container, data, options)
      const that = this
      this.network.on("click", function (params) {
        if(params.nodes.length == 0) {
          that.visible = false
        }
      })
      this.network.on("selectNode", function (params) {
        that.selectShow(that, params.nodes[0])
      })
    }
  },
  mounted () {
    this.create()
  }
}
</script>

<style scoped>
.vis-container {
  width: 960px;
  height: 540px;
};

</style>
