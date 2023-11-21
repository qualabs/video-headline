import React, {Component} from 'react'
import {connect} from 'react-redux'
import {fetchLiveVideos, clearLiveVideo} from '../../../actions/live'
import {fetchTag} from '../../../actions/tags'
import Page from '../../Page'
import LiveTable from '../Table/LiveTable'

import {ON, OFF} from '../utils/stepper'

import './index.css'
import {Link} from 'react-router-dom'

class LiveList extends Component {

  actionItems () {
    return [
      <Link className='btn btn-primary' to='/live-videos/new/'>
        <i className='fas fa-plus' /> New
      </Link>,
    ]
  }

  componentDidMount () {
    this.props.clearLiveVideo()
  }


  enderFilterByState = (search) => {
    let state = search.get('state')

    if (state === ON) {
      return (
        'in state "ON"'
      )
    }
    if (state === OFF) {
      return (
        'in state "OFF"'
      )
    }
  };

  renderFilterByTag = (search) => {
    let tag_id = parseInt(search.get('tags__id'))
    if (tag_id) {
      this.props.fetchTag(tag_id)
      let {tag} = this.props

      if (tag) {
        return (
          `with tag "${tag.name}"`
        )
      }
    }
  };
 

  renderFilterCreatedBy = (search) => {
    let username = search.get('created_by__username')

    if (username) {
      return (
        `from user "${username}"`
      )
    }
  };

  rendertitle = () => {
    let search = new URLSearchParams(this.props.location.search)
    this.renderFilterByState(search)
  

      return (
        <h1>Live Videos {
          this.renderFilterByTag(search) ||
          this.renderFilterCreatedBy(search) ||
          this.renderFilterByState(search) }
        </h1>
      );
  };

render () {
  return (
    <Page header={this.rendertitle()}>
      <div className='container-fluid videoList'>
        <LiveTable
          list={this.props.contents}
          fetch={this.props.fetchLiveVideos.bind(this)}
          actionItems={this.actionItems()}
          location={this.props.location}
          history={this.props.history}
        />
          </div>
      </Page>
    )
  }
}

function mapStateToProps ({list, session, tag}) {
  return {
    contents: list.liveVideos,
    user: session.user,
    tag: tag,
  }
}

export default connect(mapStateToProps, {
  fetchLiveVideos,
  clearLiveVideo,
  fetchTag,
})(LiveList)
