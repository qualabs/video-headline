import React, {Component} from 'react'
import Dashboard from '../../Dashboard'
import {clearDashboard} from '../../../actions/dashboard'
import {connect} from 'react-redux'

class LiveStatsDashboard extends Component {

  componentWillUnmount () {
    this.props.clearDashboard()
  }

  renderDashBoard () {
    let entries = [{
      key: 'num_loads',
      class: 'primary stats',
      title: 'Streaming loads',
      icon: 'fas fa-spinner',
      tooltip: 'Number of times the player has been loaded <br> regardless of whether the user gave play to the live-video'
    }, {
      key: 'num_plays',
      class: 'danger stats',
      title: 'Views',
      icon: 'fas fa-eye',
      tooltip: 'Number of times the play button was pressed on the player'
    }, {
      key: 'play_rate',
      class: 'success stats',
      title: 'Views Rate',
      icon: 'fas fa-percent',
      tooltip: 'Number of views <br> against amount of loads'
    }, {
      key: 'unique_players',
      class: 'warning stats',
      title: 'Unique loads',
      icon: 'fas fa-user',
      tooltip: 'Total number of different <br> users who uploaded the live-video'
    }, {
      key: 'total_time_watched',
      class: 'secondary stats',
      title: 'Total time watched',
      icon: 'fas fa-clock',
      tooltip: 'Suma del tiempo que los usuarios <br> estuvieron reproduciendo el <br> live-video en formato d hh:mm:ss',
      valueType: 'time'
    }, {
      key: 'avg_time_watched',
      class: 'info stats',
      title: 'Average time viewed',
      icon: 'fas fa-clock',
      tooltip: 'Seconds on average that the <br> users were playing the <br> live-video in d hh:mm:ss format',
      valueType: 'time'
    }]

    return (
      <div className={this.props.styleClass}>
        <Dashboard
          data={this.props.data}
          entries={entries}
        />
      </div>
    )
  }

  render () {
    return (
        <>
            {this.renderDashBoard()}
        </>
    )
  }
}

export default connect(null, {clearDashboard})(LiveStatsDashboard)
