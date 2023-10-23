import axios from 'axios'
import {APIUrl, APIHeaders} from './utils'

export const FETCH_LIST = 'fetch_list'
export const CLEAR_LIST = 'clear_list'


export function clearListDRF (listName) {
  // params: Object with the API args
  return (dispatch) => {
    dispatch({
      type: CLEAR_LIST,
      payload: listName
    })
  }
}

export function fetchListDRF (path, params, listName = null, action = null) {
  // params: Object with the API args
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(path, {queryParams: {...params}})
    return axios.get(url, {headers: APIHeaders(session)}).then( data => {
      dispatch({
        type: (action ? action : FETCH_LIST),
        payload: (listName ? {[listName]: data.data} : data.data)
      })
      return data.data
    })
  }
}

export function fetchDRF (path, id, action, params) {
  // params: Object with the API args

  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`${path}${id}/`, {queryParams: params})
    return axios.get(url, {headers: APIHeaders(session)}).then( data => {
      dispatch({
        type: action,
        payload: data.data
      })
      return data
    })
  }
}

export function createDRF (path, values, action = null) {
  // params: Object with the API args
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(path, {})
    return axios.post(url, {...values}, {headers: APIHeaders(session)}).then( data => {
      if (action) {
        dispatch({
          type: action,
          payload: data.data
        })
      }
      return data
    })
  }
}

export function patchDRF (path, values, action = null) {
  // params: Object with the API args
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`${path}${values.id}/`, {})
    return axios.patch(url, {...values}, {headers: APIHeaders(session)}).then( data => {
      if (action) {
        dispatch({
          type: action,
          payload: data.data
        })
      }
      return data
    })
  }
}

export function putDRF (path, values, action = null) {
  // params: Object with the API args
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`${path}${values.id}/`, {})
    return axios.put(url, {...values}, {headers: APIHeaders(session)}).then( data => {
      if (action) {
        dispatch({
          type: action,
          payload: data.data
        })
      }
      return data
    })
  }
}

export function deleteDRF (path, id, action = null, params = null) {
  return (dispatch, getState) => {
    const {session} = getState()
    const url = params ? APIUrl(`${path}${id}/${params}`, {}) : APIUrl(`${path}${id}/`, {})
    return axios.delete(url, {headers: APIHeaders(session)}).then( data => {
      if (action) {
        dispatch({
          type: action,
          payload: id
        })
      }
      return data
    })
  }
}
