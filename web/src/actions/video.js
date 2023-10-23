import axios from 'axios'

import {APIUrl, APIHeaders} from './utils'
import {fetchListDRF, fetchDRF, createDRF, patchDRF, deleteDRF,
  clearListDRF} from './drf'
import {fetchRankingIds} from './tracking'

export const FETCH_VIDEO = 'fetch_video'
export const PRE_FETCH_VIDEO = 'pre_fetch_video'

export function clearVideos () {
  // params: Object with the API args
  return (dispatch) => {
    return (
      dispatch(clearListDRF('videos')),
      dispatch({type: PRE_FETCH_VIDEO})
    )
  }
}

export function clearVideo () {
  // params: Object with the API args
  return (dispatch) => {
    return (
      dispatch({type: PRE_FETCH_VIDEO})
    )
  }
}

export function fetchVideos (params) {
  // params: Object with the API args
  return (dispatch) => {
    if (params.days) {
      const days = params.days
      delete params.days

      return dispatch(fetchRankingIds(days, 10)).then(videoIds => {
        return dispatch(fetchListDRF('media/', {...params, video_ids: videoIds}, 'videos'))
      })
    }

    return dispatch(fetchListDRF('media/', {...params}, 'videos'))
  }
}

export function fetchVideo (id) {
  return (dispatch, getState) => {
    dispatch({type: PRE_FETCH_VIDEO})
    return dispatch(fetchDRF('media/', id, FETCH_VIDEO))
  }
}

export function fetchVideoState (id) {
  return (dispatch, getState) => {
    return dispatch(fetchDRF('media/', id, FETCH_VIDEO))
  }
}

export function createVideo (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(createDRF('media/', values, values ? values.action : null))
  }
}

export function updateVideo (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(patchDRF('media/', values, null))
  }
}

export function deleteVideo (id) {
  return (dispatch) => {
    return dispatch(deleteDRF('media/', id, null)).then(data => {
      dispatch(clearVideos())
      return data
    })
  }
}

export function changeVideoStateToQueued (id) {
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`media/${id}/to_queued/`, {})
    return axios.post(url, {}, {headers: APIHeaders(session)})
  }
}
