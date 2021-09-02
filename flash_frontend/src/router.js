import Vue from 'vue'
import store from './store'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [{
        path: '/login',
        name: 'Login page',
        component: App.components.page_Login,
        meta: {
            title: 'Login page',
            instruction: 'Please login to start your training session'
        }
    },
    {
        path: '/session',
        name: 'Session page',
        component: App.components.page_Session,
        beforeEnter(to, from, next) {
            if (store.state.isAuth) { next() } else { next('/login') }
        },
        meta: {
            title: 'Training session parameters',
            instruction: 'Set parameters of the session and press Start'
        }
    },
    {
        path: '/decision/:session_id/:iteration_num',
        name: 'Decision page',
        component: App.components.page_Decision,
        beforeEnter(to, from, next) {
            if (store.state.isAuth) { next() } else { next('/login') }
        },
        meta: {
            title: 'Make your decision',
            instruction: 'We will close your position in 15 bars. Choose wisely!'
        }
    },
    {
        path: '/scoreboard',
        name: 'Scoreboard page',
        component: App.components.page_Scoreboard,
        beforeEnter(to, from, next) {
            if (store.state.isAuth) { next() } else { next('/login') }
        },
        meta: {
            title: 'Scoreboard',
            instruction: 'Analyze your progress'
        }
    }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;