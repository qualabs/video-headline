import React, {Component} from 'react'
import {AreaChart, XAxis, YAxis, Label, Tooltip, Area, CartesianGrid, ResponsiveContainer, BarChart, Bar} from 'recharts'
import randomColor from 'randomcolor'

import './index.css'


function renderTick (text, x = 0, y = 0, rotation = 0, textX = 0, textY = 0) {
  if (text) {
    return (
      <g transform={
        `translate(${x},${y})
                rotate(${rotation})`
      }>
        <text x={textX} y={textY} textAnchor='middle' className='tickText'>
          {text}
        </text>
      </g>
    )
  }
}

class Chart extends Component {
  renderChart () {

    return (
      <div className='chart'>
        <div>
          <h3 className='text-center'>{this.props.header}</h3>
        </div>
        <ResponsiveContainer width={this.props.width || '100%'} height={this.props.height}>
          <AreaChart
            data={this.props.data}
            margin={{bottom: 30, right: 50, left: 20}}
            isAnimationActive={true}
          >
            <XAxis dataKey={this.props.xDataKey}>
              <Label value={this.props.xValue} position='bottom' />
            </XAxis>
            <YAxis dataKey={this.props.yDataKey} tick={renderTick(this.props.yValue, 0, (this.props.height / 2), -90, 20, 50)}/>
            <CartesianGrid strokeDasharray='3 3' />
            <Tooltip />
            <Area
              type='linear'
              dataKey={this.props.yDataKey}
              stroke={this.props.fill}
              fill={this.props.fill}
              fillOpacity={0.6}
              dot={{strokeWidth: 3}}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }


  render () {
    return (
            <>
                {this.renderChart()}
            </>
    )
  }
}

export class SimpleBarChart extends Component {
  renderBarChart () {

    return (
      <div className='chart'>
        <div>
          <h3 className='text-center'>{this.props.header}</h3>
        </div>
        <ResponsiveContainer width={this.props.width || '100%'} height={this.props.height}>
          <BarChart
            data={this.props.data}
            margin={{bottom: 30, right: 50, left: 20}}
            isAnimationActive={true}
          >
            <XAxis dataKey={this.props.xDataKey}>
              <Label value={this.props.xValue} position='bottom' />
            </XAxis>
            <YAxis tick={renderTick(this.props.yValue, 0, (this.props.height / 2), -90, 20, 50)}/>
            <CartesianGrid strokeDasharray='3 3' />
            <Tooltip />
            <Bar dataKey={this.props.yDataKey} fill={this.props.fill}/>
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  render () {
    return (
            <>
                {this.renderBarChart()}
            </>
    )
  }
}

export class StackedAreaChart extends Component {
  renderAreas () {
    const {areas} = this.props

    return areas.map((area, index) => {
      let color = randomColor({luminosity: 'dark'})
      return <Area key={`stacked-${index}`} type='linear' dataKey={area} stackId={index} stroke={color} fill={color} dot={{strokeWidth: 3}}/>
    })
  }

  renderChart () {
    return (
      <div className='chart'>
        <div>
          <h3 className='text-center'>{this.props.header}</h3>
        </div>
        <ResponsiveContainer width={this.props.width || '100%'} height={this.props.height}>
          <AreaChart
            data={this.props.data}
            margin={{
              top: 10, right: 30, left: 0, bottom: 0,
            }}
          >
            <CartesianGrid strokeDasharray='3 3' />
            <XAxis dataKey={this.props.xDataKey}/>
            <YAxis tick={renderTick(this.props.yValue, 0, (this.props.height / 2), -90, 20, 50)}/>
            <Tooltip formatter={this.props.tooltipFormatter}/>
            {this.renderAreas()}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }

  render () {
    return this.renderChart()
  }
}


export default Chart


