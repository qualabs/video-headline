import queryString from 'query-string'

export const MENU_STATE_CHANGE = 'menu_state_change'

export function APIUrl (path: string, args: Object) {
  const params = queryString.stringify({
    ...args.queryParams,
    format: 'json'
  })
  return `${process.env.REACT_APP_VIDEO_HUB_API}${path}?${params}`
}

export function externalAPIUrl (path: string, args: Object) {
  const params = queryString.stringify({
    ...args.queryParams,
    format: 'json'
  })
  return `${path}?${params}`
}

export function APIHeaders (session: Object) {
  if (session.token) {
    return {Authorization: `Token ${session.token}`}
  }
  return {}
}

export function hideShowMenu () {
  return (dispatch) => {
    dispatch({
      type: MENU_STATE_CHANGE
    })
  }
}
