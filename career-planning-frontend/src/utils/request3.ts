import axios from 'axios'
import { ElMessage } from 'element-plus'
// 创建axios实例
const request = axios.create({
    baseURL: import.meta.env.VITE_API_URL,// 所有的请求地址前缀部分,及基础路径
    timeout: 80000, // 请求超时时间(毫秒)
    withCredentials: true,// 异步请求携带cookie
    // headers: {
    // 设置后端需要的传参类型
    // 'Content-Type': 'application/json',
    // 'token': x-auth-token',//一开始就要token
    // 'X-Requested-With': 'XMLHttpRequest',
    // },
})
 
// request实例添加请求和相应拦截器
request.interceptors.request.use(
    config => {
        // 如果你要去localStor获取token,(如果你有)
        // let token = localStorage.getItem("x-auth-token");
        // if (token) {
                //添加请求头
                //config.headers["Authorization"]="Bearer "+ token
        // }
        //返回配置对象
        return config
    },
    error => {
        // 对请求错误做些什么
        Promise.reject(error)
    }
)
 
//  响应拦截器
request.interceptors.response.use(
    response => {
        //成功的响应数据会进入这里，失败的响应数据会进入error
        // 对响应数据做点什么处理
        return response.data
    },
    error => {  
        //失败回调
        //定义一个数据存储网络错误信息
        let message = '';
        if (error.response) {
            // 请求已发出，但服务器响应的状态码不在 2xx 范围内
            message = error.response.data.message || "网络请求失败";
        } else if (error.request) {
            // 请求已发出，但没有收到响应
            message = "网络连接超时";
        } else {
            // 一些设置请求时发生的事
            message = error.message || "网络请求失败";
        }

        ElMessage({
            type: 'error',
            message
        });
        return Promise.reject(message);
    }
)
// 导出request实例
export default request