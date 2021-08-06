import Vue from 'vue'

import MarqueeText from 'vue-marquee-text-component' // Marquee: Lib for background moving line
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue' // Bootstrap
import 'bootstrap/dist/css/bootstrap.css' // Bootstrap
import 'bootstrap-vue/dist/bootstrap-vue.css' // Bootstrap
import Dropdown from 'vue-simple-search-dropdown' // Custom Vue dropdown with search

import router from './router'
import App from './App.vue'


Vue.config.productionTip = false

Vue.component('marquee-text', MarqueeText)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.component('Dropdown', Dropdown)

new Vue({
    router,
    render: h => h(App)
}).$mount('#app')