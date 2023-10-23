import InfiniteScroll from 'react-infinite-scroller'


export default class InfiniteScrollWithParent extends InfiniteScroll {
  /**
   * We are overriding the getParentElement function to use a custom element as the scrollable element
   *
   * @param {any} el the scroller domNode
   * @returns {any} the parentNode to base the scroll calulations on
   *
   * @memberOf InfiniteScrollOverride
   */

  filterProps (props) {
    // Filter the props before doing React.createElement
    let newProps = {...props}
    delete newProps['scrollParentElement']
    return newProps
  }

  getParentElement (el) {
    if (this.props.scrollParentElement) {
      return this.props.scrollParentElement
    }
    return super.getParentElement(el)
  }

  render () {
    return super.render()
  }
}
