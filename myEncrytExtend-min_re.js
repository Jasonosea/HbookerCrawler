function base64_encode(str){
    var c1, c2, c3;
    var base64EncodeChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";        
    var i = 0, len= str.length, string = '';
 
    while (i < len){
        c1 = str.charCodeAt(i++) & 0xff;
        if (i == len){
            string += base64EncodeChars.charAt(c1 >> 2);
            string += base64EncodeChars.charAt((c1 & 0x3) << 4);
            string += "==";
            break;
        }
        c2 = str.charCodeAt(i++);
        if (i == len){
            string += base64EncodeChars.charAt(c1 >> 2);
            string += base64EncodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
            string += base64EncodeChars.charAt((c2 & 0xF) << 2);
            string += "=";
            break;
        }
        c3 = str.charCodeAt(i++);
        string += base64EncodeChars.charAt(c1 >> 2);
        string += base64EncodeChars.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
        string += base64EncodeChars.charAt(((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6));
        string += base64EncodeChars.charAt(c3 & 0x3F)
    }
        return string
}

function base64_decode(str){
        var c1, c2, c3, c4;
        var base64DecodeChars = new Array(
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57,
            58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6,
            7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
            25, -1, -1, -1, -1, -1, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
            37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1,
            -1, -1
        );
        var i=0, len = str.length, string = '';
 
        while (i < len){
            do{
                c1 = base64DecodeChars[str.charCodeAt(i++) & 0xff]
            } while (
                i < len && c1 == -1
            );
 
            if (c1 == -1) break;
 
            do{
                c2 = base64DecodeChars[str.charCodeAt(i++) & 0xff]
            } while (
                i < len && c2 == -1
            );
 
            if (c2 == -1) break;
 
            string += String.fromCharCode((c1 << 2) | ((c2 & 0x30) >> 4));
 
            do{
                c3 = str.charCodeAt(i++) & 0xff;
                if (c3 == 61)
                    return string;
 
                c3 = base64DecodeChars[c3]
            } while (
                i < len && c3 == -1
            );
 
            if (c3 == -1) break;
 
            string += String.fromCharCode(((c2 & 0XF) << 4) | ((c3 & 0x3C) >> 2));
 
            do{
                c4 = str.charCodeAt(i++) & 0xff;
                if (c4 == 61) return string;
                c4 = base64DecodeChars[c4]
            } while (
                i < len && c4 == -1
            );
 
            if (c4 == -1) break;
 
            string += String.fromCharCode(((c3 & 0x03) << 6) | c4)
        }
        return string;
    }

var CryptoJS = require("CryptoJS/crypto-js");

function myDecrypt(f){
	var b=function(g){
		this.$element=g,this.defaults={type:"rsa"}
	};
	b.prototype={
		decrypt:function(g){
			var s=g;
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
				n=base64_decode(n);
				var p=k[i];
				var j=base64_encode(n.substr(0,16));
				var f=base64_encode(n.substr(16));
				var h=CryptoJS.format.OpenSSL.parse(f);
				n=CryptoJS.AES.decrypt(h,CryptoJS.enc.Base64.parse(p),{iv:CryptoJS.enc.Base64.parse(j),format:CryptoJS.format.OpenSSL});
				if(i<k.length-1){
					n=n.toString(CryptoJS.enc.Base64);n=base64_decode(n)
				}
			}
			return n.toString(CryptoJS.enc.Utf8)
		}
	};
	var g=new b([]);
	return g.decrypt(f)
}