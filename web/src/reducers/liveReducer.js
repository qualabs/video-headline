import {FETCH_LIVE, PRE_FETCH_LIVE} from '../actions/live'

const initialState = null

export default function (state = initialState, action) {

  switch (action.type) {
    case PRE_FETCH_LIVE:
      return initialState
    case FETCH_LIVE:
      return {...state, ...action.payload}
    default:
      return state
  }
}
