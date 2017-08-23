var CryptoJS = require("crypto-js");

    var _PADCHAR = "=", _ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    function _getbyte64(s, i) {
        var idx = _ALPHA.indexOf(s.charAt(i));
        if (idx === -1) {
            throw "Cannot decode base64";
        }
        return idx;
    }
    function _getbyte(s, i) {
        var x = s.charCodeAt(i);
        if (x > 255) {
            throw "INVALID_CHARACTER_ERR: DOM Exception 5";
        }
        return x;
    }
    function Base64decode(s) {
        var pads = 0, i, b10, imax = s.length, x = [];
        s = String(s);
        if (imax === 0) {
            return s;
        }
        if (imax % 4 !== 0) {
            throw "Cannot decode base64";
        }
        if (s.charAt(imax - 1) === _PADCHAR) {
            pads = 1;
            if (s.charAt(imax - 2) === _PADCHAR) {
                pads = 2;
            }
            imax -= 4;
        }
        for (i = 0; i < imax; i += 4) {
            b10 = (_getbyte64(s, i) << 18) | (_getbyte64(s, i + 1) << 12) | (_getbyte64(s, i + 2) << 6) | _getbyte64(s, i + 3);
            x.push(String.fromCharCode(b10 >> 16, (b10 >> 8) & 255, b10 & 255));
        }
        switch (pads) {
        case 1:
            b10 = (_getbyte64(s, i) << 18) | (_getbyte64(s, i + 1) << 12) | (_getbyte64(s, i + 2) << 6);
            x.push(String.fromCharCode(b10 >> 16, (b10 >> 8) & 255));
            break;
        case 2:
            b10 = (_getbyte64(s, i) << 18) | (_getbyte64(s, i + 1) << 12);
            x.push(String.fromCharCode(b10 >> 16));
            break;
        }
        return x.join("");
    }
    function Base64encode(s) {
        if (arguments.length !== 1) {
            throw "SyntaxError: exactly one argument required";
        }
        s = String(s);
        var i, b10, x = [], imax = s.length - s.length % 3;
        if (s.length === 0) {
            return s;
        }
        for (i = 0; i < imax; i += 3) {
            b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8) | _getbyte(s, i + 2);
            x.push(_ALPHA.charAt(b10 >> 18));
            x.push(_ALPHA.charAt((b10 >> 12) & 63));
            x.push(_ALPHA.charAt((b10 >> 6) & 63));
            x.push(_ALPHA.charAt(b10 & 63));
        }
        switch (s.length - imax) {
        case 1:
            b10 = _getbyte(s, i) << 16;
            x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 63) + _PADCHAR + _PADCHAR);
            break;
        case 2:
            b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8);
            x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 63) + _ALPHA.charAt((b10 >> 6) & 63) + _PADCHAR);
            break;
        }
        return x.join("");
    }


function decrypt(chapter_content,encryt_keys,chapter_accessKey){
	var s={content:chapter_content.replace("\\",""),keys:encryt_keys.replace("\\","").split(","),accessKey:chapter_accessKey};
	var n=s.content;
	var r=s.keys;
	var t=s.keys.length;
	var q=s.accessKey;
	var o=q.split("");
	var m=o.length;
	var k=new Array();
	k.push(r[(o[m-1].charCodeAt(0))%t]);
	k.push(r[(o[0].charCodeAt(0))%t]);
	for(i=0;i<k.length;i++){
		n=Base64decode(n);
		var p=k[i];
		var j=Base64encode(n.substr(0,16));
		var f=Base64encode(n.substr(16));
		var h=CryptoJS.format.OpenSSL.parse(f);
		n=CryptoJS.AES.decrypt(h,CryptoJS.enc.Base64.parse(p),{iv:CryptoJS.enc.Base64.parse(j),format:CryptoJS.format.OpenSSL});
		if(i<k.length-1){
			n=n.toString(CryptoJS.enc.Base64);
			n=Base64decode(n)
		}
	}
	return n.toString(CryptoJS.enc.Utf8)
}
