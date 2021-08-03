import Vue from 'vue'
import router from './router'
import App from './App.vue'

import MarqueeText from 'vue-marquee-text-component' // Lib for background moving line

Vue.config.productionTip = false
Vue.component('marquee-text', MarqueeText)

new Vue({
    router,
    render: h => h(App)
}).$mount('#app')