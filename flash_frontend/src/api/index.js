import axios from 'axios'


// In some cases it is neccessary to change AJAX API requests port to 80 or 443 manually.
// For example, if you use nginx reverse proxy with subdomains with custom '/location' routing.
// In a such case change the option 'FORCE_AJAX_API_DEF_PORT' in docker-compose .env file to '1'

let FORCE_AJAX_API_DEF_PORT
let PORT_BACKEND

// Read docker enviroment variables
if ("process.env.VUE_APP_FORCE_AJAX_API_DEF_PORT" in window) {
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
if (FORCE_AJAX_API_DEF_PORT == 1) {
    if (window.location.protocol == 'https:') {
        PORT_BACKEND = 443
    } else {
        PORT_BACKEND = 80
    }
}

let API_URL = window.location.protocol + '//' + window.location.hostname + ':' + PORT_BACKEND + '/api'


// API errors handling

// export let apiErrors = []
// function handleResponse(req) {
//     req.then(
//         response => {
//             // Check if response is correct or contains errors
//             if (String(response.data).toLowerCase().includes('error')) {
//                 apiErrors.push(response.data)
//                 return false
//             } else {
//                 console.log(response)
//                 return response
//             }
//         },
//         reject => {apiErrors.push(reject)}
//     )
// }

export let apiErrors = []
function handleResponse(req) {
    try {
        // Check if response is correct or contains errors
        if (String(req.data).toLowerCase().includes('error')) {
            apiErrors.push(req.data)
            return false
        } else {
            return req
        }
    } catch(err) {
        apiErrors.push(err)
    }
}

// API functions

export function postCreateUser(form) {
    console.log('Run postCreateUser')
    let req = axios.post(API_URL + '/create-user/', form)
    return handleResponse(req)
}

export function checkEmailIsFree(email) {
    console.log('Run checkEmailIsFree')
    let email_obj = {"email": email}
    let req = axios.post(API_URL + '/check-email/', email_obj)
    return handleResponse(req)
}

export function fetchSessionOptions() {
    console.log('Run fetchSessionOptions')
    return axios.get(API_URL + '/get-session-options/')
}


export function postStartNewSession(form) {
    console.log('Run postStartNewSession')
    return axios.post(API_URL + '/start-new-session/', form)
}


export function getIterationChart(sessionId, iterationNum) {
    console.log('Run getIterationChart')
    return axios.get(API_URL + `/get-chart/${sessionId}/${iterationNum}/`)
}


export async function postRecordDecision(decision) {
    console.log('post Record Decision')
    return await axios.post(API_URL + '/record-decision/', decision)
}


export async function getSessionsResults(sessionId) {
    console.log('Run getSessionsResults')
    return await axios.get(API_URL + `/get-sessions-results/${sessionId}/`)
}


export async function getScoreboard(userId) {
    console.log('Run getScoreboard')
    return await axios.get(API_URL + `/get-scoreboard/${userId}/`)
}