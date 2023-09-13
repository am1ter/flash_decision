import { createRouter, createWebHashHistory } from "vue-router"
import PageSessionVue from "../components/pages/PageSession.vue"

const route_home = {
    path: "/",
    component: PageSessionVue,
    beforeEnter(to, from, next) { }
}

const routes = [route_home]

export default createRouter({
    history: createWebHashHistory(),
    routes,
})

