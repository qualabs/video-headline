import {FETCH_CHANNEL, PRE_FETCH_CHANNEL} from '../actions/channel'

const initialState = {
  channel: null,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case PRE_FETCH_CHANNEL:
      return {...state, channel: null}
    case FETCH_CHANNEL:
      return {...state, channel: action.payload}
    default:
      return state
  }
}
