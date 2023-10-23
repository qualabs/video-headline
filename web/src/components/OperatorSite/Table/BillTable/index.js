import React, {Component} from 'react'
import {Link} from 'react-router-dom'
import Table from '../../../Table'

import {toNumericMonth} from '../../../../utils/formatDate'
import SubBillDetail from '../../SubBillDetail'
import '.././index.css'

class BillTable extends Component {
  getTableColumns () {
    return [
      {
        Header: 'Date',
        accessor: 'date',
        Cell: (props) => toNumericMonth(props.value)
      },
      {
        Header: 'Plan',
        accessor: 'plan',
      }, {
        Header: 'Actions',
        accessor: 'id',
        Cell: (props) => {
          return <React.Fragment>
            <Link
              className='btn btn-outline-info'
              to={`/bills/${props.value}/`}>
              <i className='fas fa-fw fa-info-circle'></i>
            </Link>
          </React.Fragment>
        }
      }]
  }

  render () {

    return (
      <Table
        className={this.props.className}
        fetch={this.props.fetch}
        list={this.props.list}
        tableColumns={this.getTableColumns()}
        SubComponent={row => {
          return (
            <SubBillDetail
              id={row.original.id}
            />
          )
        }
        }
      />
    )
  }
}

export default BillTable
