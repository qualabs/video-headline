import axios from 'axios'
import {APIUrl, APIHeaders} from './utils'
import {fetchListDRF, fetchDRF, createDRF, patchDRF, deleteDRF,
  clearListDRF} from './drf'
import history from '../history'
import {FETCH_LIST} from '../actions/drf'

export const FETCH_CHANNEL = 'fetch_channel'
export const PRE_FETCH_CHANNEL = 'pre_fetch_channel'

export function clearChannels () {
  // params: Object with the API args
  return (dispatch) => {
    return dispatch(clearListDRF('channels'))
  }
}

export function fetchChannels (params) {
  // params: Object with the API args
  return (dispatch) => {
    return dispatch(fetchListDRF('channels/', {...params}, 'channels'))
  }
}

export function fetchChannel (id) {
  return (dispatch) => {
    dispatch({type: PRE_FETCH_CHANNEL})
    return dispatch(fetchDRF('channels/', id, FETCH_CHANNEL))
  }
}

export function fetchVideos (id, params) {
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`/channels/${id}/videos`, {queryParams: {...params}})
    return axios.get(url, {headers: APIHeaders(session)}).then( data => {
      dispatch({
        type: FETCH_LIST,
        payload: data.data
      })
      return data.data
    })
  }
}

export function createChannel (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(createDRF('channels/', values, null))
  }
}

export function updateChannel (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(patchDRF('channels/', values, null))
  }
}

export function deleteChannel (id) {
  return (dispatch) => {
    return dispatch(deleteDRF('channels/', id, null)).then(data => {
      // Go to the channels list
      dispatch(clearChannels())
      history.push('/channels/')
    })
  }
}
