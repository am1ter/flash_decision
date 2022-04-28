import store from "../store"
import cookie from "../main"
import axios from "axios"


// Read docker enviroment variables
let API_URL = (process.env.VUE_APP_URL_BACKEND) ? process.env.VUE_APP_URL_BACKEND : "http://127.0.0.1:8001/api"

// API errors handling
async function handleResponse(req) {
    try {
        // Make api request and get response
        let response
        if (req["type"] == "get") {
            response = await axios.get(req["url"], { headers: { Authorization: `Bearer: ${cookie.get("user_token")}` } })
        } else if (req["type"] == "post") {
            response = await axios.post(req["url"], req["args"], { headers: { Authorization: `Bearer: ${cookie.get("user_token")}` } })
        }
        // Check if response is not empty
        if (response) {
            return response.data
        } else {
            store.commit("newApiError", "Error: Empty API response")
            return false
        }
    } catch(err) {
        // Clean cookies for auth info if have got "401 Unauthorized" response
        console.log(err.toJSON())
        if (err.toJSON().message == 'Network Error') {
            store.commit("newApiError", err)
        } else {
            if (err.response.status == 401) {
                cookie.delete("user_id")
                cookie.delete("user_email")
                cookie.delete("user_token")
            }
            store.commit("newApiError", err.response.data)
        }
    }
}


// API functions

export function apiPostCreateUser(form) {
    console.log("Run apiPostCreateUser")
    let req = {"type": "post", "url": API_URL + "/create-user/", "args": form}
    return handleResponse(req)
}


export function apiGetCheckEmailIsFree(email) {
    console.log("Run apiGetCheckEmailIsFree")
    let email_obj = {"email": email}
    let req = {"type": "post", "url": API_URL + "/check-email/", "args": email_obj}
    return handleResponse(req)
}


export function apiPostLogin(form) {
    console.log("Run apiPostLogin")
    let req = {"type": "post", "url": API_URL + "/login/", "args": form}
    return handleResponse(req)
}


export function apiGetSessionOptions(mode) {
    console.log("Run apiGetSessionOptions")
    let req = {"type": "get", "url": API_URL + `/get-session-options/${mode}/`}
    return handleResponse(req)
}


export function apiPostStartNewSession(form) {
    console.log("Run apiPostStartNewSession")
    let req = {"type": "post", "url": API_URL + "/start-new-session/", "args": form}
    return handleResponse(req)
}


export function apiGetIterationChart(sessionId, iterationNum) {
    console.log("Run apiGetIterationChart")
    let req = {"type": "get", "url": API_URL + `/get-chart/${sessionId}/${iterationNum}/`}
    return handleResponse(req)
}


export function apiGetIterationInfo(sessionId, iterationNum) {
    console.log("Run apiGetIterationChart")
    let req = {"type": "get", "url": API_URL + `/get-iteration-info/${sessionId}/${iterationNum}/`}
    return handleResponse(req)
}


export function apiPostRecordDecision(decision) {
    console.log("apiPostRecordDecision")
    let req = {"type": "post", "url": API_URL + "/record-decision/", "args": decision}
    return handleResponse(req)
}


export function apiGetSessionsResults(sessionId) {
    console.log("Run apiGetSessionsResults")
    let req = {"type": "get", "url": API_URL + `/get-sessions-results/${sessionId}/`}
    return handleResponse(req)
}


export function apiGetScoreboard(mode, userId) {
    console.log("Run apiGetScoreboard")
    let req = {"type": "get", "url": API_URL + `/get-scoreboard/${mode}/${userId}/`}
    return handleResponse(req)
}