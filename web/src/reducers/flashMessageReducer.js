import {SET_FLASH_MESSAGE, REMOVE_FLASH_MESSAGE} from '../actions/flashMessage'

const initialState = {
  message: null,
  type: null
}

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_FLASH_MESSAGE:
      return {...state,
        message: action.payload.message,
        type: action.payload.type,
        ttl: action.payload.ttl}
    case REMOVE_FLASH_MESSAGE:
    case '@@router/LOCATION_CHANGE':
      return initialState
    default:
      return state
  }
}
