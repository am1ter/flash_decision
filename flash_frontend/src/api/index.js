import axios from 'axios'


const API_URL = 'http://127.0.0.1:8000/api'


export function fetchSessionOptions() {
    return axios.get(API_URL + '/get-session-options/')
}


export function postStartNewSession(form) {
    console.log('POST request sended') //TODO: Delete before release
    return axios.post(API_URL + '/start-new-session/', form)
}


export function getIterationChart(sessionId, iterationNum) {
    console.log('Run getIterationChart')
    console.log(API_URL + `/get-chart/${sessionId}/${iterationNum}/`)
    return axios.get(API_URL + `/get-chart/${sessionId}/${iterationNum}/`)
}