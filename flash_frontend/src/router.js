import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue';

Vue.use(VueRouter);

const routes = [
    {path: '/start', component: App.components.Start, name: 'Start page'},
    {path: '/terminal', component: App.components.Terminal, name: 'Terminal page'},
    {path: '/scoreboard', component: App.components.Scoreboard, name: 'Scoreboard page'}
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;