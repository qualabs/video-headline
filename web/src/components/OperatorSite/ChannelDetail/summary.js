import React, {Component} from 'react'
import map from 'lodash/map'

import './index.css'

export default class ChannelSummary extends Component {
  formatDomains () {
    const {allowed_domains} = this.props.channel
    if (allowed_domains.length === 0) {
      return ('(No Data)')
    } else {
      let output = map(allowed_domains, allowed_domain => {
        return <li>{allowed_domain}</li>
      })
      return output
    }
  }

  render () {
    const {channel} = this.props

    return (
      <div className='summary container-fluid'>
        <ul className='properties'>
          <li><div className='property'>Name</div>
            {channel.name}
          </li>
          <li><div className='property'>Allowed Domains</div>
            <div className='domain-list'>
              <ul>
                {this.formatDomains()}
              </ul>
            </div>
          </li>
          <li><div className='property'>Ads URL</div>
            {channel.ads_vast_url || '(No Data)'}
          </li>
          <li><div className='property'>Autoplay</div>
            {channel.autoplay ? 'Si' : 'No'}
          </li>
        </ul>
      </div>
    )
  }
}
