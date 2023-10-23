export const SET_FLASH_MESSAGE = 'set_flash_message'
export const REMOVE_FLASH_MESSAGE = 'remove_flash_message'

export function setMessage (message, type, ttl = true) {
  return (dispatch) => {
    dispatch({
      type: SET_FLASH_MESSAGE,
      payload: {message, type, ttl}
    })
  }
}

export function removeFlashMessage () {
  return (dispatch) => {
    dispatch({
      type: REMOVE_FLASH_MESSAGE
    })
  }
}
