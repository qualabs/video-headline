import {fetchListDRF, fetchDRF, clearListDRF} from './drf'

export const FETCH_TAG = 'fetch_tag'
export const PRE_FETCH_TAG = 'pre_fetch_tag'

export function clearTags () {
  // params: Object with the API args
  return (dispatch, getState) => {
    return dispatch(clearListDRF('tags'))
  }
}

export function fetchTags (params) {
  return (dispatch, getState) => {
    return dispatch(fetchListDRF('tags/', {...params}, 'tags'))
  }
}

export function fetchTag (id) {
  return (dispatch) => {
    return dispatch(fetchDRF('tags/', id, FETCH_TAG))
  }
}
