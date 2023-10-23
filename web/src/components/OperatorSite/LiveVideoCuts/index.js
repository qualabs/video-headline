import React, {Component} from 'react'
import {connect} from 'react-redux'

import CutTable from '../Table/CutTable'

import {SCHEDULED, EXECUTING, PERFORMED} from '../utils/stepper'

import {fetchLiveVideoCuts, clearLiveVideoCuts} from '../../../actions/cuts'

class LiveVideoCuts extends Component {

  componentDidMount () {
    this.props.clearLiveVideoCuts()
  }

  renderFilterByState (search) {
    let state = search.get('state')

    if (state === SCHEDULED) {
      return (
        'scheduled'
      )
    }
    if (state === EXECUTING) {
      return (
        'executing'
      )
    }
    if (state === PERFORMED) {
      return (
        'performed'
      )
    }
  }

  fetchLiveCuts (params) {
    this.props.fetchLiveVideoCuts(this.props.live.id, params)
  }

  rendertitle () {
    let search = new URLSearchParams(this.props.search)
    this.renderFilterByState(search)

    return (
      <h2>Cuts {
        this.renderFilterByState(search) }
      </h2>
    )
  }

  render () {
    return (
      <div className='container-fluid'>
        {this.rendertitle()}
        <CutTable
          list={this.props.contents}
          fetch={this.fetchLiveCuts.bind(this)}
          id={this.props.live.id}
        />
      </div>
    )
  }
}

function mapStateToProps ({list, session}) {
  return {
    contents: list.cuts,
    user: session.user,
  }
}

export default connect(mapStateToProps,
  {
    fetchLiveVideoCuts,
    clearLiveVideoCuts,
  })(LiveVideoCuts)
