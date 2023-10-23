import React, {Component} from 'react'
import {connect} from 'react-redux'

import Page from '../../Page'
import Chart from '../../Stats/Chart'
import Loading from '../../Loading'

import {toNumericTime} from '../../../utils/formatDate'
import {fetchMonitorStats} from '../../../actions/monitor'

import './index.css'
import Dashboard from '../../Dashboard'

class Monitor extends Component {
  constructor () {
    super()
    this.interval = null
  }


  componentDidMount () {
    this.props.fetchMonitorStats()
    this.interval = setInterval(() => this.props.fetchMonitorStats(), 3 * 60 * 1000)
  }

  componentWillUnmount () {
    if (this.interval) {
      clearInterval(this.interval)
    }
  }

  renderDataTransferChart () {
    const {stats} = this.props.monitor

    if (stats && stats.detail) {
      let dataTransfer = stats.detail.map((val) => {
        return {
          transferred: parseFloat(val.value.toFixed(3)),
          date: toNumericTime(val.date)
        }
      })

      return (
        <Chart
          header='Last 12 Hours'
          xDataKey='date'
          yValue='GB transferred'
          yDataKey='transferred'
          data={dataTransfer}
          height={300}
          fill='#36b4a7'
        />
      )
    }
  }

  renderDashboard () {
    const entries = [
      {
        key: 'total_period',
        class: 'success stats text-sm',
        title: 'Transferred last 12 Hours',
        icon: 'fas fa-fw fa-chart-network',
        render: (value) => `${(value).toFixed(2)} GB`
      },
      {
        key: 'total',
        class: 'primary stats text-sm',
        title: 'Total transferred in the month',
        icon: 'fas fa-fw fa-chart-network',
        render: (value) => `${(value / 1024).toFixed(2)} TB`
      }
    ]

    return (
      <Dashboard
        data={this.props.monitor.stats}
        entries={entries}
      />
    )
  }

  render () {
    const {stats} = this.props.monitor

    if (!stats) {
      return <Loading fullscreen={true}/>
    }

    return (
      <Page header={<h1>Monitoring of transferred data (Beta)</h1>}>
        <div className='container-fluid'>
          <div className='row summary'>
            <div className='col-sm-12 col-md-12 col-xl-12 top-buffer'>
              {this.renderDataTransferChart()}
              {this.renderDashboard()}
            </div>
          </div>
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({monitor}) {
  return {monitor}
}

export default connect(mapStateToProps, {fetchMonitorStats})(Monitor)
