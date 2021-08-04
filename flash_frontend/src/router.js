import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [
    { path: '/login', component: App.components.page_Login, name: 'Login page' },
    { path: '/session', component: App.components.page_Session, name: 'Session page' },
    { path: '/decision', component: App.components.page_Decision, name: 'Decision page' },
    { path: '/scoreboard', component: App.components.page_Scoreboard, name: 'Scoreboard page' }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;