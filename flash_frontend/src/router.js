import Vue from 'vue'
import store from './store'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);
const APP_TITLE = 'Flash decision: '

const routes = [
    {
        path: '/sign-up',
        name: 'Signup page',
        component: App.components.page_Signup,
        meta: {
            title: 'Create account',
            instruction: 'Please enter your credentials and submit registration form'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            next()
        }
    },
    {
        path: '/sign-in',
        name: 'Login page',
        component: App.components.page_Login,
        meta: {
            title: 'Sign in',
            instruction: 'Please login to start your training session'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            next()
        }
    },
    {
        path: '/session',
        name: 'Session page',
        component: App.components.page_Session,
        meta: {
            title: 'Start new training session',
            instruction: 'Set parameters of the session and press Start'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        }
    },
    {
        path: '/decision/:session_id/:iteration_num',
        name: 'Decision’s page',
        component: App.components.page_Decision,
        meta: {
            title: 'Make your decisions',
            instruction: 'We will close your position in 15 bars. Choose wisely!'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        }
    },
    {
        path: '/sessions-results/:session_id',
        name: 'Session’s results page',
        component: App.components.page_Results,
        meta: {
            title: 'Session’s summary',
            instruction: 'Explore your results'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        }
    },
    {
        path: '/scoreboard/:user_id',
        name: 'Scoreboard page',
        component: App.components.page_Scoreboard,
        meta: {
            title: 'Scoreboard',
            instruction: 'Analyze your progress'
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit('setUserFromCookie')
            if (store.getters.isAuth) { next() } else { next('/sign-in') }
        }
    }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;