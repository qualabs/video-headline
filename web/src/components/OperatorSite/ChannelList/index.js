import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Link} from 'react-router-dom'

import Page from '../../Page'

import ChannelTable from '../Table/ChannelTable'
import {fetchChannels} from '../../../actions/channel'

class ChannelList extends Component {
  actionItems () {
    return [
      <Link className='btn btn-primary' to='/video-groups/new/'><i className='fas fa-plus'/> New </Link>,
    ]
  }

  render () {
    return (
      <Page header={<h1>Video Groups</h1>}>
        <div className='container-fluid'>
          <ChannelTable
            list={this.props.contents}
            actionItems={this.actionItems()}
            fetch={this.props.fetchChannels.bind(this)}
          />
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({list, session}) {
  return {
    contents: list.channels,
    user: session.user,
  }
}

export default connect(mapStateToProps, {fetchChannels})(ChannelList)
