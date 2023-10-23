import axios from 'axios'
import {externalAPIUrl} from './utils'

export const FETCH_STATS = 'fetch_stats'
export const FETCH_RANKING = 'fetch_ranking'


export function fetchRawStats (params) {
  return (dispatch, getState) => {
    const {tracking} = getState()
    if (tracking.enabled) {
      const url = externalAPIUrl(
        `${tracking.config.tracking_api_url}/api/v1/analyse/`,
        {queryParams: {...params}}
      )
      return axios.get(url, {headers: {
        Authorization: tracking.config.admin_api_key
      }})
    }
  }
}

export function fetchStats (params) {
  return (dispatch) => {
    dispatch(fetchRawStats(params)).then(
      data => {
        dispatch({
          type: FETCH_STATS,
          payload: data.data
        })
        return data.data
      }
    )
  }
}

export function fetchRawRanking (params) {
  return (dispatch, getState) => {
    const {tracking} = getState()
    if (tracking.enabled) {
      const url = externalAPIUrl(
        `${tracking.config.tracking_api_url}/api/v1/ranking/`,
        {queryParams: {...params}}
      )
      return axios.get(url, {headers: {
        Authorization: tracking.config.admin_api_key
      }})
    }
  }
}

export function fetchRankingIds (days, limit) {
  return (dispatch) => {
    let now = new Date()
    const date_to = now.toISOString()
    now.setDate(now.getDate() - days)
    const date_from = now.toISOString()
    const params = {date_to, date_from, limit}
    return dispatch(fetchRawRanking(params)).then(
      ({data}) => {
        return data.join(',')
      }
    )
  }
}

