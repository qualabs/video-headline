import axios from 'axios'

import {fetchListDRF, fetchDRF, patchDRF, clearListDRF, createDRF, deleteDRF} from './drf'
import {APIHeaders, APIUrl} from './utils'
import {setMessage} from './flashMessage'

export const FETCH_LIVE = 'fetch_live'
export const PRE_FETCH_LIVE = 'pre_fetch_live'

export function clearLiveVideos () {
  // params: Object with the API args
  return (dispatch) => {
    return (
      dispatch(clearListDRF('live-videos')), dispatch({type: PRE_FETCH_LIVE})
    )
  }
}

export function clearLiveVideo () {
  // params: Object with the API args
  return (dispatch) => {
    return dispatch({type: PRE_FETCH_LIVE})
  }
}

export function fetchLiveVideos (params) {
  // params: Object with the API args
  return (dispatch, getState) => {
    return dispatch(fetchListDRF('live-videos/', {...params}, 'liveVideos'))
  }
}

export function fetchLiveVideo (id, prefetch = true) {
  return (dispatch, getState) => {
    if (prefetch) {
      dispatch({type: PRE_FETCH_LIVE})
    }
    return dispatch(fetchDRF('live-videos/', id, FETCH_LIVE))
  }
}

export function updateLiveVideo (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(patchDRF('live-videos/', values, null))
  }
}

export function createLiveVideo (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(createDRF('live-videos/', values, null))
  }
}

export function changeLiveStateToStarting (id, session) {
  return (dispatch) => {
    const url = APIUrl(`live-videos/${id}/to_on/`, {})
    return axios
      .post(url, {}, {headers: APIHeaders(session)})
      .then(() => {
        dispatch(fetchLiveVideo(id))
        dispatch(
          setMessage(
            'This action can last about 5 minutes. Please, wait.', 'warning'
          )
        )
      })
      .catch((e) => {
        dispatch(setMessage(e.response.data.detail, 'error'))
      })
  }
}

export function changeLiveStateToStopping (id, session) {
  return (dispatch) => {
    const url = APIUrl(`live-videos/${id}/to_off/`, {})
    return axios
      .post(url, {}, {headers: APIHeaders(session)})
      .then(() => {
        dispatch(fetchLiveVideo(id))
        dispatch(
          setMessage(
            'This action can last about 5 minutes. Please, wait.', 'warning'
          )
        )
      })
      .catch((e) => {
        dispatch(setMessage(e.response.data.detail, 'error'))
      })
  }
}

export function deleteLiveVideo(values) {
  return (dispatch) => {
    return dispatch(deleteDRF('live-videos/', values, null,'to_delete/'))
  }
}