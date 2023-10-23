import React, {Component} from 'react'
import {Link} from 'react-router-dom'
import {connect} from 'react-redux'

import {renderStepper, QUEUING_FAILED, PROCESSING_FAILED, FINISHED} from '../utils/stepper'

import {toNumericDate} from '../../../utils/formatDate'

import './index.css'

const FETCH_VIDEO_TIMEOUT = 30 * 1000

class VideoSummary extends Component {
  componentDidMount () {
    this.fetchVideoDataTimer = setInterval(this.fetchVideoData, FETCH_VIDEO_TIMEOUT)

    if (this.props.securityEnabled) {
      this.props.fetchIframe(this.props.video.video_id)
    }
  }

  componentWillUnmount () {
    window.clearTimeout(this.fetchVideoDataTimer)
  }

  fetchVideoData = () => {
    const {id} = this.props.video
    this.props.fetchVideoState(id)

    const {state} = this.props.video

    if (state === QUEUING_FAILED || state === PROCESSING_FAILED || state === FINISHED) {
      window.clearTimeout(this.fetchVideoDataTimer)
    }
  }

  componentWillReceiveProps (nextProps) {
    const actualProps = this.props

    if (actualProps.video !== nextProps.video) {
      this.props = nextProps
    }
  }

  renderTags () {
    const {tags} = this.props.video
    if (tags.length === 0) {
      return ('(No data)')
    } else {
      let links = tags.map((tag) => {
        return <li key={tag.id} className='li'>
          <Link to={`/video-on-demand/?tags__id=${tag.id}`}>
            {tag.name}
          </Link>
        </li>
      })
      return links
    }
  }

  renderChannel () {
    const {channel, id} = this.props.video

    if (!channel) {
      return (
        <Link to={`/video-on-demand/${id}/edit/`} className='alert-summary'>
          Add Video Group
        </Link>
      )
    } else {
      return (
        <Link to={`/video-groups/${channel.id}`}>
          {channel.name}
        </Link>
      )
    }
  }

  getEmbedUrl () {
    const {video, securityEnabled, security} = this.props
    if (security && securityEnabled) {
      return this.props.security.embed_url
    }

    if (!securityEnabled) {
      return `/player/embed/${video.video_id}/`
    }
  }

  getEmbedIframe () {
    const {video, securityEnabled, security} = this.props
    if (security && securityEnabled) {
      return this.props.security.embed_code.replaceAll(' ', '\n ')
    }

    // TODO: there is a bug with ads autoplay, a hack for solving this
    // is not allowing autoplay in iframe. This is a fast hack that solves
    // the issue. In future, solve this given that disable autoplay allow is wrong.
    let allowStr = 'autoplay;fullscreen'
    if (video.autoplay === 'n') {
      allowStr = 'fullscreen'
    }
    return `<iframe
    src='//${window.location.host}/player/embed/${video.video_id}/'
    width='560'
    height='315'
    frameBorder='0'
    scrolling='no'
    seamless='seamless'
    allow='${allowStr}'>
</iframe>`
  }

  renderContentTypeIcon = (media_type) => {
    let icon = media_type === 'video' ? <i className='fas fa-fw fa-film'/> : <i className='fas fa-fw fa-music'/>
    let text = media_type === 'video' ? 'Video' : 'Audio'

    return (<>{icon} {text}</>)
  }

  render () {
    const {video} = this.props

    const autoplayOptions = {
      'c': 'According to video group configuration',
      'y': 'Yes',
      'n': 'No'
    }

    return (
      <div className='row summary'>
        <div className='col-md-12 col-xl-6'>
          <div className='detail'>
            <ul className='properties'>
              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-signature'></i> Name</div>
                  {video.name}
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'> Type </div>
                  {this.renderContentTypeIcon(video.media_type)}
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'>Id</div>
                  {video.video_id}
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-user-crown'></i> Creator</div>
                  {video.created_by.username}
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-calendar'></i> Date Creation</div>
                  {toNumericDate(video.created_at)}
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-tv'></i> Video Group</div>
                  <div className='summary-inner-list'>
                    <ul>
                      {this.renderChannel()}
                    </ul>
                  </div>
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-tags'></i> Tags</div>
                  <div className='summary-inner-list'>
                    <ul>
                      {this.renderTags()}
                    </ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-ad'></i>Ads URL</div>
                  <div className='summary-inner-list'>
                    <ul style={{'wordWrap': 'break-word'}}>
                      {video.ads_vast_url || '(No data)'}
                    </ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'><i className='fas fa-fw fa-play-circle'></i>Autoplay</div>
                  <div className='summary-inner-list'>
                    <ul style={{'wordWrap': 'break-word'}}>
                      {autoplayOptions[video.autoplay]}
                    </ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='property'>
                  {renderStepper(video)}
                </div>
              </li>
            </ul>
          </div>
        </div>

        {(video.state === FINISHED && video.channel) &&
          <div className='col-md-12 col-xl-6'>
            <div id='iframe-info-detail' className='alert alert-info highlight'>
              <div className='iframe'>
                <iframe
                  className='resp-iframe'
                  title='player'
                  src={this.getEmbedUrl()}
                  width='720'
                  height='405'
                  scrolling='no'
                  seamless='seamless'
                  allow='autoplay; fullscreen'/>
              </div>
              <div className='iframe-code'>
                <hr />
                <h5> Embed the video on your page using the following code:</h5>
                <pre><code>
                  {this.getEmbedIframe()}
                </code></pre>
              </div>
            </div>
          </div>
        }
      </div>
    )
  }
}

function mapStateToProps ({security}) {
  return {
    security,
  }
}

export default connect(mapStateToProps, {
})(VideoSummary)
