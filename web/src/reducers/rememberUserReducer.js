import {REMEMBER_USER} from '../actions/customer'

const initialState = {
  email: null,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case REMEMBER_USER:
      return {...state, email: action.payload}
    default:
      return state
  }
}
