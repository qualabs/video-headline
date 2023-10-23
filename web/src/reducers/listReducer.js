import {FETCH_LIST, CLEAR_LIST} from '../actions/drf'
import {USER_LOGOUT} from '../actions/user'

const initialState = {
}

export default function (state = initialState, action) {
  switch (action.type) {
    case FETCH_LIST:
      return {...state, ...action.payload}
    case CLEAR_LIST: {
      const newState = {...state}
      if (newState[action.payload]) delete newState[action.payload]
      return newState
    }
    case USER_LOGOUT: {
      return {...initialState}
    }
    default:
      return state
  }
}
