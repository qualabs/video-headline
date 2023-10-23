import axios from 'axios'
import {APIUrl, APIHeaders} from './utils'
import {stopSubmit} from 'redux-form'

import {hideShowMenu} from './utils'

import history from '../history'

import {fetchChannels} from '../actions/channel'

export const USER_LOGIN = 'user_login'
export const USER_LOGOUT = 'user_logout'
export const FETCH_USER = 'fetch_user'
export const APP_INITIALIZED = 'app_initialized'

const LOCAL_STORAGE_TOKEN = 'token'

export function fetchMyUser () {
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl('accounts/me/', {})
    axios.get(url, {headers: APIHeaders(session)}).then( ({data}) => {
      dispatch({
        type: FETCH_USER,
        payload: data
      })
    }).catch(() => {
      window.localStorage.removeItem(LOCAL_STORAGE_TOKEN)
      dispatch({
        type: APP_INITIALIZED,
        payload: true
      })
    })
  }
}

export function login (values) {
  return (dispatch) => {
    return axios.post(APIUrl('token/login/', {}), values).then( ({data}) => {
      const token = data.token
      window.localStorage.setItem(LOCAL_STORAGE_TOKEN, token)
      dispatch({
        type: USER_LOGIN,
        payload: token
      })
      dispatch(fetchMyUser())
      dispatch(fetchChannels())
    }).catch(() => {
      dispatch(stopSubmit('login',
        {'_error': 'Password or user incorrect.'})
      )
    })
  }
}

export function logout () {
  return (dispatch, getState) => {
    const {session} = getState()

    return axios.post(APIUrl('token/logout/', {}), {}, {headers: APIHeaders(session)}).then( () => {
      window.localStorage.removeItem(LOCAL_STORAGE_TOKEN)
      dispatch(hideShowMenu())
      dispatch({
        type: USER_LOGOUT
      })
    })
  }
}

export function resumeSession () {
  return (dispatch) => {
    const token = window.localStorage.getItem(LOCAL_STORAGE_TOKEN)
    if (token) {
      dispatch({
        type: USER_LOGIN,
        payload: token
      })
      dispatch(fetchMyUser())
      dispatch(fetchChannels())
    } else {
      dispatch({
        type: APP_INITIALIZED,
        payload: true
      })
    }
  }
}

export function changePassword (values) {
  return (dispatch, getState) => {
    const {session} = getState()
    return axios.post(APIUrl('accounts/change_password/', {}), {...values}, {headers: APIHeaders(session)}).then( () => {
      history.push('/')
    }).catch(e => {
      dispatch(stopSubmit('change-password',
        {'_error': e.response.data.detail})
      )
    })
  }
}
