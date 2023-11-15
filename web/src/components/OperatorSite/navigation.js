import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Switch, Route, Link} from 'react-router-dom'
import history from '../../history'

import DashboardOperator from './DashboardOperator'
import VideoList from './VideoList'
import VideoDetail from './VideoDetail'
import VideoNew from './VideoNew'
import ChannelList from './ChannelList'
import ChangePassword from './ChangePassword'
import ChannelNew from './ChannelNew'
import LiveNew from './LiveNew'
import ChannelDetail from './ChannelDetail'
import VideoUploadPage from './VideoUploadPage'
import AudioUploadPage from './AudioUploadPage'
import LiveList from './LiveList'
import BillList from './BillList'

import {clearVideo} from '../../actions/video'
import LiveDetail from './LiveDetail'
import BillDetail from './BillDetail'
import Monitor from './Monitor'
let FASTChannelDashboard, CreateNewChannel, CreateAdConfiguration, Scheduler;

if (isSshKeyAvailable()) {
  ({ FASTChannelDashboard, CreateNewChannel, CreateAdConfiguration, Scheduler } =import('video-headline-fast-channels/dist'));
}

export class OperatorRoutes extends Component {
  constructor (props) {
    super(props)
    this.config = this.props.user.organization.config
  }
  render () {
    return (
      <Switch>
        {this.config && FASTChannelDashboard && (
        <Route exact path='/fast-channels/' render={(props) => <FASTChannelDashboard history={history}
          routes={{newChannel: '/fast-channels/channel/new',
            newAd: '/fast-channels/ad/new',
            scheduler: '/fast-channels/scheduler'}}
          {...props}
        />}
        />
        )}
        {this.config && FASTCCreateNewChannelhannelDashboard && ( <Route exact path='/fast-channels/channel/new/' component={CreateNewChannel}/>)}
        {this.config && CreateAdConfiguration && (<Route exact path='/fast-channels/ad/new/' component={CreateAdConfiguration}/>)}
        {this.config && Scheduler &&  (<Route exact path='/fast-channels/scheduler/:id/'  render={(props) =>
          isSshKeyAvailable() ? <Scheduler history={history} {...props} /> : <Redirect to='/' />
        }/> )}
  

        <Route exact path='/video-on-demand/new/' component={VideoNew} />
        <Route exact path='/video-on-demand/:id/*/' component={VideoDetail} />
        <Route exact path='/video-on-demand/:id/' component={VideoDetail} />
        <Route exact path='/video-on-demand/' component={VideoList} />

        <Route exact path='/live-videos/new/' component={LiveNew} />
        <Route exact path='/live-videos/:id/*' component={LiveDetail} />
        <Route exact path='/live-videos/:id' component={LiveDetail} />
        <Route exact path='/live-videos/' component={LiveList} />

        <Route exact path='/video-groups/new/' component={ChannelNew} />
        <Route exact path='/video-groups/:id/*/' component={ChannelDetail} />
        <Route exact path='/video-groups/:id/' component={ChannelDetail} />
        <Route exact path='/video-groups/' component={ChannelList} />

        <Route exact path='/bills/:id/' component={BillDetail} />
        <Route exact path='/bills/' component={BillList} />

        <Route exact path='/drop/:video-group_id/' component={VideoUploadPage} />
        <Route exact path='/drop/' component={VideoUploadPage} />

        <Route
          exact
          path='/drop-audio/:video-group_id/'
          render={(props) => <AudioUploadPage isAudio={true} {...props} />}
        />
        <Route
          exact
          path='/drop-audio/'
          render={(props) => <AudioUploadPage isAudio={true} {...props} />}
        />
        <Route exact path='/monitor/' component={Monitor} />

        <Route exact path='/change-password/' component={ChangePassword} />
        <Route exact path='/' component={DashboardOperator} />
        <Route path='*' render={() => <div>{history.push('/')}</div>} />

        
        
      </Switch>
    )
  }
}

class OperatorMenu extends Component {
  renderChannels () {
    const {channels} = this.props
    if (channels) {
      let links = channels.results.map((videoGroup) => {
        let url = `/video-groups/${videoGroup.id}/video-on-demand`
        return (
          <li key={videoGroup.id}>
            <Link className='btn channels' to={url}>
              <i className='fas fa-fw fa-angle-right'/>
              {videoGroup.name}
            </Link>
          </li>
        )
      })

      return links
    }
  }

  renderMonitor () {
    if (this.props.monitorEnabled) {
      return (
        <li><Link className='btn' to='/monitor/'><i className='fas fa-fw fa-chart-network'/> Monitoring (Beta)</Link></li>
      )
    }
  }

  render () {
    return (
      <React.Fragment>
        <li className='new-video'><Link className='btn' to='/drop/' onClick={this.props.clearVideo}><i className='fas fa-fw fa-plus'/> New Video</Link></li>
        <li className='new-audio'><Link className='btn' to='/drop-audio/' onClick={this.props.clearVideo}><i className='fas fa-fw fa-plus'/> New Audio</Link></li>
        <li><Link className='btn' to='/'><i className='fas fa-fw fa-home'/> Dashboard</Link></li>
        <li><Link className='btn' to='/video-on-demand/'><i className='fas fa-fw fa-film'/> Videos On Demand</Link></li>
        <li><Link className='btn' to='/live-videos/'><i className='fas fa-fw fa-video'/> Live Videos</Link></li>
        <li><Link className='btn' to='/video-groups/'><i className='fas fa-fw fa-tv'/> Video Groups</Link></li>
        <li><Link className='btn' to='/fast-channels/'><i className='fas fa-fw fa-tv'/> Fast Channels</Link></li>
        {this.renderChannels()}
        <li><Link className='btn' to='/bills/'><i className='fas fa-fw fa-calculator'/> Usage Report</Link></li>
        {this.renderMonitor()}
        <li><Link className='btn' to='/change-password/'><i className='fas fa-fw fa-cog'/> Change Password</Link></li>
      </React.Fragment>
    )
  }
}

function mapStateToProps ({list, monitor}) {
  return {
    channels: list.channels,
    monitorEnabled: monitor.enabled
  }
}

export default connect(mapStateToProps, {clearVideo})(OperatorMenu)
