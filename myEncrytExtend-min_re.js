(function(d,c,a,e){
	var b=function(g,f){
		this.$element=g,this.defaults={type:"rsa"},this.options=d.extend({},this.defaults,f)
	};
	b.prototype={
		encrypt:function(g){
			var h={
				content:"",keys:[],accessKey:""
			};
			var f=d.extend({},h,g)
		},
		decrypt:function(g){
			var l={
				content:"",keys:[],accessKey:""
			};
			var s=d.extend({},l,g);
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
				n=d.base64.decode(n);
				var p=k[i];
				var j=d.base64.encode(n.substr(0,16));
				var f=d.base64.encode(n.substr(16));
				var h=CryptoJS.format.OpenSSL.parse(f);
				n=CryptoJS.AES.decrypt(h,CryptoJS.enc.Base64.parse(p),{iv:CryptoJS.enc.Base64.parse(j),format:CryptoJS.format.OpenSSL});
				if(i<k.length-1){
					n=n.toString(CryptoJS.enc.Base64);n=d.base64.decode(n)
				}
			}
			return n.toString(CryptoJS.enc.Utf8)
		}
	};
	d.extend({
		myDecrypt:function(f){
			var g=new b([]);
			return g.decrypt(f)
		}
	})
})(jQuery,window,document);