import {FETCH_IFRAME, PRE_FETCH_IFRAME} from '../actions/security'

const initialState = null

export default function (state = initialState, action) {
  switch (action.type) {
    case PRE_FETCH_IFRAME:
      return initialState
    case FETCH_IFRAME:
      return {...state, ...action.payload}
    default:
      return state
  }
}
