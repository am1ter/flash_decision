import Vue from 'vue'
import Vuex from 'vuex'

import { fetchSessions } from '../api'

Vue.use(Vuex)

const state = {
    // single source of data
    version: '0.5.02',
    isAuth: true,
    user: { id: 1, name: 'amiter' },
    sessions: [],
    currentSession: {}
}

const actions = {
    // asynchronous operations
    loadSessions(context) {
        return fetchSessions()
            .then((respone) => context.commit('setSessions', { sessions: respone }))
    },
    addIdToSession(context) {
        console.log(context)
    }
}

const mutations = {
    // isolated data mutations
    setSessions(state, payload) {
        state.sessions = payload.sessions
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