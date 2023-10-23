import {FETCH_TAG} from '../actions/tags'

const initialState = null

export default function (state = initialState, action) {
  switch (action.type) {
    case FETCH_TAG:
      return action.payload
    default:
      return state
  }
}