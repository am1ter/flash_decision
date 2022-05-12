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

export function apiFetchSessionOptions(mode) {
    console.log("Run apiFetchSessionOptions")
    let reqUrl = `/session-options/${mode}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiStartNewSession(mode, form) {
    console.log("Run apiStartNewSession")
    let reqUrl = `/sessions/${mode}/`
    let req = {"type": "post", "url": API_URL + reqUrl, "args": form}
    return handleResponse(req)
}


export function apiRenderChart(mode, sessionId, iterationNum) {
    console.log("Run apiRenderChart")
    let reqUrl = `/sessions/${mode}/${sessionId}/iterations/${iterationNum}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiRecordDecision(mode, sessionId, iterationNum, decision) {
    console.log("Run apiRecordDecision")
    let reqUrl = `/sessions/${mode}/${sessionId}/decisions/${iterationNum}/`
    let req = {"type": "post", "url": API_URL + reqUrl, "args": decision}
    return handleResponse(req)
}


export function apiRenderSessionsResults(mode, sessionId) {
    console.log("Run apiRenderSessionsResults")
    let reqUrl = `/session-results/${mode}/${sessionId}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}


export function apiRenderScoreboard(mode, userId) {
    console.log("Run apiRenderScoreboard")
    let reqUrl = `/scoreboards/${mode}/${userId}/`
    let req = {"type": "get", "url": API_URL + reqUrl}
    return handleResponse(req)
}
