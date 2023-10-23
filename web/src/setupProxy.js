const proxy = require('http-proxy-middleware')

module.exports = function (app) {
  app.use(proxy('/api', {target: 'http://video-hub/'}))
  app.use(proxy('/admin', {target: 'http://video-hub/'}))
  app.use(proxy('/player', {target: 'http://video-hub/'}))
}
