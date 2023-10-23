import {fetchDRF} from './drf'

export const PRE_FETCH_IFRAME = 'pre_fetch_iframe'
export const FETCH_IFRAME = 'fetch_iframe'

export function fetchIframe (id) {
  return (dispatch, getState) => {
    dispatch({type: PRE_FETCH_IFRAME})
    return dispatch(fetchDRF('link/', id, FETCH_IFRAME))
  }
}

