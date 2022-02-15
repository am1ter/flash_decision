import Vue from 'vue'
import store from './store'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [
    {
        path: '/sign-up',
        name: 'Signup page',
        component: App.components.page_Signup,
        meta: {
            title: 'Create account',
            instruction: 'Please enter your credentials and submit registration form'
        }
    },
    {
        path: '/sign-in',
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
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        },
        meta: {
            title: 'Training session parameters',
            instruction: 'Set parameters of the session and press Start'
        }
    },
    {
        path: '/decision/:session_id/:iteration_num',
        name: 'Decision’s page',
        component: App.components.page_Decision,
        beforeEnter(to, from, next) {
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        },
        meta: {
            title: 'Make your decision',
            instruction: 'We will close your position in 15 bars. Choose wisely!'
        }
    },
    {
        path: '/sessions-results/:session_id',
        name: 'Session’s results page',
        component: App.components.page_Results,
        beforeEnter(to, from, next) {
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        },
        meta: {
            title: 'Explore your results',
            instruction: 'Session’s summary'
        }
    },
    {
        path: '/scoreboard/:user_id',
        name: 'Scoreboard page',
        component: App.components.page_Scoreboard,
        beforeEnter(to, from, next) {
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
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