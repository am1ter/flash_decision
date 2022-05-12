import Vue from "vue"
import Vuex from "vuex"
import { isValidJwt } from "@/utils"


Vue.use(Vuex)

const state = {
    // single source of data
    version: "0.7.13",
    user: {},
    apiErrors: [],
    currentSession: {"userId": {},
                     "mode": {},
                     "options": {"values": {},
                                 "aliases": {}}, 
                     "sessionsResults": {}},
    copyright_year: new Date().getFullYear(),
    isLoading: false
}

const actions = {
    // asynchronous operations
}

const mutations = {
    // isolated data mutations
    setNoUser (state) {
        Vue.cookie.delete("user_id")
        Vue.cookie.delete("user_email")
        Vue.cookie.delete("user_token")
        state.user = {};
      },
    setUserFromApi (state, user) {
        Vue.cookie.set("user_id", user["id"])
        Vue.cookie.set("user_email", user["email"])
        Vue.cookie.set("user_token", user["token"])
        state.user = user
    },
    setUserFromCookie (state) {
        let user_id = Vue.cookie.get("user_id")
        let user_email = Vue.cookie.get("user_email")
        let user_token = Vue.cookie.get("user_token")
        state.user = {"id": user_id, "email": user_email, "token": user_token}
    },
    newApiError (state, error) {
        state.apiErrors.push(error)
    },
    startLoading () {
        state.isLoading = true
    },
    stopLoading () {
        state.isLoading = false
    },
    setSessionMode (state, mode) {
        state.currentSession["mode"] = mode
    }
}

const getters = {
    // reusable data accessors
    isAuth (state) {
        return isValidJwt(state.user.token)
    },
    sessionMode (state) {
        let mode = state.currentSession["mode"]
        return mode
    }
}

const store = new Vuex.Store({
    state,
    actions,
    mutations,
    getters
})

export default store