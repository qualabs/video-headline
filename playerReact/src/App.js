import React, { Component } from 'react'
import './App.css'
import queryString from 'query-string'
import UAParser from 'ua-parser-js'
import VideoPlayer from 'qualabs-player-web'
import {loadScript, checkBoolString} from './utils'

export default class App extends Component {

  componentDidMount() {
    if (checkBoolString(window.qhub_analytics_enabled) && window.qhub_analytics_plugin_url){
      loadScript(window.qhub_analytics_plugin_url)
    }
  }

  onPlayerCreated(playerInstance){
    // If the QhubAnalytics plugin loads correctly we use it.
    if (checkBoolString(window.qhub_analytics_enabled) && playerInstance.QhubAnalytics){
      playerInstance.QhubAnalytics({
        organization_id: window.qhub_analytics_organization_id,
        organization_name: window.qhub_analytics_organization_name,
        channel_id: window.qhub_analytics_channel_id,
        channel_name: window.qhub_analytics_channel_name,
        content_id: window.qhub_analytics_content_id,
        content_title: window.qhub_analytics_content_title,
        tags: window.qhub_analytics_tags // array
      })
    }
    
    playerInstance.on('error', () => {
      if (playerInstance.error().code === 4) {
        const ua = UAParser(navigator.userAgent)
        // IE 11 in Windows 7
        if (ua.os.name === 'Windows' && ua.os.version === '7' && ua.browser.name === 'IE' && ua.browser.major === '11') {
          playerInstance.error(null)
          playerInstance.error({
            code: 41,
            message: "No se puede reproducir el video en este navegador. Se recomienda utilizar Google Chrome o Firefox actualizados"
          })
        }
      }
    })
    
    if (window.token) {
      playerInstance.on('loadstart', () => {
        playerInstance.tech().hls.xhr.beforeRequest = function(options) {
          options.uri = options.uri.concat(window.token)
          return options
        }
      })
    }
  }

  render () {
    const parsedParams = queryString.parse(window.location.search)
    const detectAdblock = parsedParams['detectadblock']
    const autoplay = parsedParams['autoplay']
    const token = window.token || ''

    const params = {
      url: parsedParams['url'] || (window.url.concat(token)),
      type: parsedParams['type'] || window.type,
      laUrl: parsedParams['laurl'] || window.laUrl,
      laType: parsedParams['latype'] || window.laType,
      certUrl: parsedParams['certurl'] || window.certUrl,
      adTagUrl: parsedParams['adtagurl'] || window.adTagUrl,
      posterUrl: parsedParams['posterurl'] || (window.posterUrl.concat(token)),
      playerCustomCss: parsedParams['playerCustomCss'] || window.playerCustomCss,
      detectAdblock: detectAdblock ? checkBoolString(detectAdblock) : checkBoolString(window.detectAdblock),
      autoplay: autoplay ? (checkBoolString(autoplay)) : ( checkBoolString(window.autoplay)),
      onPlayerCreated: this.onPlayerCreated.bind(this),
    }

    return (
      <div className='App'>
        <VideoPlayer {...params} />
      </div>
    )
  }
}
