package org.ogios;

import net.dongliu.requests.Cookie;
import net.dongliu.requests.RawResponse;
import net.dongliu.requests.Requests;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLDecoder;
import java.security.Security;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Login {

    String username;
    String password;
    Map<String, String> headers = new HashMap<>();
    Map<String, Object> cookies_lms = new HashMap<>();
    Map<String, Object> cookies_identify = new HashMap<>();
    Map<String, Object> cookies_sso = new HashMap<>();

    public Login(String username, String  password){
        this.username = username;
        this.password = password;
        this.cookies_sso.put("org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE", "zh_CN");
        String UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50";
        this.headers.put("User-Agent", UA);
    }

    RawResponse init(){
        RawResponse res;
        List<Cookie> cookies;
        String location;

        // 进入lms登录网址等待session和重定向网址
        String url = "http://lms.eurasia.edu/login";
        res =  Requests.get(url)
                .headers(this.headers)
                .followRedirect(false)
                .cookies(this.cookies_lms)
                .send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_lms.put(cookie.getName(), cookie.getValue());
        }
        System.out.println("this.cookies_lms = " + this.cookies_lms);


        // 获取identity重定向网址获取cookies
        location = res.getHeader("Location");
        System.out.println("location = " + location);
        assert location != null;
        res = Requests.get(location).headers(this.headers).followRedirect(false).cookies(this.cookies_identify).send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_identify.put(cookie.getName(), cookie.getValue());
        }
        System.out.println("this.cookies_identify = " + this.cookies_identify);


        // 初始化 cookies_identify 里的 CLIENT_URL 和 SERVICE。获取登录页的url
        location = res.getHeader("Location");
        System.out.println("location = " + location);
        assert location != null;
        res = Requests.get(location).headers(this.headers).followRedirect(false).cookies(this.cookies_identify).send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_identify.put(cookie.getName(), cookie.getValue());
        }
        System.out.println("this.cookies_identify = " + this.cookies_identify);


        // 进入sso登录页，获取cookie和加密参数等
        location = res.getHeader("Location");
        System.out.println("location = " + location);
        assert location != null;
        res = Requests.get(location).headers(this.headers).cookies(this.cookies_sso).followRedirect(false).send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_sso.put(cookie.getName(), cookie.getValue());
        }
        System.out.println("this.cookies_sso = " + this.cookies_sso);
        return res;
    }


    Map<String, String> dataGen(String salt, String execution, String dllt){
        String cipherText = Encrypt.encrypt(this.password, salt);
        Map<String, String> data = new HashMap<>();
        data.put("username", this.username);
        data.put("password", cipherText);
        data.put("captcha", "");
        data.put("_eventId", "submit");
        data.put("cllt", "userNameLogin");
        data.put("dllt", dllt);
        data.put("lt", "");
        data.put("execution", execution);
        return data;
    }

    Map<String, String> parseSSO(String html){
        Document doc = Jsoup.parse(html);
        String salt = doc.select("#pwdEncryptSalt").val();
        String execution = doc.select("#execution").val();
        String dllt = doc.select("#dllt").val();
        return dataGen(salt, execution, dllt);
    }

    Map<String, Object> _login(String url, Map<String, String> formdata){
        RawResponse res;
        List<Cookie> cookies;
        String location;

        // post登录
        res = Requests.post(url)
                .body(formdata)
                .headers(this.headers)
                .cookies(this.cookies_sso)
                .followRedirect(false)
                .send();
        location = res.getHeader("Location");
        location = URLDecoder.decode(location);
        assert location != null;
        String hostname;
        try {
            hostname = new URL(location).getHost();
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
        assert hostname.equals("identity.eurasia.edu");
        res = Requests.get(location)
                .headers(this.headers)
                .cookies(this.cookies_identify)
                .followRedirect(false)
                .send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_identify.put(cookie.getName(), cookie.getValue());
        }
        System.out.println("this.cookies_identify = " + this.cookies_identify);

        location = res.getHeader("Location");
        location = URLDecoder.decode(location);
        try{
            hostname = new URL(location).getHost();
        } catch (Exception e){
            e.printStackTrace();
        }
        assert hostname.equals("lms.eurasia.edu");
        res = Requests.get(location)
                .headers(this.headers)
                .cookies(this.cookies_lms)
                .followRedirect(false)
                .send();
        cookies = res.getCookies();
        for (Cookie cookie : cookies) {
            this.cookies_lms.put(cookie.getName(),cookie.getValue());
        }
        System.out.println("this.cookies_lms = " + this.cookies_lms);

        return this.cookies_lms;
    }

    public Map<String, Object> login(){
        RawResponse loginhtml = init();
        Map<String, String> formdata = parseSSO(loginhtml.readToText());
        return _login(loginhtml.getURL(), formdata);
    }


}