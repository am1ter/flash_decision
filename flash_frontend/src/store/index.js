import Vue from 'vue'
import Vuex from 'vuex'
// import { postCreateUser, postLogin } from '@/api'
// import { isValidJwt, EventBus } from '@/utils'
import { isValidJwt } from '@/utils'


Vue.use(Vuex)

const state = {
    // single source of data
    version: '0.6.03',
    user: {},
    apiErrors: [],
    currentSession: {},
    copyright_year: new Date().getFullYear()
}

const actions = {
    // asynchronous operations
}

const mutations = {
    // isolated data mutations
    setNoUser (state) {
        state.user = {};
      },
    setUser (state, user) {
        state.user = user
    },
    newApiError (state, error) {
        state.apiErrors.push(error)
    }
}

const getters = {
    // reusable data accessors
    isAuth (state) {
        return isValidJwt(state.user.token)
      }
}

const store = new Vuex.Store({
    state,
    actions,
    mutations,
    getters
})

export default store