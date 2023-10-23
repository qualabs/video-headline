import React, {Component} from 'react'
import {withRouter} from 'react-router'
import ReactTable from 'react-table'
import queryString from 'query-string'
import debounce from 'lodash/debounce'
import classnames from 'classnames'

import Loading from '../Loading'
import 'react-table/react-table.css'

import './table.css'

const PAGE_SIZE = 30

const TABLE_I18N = {
  previousText: 'Previous',
  nextText: 'Next',
  loadingText: 'Loading...',
  noDataText: 'No data',
  pageText: 'Page',
  ofText: 'from',
  rowsText: 'records',
}


class Table extends Component {
  constructor (props) {
    super(props)
    this.onSearchChange = debounce(this.onSearchChange.bind(this), 500)

    let interval
    if (props.refresh) {
      let intervalTimer = 2 * 1000

      if (props.refreshTime) {
        intervalTimer = props.refreshTime
      }

      interval = window.setInterval(this.fetchList.bind(this, false), intervalTimer)
    }

    this.state = {
      loading: true,
      interval,
      filterUpdated: false
    }

    this.searchNode = React.createRef()
  }

  componentWillUnmount () {
    if (this.state.interval) {
      window.clearInterval(this.state.interval)
    }
  }

  componentDidMount () {
    if (this.props.updateOn) {
      this.fetchList()
    }
  }

  componentDidUpdate (prevProps, prevState) {
    const prevSearch = prevProps.location.search
    const search = this.props.location.search
    const params = queryString.parse(search)

    const {filterUpdated} = this.state
    // set the search input text
    if (params.search && this.searchNode.current && !filterUpdated) {
      this.searchNode.current.value = params.search
      this.setState({filterUpdated: true})
    }

    // If the object list has changed,
    // then we are not loading any more
    if (this.props.list !== prevProps.list && this.state.loading) {
      this.setState({loading: false})
    }

    // If we had a list and the redux state was deleted,
    // fetch the list again!
    if (prevProps.list && !this.props.list) {
      this.fetchList()
    }

    // Check if the params have changed and fetch the data
    if (prevSearch !== search) {
      this.fetchList()
    }

    if (prevProps.updateOn !== this.props.updateOn) {
      this.fetchList()
    }
  }

  onPageChange (selected) {
    // Get the current params and push it to the history
    const {location, history} = this.props
    const page = selected + 1
    const params = queryString.parse(location.search)
    let query = queryString.stringify({...params, page})

    if (page < 0) {
      if (params.page) delete params.page
      query = queryString.stringify({...params})
    }
    history.push(`?${query}`)
  }

  onSortedChage (sort) {
    if (sort && sort.length === 1) {
      const direction = sort[0].desc ? '-' : ''
      const field = sort[0].id

      const {location, history} = this.props
      const params = queryString.parse(location.search)
      const query = queryString.stringify(
        {...params, ordering: `${direction}${field}`})
      history.push(`?${query}`)
    }
  }

  onSubmitFilters (event) {
    this.filter()
    event.preventDefault()
  }

  filter () {
    const {location, history} = this.props
    const params = queryString.parse(location.search)
    const search = this.searchNode.current.value
    if (params.search) delete params.search
    if (params.page) delete params.page
    let query = queryString.stringify({...params})
    if (search) {
      query = queryString.stringify(
        {...params, search: `${search}`})
    }
    history.push(`?${query}`)
  }

  onSearchChange (event) {
    this.filter()
  }

  fetchList (showLoading = true) {
    if (this.props.fetch) {
      const {location} = this.props
      if (showLoading) {
        this.setState({loading: true})
      }
      this.props.fetch(queryString.parse(location.search))
    }
  }

  pageCount () {
    // Calculate how many pages the API has.
    const {list} = this.props
    if (list && list.results.length) {
      return Math.ceil(list.count / PAGE_SIZE)
    }
    return 0
  }

  getTableColumns () {
    return this.props.tableColumns
  }

  getSubComponent (row) {
    return (
      <div className='table-item-subcomponent'>
        {this.props.SubComponent(row)}
      </div>
    )
  }

  getTableProps () {
    const {fetch} = this.props
    let props = {
      manual: true,
      columns: this.getTableColumns(),
      data: this.props.list.results,
      pages: this.pageCount(),
      pageSize: PAGE_SIZE,
      minRows: false,
      showPageSizeOptions: false,
      onPageChange: this.onPageChange.bind(this),
      sortable: fetch ? true : false,
      multiSort: false,
      resizable: false,
      loading: this.state.loading,
      onSortedChange: this.onSortedChage.bind(this),
      SubComponent: (this.props.SubComponent ? this.getSubComponent.bind(this) : null)
    }
    if (this.props.tableProps) {
      // Override props with custom props
      props = {...props, ...this.props.tableProps}
    }
    return props
  }

  renderAditionalFilters () {
    let {aditionalFilters} = this.props

    if (aditionalFilters) {
      return aditionalFilters()
    }
  }

  renderFilters () {
    const {fetch, showSearch} = this.props
    if (!fetch || !showSearch) return null
    return (
      <>
        <form className='filters' onSubmit={this.onSubmitFilters.bind(this)}>
          <div className='search'>
            <input
              type='search'
              placeholder='&#xf002; Search'
              ref={this.searchNode}
              onChange={this.onSearchChange.bind(this)}
            />
          </div>

          {this.renderAditionalFilters()}
        </form>
      </>
    )
  }

  renderActions () {
    const {actionItems} = this.props
    if (!actionItems) {
      return null
    }
    const items = actionItems.map( (item, index) => {
      return <div key={index}>{item}</div>
    })
    return (
      <div className='actions'>
        {items}
      </div>
    )
  }

  render () {
    const {list} = this.props
    if (!list) {
      return <Loading fullscreen={true} />
    }
    const {className} = this.props
    const noDataClassName = this.props.list.results.length === 0 ? 'no-data' : ''
    return (
      <div className={classnames('table', {[className]: className}, {[noDataClassName]: noDataClassName})}>
        <div className='actions'>
          {this.renderActions()}
        </div>
        <div className='operations'>
          {this.renderFilters()}
        </div>
        <ReactTable
          {...this.getTableProps()}
          {...TABLE_I18N}
        />
      </div>
    )
  }
}

Table.defaultProps = {
  updateOn: true,
  showSearch: true
}

export default (withRouter(Table))

export class DummyTable extends Component {
  render () {
    return (
      <div className='table'>
        <ReactTable
          showPagination={false}
          showPaginationTop={false}
          showPaginationBottom={false}
          showPageSizeOptions={false}
          sortable={false}
          resizable={false}
          minRows={false}
          data={this.props.data}
          columns={this.props.columns}
          {...TABLE_I18N}
        />
      </div>
    )
  }
}
