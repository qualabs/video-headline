import React, {Component} from 'react'
import {connect} from 'react-redux'
import {fetchStats} from '../../../actions/tracking'
import VideoStatsDashboard from '../../Stats/VideoStatsDashboard'
import Chart from '../../Stats/Chart'
import {toNumericDateNoTime} from '../../../utils/formatDate'

import './index.css'

class ChannelStats extends Component {
  componentDidMount () {
    const {channel_id} = this.props

    const now_date = new Date()
    now_date.setDate(now_date.getDate() - 7)
    let last_seven_days = now_date.toISOString()

    this.props.fetchStats({
      channel_id: channel_id,
      date_from: last_seven_days
    })
  }

  renderViewsPerDayChart () {
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let {views_per_day} = stats

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
          xDataKey='date'
          yValue='Playbacks'
          yDataKey='playbacks'
          data={data}
          height={300}
          fill='#36b4a7'
        />
      )
    }
  }

  renderDashBoard () {
    return (
      <VideoStatsDashboard
        data={this.props.tracking.stats}
        styleClass='col-6'
        showSpecificVideoInfo = {false}
      />
    )
  }

  render () {
    return (
      <div className='row'>
        {this.renderDashBoard()}
        <div className='col-6 top-buffer'>
          {this.renderViewsPerDayChart()}
        </div>
      </div>
    )
  }
}

function mapStateToProps ({video, tracking}) {
  return {
    video,
    tracking
  }
}

export default connect(mapStateToProps, {
  fetchStats
})(ChannelStats)
