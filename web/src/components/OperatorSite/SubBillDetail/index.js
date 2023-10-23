import React, {Component} from 'react'
import {connect} from 'react-redux'
import CustomProgressBar from '../../ProgressBar'

import Page from '../../Page'
import Chart from '../../Stats/Chart'
import Loading from '../../Loading'

import {toNumericDateNoTime, humanizeDate} from '../../../utils/formatDate'
import {fetchSubBill} from '../../../actions/bill'
import './index.css'

class SubBillDetail extends Component {

  componentDidMount () {
    let {id} = this.props
    this.props.fetchSubBill(id, false)

  }

  renderUsageProgress () {
    if (this.props.subBill && this.props.subBill[this.props.id]) {
      const subBill = this.props.subBill[this.props.id]
      return (
        <div className='stats'>
          <li>
            <div className='col-xl-12'>
              <div className='property'><i className='fas fa-fw fa-database'></i> Storage used </div>
              <CustomProgressBar value={subBill.storage} maxValue={subBill.plan.storage} units='GB'/>
            </div>
          </li>
          <li>
            <div className='col-xl-12'>
              <div className='property'><i className='fas fa-fw fa-file-video'></i> Minutes of video uploaded</div>
              <CustomProgressBar value={subBill.video_transcoding} maxValue={subBill.plan.video_transcoding} units='Minutes'/>
            </div>
          </li>
          <li>
            <div className='col-xl-12'>
              <div className='property'><i className='fas fa-fw fa-file-audio'></i> Minutes of audio uploaded</div>
              <CustomProgressBar value={subBill.audio_transcoding} maxValue={subBill.plan.audio_transcoding} units='Minutes'/>
            </div>
          </li>
          <li>
            <div className='col-xl-12'>
              <div className='property'><i className='fas fa-fw fa-chart-network'></i> Transferred data</div>
              <CustomProgressBar value={subBill.data_transfer} maxValue={subBill.plan.data_transfer} units='GB'/>
            </div>
          </li>
        </div>
      )
    } else {
      return <Loading fullscreen={true}/>
    }

  }

  renderDataTransferChart () {
    if (this.props.subBill && this.props.subBill[this.props.id]) {
      const subBill = this.props.subBill[this.props.id]
      if (subBill && subBill.extras.traffic_per_day) {
        let dataTransfer = subBill.extras.traffic_per_day

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
            yValue='GB transferred'
            yDataKey='transferred'
            data={data}
            height={300}
            fill='#36b4a7'
          />
        )
      }
    } else {
      return <Loading fullscreen={true}/>
    }
  }

  render () {
    if (this.props.subBill && this.props.subBill[this.props.id]) {
      const subBill = this.props.subBill[this.props.id]
      return (
        <Page>
          <div className='container-fluid'>
            <div className='row summary'>
              <div className='col-md-12 col-xl-6'>
                <div className='detail'>
                  <ul className='properties'>
                    <li>
                      <div className='col-xl-12'>
                        <div className='property'><i className='fas fa-fw fa-file-signature'></i> Plan</div>
                        {subBill.plan.name}
                      </div>
                    </li>
                    <li>
                      <div className='col-xl-12'>
                        <div className='property'><i className='fas fa-fw fa-calendar-day'></i> Last updated date</div>
                        {humanizeDate(subBill.last_modified)}
                      </div>
                    </li>
                    {this.renderUsageProgress()}
                  </ul>
                </div>
              </div>

              <div className='col-6 top-buffer'>
                {this.renderDataTransferChart()}
              </div>
            </div>
          </div>
        </Page>
      )
    } else {
      return <Loading fullscreen={true}/>
    }
  }
}

function mapStateToProps ({session, subBill}) {
  return {
    user: session.user,
    subBill,
  }
}

export default connect(mapStateToProps, {
  fetchSubBill
})(SubBillDetail)
