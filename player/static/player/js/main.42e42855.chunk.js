(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{175:function(n,e,a){n.exports=a(415)},395:function(n,e,a){},397:function(n,e,a){},415:function(n,e,a){"use strict";a.r(e);a(176),a(191);var t=a(25),o=a.n(t),r=a(166),i=a.n(r),l=(a(395),a(167)),c=a(168),d=a(173),u=a(169),s=a(174),w=(a(397),a(170)),p=a.n(w),_=a(171),y=a.n(_),h=a(172);function b(n){return n&&"true"===n.toLowerCase()}var m=function(n){function e(){return Object(l.a)(this,e),Object(d.a)(this,Object(u.a)(e).apply(this,arguments))}return Object(s.a)(e,n),Object(c.a)(e,[{key:"componentDidMount",value:function(){var n;b(window.qhub_analytics_enabled)&&window.qhub_analytics_plugin_url&&(n=window.qhub_analytics_plugin_url,new Promise(function(e,a){var t=document.createElement("script");t.type="text/javascript",t.src=n;var o=document.getElementsByTagName("head")[0].appendChild(t);o.onload=e,o.onerror=a}))}},{key:"onPlayerCreated",value:function(n){b(window.qhub_analytics_enabled)&&n.QhubAnalytics&&n.QhubAnalytics({organization_id:window.qhub_analytics_organization_id,organization_name:window.qhub_analytics_organization_name,channel_id:window.qhub_analytics_channel_id,channel_name:window.qhub_analytics_channel_name,content_id:window.qhub_analytics_content_id,content_title:window.qhub_analytics_content_title,tags:window.qhub_analytics_tags}),n.on("error",function(){if(4===n.error().code){var e=y()(navigator.userAgent);"Windows"===e.os.name&&"7"===e.os.version&&"IE"===e.browser.name&&"11"===e.browser.major&&(n.error(null),n.error({code:41,message:"No se puede reproducir el video en este navegador. Se recomienda utilizar Google Chrome o Firefox actualizados"}))}}),window.token&&n.on("loadstart",function(){n.tech().hls.xhr.beforeRequest=function(n){return n.uri=n.uri.concat(window.token),n}})}},{key:"render",value:function(){var n=p.a.parse(window.location.search),e=n.detectadblock,a=n.autoplay,t=window.token||"",r={url:n.url||window.url.concat(t),type:n.type||window.type,laUrl:n.laurl||window.laUrl,laType:n.latype||window.laType,certUrl:n.certurl||window.certUrl,adTagUrl:n.adtagurl||window.adTagUrl,posterUrl:n.posterurl||window.posterUrl.concat(t),playerCustomCss:n.playerCustomCss||window.playerCustomCss,detectAdblock:b(e||window.detectAdblock),autoplay:b(a||window.autoplay),onPlayerCreated:this.onPlayerCreated.bind(this)};return o.a.createElement("div",{className:"App"},o.a.createElement(h.a,r))}}]),e}(t.Component);i.a.render(o.a.createElement(m,null),document.getElementById("root"))}},[[175,2,1]]]);
//# sourceMappingURL=main.42e42855.chunk.js.map