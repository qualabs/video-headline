import {FETCH_VIDEO, PRE_FETCH_VIDEO} from '../actions/video'

const initialState = null

export default function (state = initialState, action) {
  switch (action.type) {
    case PRE_FETCH_VIDEO:
      return initialState
    case FETCH_VIDEO:
      return {...state, ...action.payload}
    default:
      return state
  }
}
