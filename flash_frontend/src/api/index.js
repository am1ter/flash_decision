import store from "../store"
import cookie from "../main"
import axios from "axios"


// Read docker enviroment variables
// ================================

let API_URL = (process.env.VUE_APP_URL_BACKEND) ? process.env.VUE_APP_URL_BACKEND : "http://127.0.0.1:8001/api"


// API errors handling
// ===================

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
    } catch (err) {
        // Clean cookies for auth info if have got "401 Unauthorized" response
        console.log(err.toJSON())
        if (err.toJSON().message == 'Network Error') {
            store.commit("newApiError", err)
            store.commit("stopLoading")
        } else {
            if (err.response.status == 401) {
                cookie.delete("user_id")
                cookie.delete("user_email")
                cookie.delete("user_token")
            }
            store.commit("newApiError", err.response.data)
            store.commit("stopLoading")
        }
    }
}


// API requests for authentication
// ===============================

export function apiSignUp(form) {
    console.log("Run apiSignUp")
    let reqUrl = "/sign-up/"
    let req = { "type": "post", "url": API_URL + reqUrl, "args": form }
    return handleResponse(req)
}


export function apiCheckEmailValidity(email) {
    console.log("Run apiCheckEmailValidity")
    let reqUrl = "/check-email-validity/"
    let email_obj = { "email": email }
    let req = { "type": "post", "url": API_URL + reqUrl, "args": email_obj }
    return handleResponse(req)
}


export function apiLogin(form) {
    console.log("Run apiLogin")
    let reqUrl = "/login/"
    let req = { "type": "post", "url": API_URL + reqUrl, "args": form }
    return handleResponse(req)
}


// API requests for app operations
// ===============================

export function apiGetSessionOptions(mode) {
    console.log("Run apiGetSessionOptions")
    let reqUrl = `/get-session-options/${mode}/`
    console.log(reqUrl)
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiPostStartNewSession(form) {
    console.log("Run apiPostStartNewSession")
    let reqUrl = "/start-new-session/"
    let req = {"type": "post", "url": API_URL + reqUrl, "args": form}
    return handleResponse(req)
}


export function apiGetIterationChart(sessionId, iterationNum) {
    console.log("Run apiGetIterationChart")
    let reqUrl = `/get-chart/${sessionId}/${iterationNum}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiGetIterationInfo(sessionId, iterationNum) {
    console.log("Run apiGetIterationInfo")
    let reqUrl = `/get-iteration-info/${sessionId}/${iterationNum}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiPostRecordDecision(decision) {
    console.log("apiPostRecordDecision")
    let reqUrl = "/record-decision/"
    let req = {"type": "post", "url": API_URL + reqUrl, "args": decision}
    return handleResponse(req)
}


export function apiGetSessionsResults(sessionId) {
    console.log("Run apiGetSessionsResults")
    let reqUrl = `/get-sessions-results/${sessionId}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiGetScoreboard(mode, userId) {
    console.log("Run apiGetScoreboard")
    let reqUrl = `/get-scoreboard/${mode}/${userId}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}
