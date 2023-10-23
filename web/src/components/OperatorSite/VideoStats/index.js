import React, {Component} from 'react'
import {connect} from 'react-redux'
import {fetchStats} from '../../../actions/tracking'
import VideoStatsDashboard from '../../Stats/VideoStatsDashboard'
import Chart, {SimpleBarChart} from '../../Stats/Chart'
import {toNumericDateNoTime, secondsToMinutes} from '../../../utils/formatDate'

import './index.css'

class VideoStats extends Component {
  componentDidMount () {
    const {content_id} = this.props
    this.props.fetchStats({content_id: content_id})
  }

  renderViewsPerDayChart () {
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let views_per_day = stats.views_per_day || []

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
          header='Playbacks per day'
          xValue='Date'
          xDataKey='Date'
          yValue='Number of Playbacks'
          yDataKey='playbacks'
          data = {data}
          height = {300}
          fill = '#36b4a7'
          styleClass='col-6'
        />
      )
    }
  }

  renderProgressSeenChart () {
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let progress_seen = stats.progress_seen || []

      if (progress_seen.length === 0) {
        return null
      }

      let data = []
      for (let i = 0; i < progress_seen.length; i++) {
        data.push(
          {
            seconds: secondsToMinutes(progress_seen[i][0]),
            playbacks: progress_seen[i][1]
          }
        )
      }

      return (
        <Chart
          header='Progress achieved'
          xValue='Time'
          xDataKey='seconds'
          yValue='playbacks'
          yDataKey='playbacks'
          data={data}
          height={300}
          fill='#ea7979'
        />
      )
    }
  }

  renderDropoutsChart () {
    
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let dropouts = stats.dropouts || []

      if (dropouts.length === 0) {
        return null
      }

      let data = []
      for (let i = 0; i < dropouts.length; i++) {
        data.push(
          {
            seconds: secondsToMinutes(dropouts[i][0]),
            dropouts: dropouts[i][1]
          }
        )
      }


      return (
        <SimpleBarChart
          header='Dropout time'
          xValue='Maximum time achieved'
          xDataKey='seconds'
          yValue='Amount of dropouts'
          yDataKey='dropouts'
          data={data}
          height={300}
          fill='#ea7979'
        />
      )
    }
  }

  renderDropoutsAccumChart () {
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let dropouts_accum = stats.dropouts_accum || []

      if (dropouts_accum.length === 0) {
        return null
      }

      let data = []
      for (let i = 0; i < dropouts_accum.length; i++) {
        data.push(
          {
            seconds: secondsToMinutes(dropouts_accum[i][0]),
            dropouts: dropouts_accum[i][1]
          }
        )
      }


      return (
        <Chart
          header='Accumulated dropouts'
          xValue='Time'
          xDataKey='seconds'
          yValue='Amount of dropouts'
          yDataKey='dropouts'
          data={data}
          height={300}
          fill='#ea7979'
        />
      )
    }
  }
  renderDashBoard () {
    return (
      <VideoStatsDashboard
        data={this.props.tracking.stats}
        styleClass='col-6'
        showSpecificVideoInfo = {true}
      />
    )
  }

  render () {
    return (
      <div className='row'>
        {this.renderDashBoard()}
        <div className='col-6 top-buffer'>
          {this.renderViewsPerDayChart()}
          {this.renderProgressSeenChart()}
          {this.renderDropoutsChart()}
          {this.renderDropoutsAccumChart()}
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
})(VideoStats)
