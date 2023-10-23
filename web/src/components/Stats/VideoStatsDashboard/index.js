import React, {Component} from 'react'
import Dashboard from '../../Dashboard'
import {clearDashboard} from '../../../actions/dashboard'
import {connect} from 'react-redux'

class VideoStatsDashboard extends Component {

  componentWillUnmount () {
    this.props.clearDashboard()
  }

  renderDashBoard () {
    let {showSpecificVideoInfo} = this.props

    let entries = [{
      key: 'num_loads',
      class: 'primary stats',
      title: 'Player loads',
      icon: 'fas fa-spinner',
      tooltip: 'Amount of times that the player has been loaded<br> regardless of whether the user pressed Play'
    }, {
      key: 'num_plays',
      class: 'danger stats',
      title: 'Playbacks',
      icon: 'fas fa-eye',
      tooltip: 'Amount of times the play button was pressed on the player'
    }, {
      key: 'play_rate',
      class: 'success stats',
      title: 'Play rate',
      icon: 'fas fa-percent',
      tooltip: 'Amount of playbacks <br> against amount of loads'
    }, {
      key: 'unique_players',
      class: 'warning stats',
      title: 'Uniques loads',
      icon: 'fas fa-user',
      tooltip: 'Total amount of different <br> users that have loaded the content'
    }, {
      key: 'rewatchers',
      class: 'secondary stats',
      title: 'Rewatchers',
      icon: 'fas fa-repeat',
      tooltip: 'Amount of playbacks that had <br> a duration greater than the total duration of the content'
    }, {
      key: 'skippers',
      class: 'warning stats',
      title: 'Skippers',
      icon: 'fas fa-forward',
      tooltip: 'Amount of playbacks that advanced <br> at some point the content'
    }, {
      key: 'total_time_watched',
      class: 'success stats',
      title: 'Total time viewed',
      icon: 'fas fa-clock',
      tooltip: 'Sum of the time that users <br> were playing <br> content in hh:mm:ss format',
      valueType: 'time'
    }, {
      key: 'avg_time_watched',
      class: 'info stats',
      title: 'Average time viewed',
      icon: 'fas fa-clock',
      tooltip: 'Seconds on average that <br> users were playing <br> content in format d hh:mm:ss',
      valueType: 'time'
    }]

    if (showSpecificVideoInfo) {
      entries.push({
        key: 'avg_time_reached',
        class: 'primary stats',
        title: 'Average reached',
        icon: 'fas fa-percent',
        tooltip: 'Average of maximum time that users <br> reached',
        valueType: 'percent',
        render: (value) => {
          let {data} = this.props
          if (data) {
            return (data.duration ? (value / data.duration * 100).toFixed(2) : '0.00')
          }
          return '...'
        }
      }, {
        key: 'max_time',
        class: 'danger stats',
        title: 'Maximum time reached',
        icon: 'fas fa-clock',
        tooltip: 'Maximum time reached by some user',
        valueType: 'time'
      })
    }

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

export default connect(null, {clearDashboard})(VideoStatsDashboard)
