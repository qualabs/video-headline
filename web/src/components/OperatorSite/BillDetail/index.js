import React, {Component} from 'react'
import {connect} from 'react-redux'
import CustomProgressBar from '../../ProgressBar'

import Page from '../../Page'
import Chart, {StackedAreaChart} from '../../Stats/Chart'
import Loading from '../../Loading'

import {DummyTable} from '../../Table'

import {merge} from 'lodash'

import {fetchBill} from '../../../actions/bill'
import {toNumericMonth, toNumericDateNoTime, humanizeDate} from '../../../utils/formatDate'

import './index.css'

class BillDetail extends Component {
  componentDidMount () {
    const {id} = this.props.match.params
    this.props.fetchBill(id)
  }

  renderUsageProgress () {
    const {bill} = this.props

    return (
      <div className='stats'>
        <li>
          <div className='col-xl-12'>
            <div className='property'><i className='fas fa-fw fa-database'></i> Storage used</div>
            <CustomProgressBar value={bill.storage} maxValue={bill.plan.storage} units='GB'/>
          </div>
        </li>
        <li>
          <div className='col-xl-12'>
            <div className='property'><i className='fas fa-fw fa-file-video'></i> Minutes of uploaded videos</div>
            <CustomProgressBar value={bill.video_transcoding} maxValue={bill.plan.video_transcoding} units='Minutes'/>
          </div>
        </li>
        <li>
          <div className='col-xl-12'>
            <div className='property'><i className='fas fa-fw fa-file-video'></i> Minutes of uploaded audios</div>
            <CustomProgressBar value={bill.audio_transcoding} maxValue={bill.plan.audio_transcoding} units='Minutes'/>
          </div>
        </li>
        <li>
          <div className='col-xl-12'>
            <div className='property'><i className='fas fa-fw fa-chart-network'></i> Data transferred </div>
            <CustomProgressBar value={bill.data_transfer} maxValue={bill.plan.data_transfer} units='GB'/>
          </div>
        </li>
      </div>
    )
  }

  renderDataTransferChart () {
    const {bill} = this.props

    if (bill && bill.extras.traffic_per_day) {
      let dataTransfer = bill.extras.traffic_per_day

      let data = []
      for (let i = 0; i < dataTransfer.length; i++) {
        data.push(
          {
            transferred: parseFloat(dataTransfer[i][0].toFixed(3)),
            date: toNumericDateNoTime(dataTransfer[i][1])
          }
        )
      }

      return (
        <Chart
          header='Transfer'
          xDataKey='date'
          yValue='Gb transferred'
          yDataKey='transferred'
          data={data}
          height={300}
          fill='#36b4a7'
        />
      )
    }
  }

  renderChannelDataTransferChart () {
    const {bill} = this.props

    if (bill && bill.extras.usage_per_channel) {
      let {usage_per_channel} = bill.extras

      let data = {}
      let areas = []

      Object.keys(usage_per_channel).forEach(channel_key => {
        let channel = usage_per_channel[channel_key]
        let {traffic_per_day} = channel
        areas.push(channel.name)

        Object.keys(traffic_per_day).forEach(day => {
          data[day] = merge(data[day], {[channel.name]: traffic_per_day[day]})
        })
      })

      let lines = []
      Object.keys(data).forEach(key => {
        let line = {
          'date': toNumericDateNoTime(key),
          ...data[key]
        }

        lines.push(line)
      })

      return (
        <StackedAreaChart
          header='Transfer by video group'
          yValue='Gb transferred'
          xDataKey='date'
          data={lines}
          areas={areas}
          height={300}
          tooltipFormatter={(value, name) => {return [`${value} GB`, name]}}
        />
      )
    }
  }

  getTableColumns () {
    return [{
      Header: 'Video Group',
      accessor: 'name',
    },
    {
      Header: 'Storage (GB)',
      accessor: 'storage',
    },
    {
      Header: 'Video minutes',
      accessor: 'video_transcoding',
    },
    {
      Header: 'Audio minutes',
      accessor: 'audio_transcoding',
    },
    {
      Header: 'Transferred Data (GB)',
      accessor: 'data_transfer',
    },
    ]
  }

  renderChannelDataResume () {
    const {bill} = this.props

    if (bill && bill.extras.usage_per_channel) {
      let {usage_per_channel} = bill.extras

      let elementKeys = Object.keys(usage_per_channel)

      let rows = []
      rows = elementKeys.map(key => {
        let channel_usage = usage_per_channel[key]
        let {name, storage, data_transfer, transcoding} = channel_usage

        return {
          name: name,
          storage: storage,
          video_transcoding: transcoding.hasOwnProperty('video') ? transcoding.video : transcoding,
          audio_transcoding: transcoding.hasOwnProperty('audio') ? transcoding.audio : 0,
          data_transfer: parseFloat(data_transfer.toFixed(3))
        }
      })

      return (
        <DummyTable
          columns={this.getTableColumns()}
          data={rows}
        />
      )
    }
  }

  render () {
    const {bill} = this.props

    if (!bill) {
      return <Loading fullscreen={true}/>
    }

    return (
      <Page header={<h1>Report {toNumericMonth(bill.date)}</h1>}>
        <div className='container-fluid'>
          <div className='row summary'>
            <div className='col-sm-12 col-md-12 col-xl-6'>
              <div className='detail'>
                <ul className='properties'>
                  <li>
                    <div className='col-xl-12'>
                      <div className='property'><i className='fas fa-fw fa-file-signature'></i> Plan</div>
                      {bill.plan.name}
                    </div>
                  </li>

                  <li>
                    <div className='col-xl-12'>
                      <div className='property'><i className='fas fa-fw fa-calendar-day'></i> Last Update</div>
                      {humanizeDate(bill.last_modified)}
                    </div>
                  </li>

                  {this.renderUsageProgress()}
                </ul>
              </div>
            </div>

            <div className='col-sm-12 col-md-12 col-xl-6 top-buffer'>
              {this.renderDataTransferChart()}
            </div>
          </div>
          <div className='row'>
            <div className='col-sm-12 col-md-12 col-xl-6'>
              {this.renderChannelDataResume()}
            </div>
            <div className='col-sm-12 col-md-12 col-xl-6 top-buffer'>
              {this.renderChannelDataTransferChart()}
            </div>
          </div>
          <div className='row'>
            <div className='col'>

            </div>
          </div>
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({session, bill}) {
  return {
    user: session.user,
    bill
  }
}

export default connect(mapStateToProps, {fetchBill})(BillDetail)
