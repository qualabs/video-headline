import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Link} from 'react-router-dom'
import Loading from '../Loading'
import ReactTooltip from 'react-tooltip'
import {convertDHMS} from '../../utils/formatDate'

import './index.css'

export function DashboardEntry (props) {
  let entry = <div className={`dashboard-inner ${props.class}`}>
    <div className='dashboard-icon'>
      <i className={`fas fa-fw fa-4x ${props.icon}`} />
    </div>
    <div className='dashboard-data'>
      {renderValue(props.value, props.valueType, props.render)}
      <div className='dashboard-title'>{props.title}</div>
    </div>
  </div>

  if (props.link) {
    return (
      <Link to={props.link} className='dashboard-entry' data-tip={props.tooltip}>
        {renderToolTip()}
        {entry}
      </Link>
    )
  } else {
    return (
      <div className='dashboard-entry' data-tip={props.tooltip}>
        {renderToolTip()}
        {entry}
      </div>
    )
  }
}

function renderToolTip () {
  return (
    <ReactTooltip place='top' type='dark' effect='float' html={true}/>
  )
}

function renderValue (value, valueType, render) {

  let val = value
  if (render) {
    val = render(value)
  }

  switch (valueType) {
    case 'time':
      return (<div className='dashboard-value-sm'>{convertDHMS(val)}</div>)

    default:
      return (<div className='dashboard-value'>{val}</div>)
  }
}

class Dashboard extends Component {
  render () {
    let dashboard

    if (this.props.data) {
      dashboard = this.props.data
    } else {
      dashboard = this.props.dashboard
    }

    if (!dashboard) {
      return <Loading fullscreen={true}/>
    }
    return (
      <div className='dashboard container-fluid top-buffer'>
        {this.props.entries.map(entry => {
          return (
            <DashboardEntry
              key={entry.key}
              value={dashboard[entry.key] !== undefined ? dashboard[entry.key] : '...'}
              valueType={entry.valueType || null}
              title={entry.title}
              icon={entry.icon}
              link={entry.link}
              class={entry.class}
              tooltip={entry.tooltip || null}
              render={entry.render}
            />
          )
        })}
      </div>
    )
  }
}

export default connect(state => {
  return {
    dashboard: state.dashboardPage.dashboard
  }
})(Dashboard)
