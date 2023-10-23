import {FETCH_SUB_BILL, PRE_FETCH_SUB_BILL} from '../actions/bill'

const initialState = null

export default function (state = initialState, action) {
  switch (action.type) {
    case PRE_FETCH_SUB_BILL:
      return initialState
    case FETCH_SUB_BILL:
      return {...state, ...action.payload}
    default:
      return state
  }
}
