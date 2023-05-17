import store from "../store"
import cookie from "../main"
import axios from "axios"


// Read docker enviroment variables
// ================================

let API_URL = (process.env.VUE_APP_BACKEND_URL) ? process.env.VUE_APP_BACKEND_URL : "http://127.0.0.1:8001/api"


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
        // Show error on the DOM
        let err_msg
        if (Object.keys(err.response).length > 1) {
            if (err.response.status == 404) {
                err_msg = `Wrong API request: ${err.response.request.responseURL}`
            } else if (err.response.status == 401) {
                cookie.delete("user_id")
                cookie.delete("user_email")
                cookie.delete("user_token")
            } else if (typeof (err.response.data) == 'string') {
                err_msg = `Error ${err.response.status}: ${err.response.statusText}`
            } else {
                err_msg = (Object.keys(err.response.data.errors).length > 0) ?
                    err.response.data.errors :
                    err.response.data
            }
        } else if (err.toJSON().message != undefined && err.toJSON().message != '') {
            err_msg = err.toJSON().message
        } else {
            err_msg = 'Error: Connection to server failed. Please try again.'
        }

        store.commit("newApiError", err_msg)
        store.commit("stopLoading")
    }
}


// API requests for authentification
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
    let req = { "type": "get", "url": API_URL + reqUrl }
    return handleResponse(req)
}


export function apiStartNewSession(mode, form) {
    console.log("Run apiStartNewSession")
    let reqUrl = `/sessions/${mode}/`
    let req = { "type": "post", "url": API_URL + reqUrl, "args": form }
    return handleResponse(req)
}


export function apiRenderChart(mode, sessionId, iterNum) {
    console.log("Run apiRenderChart")
    let reqUrl = `/sessions/${mode}/${sessionId}/iterations/${iterNum}/`
    let req = { "type": "get", "url": API_URL + reqUrl }
    return handleResponse(req)
}


export function apiRecordDecision(mode, sessionId, iterNum, decision) {
    console.log("Run apiRecordDecision")
    let reqUrl = `/sessions/${mode}/${sessionId}/decisions/${iterNum}/`
    let req = { "type": "post", "url": API_URL + reqUrl, "args": decision }
    return handleResponse(req)
}


export function apiRenderSessionsResults(mode, sessionId) {
    console.log("Run apiRenderSessionsResults")
    let reqUrl = `/session-results/${mode}/${sessionId}/`
    let req = { "type": "get", "url": API_URL + reqUrl }
    return handleResponse(req)
}


export function apiRenderScoreboard(mode, userId) {
    console.log("Run apiRenderScoreboard")
    let reqUrl = `/scoreboards/${mode}/${userId}/`
    let req = { "type": "get", "url": API_URL + reqUrl }
    return handleResponse(req)
}
