// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import * as visnetwork from 'vis-network/peer/esm/vis-network'
import * as visdata from 'vis-data/peer/esm/vis-data'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.prototype.$axios = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'accept': 'application/json',
    'Content-Type': 'application/json',
  }
})

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)

Vue.prototype.$visnetwork = visnetwork
Vue.prototype.$visdata = visdata

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
