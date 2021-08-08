import axios from 'axios'

const API_URL = 'http://127.0.0.1:8001/api'

let Sessions = [
    {
      "session_id": 1,
      "session_status": "active",
      "session_datetime": "2020-10-23 15:34:55.300908",
      "user_id": 1,
      "case_market": "Market.SHARES",
      "case_ticker": "SBER",
      "case_timeframe": "Timeframe.MINUTES1",
      "case_barsnumber": 50,
      "case_timer": 5,
      "case_datetime": "2020-09-22 18:01:00.000000",
      "case_iterations": 10,
      "case_slippage": 0.001,
      "case_fixingbar": 15
    },
    {
      "session_id": 2,
      "session_status": "active",
      "session_datetime": "2020-10-29 21:39:31.902851",
      "user_id": 1,
      "case_market": "Market.SHARES",
      "case_ticker": "SBER",
      "case_timeframe": "Timeframe.MINUTES1",
      "case_barsnumber": 50,
      "case_timer": 5,
      "case_datetime": "2020-09-30 00:39:00.000000",
      "case_iterations": 10,
      "case_slippage": 0.001,
      "case_fixingbar": 15
    }
  ]

export function fetchSessionOptions() {
    return axios.get(API_URL + '/get-session-options/')
}

export function fetchSessions() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(Sessions)
        }, 300)
    })
}