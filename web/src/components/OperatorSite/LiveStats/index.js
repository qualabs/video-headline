import React, {Component} from 'react'
import {connect} from 'react-redux'
import {fetchStats} from '../../../actions/tracking'
import LiveStatsDadshboard from '../../Stats/LiveStatsDashboard'
import Chart from '../../Stats/Chart'
import moment from 'moment'

import './index.css'

class LiveStats extends Component {
  componentDidMount () {
    const {content_id} = this.props
    const now_date = new Date()
    let date_to = now_date.toISOString()
    now_date.setHours(now_date.getHours() - 24)
    let date_from = now_date.toISOString()
    this.props.fetchStats({content_id: content_id, date_from: date_from, date_to: date_to, time_unit: 'hours'})
  }

  renderViewsPerDayChart () {
    if (this.props.tracking && this.props.tracking.stats) {
      let {stats} = this.props.tracking
      let views_per_hour = stats.views_per_hour || []

      if (views_per_hour.length === 0) {
        return null
      }
      
      let data = []
      for (let i = 0; i < views_per_hour.length; i++) {
        data.push(
          {
            playbacks: views_per_hour[i][0],
            date: moment(views_per_hour[i][1]).format('DD/MM-HH')
          }
        )
      }

      return (
        <Chart
          header='Amount of viewers per hour'
          xValue='Date - Hour'
          xDataKey='date'
          yValue='Viewers'
          yDataKey='playbacks'
          data = {data}
          height = {300}
          fill = '#36b4a7'
          styleClass='col-6'
        />
      )
    }
  }

  renderDashBoard () {
    return (
      <LiveStatsDadshboard
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
        </div>
      </div>
    )
  }
}

function mapStateToProps ({live, tracking}) {
  return {
    live,
    tracking
  }
}

export default connect(mapStateToProps, {
  fetchStats
})(LiveStats)
