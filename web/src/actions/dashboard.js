import axios from 'axios'
import {fetchRawStats} from './tracking'
import {APIHeaders, APIUrl} from './utils'

export const FETCH_DASHBOARD = 'fetch_dashboard'
export const CLEAR_DASHBOARD = 'clear_dashboard'

export function fetchDashboard () {
  const now_date = new Date()
  now_date.setDate(now_date.getDate() - 7)
  let last_seven_days = now_date.toISOString()

  return (dispatch, getState) => {
    const {session, tracking} = getState()
    const url = APIUrl('dashboard/', {})
    axios.get(url, {headers: APIHeaders(session)}).then(data => {
      dispatch({type: FETCH_DASHBOARD, payload: data.data})
    })

    if (tracking.enabled) {
      dispatch(fetchRawStats({
        date_from: last_seven_days,
      })).then(data => {
        if (data.data.views_per_day && data.data.views_per_day[0]) {
          let count_views_last_seven_days = 0
          data.data.views_per_day.map( (day) => {
            count_views_last_seven_days += day[0]
            return count_views_last_seven_days
          })

          let views_last_day = data.data.views_per_day[data.data.views_per_day.length - 1][0]
          dispatch({type: FETCH_DASHBOARD, payload: {
            count_views_last_seven_days,
            views_last_seven_days: data.data,
            views_last_day: views_last_day
          }})
        }
      })
    }
  }
}

export function clearDashboard () {
  return (dispatch) => {
    return (
      dispatch({type: CLEAR_DASHBOARD})
    )
  }
}
