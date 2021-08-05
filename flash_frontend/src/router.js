import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [{
        path: '/login',
        name: 'Login page',
        component: App.components.page_Login
    },
    {
        path: '/session',
        name: 'Session page',
        component: App.components.page_Session,
        beforeEnter(to, from, next) {
            if (App.computed.isAuth()) { next() } else { next('/login') }
        }
    },
    {
        path: '/decision',
        name: 'Decision page',
        component: App.components.page_Decision,
        beforeEnter(to, from, next) {
            if (App.computed.isAuth()) { next() } else { next('/login') }
        }
    },
    {
        path: '/scoreboard',
        name: 'Scoreboard page',
        component: App.components.page_Scoreboard,
        beforeEnter(to, from, next) {
            if (App.computed.isAuth()) { next() } else { next('/login') }
        }
    }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;