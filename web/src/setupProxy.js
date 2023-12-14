const proxy = require('http-proxy-middleware')

module.exports = function (app) {
  app.use(proxy('/api', {target: 'http://localhost:8010/'}))
  app.use(proxy('/admin', {target: 'http://localhost:8010/'}))
  app.use(proxy('/player', {target: 'http://localhost:8010/'}))
}