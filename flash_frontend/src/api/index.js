import store from '../store'
import axios from 'axios'


// In some cases it is neccessary to change AJAX API requests port to 80 or 443 manually.
// For example, if you use nginx reverse proxy with subdomains with custom '/location' routing.
// In a such case change the option 'FORCE_AJAX_API_DEF_PORT' in docker-compose .env file to '1'

let FORCE_AJAX_API_DEF_PORT
let PORT_BACKEND

// Read docker enviroment variables
if (process.env.VUE_APP_FORCE_AJAX_API_DEF_PORT) {
    FORCE_AJAX_API_DEF_PORT = process.env.VUE_APP_FORCE_AJAX_API_DEF_PORT
} else {
    FORCE_AJAX_API_DEF_PORT = 0
}

if ("process.env.VUE_APP_PORT_BACKEND" in window) {
    PORT_BACKEND = process.env.VUE_APP_PORT_BACKEND
} else {
    PORT_BACKEND = 8001
}

// Override API PORT to 443 (https) or 80 (http) if there is a following option in docker-compose .env file
if (FORCE_AJAX_API_DEF_PORT == '1') {
    if (window.location.protocol == 'https:') {
        PORT_BACKEND = 443
    } else {
        PORT_BACKEND = 80
    }
}

let API_URL = window.location.protocol + '//' + window.location.hostname + ':' + PORT_BACKEND + '/api'


// API errors handling

async function handleResponse(req) {
    try {
        // Make api request and get response
        let response
        if (req['type'] == 'get') {
            response = await axios.get(req['url'], { headers: { Authorization: `Bearer: ${store.state.user.token}` } })
        } else if (req['type'] == 'post') {
            response = await axios.post(req['url'], req['args'], { headers: { Authorization: `Bearer: ${store.state.user.token}` } })
        }
        // Check if response is not empty
        if (response) {
            return response.data
        } else {
            store.commit('newApiError', 'Error: Empty API response')
            return false
        }
    } catch(err) {
        store.commit('newApiError', err.response.data)
    }
}


// API functions

export function apiPostCreateUser(form) {
    console.log('Run apiPostCreateUser')
    let req = {'type': 'post', 'url': API_URL + '/create-user/', 'args': form}
    return handleResponse(req)
}


export function apiGetCheckEmailIsFree(email) {
    console.log('Run apiGetCheckEmailIsFree')
    let email_obj = {"email": email}
    let req = {'type': 'post', 'url': API_URL + '/check-email/', 'args': email_obj}
    return handleResponse(req)
}


export function apiPostLogin(form) {
    console.log('Run apiPostLogin')
    let req = {'type': 'post', 'url': API_URL + '/login/', 'args': form}
    return handleResponse(req)
}


export function apiGetSessionOptions() {
    console.log('Run apiGetSessionOptions')
    let req = {'type': 'get', 'url': API_URL + '/get-session-options/'}
    // let req = {'type': 'get', 'url': API_URL + '/get-session-options/', 'header': { headers: { Authorization: `Bearer: ${jwt}` } }}
    return handleResponse(req)
}


export function apiPostStartNewSession(form) {
    console.log('Run apiPostStartNewSession')
    let req = {'type': 'post', 'url': API_URL + '/start-new-session/', 'args': form}
    return handleResponse(req)
}


export function apiGetIterationChart(sessionId, iterationNum) {
    console.log('Run apiGetIterationChart')
    let req = {'type': 'get', 'url': API_URL + `/get-chart/${sessionId}/${iterationNum}/`}
    return handleResponse(req)
}


export function apiPostRecordDecision(decision) {
    console.log('apiPostRecordDecision')
    let req = {'type': 'post', 'url': API_URL + '/record-decision/', 'args': decision}
    return handleResponse(req)
}


export function apiGetSessionsResults(sessionId) {
    console.log('Run apiGetSessionsResults')
    let req = {'type': 'get', 'url': API_URL + `/get-sessions-results/${sessionId}/`}
    return handleResponse(req)
}


export function apiGetScoreboard(userId) {
    console.log('Run apiGetScoreboard')
    let req = {'type': 'get', 'url': API_URL + `/get-scoreboard/${userId}/`}
    return handleResponse(req)
}