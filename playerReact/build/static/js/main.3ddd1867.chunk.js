(window.webpackJsonp=window.webpackJsonp||[]).push([[0],{264:function(n,e,a){n.exports=a(606)},581:function(n,e,a){},583:function(n,e,a){},606:function(n,e,a){"use strict";a.r(e);a(265),a(301);var t=a(60),o=a.n(t),r=a(255),i=a.n(r),l=(a(581),a(256)),c=a(257),d=a(262),u=a(258),s=a(263),w=(a(583),a(259)),p=a.n(w),_=a(260),y=a.n(_),h=a(261),b=a.n(h);function m(n){return n&&"true"===n.toLowerCase()}var g=function(n){function e(){return Object(l.a)(this,e),Object(d.a)(this,Object(u.a)(e).apply(this,arguments))}return Object(s.a)(e,n),Object(c.a)(e,[{key:"componentDidMount",value:function(){var n;m(window.qhub_analytics_enabled)&&window.qhub_analytics_plugin_url&&(n=window.qhub_analytics_plugin_url,new Promise(function(e,a){var t=document.createElement("script");t.type="text/javascript",t.src=n;var o=document.getElementsByTagName("head")[0].appendChild(t);o.onload=e,o.onerror=a}))}},{key:"onPlayerCreated",value:function(n){m(window.qhub_analytics_enabled)&&n.QhubAnalytics&&n.QhubAnalytics({organization_id:window.qhub_analytics_organization_id,organization_name:window.qhub_analytics_organization_name,channel_id:window.qhub_analytics_channel_id,channel_name:window.qhub_analytics_channel_name,content_id:window.qhub_analytics_content_id,content_title:window.qhub_analytics_content_title,tags:window.qhub_analytics_tags}),n.on("error",function(){if(4===n.error().code){var e=y()(navigator.userAgent);"Windows"===e.os.name&&"7"===e.os.version&&"IE"===e.browser.name&&"11"===e.browser.major&&(n.error(null),n.error({code:41,message:"No se puede reproducir el video en este navegador. Se recomienda utilizar Google Chrome o Firefox actualizados"}))}}),window.token&&n.on("loadstart",function(){n.tech().hls.xhr.beforeRequest=function(n){return n.uri=n.uri.concat(window.token),n}})}},{key:"render",value:function(){var n=p.a.parse(window.location.search),e=n.detectadblock,a=n.autoplay,t=window.token||"",r={url:n.url||window.url.concat(t),type:n.type||window.type,laUrl:n.laurl||window.laUrl,laType:n.latype||window.laType,certUrl:n.certurl||window.certUrl,adTagUrl:n.adtagurl||window.adTagUrl,posterUrl:n.posterurl||window.posterUrl.concat(t),playerCustomCss:n.playerCustomCss||window.playerCustomCss,detectAdblock:m(e||window.detectAdblock),autoplay:m(a||window.autoplay),onPlayerCreated:this.onPlayerCreated.bind(this)};return o.a.createElement("div",{className:"App"},o.a.createElement(b.a,r))}}]),e}(t.Component);i.a.render(o.a.createElement(g,null),document.getElementById("root"))}},[[264,2,1]]]);
//# sourceMappingURL=main.3ddd1867.chunk.js.map