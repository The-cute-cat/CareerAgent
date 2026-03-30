package com.backend.careerplanningbackend.service;

import com.alipay.api.AlipayApiException;
import com.backend.careerplanningbackend.domain.po.PointsTransaction;
import com.backend.careerplanningbackend.domain.po.Result;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

public interface PayService {
//    这个是支付宝的接口，暂时不需要了，后续如果需要再加上
//    电脑生成二维码,手机点击支付的那种
//    Result pay(OrderListDTO order) throws AlipayApiException;

    /**
     * 电脑支付宝网站支付：
     */
    void pagePay(PointsTransaction pointsTransaction, HttpServletResponse response) throws AlipayApiException, IOException;

    /**
     * 支付成功异步通知
     */
    void notifyPayment(HttpServletRequest request);
}
