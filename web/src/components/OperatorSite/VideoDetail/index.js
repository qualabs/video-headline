import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Route, Link} from 'react-router-dom'
import map from 'lodash/map'
import omit from 'lodash/omit'

import {fetchVideo, fetchVideoState} from '../../../actions/video'
import {fetchIframe} from '../../../actions/security'
import Loading from '../../Loading'
import Page from '../../Page'

import VideoSummary from './summary'
import VideoForm from '../VideoForm'
import VideoStats from '../VideoStats'


class VideoDetail extends Component {

  componentDidMount () {
    const {id} = this.props.match.params
    this.props.fetchVideo(id)
  }

  componentDidUpdate (prevProps) {
    const {params} = this.props.match
    const prevParams = prevProps.match.params

    if (params !== prevParams) {
      this.props.fetchVideo(params.id)
    }
  }

  menuItems () {
    const {video, tracking} = this.props

    const url = `/video-on-demand/${video.id}/`
    return [
      <Link key='video-summary' className='btn' to={url}>Summary</Link>,
      <Link key='video-edit' className='btn' to={`${url}edit/`}>Edit</Link>,
      tracking.enabled && <Link key='video-stats' className='btn' to={`${url}stats/`}>Statistics</Link>
    ]
  }

  renderStats () {
    return (
      <div className='container-fluid'>
        <VideoStats
          content_id= {this.props.video.video_id}
        />
      </div>
    )
  }

  renderSummary () {
    return (
      <div className='container-fluid'>
        <VideoSummary
          video={this.props.video}
          fetchVideoState={this.props.fetchVideoState}
          fetchIframe={this.props.fetchIframe}
          securityEnabled={this.props.user.organization.security_enabled}
        />
      </div>
    )
  }

  renderEdit () {
    const videoProps = omit(this.props.video, ['has_thumbnail'])
    return (
      <div className='container-fluid'>
        <h2>Editing</h2>
        <VideoForm
          initialValues={{...videoProps,
            id: this.props.video.id,
            channel: this.props.video.channel ? this.props.video.channel.id : null,
            tags: map(this.props.video.tags, tag => tag.name)}
          }
        />
      </div>
    )
  }

  renderHeader () {
    const {video} = this.props
    return <h1>{`${video.name}`}</h1>
  }

  render () {
    const {video, tracking} = this.props
    if (!video) {
      return <Loading fullscreen={true}/>
    }
    return (
      <div className='content-detail'>
        <Page header={this.renderHeader()} menuItems={this.menuItems()}>
          <Route key='video-summary-r' exact path='/video-on-demand/:id/' render={this.renderSummary.bind(this)}/>
          <Route key='route-video-edit' exact path='/video-on-demand/:id/edit/' render={this.renderEdit.bind(this)}/>
          {tracking.enabled && <Route key='route-video-stats' exact path='/video-on-demand/:id/stats/' render={this.renderStats.bind(this)}/>}
        </Page>
      </div>
    )
  }
}

function mapStateToProps ({video, session, tracking, security}) {
  return {
    video,
    user: session.user,
    tracking,
    security
  }
}

export default connect(mapStateToProps, {
  fetchVideo,
  fetchVideoState,
  fetchIframe
})(VideoDetail)
