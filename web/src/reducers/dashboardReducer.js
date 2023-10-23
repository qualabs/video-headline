import {FETCH_DASHBOARD} from '../actions/dashboard'
import {CLEAR_DASHBOARD} from '../actions/dashboard'
import {USER_LOGOUT} from '../actions/user'

const initialState = {
  dashboard: {}
}

export default function (state = initialState, action) {
  switch (action.type) {
    case FETCH_DASHBOARD: {
      let dashboard = {...state.dashboard, ...action.payload}
      return {...state, dashboard: dashboard}
    }
    case CLEAR_DASHBOARD: 
    case USER_LOGOUT: {
      return {...initialState}
    }
    default:
      return state
  }
}

