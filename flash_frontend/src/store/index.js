import Vue from 'vue'
import Vuex from 'vuex'

// TODO: Remove before release
// import { fetchSessions } from '../api'

Vue.use(Vuex)

const state = {
    // single source of data
    version: '0.5.08',
    isAuth: true,
    user: { id: 1, name: 'amiter' },
    sessions: [],
    currentSession: {}
}

const actions = {
    // asynchronous operations
}

const mutations = {
    // isolated data mutations
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