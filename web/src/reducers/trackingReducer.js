import {FETCH_STATS, FETCH_RANKING} from '../actions/tracking'
import {USER_LOGOUT, FETCH_USER} from '../actions/user'
import {CLEAR_DASHBOARD} from '../actions/dashboard'

const initialState = {
  stats: null,
  config: {},
  enabled: false
}

export default function (state = initialState, action) {
  switch (action.type) {
    case FETCH_STATS:
      return {...state, stats: action.payload}
    case FETCH_RANKING:
      return {...state, ranking: action.payload}
    case USER_LOGOUT:
      return {...initialState}
    case FETCH_USER: {
      let orgConfig = action.payload.organization.config
      return {
        ...state,
        config: orgConfig.qtracking ? orgConfig.qtracking : {},
        enabled: (orgConfig.qtracking && orgConfig.qtracking.enabled) || false
      }
    }
    case CLEAR_DASHBOARD: {
      return {...state, stats: null}
    }
    default:
      return state
  }
}
