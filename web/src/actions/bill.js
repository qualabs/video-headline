import {fetchListDRF, fetchDRF} from './drf'

export const FETCH_BILL = 'fetch_bill'
export const PRE_FETCH_BILL = 'pre_fetch_bill'

export const FETCH_SUB_BILL = 'fetch_sub_bill'
export const PRE_FETCH_SUB_BILL = 'pre_fetch_sub_bill'


export function fetchBills (params) {
  return (dispatch, getState) => {
    return dispatch(fetchListDRF('bills/', {...params}, 'bills'))
  }
}

export function fetchBill (id, prefetch = true) {
  return (dispatch, getState) => {
    if (prefetch) {
      dispatch({type: PRE_FETCH_BILL})
    }
    return dispatch(fetchDRF('bills/', id, FETCH_BILL))
  }
}

export function fetchSubBill (id, prefetch = true) {
  return (dispatch, getState) => {
    if (prefetch) {
      dispatch({type: PRE_FETCH_SUB_BILL})
    }
    return dispatch(fetchListDRF(`bills/${id}/`, null, id, FETCH_SUB_BILL))
  }
}
