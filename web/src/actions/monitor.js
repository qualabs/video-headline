import axios from 'axios'
import {APIHeaders} from './utils'

export const FETCH_MONITOR_STATS = 'fetch_monitor_stats'

export function fetchMonitorStats () {
    return (dispatch, getState) => {
        const {session, monitor} = getState()
        const url = monitor.url
        axios.get(url, {headers: APIHeaders(session)}).then( ({data}) => {
            dispatch({
                type: FETCH_MONITOR_STATS,
                payload: data
            })
        }).catch(() => {
            dispatch({
                type: FETCH_MONITOR_STATS,
                payload: null
            })
        })
    }
}