import Vue from 'vue'

import MarqueeText from 'vue-marquee-text-component' // Marquee: Lib for background moving line
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue' // Bootstrap
import 'bootstrap/dist/css/bootstrap.css' // Bootstrap
import 'bootstrap-vue/dist/bootstrap-vue.css' // Bootstrap

import router from './router'
import App from './App.vue'


Vue.config.productionTip = false

Vue.component('marquee-text', MarqueeText)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

new Vue({
    router,
    render: h => h(App)
}).$mount('#app')