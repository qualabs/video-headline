import React, {Component} from 'react'
import {Link} from 'react-router-dom'
import {connect} from 'react-redux'
import queryString from 'query-string'
import {renderStateName, FAILED, NOT_FINISHED} from '../../utils/stepper'
import Table from '../../../Table'
import Multiselect from 'react-widgets/lib/Multiselect'
import {fetchTag, fetchTags} from '../../../../actions/tags'
import ConfirmButton from '../../../ConfirmButton'
import {deleteVideo} from '../../../../actions/video'
import {setMessage} from '../../../../actions/flashMessage'
import {debounce} from 'lodash'
import '.././index.css'
import {humanizeDate} from '../../../../utils/formatDate'
const FETCH_VIDEOS_TIME = 10 * 1000
const NO_TAGS_FOUND = 'No tags found'
const SEARCHING = 'Searching...'
class VideoTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      showFilterButtons: false,
      showFilterTags: false,
      searchingTags: false,
      emptyListText: NO_TAGS_FOUND
    }
    this.onSearchChange = debounce(this.onSearchChange.bind(this), 500)
  }

  componentDidMount () {
    this.props.fetchTags()
  }

  onSearchChange (search) {
    this.props.fetchTags({search}).then(() => {
      this.setState({searchingTags: false, emptyListText: NO_TAGS_FOUND})
    })
  }

  handleDelete = (id) => {
    this.props.deleteVideo(id).then(() => {
      this.props.setMessage('Video deleted correctly.', 'success')
    }).catch(e => {
      let msg = e.response.data.detail[0]
      this.props.setMessage(msg, 'error')
    })
  }

  renderFilterButtons = () => {
    const table_url = this.props.table_url || '/video-on-demand'
    const {user, tracking} = this.props

    return (
      <div className='filterButtons'>
        <Link key='1' className='btn' to={table_url}>All</Link>
        <Link key='2' className='btn' to={`${table_url}/?media_type=video`}>Videos</Link>
        <Link key='3' className='btn' to={`${table_url}/?media_type=audio`}>Audios</Link>
        <Link key='4' className='btn' to={`${table_url}/?state=${NOT_FINISHED}`}>Processing</Link>
        <Link key='5' className='btn' to={`${table_url}/?state=${FAILED}`}>Failed</Link>
        <Link key='6' className='btn' to={`${table_url}/?created_by__username=${user.username}`}>Uploaded by me</Link>
        {tracking.enabled && <Link key='5' className='btn' to={`${table_url}/?days=${7}`}>Most seen</Link>}
      </div>
    )
  }

  onTagsFilterChange = (selectedTags) => {
    const {location, history} = this.props
    const params = queryString.parse(location.search)
    if (params.tags) delete params.tags
    let query = queryString.stringify({...params})
    let tagsFilter = []
    for (let i = 0; i < selectedTags.length; i++) {
      let tag = selectedTags[i]
      tagsFilter.push(tag.name)
    }
    if (tagsFilter.length > 0) {
      query = queryString.stringify(
        {...params, tags: `${tagsFilter}`})
    }
    history.push(`?${query}`)
  }

  renderFilterTags = () => {
    let {tags} = this.props
    return (
      <div className='filterTags'>
        <Multiselect
          data={tags ? (tags.results) : []}
          onSearch={() => this.setState({searchingTags: true, emptyListText: SEARCHING}, this.onSearchChange.bind(this))}
          allowCreate={false}
          filter='contains'
          textField='name'
          valueField='name'
          onChange={selectedTags => {this.onTagsFilterChange(selectedTags)}}
          busy = {this.state.searchingTags}
          messages = {{emptyList: this.state.emptyListText, emptyFilter: this.state.emptyListText}}
        />
      </div>
    )
  }

  showTagsFilterButtonClick = () => {
    this.setState({showFilterTags: !this.state.showFilterTags, showFilterButtons: false})
  }

  renderAditionalFilters = () => {
    return (
      <>
        <button className='btn showFiltersButton' onClick={() => this.setState({showFilterButtons: !this.state.showFilterButtons, showFilterTags: false})}> Filters </button>
        <button className='btn showFiltersButton' onClick={this.showTagsFilterButtonClick}> Tags </button>
        {
          this.state.showFilterButtons &&
          this.renderFilterButtons()
        }
        {
          this.state.showFilterTags &&
          this.renderFilterTags()
        }
      </>
    )
  }

  actionItems () {
    if (this.props.actionItems) {
      return this.props.actionItems
    }
    return [
      <Link className='btn btn-primary' to='/drop/'><i className='fas fa-plus'/> New</Link>,
    ]
  }

  renderContentName (video) {
    let icon = video.media_type === 'video' ? <i className='fas fa-fw fa-film'/> : <i className='fas fa-fw fa-music'/>
    return (<>{icon} {video.name}</>)
  }

  getTableColumns () {
    return [{
      Header: 'Name',
      accessor: 'name',
      Cell: (props) => this.renderContentName(props.original)
    }, {
      Header: 'Creator',
      accessor: 'created_by.username',
    }, {
      Header: 'State',
      accessor: 'state',
      Cell: (props) => renderStateName(props.value)
    }, {
      Header: 'Created at',
      accessor: 'created_at',
      Cell: (props) => humanizeDate(props.value)
    }, {
      Header: 'Actions',
      accessor: 'id',
      Cell: (props) => {
        return <React.Fragment>
          <Link
            className='btn btn-outline-info'
            to={`/video-on-demand/${props.value}/`}>
            <i className='fas fa-fw fa-info-circle'></i>
          </Link>
          <Link
            className='btn btn-outline-info'
            to={`/video-on-demand/${props.value}/edit/`}>
            <i className='fas fa-edit'></i>
          </Link>
          <ConfirmButton
            className='btn btn-outline-danger'
            dialogMessage='Delete this video'
            handleConfirm={() => this.handleDelete(props.value)}>
            <i className='fas fa-trash'/>
          </ConfirmButton>
        </React.Fragment>
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
        refreshTime={FETCH_VIDEOS_TIME}
        aditionalFilters={this.renderAditionalFilters}
      />
    )
  }
}

function mapStateToProps ({list, session, tag, tracking}) {
  return {
    user: session.user,
    tag: tag,
    tags: list.tags,
    tracking
  }
}

export default connect(mapStateToProps,
  {
    deleteVideo,
    setMessage,
    fetchTag,
    fetchTags
  }) (VideoTable)
