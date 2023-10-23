import React, {Component} from 'react'
import {Link} from 'react-router-dom'
import map from 'lodash/map'

import Table from '../../../Table'
import '.././index.css'

const FETCH_CHANNELS_TIME = 10 * 1000

class ChannelTable extends Component {
  getTableColumns () {
    return [{
      Header: 'Name',
      accessor: 'name',
    }, {
      Header: 'Allowed domains',
      id: 'allowed_domains',
      accessor: data => {
        let output = []
        map(data.allowed_domains, allowed_domain => {
          output.push(allowed_domain)
        })
        return output.join(', ')
      },
    }, {
      Header: 'Actions',
      accessor: 'id',
      Cell: (props) => {
        return (
          <React.Fragment>
            <Link
              className='btn btn-outline-info'
              to={`/video-groups/${props.value}/video-on-demand`}>
              <i className='fas fa-fw fa-info-circle'></i>
            </Link>
            <Link
              className='btn btn-outline-info'
              to={`/video-groups/${props.value}/edit`}>
              <i className='fas fa-fw fa-edit'></i>
            </Link>
          </React.Fragment>
        )
      }
    }]
  }

  render () {
    return (
      <Table
        className={this.props.className}
        fetch={this.props.fetch}
        refresh={this.props.refresh || true}
        list={this.props.list}
        tableColumns={this.getTableColumns()}
        actionItems={this.props.actionItems}
        updateOn={true}
        refreshTime={FETCH_CHANNELS_TIME}
      />
    )
  }
}

export default ChannelTable
