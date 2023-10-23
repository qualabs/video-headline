import {FETCH_CUT, PRE_FETCH_CUT} from '../actions/cuts'

const initialState = null

export default function (state = initialState, action) {

  switch (action.type) {
    case PRE_FETCH_CUT:
      return initialState
    case FETCH_CUT:
      return {...state, ...action.payload}
    default:
      return state
  }
}
