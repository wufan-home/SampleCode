# OPTIONS

In this note, we shall collect some example usages of the HTTP method `OPTIONS`.

## Basic usage
Run
```bash
curl -i -X OPTIONS www.google.com
```

Output
```bash
HTTP/1.1 405 Method Not Allowed
Via: 1.1 2606:b400:1824:e004:4000::101 (McAfee Web Gateway 7.7.2.3.0.23892)
Date: Tue, 30 Apr 2019 03:45:03 GMT
Allow: GET, HEAD
Server: gws
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
Content-Length: 1592
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 0

<!DOCTYPE html>
<html lang=en>
  <meta charset=utf-8>
  <meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">
  <title>Error 405 (Method Not Allowed)!!1</title>
  <style>
    *{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}@media only screen and (-webkit-min-device-pixel-ratio:2){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}
  </style>
  <a href=//www.google.com/><span id=logo aria-label=Google></span></a>
  <p><b>405.</b> <ins>That’s an error.</ins>
  <p>The request method <code>OPTIONS</code> is inappropriate for the URL <code>/</code>.  <ins>That’s all we know.</ins>
```
