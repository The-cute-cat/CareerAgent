

//登录接口需要携带的参数类型定义
export interface loginForm {
    username: string,
    password: string,
    rememberMe: boolean
}

interface dataType{
    token: string,
}

//登录接口返回的数据类型定义
export interface loginResponseData {
    code: number,
    data: dataType
}


interface userInfo{
    userId:number,
    avatar: string,
    username: string,
    password: string,
    desc: string,
    email: string,
    phone: string,
    role: string[],
    createTime: string,
    updateTime: string,
    token: string
}


//服务器返回的用户信息类型定义

interface user {
    checkUser:userInfo,
}

export interface userInfoResponseData {
    code: number,
    data: user
}