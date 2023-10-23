import {fetchListDRF, fetchDRF, createDRF, patchDRF, deleteDRF,
  clearListDRF} from './drf'

export const FETCH_CUT = 'fetch_cut'
export const PRE_FETCH_CUT = 'pre_fetch_cut'

export function clearLiveVideoCuts () {
  // params: Object with the API args
  return (dispatch) => {
    return (
      dispatch(clearListDRF('cuts/')),
      dispatch({type: PRE_FETCH_CUT})
    )
  }
}

export function clearCut () {
  // params: Object with the API args
  return (dispatch) => {
    return (
      dispatch({type: PRE_FETCH_CUT})
    )
  }
}

export function fetchLiveVideoCut (id, prefetch = true) {
  return (dispatch) => {
    if (prefetch) {
      dispatch({type: PRE_FETCH_CUT})
    }
    return dispatch(fetchDRF('cuts/', id, FETCH_CUT))
  }
}

export function fetchLiveVideoCuts (id, params) {
  params.live_id = id

  return (dispatch) => {
    dispatch({type: PRE_FETCH_CUT})
    return dispatch(fetchListDRF(`cuts/`, {...params}, 'cuts'))
  }
}

export function createLiveVideoCut (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(createDRF('cuts/', values, values ? values.action : null))
  }
}

export function updateLiveVideoCut (values) {
  // values: Object with the API values
  return (dispatch) => {
    return dispatch(patchDRF('cuts/', values, null))
  }
}

export function deleteLiveVideoCut (id) {
  return (dispatch) => {
    return dispatch(deleteDRF('cuts/', id, null)).then(data => {
      dispatch(clearLiveVideoCuts())
      return data
    })
  }
}
