import {MENU_STATE_CHANGE} from '../actions/utils'

const initialState = {
  show_menu: false
}

export default function (state = initialState, action) {
  switch (action.type) {
    case MENU_STATE_CHANGE:
      return {
        ...state,
        show_menu: !state.show_menu
      }
    case '@@router/LOCATION_CHANGE':
      return initialState
    default:
      return state
  }
}
