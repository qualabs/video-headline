import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Link} from 'react-router-dom'
import history from '../../../history'

import {
  renderStateName,
  ON,
  OFF,
  STARTING,
  STOPPING,
  renderCutState,
  renderInputState,
  WAITING_INPUT,
  renderSimpleInputState,
  DELETING
} from '../utils/stepper'
import {toNumericDate} from '../../../utils/formatDate'
import {isoCountries, geoType} from '../../../utils/isoCountries'
import {setMessage} from '../../../actions/flashMessage'

import './index.css'
import {
  changeLiveStateToStarting,
  changeLiveStateToStopping,
  fetchLiveVideo,
  deleteLiveVideo
} from '../../../actions/live'
import ConfirmButton from '../../ConfirmButton'
import CustomAlert from '../../CustomAlert'
import Tooltip from '../../Tooltip'
import Loading from '../../Loading'

class LiveSummary extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isDeleteSubmitting: false,
      iframeKey: 'old-key',
    }
   
  }
 
  componentDidUpdate(prevProps) {
    if (this.props.video.state != prevProps.video.state || this.props.video.input_state != prevProps.video.input_state) {
      if (this.props.video.state == ON && this.props.video.input_state.length== 0) {
        const iframe = document.querySelector('iframe');
        const iframeSrc = iframe.src;
        const cloudFrontUrl = iframeSrc.split('/')[2];  
        const checkStatusInterval = setInterval(() => {
        fetch(cloudFrontUrl, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json'
                }
            }).then((response) => {
                if (response.status === 200) {
                  clearInterval(checkStatusInterval);
                  this.setState({ iframeKey: 'new-key' + Math.random()});
                }
              });
          }, 5000); 
        }
        }
        if (this.props.securityEnabled) {
          this.props.fetchIframe(this.props.video.video_id)
        }
    }

   
  componentWillUnmount () {
    clearInterval(this.timerId)
  }

  handleDelete = (id) => {
    this.setState({isDeleteSubmitting: true})
    this.props.deleteLiveVideo(id).then(() => {
      this.setState({isDeleteSubmitting: false})
      this.props.setMessage('Live video deleted correctly.', 'success')
      history.push('/live-videos/')
    }).catch(e => {
      this.setState({isDeleteSubmitting: false})
      let msg = e.response.data.detail[0]
      this.props.setMessage(msg, 'error')
    })
  }

  componentDidMount () {
    if (this.props.securityEnabled) {
      this.props.fetchIframe(this.props.video.video_id)
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
      return '(No data)'
    } else {
      let links = tags.map((tag) => {
        return (
          <li key={tag.id} className='li'>
            <Link to={`/live-videos/?tags__id=${tag.id}`}>{tag.name}</Link>
          </li>
        )
      })
      return links
    }
  }

  getEmbedUrl () {
    const {video} = this.props
    const {securityEnabled} = this.props
    const {security} = this.props
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

  renderChannel () {
    const {channel, id} = this.props.video

    if (!channel) {
      return (
        <Link to={`/live-videos/${id}/edit/`} className='alert-summary'>
          Add channel
        </Link>
      )
    } else {
      return <Link to={`/video-groups/${channel.id}`}>{channel.name}</Link>
    }
  }

  renderRestrictions (video) {
    if (video.geolocation_type !== 'none') {
      return (
        <div>
          <div>
            Type:{' '}
            {geoType.find((dict) => dict.id === video.geolocation_type).name}
          </div>
          <div>
          Countries:{' '}
            {video.geolocation_countries
              .map(
                (countryCode) =>
                  isoCountries.find((dict) => dict.id === countryCode).name
              )
              .join(', ')}
          </div>
        </div>
      )
    } else {
      return <div>(No restriction)</div>
    }
  }

  getLiveInputState (input_state, withDotsState = true) {
    return (
      <div>
        {renderInputState(input_state, withDotsState)}
      </div>
    )
  }

  handleCopyClick = (value) => {
    navigator.clipboard.writeText(value)
  }

  render () {
    const {video} = this.props
    const {session} = this.props
    const splitURL = video.ml_input_url.split('/')
    const videoInputURL = splitURL.slice(0, -1).join('/')
    const videoInputKey = splitURL.slice(-1)[0]

    const autoplayOptions = {
      c: 'According to video group configuration',
      y: 'Yes',
      n: 'No',
    }

    if (this.state.isDeleteSubmitting) {
      return <Loading />
    }

    return (
      <div className='row summary'>
        <div className='col-md-12 col-xl-6'>
          {video.state !== OFF && video.input_state.length > 0 &&
            <CustomAlert alertType='danger'>
              <h4>Alerts:</h4>
              <div>
                {video.input_state.map((item, index) => (
                  <div key={index}>- {item}</div>
                ))}
              </div>
            </CustomAlert>}
          <div className='detail'>
            <ul className='properties'>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-signature'></i> Name
                  </div>
                  {video.name}
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-id-card'></i> Id
                  </div>
                  {video.video_id}
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-user-crown'></i> Creator
                  </div>
                  {video.created_by.username}
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-calendar'></i> Creation Date
                  </div>
                  {toNumericDate(video.created_at)}
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-tv'></i> Video Group
                  </div>
                  <div className='summary-inner-list'>
                    <ul>{this.renderChannel()}</ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-tags'></i> Tags
                  </div>
                  <div className='summary-inner-list'>
                    <ul>{this.renderTags()}</ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12 state-container'>
                  {(video.state === ON || video.state === WAITING_INPUT) && <div className='input-state-container'>
                    <div className='property'>
                      <><i className='fas fa-fw fa-stethoscope'></i> Origin State </>
                    </div>
                    <div className={`${(video.state === ON || video.state === WAITING_INPUT) ? 'state-dot-on' : ''}`}>
                      {(video.state === ON || video.state === WAITING_INPUT) && (
                        <div >
                          {renderSimpleInputState(video)}
                        </div>
                      )}
                    </div>
                  </div>}
                  <div className='channel-state-container'>
                    <div className='property'>
                      <><i className='fas fa-fw fa-signal-stream'></i> State </>
                    </div>
                    <div>
                      {renderStateName(video.state)}
                      {renderCutState(video.actual_cut, video.id)}
                    </div>
                  </div>
                </div>
              </li>

              {video.state !== DELETING && <li>
                <div className='col-xl-12'>
                  <div className='btn-group' role='group'>
                    {(video.state === OFF || video.state === STOPPING) &&
                        <ConfirmButton
                          className='btn btn-danger pull-right'
                          dialogMessage = 'This action will incur in AWS costs. For more information, contact your administrator.'
                          handleConfirm={() => this.props.changeLiveStateToStarting(video.id, session)}
                        >
                          Turn ON
                        </ConfirmButton>
                    }

                    {(video.state === ON || video.state === STARTING || video.state === WAITING_INPUT) && (
                      <button
                        type='button'
                        className='btn btn-primary'
                        onClick={() =>
                          this.props.changeLiveStateToStopping(
                            video.id,
                            session
                          )
                        }
                      >
                        <i className='fas fa-stop'></i> Turn OFF
                      </button>
                    )}
                  </div>
                </div>
              </li>}

              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-video'></i> Streaming
                  </div>
                  <div className='col-xl-12'>
                    <div className='property'>
                      <i className='fas fa-fw fa-link'></i> URL
                      <i className='fas fa-copy copy-icon' onClick={() => this.handleCopyClick(videoInputURL)}/>
                    </div>
                    {video.ml_input_url ? videoInputURL : '(No Data)'}
                  </div>
                  <div className='col-xl-12'>
                    <div className='property'>
                      <i className='fas fa-fw fa-key-skeleton'></i> Key
                      <i className='fas fa-copy copy-icon' onClick={() => this.handleCopyClick(videoInputKey)}/>
                    </div>
                    {video.ml_input_url ? videoInputKey : '(No Data)'}
                  </div>
                </div>
              </li>

              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-ad'></i> Advertising URL
                  </div>
                  <div className='summary-inner-list'>
                    <ul style={{wordWrap: 'break-word'}}>
                      {video.ads_vast_url || '(No data)'}
                    </ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-play-circle'></i> Autoplay
                  </div>
                  <div className='summary-inner-list'>
                    <ul style={{wordWrap: 'break-word'}}>
                      {autoplayOptions[video.autoplay]}
                    </ul>
                  </div>
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='property'>
                    <i className='fas fa-fw fa-globe-americas'></i>
                      Geographic restriction
                  </div>
                  {this.renderRestrictions(video)}
                </div>
              </li>
              <li>
                <div className='col-xl-12'>
                  <div className='btn-group' role='group'>
                    <Tooltip placement='top' text='State should be OFF to delete' show={video.state !== 'off'}>
                      <ConfirmButton
                        className='btn btn-outline-danger'
                        dialogMessage='Delete this video'
                        handleConfirm={() => this.handleDelete(video.id)}
                        disable={video.state !== 'off'}
                      >
                        <i className='fas fa-trash'/>
                      </ConfirmButton>
                    </Tooltip>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
        {video.channel && (
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
                  allow='autoplay; fullscreen'
                  key={this.state.iframeKey}
                />
              </div>
              <div className='iframe-code'>
                <hr />
                <h5>
                  Embed the live video on your page using the following code:
                </h5>
                <pre>
                  <code>{this.getEmbedIframe()}</code>
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
}


function mapStateToProps ({live, session, tracking, security}) {
  return {
    video: live,
    user: session.user,
    session,
    tracking,
    security,
  }
}

export default connect(mapStateToProps, {
  changeLiveStateToStarting,
  changeLiveStateToStopping,
  fetchLiveVideo,
  deleteLiveVideo,
  setMessage
})(LiveSummary)
