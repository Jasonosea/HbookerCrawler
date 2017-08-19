function initResponse(){var d,b,a=window.innerWidth||document.documentElement.clientWidth,g=navigator.userAgent.toLowerCase(),h=/(msie) ([\w.]+)/,f=h.exec(g),c;if(f!==null&&f[1]==="msie"){c=f[2];if(c==="8.0"||c==="7.0"||c==="6.0"){a=a+21}}document.body.style.width="";var e=(document.body.className&&document.body.className.indexOf("sw-list-")!=-1);if(a>=1280||e){d=1}else{d=0}switch(d){case 1:b="s-layout-1190";break;case 0:b="s-layout-990";break;default:b="s-layout-990";break}document.body.className=b}
$(function () {initResponse();});


