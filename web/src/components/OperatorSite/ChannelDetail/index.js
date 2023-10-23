import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Route, Link} from 'react-router-dom'

import {fetchChannel, deleteChannel} from '../../../actions/channel'
import {fetchVideos} from '../../../actions/video'
import {fetchLiveVideos} from '../../../actions/live'

import Loading from '../../Loading'
import Page from '../../Page'

import ChannelSummary from './summary'
import ChannelForm from '../ChannelForm'
import VideoTable from '../Table/VideoTable'
import LiveTable from '../Table/LiveTable'
import ChannelStats from '../ChannelStats'

class ChannelDetail extends Component {
  componentDidMount () {
    const {id} = this.props.match.params
    this.props.fetchChannel(id)
  }

  componentDidUpdate (prevProps) {
    const {params} = this.props.match
    const prevParams = prevProps.match.params

    if (params.id !== prevParams.id) {
      this.props.fetchChannel(params.id)
    }
  }

  actionItems () {
    return [
      <Link className='btn btn-primary' to='/live-videos/new/'>
        <i className='fas fa-plus' /> New
      </Link>,
    ]
  }

  menuItems () {
    const {channel, tracking} = this.props
    const url = `/video-groups/${channel.id}/`
    return [
      <Link key='channel-summary' className='btn' to={url}>
        Summary
      </Link>,
      <Link key='channel-edit' className='btn' to={`${url}edit/`}>
        Edit
      </Link>,
      <Link key='channel-videos' className='btn' to={`${url}video-on-demand/`}>
        Videos On Demand
      </Link>,
      <Link key='channel-live-videos' className='btn' to={`${url}live-videos/`}>
        Live Videos
      </Link>,
      tracking.enabled && (
        <Link key='channel-stats' className='btn' to={`${url}stats/`}>
          Statistics
        </Link>
      ),
    ]
  }

  renderSummary () {
    return (
      <div className='container-fluid'>
        <ChannelSummary channel={this.props.channel} />
      </div>
    )
  }

  renderEdit () {
    return (
      <div className='container-fluid'>
        <h2>Editing</h2>
        <ChannelForm
          initialValues={{
            ...this.props.channel,
            allowed_domains: this.props.channel.allowed_domains.join(','),
            id: this.props.channel.id,
          }}
          deleteChannel={this.props.deleteChannel}
        />
      </div>
    )
  }

  renderHeader () {
    const {channel} = this.props
    return <h1>{`Video Group ${channel.name}`}</h1>
  }

  fetchVideoList (params) {
    const {id} = this.props.match.params
    this.props.fetchVideos({...params, channel__id: id})
  }

  fetchLiveVideoList (params) {
    const {id} = this.props.match.params
    this.props.fetchLiveVideos({...params, channel__id: id})
  }

  videoActions () {
    const {id} = this.props.match.params
    return [
      <Link key='video-new' className='btn btn-primary' to={`/drop/${id}`}>
        <i className='fas fa-plus' /> New
      </Link>,
    ]
  }

  renderStats () {
    const {channel} = this.props

    return (
      <div className='container-fluid'>
        <ChannelStats channel_id={channel.channel_id} />
      </div>
    )
  }

  renderVideoTable () {
    const {channel} = this.props
    return (
      <VideoTable
        list={this.props.videos}
        fetch={this.fetchVideoList.bind(this)}
        actionItems={this.videoActions()}
        table_url={`/video-groups/${channel.id}/video-on-demand`}
        location={this.props.location}
        history={this.props.history}
      />
    )
  }

  renderLiveVideoTable () {
    const {channel} = this.props
    return (
      <LiveTable
        list={this.props.live}
        fetch={this.fetchLiveVideoList.bind(this)}
        actionItems={this.actionItems()}
        table_url={`/video-groups/${channel.id}/live-videos`}
        location={this.props.location}
        history={this.props.history}
      />
    )
  }

  renderVideoList () {
    return (
      <div className='container-fluid'>
        <h2>Videos On Demand</h2>
        {this.renderVideoTable()}
      </div>
    )
  }

  renderLiveVideoList () {
    return (
      <div className='container-fluid'>
        <h2>Live Videos</h2>
        {this.renderLiveVideoTable()}
      </div>
    )
  }

  render () {
    const {channel, tracking} = this.props
    if (!channel) {
      return <Loading fullscreen={true} />
    }
    return (
      <div className='content-detail'>
        <Page header={this.renderHeader()} menuItems={this.menuItems()}>
          <Route
            key='channel-summary'
            exact
            path='/video-groups/:id/'
            render={this.renderSummary.bind(this)}
          />
          <Route
            key='route-channel-edit'
            exact
            path='/video-groups/:id/edit/'
            render={this.renderEdit.bind(this)}
          />
          <Route
            key='route-channel-videos'
            exact
            path='/video-groups/:id/video-on-demand/'
            render={this.renderVideoList.bind(this)}
          />
          <Route
            key='route-channel-live-videos'
            exact
            path='/video-groups/:id/live-videos/'
            render={this.renderLiveVideoList.bind(this)}
          />
          {tracking.enabled && (
            <Route
              key='route-video-stats'
              exact
              path='/video-groups/:id/stats/'
              render={this.renderStats.bind(this)}
            />
          )}
        </Page>
      </div>
    )
  }
}

function mapStateToProps ({channel, session, list, tracking}) {
  return {
    channel: channel.channel,
    user: session.user,
    videos: list.videos,
    live: list.liveVideos,
    tracking,
  }
}

export default connect(mapStateToProps, {
  fetchChannel,
  deleteChannel,
  fetchVideos,
  fetchLiveVideos
})(ChannelDetail)
