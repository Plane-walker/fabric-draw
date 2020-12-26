import Vue from 'vue'
import Router from 'vue-router'
import Vis from '@/components/Vis'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Vis',
      component: Vis
    }
  ]
})
