import {FETCH_VIDEO, PRE_FETCH_VIDEO} from '../actions/video'

const initialState = {
  video: null,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case PRE_FETCH_VIDEO:
      return {...state, video: null}
    case FETCH_VIDEO:
      return {...state, video: action.payload}
    default:
      return state
  }
}
