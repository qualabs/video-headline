import React, {Component} from 'react'
import {Link} from 'react-router-dom'
import {connect} from 'react-redux'
import {renderStateName, SCHEDULED, EXECUTING, PERFORMED} from '../../utils/stepper'
import Table from '../../../Table'

import {deleteLiveVideoCut} from '../../../../actions/cuts'

import ConfirmButton from '../../../ConfirmButton'
import {setMessage} from '../../../../actions/flashMessage'

import '.././index.css'
import {humanizeDate} from '../../../../utils/formatDate'

const FETCH_CUT_TIME = 5 * 1000


class CutTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      showFilterButtons: false
    }
  }

  renderFilterButtons = () => {
    const table_url = `/live-videos/${this.props.id}/cuts`

    return (
      <div className='filterButtons'>
        <Link key='1' className='btn' to={table_url}>All</Link>
        <Link key='2' className='btn' to={`${table_url}/?state=${SCHEDULED}`}>Scheduled</Link>
        <Link key='3' className='btn' to={`${table_url}/?state=${EXECUTING}`}>In process</Link>
        <Link key='4' className='btn' to={`${table_url}/?state=${PERFORMED}`}>Finished</Link>
      </div>
    )
  }

  showTagsFilterButtonClick = () => {
    this.setState({showFilterTags: !this.state.showFilterTags, showFilterButtons: false})
  }

  renderAditionalFilters = () => {
    return (
      <>
        <button className='btn showFiltersButton' onClick={() => this.setState({showFilterButtons: !this.state.showFilterButtons})}> Filters </button>

        {
          this.state.showFilterButtons &&
          this.renderFilterButtons()
        }

      </>
    )
  }

  handleDelete = (id) => {
    this.props.deleteLiveVideoCut(id).then(() => {

      this.props.setMessage('Cut deleted correctly.', 'success')
    }).catch(e => {
      let msg = e.response.data.detail[0]
      this.props.setMessage(msg, 'error')
    })
  }

  actionItems = () => {
    if (this.props.actionItems) {
      return this.props.actionItems
    }
    return [
      <Link className='btn btn-primary' to={`/live-videos/${this.props.id}/cuts/new`}><i className='fas fa-plus'/> New</Link>,
    ]
  }

  showCut = () => {

  }

  getTableColumns () {
    return [{
      Header: 'Description',
      accessor: 'description',
    }, {
      Header: 'Start time',
      accessor: 'initial_time',
      Cell: (props) => humanizeDate(props.value)
    }, {
      Header: 'End time',
      accessor: 'final_time',
      Cell: (props) => humanizeDate(props.value)
    }, {
      Header: 'State',
      accessor: 'state',
      Cell: (props) => renderStateName(props.value)
    }, {
      Header: 'Creator',
      accessor: 'created_by.username',
    }, {
      Header: 'Acciones',
      accessor: 'id',
      Cell: (props) => {
        return (
          <li>
            {props.original.state !== PERFORMED && <React.Fragment>
              <Link
                className='btn btn-outline-info'
                to={`/live-videos/${this.props.id}/cuts/${props.value}`}>
                <i className='fas fa-edit'></i>
              </Link>
            </React.Fragment>}
            {props.original.state === SCHEDULED && <React.Fragment>
              <ConfirmButton
                className='btn btn-outline-danger'
                dialogMessage='Delete this cut?'
                handleConfirm={() => this.handleDelete(props.value)}>
                <i className='fas fa-trash'/>
              </ConfirmButton>
            </React.Fragment>}
          </li>
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
        actionItems={this.actionItems()}
        updateOn={true}
        refreshTime={FETCH_CUT_TIME}
        aditionalFilters={this.renderAditionalFilters}
      />
    )
  }
}

function mapStateToProps ({session}) {
  return {
    user: session.user,
  }
}

export default connect(mapStateToProps, {
  deleteLiveVideoCut,
  setMessage
}) (CutTable)
