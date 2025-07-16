import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Account from '../views/Account.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/account',
    name: 'Account',
    component: Account
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 