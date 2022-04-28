import Vue from "vue"
import store from "./store"
import VueRouter from "vue-router";
import App from "./App.vue";

Vue.use(VueRouter);
const APP_TITLE = "Flash decision: "

const routes = [
    {
        path: "/",
        beforeEnter (to, from, next) {
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next("/session") } else { next("/login") }
          }
    },
    {
        path: "/sign-up",
        name: "Signup page",
        component: App.components.PageSignup,
        meta: {
            title: "Create account",
            instruction: "Please enter your credentials for sign up"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            next()
        }
    },
    {
        path: "/login",
        name: "Login page",
        component: App.components.PageLogin,
        meta: {
            title: "Login",
            instruction: "Please login to start your training session"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            next()
        }
    },
    {
        path: "/session/",
        name: "Session Mode Selector",
        component: App.components.PageSession,
        meta: {
            title: "Start new training session",
            instruction: "Please select mode for your session"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next() } else { next("/login") }
        }
    },
    {
        path: "/session/:mode",
        name: "Session page",
        component: App.components.PageSessionForm,
        meta: {
            title: "Start new training session",
            instruction: "Set parameters of the session and press Start"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next() } else { next("/login") }
        }
    },
    {
        path: "/decision/:session_id/:iteration_num",
        name: "Decision’s page",
        component: App.components.PageDecision,
        meta: {
            title: "Make your decisions",
            instruction: "We will close your position in 15 bars. Choose wisely!"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next() } else { next("/login") }
        }
    },
    {
        path: "/sessions-results/:session_id",
        name: "Session’s results page",
        component: App.components.PageResults,
        meta: {
            title: "Session’s summary",
            instruction: "Explore your results"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next() } else { next("/login") }
        }
    },
    {
        path: "/scoreboard/:mode/:user_id",
        name: "Scoreboard page",
        component: App.components.PageScoreboard,
        meta: {
            title: "Scoreboard",
            instruction: "Analyze your progress"
        },
        beforeEnter(to, from, next) {
            document.title = APP_TITLE + to.meta.title
            store.commit("setUserFromCookie")
            if (store.getters.isAuth) { next() } else { next("/login") }
        }
    },
    {
        path: "*",
        redirect: '/'
    }
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

export default router;