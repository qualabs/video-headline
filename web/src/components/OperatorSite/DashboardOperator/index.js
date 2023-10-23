import React, {Component} from 'react'
import {connect} from 'react-redux'

import Page from '../../Page'
import Dashboard from '../../Dashboard'
import Chart from '../../Stats/Chart'

import {fetchDashboard} from '../../../actions/dashboard'
import {setMessage} from '../../../actions/flashMessage'
import {NOT_FINISHED, FAILED} from '../utils/stepper'
import {toNumericDateNoTime} from '../../../utils/formatDate'

const FETCH_DASHBOARD_INTERVAL = 30 * 1000 // 30 seconds

class DashboardOperator extends Component {
  constructor () {
    super()
    this.dashboardInterval = null
  }

  componentDidMount () {
    this.props.fetchDashboard()
    this.dashboardInterval = window.setInterval(
      this.props.fetchDashboard,
      FETCH_DASHBOARD_INTERVAL
    )
  }

  componentWillUnmount () {
    window.clearInterval(this.dashboardInterval)
  }

  renderDashboard () {
    const {user} = this.props

    const entries = [{
      key: 'videos_in_process',
      class: 'primary stats',
      title: 'Videos in process',
      icon: 'fas fa-fw fa-spinner',
      link: `/video-on-demand/?state=${NOT_FINISHED}`
    }, {
      key: 'failed_videos',
      class: 'danger stats',
      title: 'Failed videos',
      icon: 'fas fa-exclamation-circle',
      link: `/video-on-demand/?state=${FAILED}`
    }, {
      key: 'uploaded_by_user',
      class: 'warning stats',
      title: 'Videos uploaded by me',
      icon: 'fas fa-play',
      link: `/video-on-demand/?created_by__username=${user.username}`
    }, {
      key: 'uploaded_by_org',
      class: 'info stats',
      title: 'Organization videos',
      icon: 'fas fa-fw fa-film',
      link: '/video-on-demand/'
    }, {
      key: 'live_videos_by_org',
      class: 'success stats',
      title: 'Live videos of the Organization',
      icon: 'fas fa-fw fa-video',
      link: '/live-videos/'
    }]

    if (this.props.tracking.enabled) {
      entries.push({
        key: 'views_last_day',
        class: 'success stats',
        title: 'Last day playbacks',
        icon: 'fa fa-eye'
      })
      entries.push({
        key: 'count_views_last_seven_days',
        class: 'primary stats',
        title: 'Last 7 days playbacks',
        icon: 'fa fa-eye'
      })
    }

    return (
      <Dashboard
        entries={entries}
      />
    )
  }

  renderLastSevenDaysChart () {
    const {dashboard} = this.props
    if (dashboard && dashboard.views_last_seven_days) {
      let {views_per_day} = dashboard.views_last_seven_days

      if (views_per_day.length === 0) {
        return null
      }

      let data = []
      for (let i = 0; i < views_per_day.length; i++) {
        data.push(
          {
            playbacks: views_per_day[i][0],
            date: toNumericDateNoTime(views_per_day[i][1])
          }
        )
      }

      return (
        <Chart
          header='Last 7 days playbacks'
          xValue='Date'
          xDataKey='Date'
          yValue='Number of playbacks'
          yDataKey='playbacks'
          data = {data}
          height = {300}
          fill = '#36b4a7'
        />
      )
    }
  }

  render () {
    return (
      <Page header={<h1>Dashboard</h1>}>
        <div className='row'>
          <div className='col-6'>
            {this.renderDashboard()}
          </div>
          <div className='col-6 top-buffer'>
            {this.renderLastSevenDaysChart()}
          </div>
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({session, dashboardPage, tracking}) {
  return {
    user: session.user,
    dashboard: dashboardPage.dashboard,
    tracking,
  }
}

export default connect(mapStateToProps, {fetchDashboard, setMessage})(DashboardOperator)
