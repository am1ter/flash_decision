import Vue from 'vue'
import Vuex from 'vuex'
import { apiErrors } from '@/api'

Vue.use(Vuex)

const state = {
    // single source of data
    version: '0.6.01',
    isAuth: false,
    user: { id: 53, email: 'demo@alekseisemenov.ru' },
    // user: {},
    registrationForm: {},
    apiErrors: apiErrors,
    sessions: [],
    currentSession: {},
    copyright_year: new Date().getFullYear()
}

const actions = {
    // asynchronous operations
}

const mutations = {
    // isolated data mutations
    setAuth (state, authStatus) {
        state.isAuth = authStatus;
      },
    setUser (state, user) {
        state.user = user
    }
}

const getters = {
    // reusable data accessors
}

const store = new Vuex.Store({
    state,
    actions,
    mutations,
    getters
})

export default store