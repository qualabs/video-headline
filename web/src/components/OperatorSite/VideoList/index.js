import React, {Component} from 'react'
import {connect} from 'react-redux'

import Page from '../../Page'
import VideoTable from '../Table/VideoTable'

import {NOT_FINISHED, FAILED} from '../utils/stepper'

import {fetchVideos, clearVideo} from '../../../actions/video'
import {fetchTag} from '../../../actions/tags'

import './index.css'

class VideoList extends Component {

  componentDidMount () {
    this.props.clearVideo()
  }

  renderFilterByState = (search) => {
    let state = search.get('state')

    if (state) {
      if (state === NOT_FINISHED) {
        return (
          'in state "processing"'
        )
      }

      if (state === FAILED) {
        return (
          'in state "failed"'
        )
      }
    }
  }

  renderFilterByTag = (search) => {
    let tag_id = parseInt(search.get('tags__id'))

    if (tag_id) {
      this.props.fetchTag(tag_id)
      let {tag} = this.props

      if (tag) {
        return (
          `with tag "${tag.name}"`
        )
      }
    }
  }

  renderFilterCreatedBy = (search) => {
    let username = search.get('created_by__username')

    if (username) {
      return (
        `from user "${username}"`
      )
    }
  }

  renderFilterByRanking = (search) => {
    let days = search.get('days')

    if (days) {
      return (
        `most seen of last ${days} days`
      )
    }
  }

  renderFilterByMediaType = (search) => {
    let mediaType = search.get('media_type')

    if (mediaType) {
      if (mediaType === 'video') {
        return (
          `of video`
        )
      }

      if (mediaType === 'audio') {
        return (
          `of audio`
        )
      }
    }
  }

  rendertitle = () => {
    let search = new URLSearchParams(this.props.location.search)
    this.renderFilterByState(search)

    return (
      <h1>Videos {
          this.renderFilterByTag(search) ||
          this.renderFilterCreatedBy(search) ||
          this.renderFilterByState(search) ||
          this.renderFilterByRanking(search) ||
          this.renderFilterByMediaType(search)
        }
      </h1>
    )
  }

  render () {
    return (
      <Page header={this.rendertitle()}>
        <div className='container-fluid videoList'>
          <VideoTable
            list={this.props.contents}
            fetch={this.props.fetchVideos.bind(this)}
            location={this.props.location}
            history={this.props.history}
          />
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({list, session, tag}) {
  return {
    contents: list.videos,
    user: session.user,
    tag: tag
  }
}

export default connect(mapStateToProps,
  {
    fetchVideos,
    clearVideo,
    fetchTag
  }
)(VideoList)
