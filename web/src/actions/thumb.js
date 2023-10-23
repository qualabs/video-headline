import {createDRF} from './drf'
import axios from 'axios'
import {APIUrl, APIHeaders} from './utils'

export function getThumbnailSignedUrl (video_id, content_type) {
  return (dispatch) => {
    return dispatch(createDRF(`media/${video_id}/thumbnail/`, {content_type}, null))
  }
}


export function deleteThumbnail (video_id) {
  return (dispatch, getState) => {
    const {session} = getState()
    const url = APIUrl(`media/${video_id}/thumbnail/`, {})

    return axios.delete(url, {headers: APIHeaders(session)}).then( () => {
      dispatch({
        type: 'delete_thumbnail'
      })
    })
  }
}
