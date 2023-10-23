import {USER_LOGIN, USER_LOGOUT, FETCH_USER,
  APP_INITIALIZED} from '../actions/user'

const initialState = {
  appInitialized: false,
  token: null,
  user: null,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case APP_INITIALIZED:
      return {...state, appInitialized: action.payload}
    case USER_LOGIN:
      return {...state, token: action.payload, appInitialized: false}
    case USER_LOGOUT:
      return {...state,
        user: null,
        token: null}
    case FETCH_USER:
      return {...state,
        appInitialized: true,
        user: action.payload}
    default:
      return state
  }
}
