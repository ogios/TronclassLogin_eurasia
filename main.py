from urllib.parse import urlparse
from pyquery import PyQuery as pq
from typing import Union
import requests
import requests.utils
import requests.cookies
import encrypt


class SSO:
    def __init__(self, cookies: Union[dict, requests.cookies.RequestsCookieJar]):
        self.cookies = cookies
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
        }

    def get(self, url, params=None, proxies=None, allow_redirects=True, stream=False, headers=None):
        res = requests.get(url, params=params, headers=self.headers, cookies=self.cookies, proxies=proxies,
                           allow_redirects=allow_redirects, stream=stream)
        self.resetCookies(res.cookies)
        return res

    def post(self, url, data=None, params=None, proxies=None, allow_redirects=True, stream=False, headers=None):
        if headers is None:
            headers = self.headers
        res = requests.post(url, params=params, data=data, proxies=proxies, headers=headers, cookies=self.cookies,
                            allow_redirects=allow_redirects, stream=stream)
        self.resetCookies(res.cookies)
        return res

    def resetCookies(self, cookies):
        for i in cookies:
            if i.name == "session" or i.name == "core.data.console.session":
                self.cookies.set(i.name, i.value)

    def getCookies(self):
        return self.cookies

    def setCookie(self, name, value):
        self.cookies.set(name, value)

    def replaceCookies(self, cookies):
        if isinstance(cookies, dict):
            self.cookies = requests.utils.cookiejar_from_dict(cookies)
        elif isinstance(cookies, requests.cookies.RequestsCookieJar):
            self.cookies = cookies
        else:
            raise Exception("Cookies格式错误！格式仅可为 'dict' 或 'RequestsCookieJar'")
        return


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
        }
        self.cookies_lms = requests.utils.cookiejar_from_dict({})
        self.cookies_identify = requests.utils.cookiejar_from_dict({})
        self.cookies_sso = requests.utils.cookiejar_from_dict({
            "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE": "zh_CN"
        })

    def init(self):
        """
        请求获取各种cookies，最后获取登录页面
        """

        """
        初始化 cookies_lms 里的 session
        """
        url = "http://lms.eurasia.edu/login"
        res = requests.get(url, headers=self.headers, allow_redirects=False, cookies=self.cookies_lms)
        for i in res.cookies:
            self.cookies_lms.set(i.name, i.value)
        print("cookies_lms:", self.cookies_lms)

        """
        初始化 cookies_identify 里的 AUTH_SESSION 和 KC_RESTART
        """
        url = res.headers["Location"]
        res = requests.get(url, headers=self.headers, allow_redirects=False, cookies=self.cookies_identify)
        for i in res.cookies:
            self.cookies_identify.set(i.name, i.value)
        print("cookies_identify:", self.cookies_identify)

        """
        初始化 cookies_identify 里的 CLIENT_URL 和 SERVICE
        并获取登录页面的html
        """
        url = res.headers["Location"]
        res = requests.get(url, headers=self.headers, allow_redirects=False, cookies=self.cookies_identify)
        for i in res.cookies:
            self.cookies_identify.set(i.name, i.value)
        print("cookies_identify:", self.cookies_identify)
        print(url)

        """
        请求登录页
        """
        url = res.headers["Location"]
        res = requests.get(url, headers=self.headers, allow_redirects=False)
        for i in res.cookies:
            self.cookies_sso.set(i.name, i.value)
        print("cookies_sso:", self.cookies_sso)
        return res

    def _login(self, url, data):
        """
        登录子方法
        """

        """
        发送sso登录所需内容获取Location
        """
        res = requests.post(url, data=data, headers=self.headers, cookies=self.cookies_sso, allow_redirects=False)

        """
        获取lms域名下有效ticket的网址
        """
        url = res.headers["Location"]
        parsed = urlparse(url)
        if parsed.hostname != "identity.eurasia.edu":
            raise Exception(f"Wrong url: {url}")
        res = requests.get(url, headers=self.headers, cookies=self.cookies_identify, allow_redirects=False)
        for i in res.cookies:
            self.cookies_identify.set(i.name, i.value)

        """
        根据网址获得有效session
        """
        try:
            url = res.headers["Location"]
        except Exception as e:
            raise Exception("lms Location获取失败")
        parsed = urlparse(url)
        if parsed.hostname != "lms.eurasia.edu":
            raise Exception(f"Wrong url: {url}")
        res = requests.get(url, headers=self.headers, cookies=self.cookies_lms, allow_redirects=False)
        for i in res.cookies:
            self.cookies_lms.set(i.name, i.value)

        return SSO(self.cookies_lms)

    def login(self) -> SSO:
        baseRequest = self.init()
        data = self.parseSSO(baseRequest.text)
        return self._login(baseRequest.url, data)

    def dataGen(self, dic):
        # with open("./login.js", "r") as f:
        #     js = execjs.compile(f.read())
        # pwd = js.call("encryptPassword", password, dic["salt"])
        pwd = encrypt.encrypt(self.password, dic["salt"])

        data = {
            "username": self.username,
            "password": pwd,
            "captcha": "",
            "_eventId": "submit",
            "cllt": "userNameLogin",
            "dllt": dic["dllt"],
            "lt": "",
            "execution": dic["execution"],
        }
        return data

    def parseSSO(self, text):
        doc = pq(text)
        dic = dict()
        dic["salt"] = doc("#pwdEncryptSalt").val()
        dic["execution"] = doc("#execution").val()
        dic["dllt"] = doc("#dllt").val()
        return self.dataGen(dic)


def test(req: SSO, url: str = "http://lms.eurasia.edu/user/index"):
    res = req.get(url, allow_redirects=False)
    print(res.status_code)
    print("大学生职业生涯规划与就业指导" in res.text)
    # print("后1:",req.getCookies())


if __name__ == "__main__":
    username = 学号
    password = 密码
    login = Login(username, password)
    sso = login.login()
    print("前:", sso.getCookies())
    test(sso)
    print("后:", sso.getCookies())
    test(sso, "http://lms.eurasia.edu/course/155928/content")
    print("后:", sso.getCookies())
