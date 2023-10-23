import React, {Component} from 'react'
import {connect} from 'react-redux'

import {fetchLiveVideoCut} from '../../../actions/cuts'
import LiveVideoCutForm from '../LiveVideoCutForm'


class LiveVideoCutEdit extends Component {
  componentDidMount () {
    const {cut_id} = this.props.match.params

    if (cut_id) {
      this.props.fetchLiveVideoCut(cut_id)
    }
  }

  render () {
    return (
      <div className='container-fluid'>
        <h2>Editing Cut</h2>
        <LiveVideoCutForm initialValues={{...this.props.cut}}/>
      </div>
    )
  }
}

function mapStateToProps ({cut}) {
  return {
    cut
  }
}

export default connect(mapStateToProps, {
  fetchLiveVideoCut,
})(LiveVideoCutEdit)
