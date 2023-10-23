import { FETCH_MONITOR_STATS } from '../actions/monitor'
import {USER_LOGOUT, FETCH_USER} from '../actions/user'

const initialState = {
  stats: null,
  enabled: false,
  url: ''
}

export default function (state = initialState, action) {
  switch (action.type) {
    case USER_LOGOUT:
      return {...initialState}
    case FETCH_USER: {
      let orgConfig = action.payload.organization.config.dataTransferMonitor
      return {
        ...state,
        enabled: orgConfig ? orgConfig.enabled : false,
        url: orgConfig ? orgConfig.url : ''
      }
    }
    case FETCH_MONITOR_STATS:
      return {
        ...state,
        stats: action.payload
      }
    default:
      return state
  }
}
