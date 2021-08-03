import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [
    { path: '/session', component: App.components.Session, name: 'Session page' },
    { path: '/decision', component: App.components.Decision, name: 'Decision page' },
    { path: '/scoreboard', component: App.components.Scoreboard, name: 'Scoreboard page' }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;