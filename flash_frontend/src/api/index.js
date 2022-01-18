import axios from 'axios'


const API_URL = window.location.protocol + '//' + 'it1.nemanadvisors.com' + ':8001/api'


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

export async function getScoreboard(userId, sessionId) {
    console.log('Run getScoreboard')
    return await axios.get(API_URL + `/get-scoreboard/${userId}/${sessionId}/`)
}