<div align="center">

# 欧亚学院畅课登录
> 主要用于闲时练手，平常还是直接用网页端方便
</div>

sso这套登录流程... 在最开始那会我什么知识都不懂的时候根本不知道是怎么给的session。  
就只会一直在浏览器的开发者页面死磕，直到最后放弃，改用手动提取session，虽然selenium/playwright这类自动化也可以解决，但是会让整个程序变得臃肿不堪。

我在密码学上一有些一窍不通。  

总结一下过程吧  
抓包之后过程很清晰明朗，属于是通读一遍就知道是怎么个流程。关于密码的加密方式在做打卡程序的时候就已经了解了，是相同的js文件。  
今天一口气写完之后觉得还可以精简，因为用到js，也就用到pyexecjs，也就是说会调用node环境，但密码实际上只是简单的aes加密而已。我决定用python直接实现得了，这要看懂他的js代码，然后根据加密原理自己写一套python代码，但是我屁都不会，费了一些时间学了原理之后磕磕绊绊的才写出来...

## 登录
> 主程序 `main.py` 
创建 `Login` 对象传入学号密码之后直接调用login方法即可
```python
class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    ...
    
    def login(self) -> SSO:
        baseRequest = self.init()
        data = self.parseSSO(baseRequest.text)
        return self._login(baseRequest.url, data)
```
返回的是一个SSO对象，该类是为了保证session持续化的，每次请求服务器都会返回一个新的session，之前的session可以使用，但是持久性我并没有测试过

不过我没做验证码的模块，主要是因为懒，其次是因为没必要。登录失败次数过多时才进入状态要你输入验证码，登陆成功之后就取消了这个状态，而且基本没有莫名其妙登录失败的情况

## 登陆后使用
由于登陆后每次请求一个页面都会传给你一个新的session，我没测试旧session的持续时间是多少，但是旧session是可以用的。  

SSO主要便于之后拓展功能的使用
```python
class SSO:
    def __init__(self, cookies: requests.cookies.RequestsCookieJar):
        self.cookies = cookies
        
    ...

    def get(self, url, params=None, proxies=None, allow_redirects=True):
        res = requests.get(url, params=params, headers=self.headers, cookies=self.cookies, proxies=proxies,
                           allow_redirects=allow_redirects)
        for i in res.cookies:
            if i.name == "session":
                self.cookies.set(i.name, i.value)
        return res

    def post(self, url, data=None, params=None, proxies=None, allow_redirects=True):
        res = requests.post(url, params=params, data=data, proxies=proxies, headers=self.headers, cookies=self.cookies,
                            allow_redirects=allow_redirects)
        for i in res.cookies:
            if i.name == "session":
                self.cookies.set(i.name, i.value)
        return res

    ...
```
