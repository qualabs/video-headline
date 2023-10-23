import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Switch, Route, Link} from 'react-router-dom'
import map from 'lodash/map'

import {fetchLiveVideo} from '../../../actions/live'
import {fetchIframe} from '../../../actions/security'
import Loading from '../../Loading'
import Page from '../../Page'

import LiveSummary from './summary'
import LiveForm from '../LiveForm'
import LiveStats from '../LiveStats'
import LiveVideoCuts from '../LiveVideoCuts'
import LiveVideoCutForm from '../LiveVideoCutForm'
import LiveVideoCutEdit from '../LiveVideoCutEdit'


class LiveDetail extends Component {
  componentDidMount () {
    const {id} = this.props.match.params
    this.refreshVideo(id)
    this.timerId = setInterval(() => {
      this.refreshVideo(id)
    },
    5000, id)
  }

  componentWillUnmount () {
    clearInterval(this.timerId)
  }

  componentDidUpdate (prevProps) {
    const {params} = this.props.match
    const prevParams = prevProps.match.params
    if (params.id !== prevParams.id) {
      this.props.fetchLiveVideo(params.id)
    }
  }

  refreshVideo () {
    const {params} = this.props.match
    this.props.fetchLiveVideo(params.id, false)
  }

  menuItems () {
    const {live, tracking} = this.props
    const url = `/live-videos/${live.id}/`
    return [
      <Link key='video-summary' className='btn' to={url}>Summary</Link>,
      <Link key='video-edit' className='btn' to={`${url}edit/`}>Edit</Link>,
      <Link key='video-cut' className='btn' to={`${url}cuts/`}>Cuts</Link>,
      tracking.enabled && <Link key='video-stats' className='btn' to={`${url}stats/`}>Statistics</Link>
    ]
  }

  renderStats () {
    return (
      <div className='container-fluid'>
        <LiveStats
          content_id= {this.props.live.video_id}
        />
      </div>
    )
  }

  renderSummary () {
    return (
      <div className='container-fluid'>
        <LiveSummary
          video={this.props.live}
          fetchIframe={this.props.fetchIframe}
          securityEnabled={this.props.user.organization.security_enabled}
        />
      </div>
    )
  }

  renderEdit () {
    return (
      <div className='container-fluid'>
        <h2>Editing</h2>
        <LiveForm
          initialValues={{...this.props.live,
            id: this.props.live.id,
            channel: this.props.live.channel ? this.props.live.channel.id : null,
            tags: map(this.props.live.tags, tag => tag.name)}
          }
        />
      </div>
    )
  }

  renderCuts () {
    return (
      <div className='container-fluid'>
        <LiveVideoCuts
          live={this.props.live}
          search={this.props.location.search}
        />
      </div>
    )
  }

  renderLiveVideoCutNew () {
    return (
      <div className='container-fluid'>
        <h2>New Cut</h2>
        <LiveVideoCutForm initialValues={{live: this.props.live.id}}/>
      </div>
    )
  }

  renderHeader () {
    const {live} = this.props
    return <h1>{`${live.name}`}</h1>
  }

  render () {
    const {live, tracking} = this.props
    if (!live) {
      return <Loading fullscreen={true}/>
    }
    return (
      <div className='content-detail'>
        <Page header={this.renderHeader()} menuItems={this.menuItems()}>
          <Switch>
            <Route key='live-video-summary-r' exact path='/live-videos/:id/' render={this.renderSummary.bind(this)}/>
            <Route key='route-live-video-edit' exact path='/live-videos/:id/edit/' render={this.renderEdit.bind(this)}/>
            <Route key='route-live-video-cuts' exact path='/live-videos/:id/cuts/' render={this.renderCuts.bind(this)}/>
            <Route key='route-live-video-cuts-new' exact path='/live-videos/:id/cuts/new' render={this.renderLiveVideoCutNew.bind(this)} />
            <Route key='route-live-video-cuts-id' exact path='/live-videos/:id/cuts/:cut_id' component={LiveVideoCutEdit} />
            {tracking.enabled && <Route key='route-live-video-stats' exact path='/live-videos/:id/stats/' render={this.renderStats.bind(this)}/>}
          </Switch>
        </Page>
      </div>
    )
  }
}

function mapStateToProps ({live, session, tracking}) {
  return {
    live,
    user: session.user,
    tracking
  }
}

export default connect(mapStateToProps, {
  fetchLiveVideo,
  fetchIframe,
})(LiveDetail)
