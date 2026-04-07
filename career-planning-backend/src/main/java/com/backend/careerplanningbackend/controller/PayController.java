package com.backend.careerplanningbackend.controller;

import com.alipay.api.AlipayApiException;
import com.backend.careerplanningbackend.domain.po.PaymentOrder;
import com.backend.careerplanningbackend.service.PayService;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * PayController
 * 支付控制器
 * 处理与支付相关的业务逻辑，包括创建订单、支付回调等
 * 主要功能：
 * 1. 创建支付订单并跳转到支付宝收银台
 * 2. 处理支付宝异步支付结果通知
 * 3. 订单支付接口
 * @module PayController
 */
@Slf4j
@RestController
@RequestMapping("/alipay")
@RequiredArgsConstructor
public class PayController {

    private final PayService payService;

    /**
     * 前端点击下单 → 创建待支付订单 → 调用支付宝接口生成支付二维码 →
     * 用户扫码支付 → 支付宝异步通知支付结果 → 系统处理通知并更新订单状态
     * 1. 前端点击“立即支付”→ 调用本接口
     * 2. 本接口返回二维码链接（qr_code）→ 前端生成二维码展示
     */
//    @PostMapping("/pay/{orderNumber}")
//    public Result pay(@PathVariable String orderNumber) throws AlipayApiException {
//        PonintsTransactionDTO order = new OrderListDTO();
//        Long userId = Long.parseLong(ThreadLocalUtil.get());
//        order.setUserId(userId);
//        order.setOrderNumber(orderNumber);
//        return payService.pay(order);
//    }

    /**
     * orderNoPay
     * 电脑网站支付订单接口
     * 前端直接访问此接口，浏览器会 302 重定向到支付宝沙箱收银台
     *
     * @param paymentOrder 支付订单信息
     * @param response HTTP 响应对象
     * @throws Exception 支付异常
     */
    @PostMapping("/pay/order")
    public void orderNoPay(@RequestBody PaymentOrder paymentOrder, HttpServletResponse response) throws Exception {
        log.info("paymentOrder: {}", paymentOrder);
        payService.orderNoPay(paymentOrder,response);
    }

    /**
     * pagePay
     * 页面支付接口
     * 根据订单号跳转到支付宝收银台
     *
     * @param orderNumber 订单号
     * @param response HTTP 响应对象
     * @throws Exception 支付异常
     */
    @GetMapping("/pay/{orderNumber}")
    public void pagePay(@PathVariable Long orderNumber, HttpServletResponse response) throws Exception {
        log.info("orderNumber: {}", orderNumber);
        payService.pagePay(orderNumber,response);
    }

    /**
     * returns
     * 支付宝异步通知回调接口
     * 当用户支付成功后，支付宝会调用此接口通知支付结果
     *
     * @param request HTTP 请求对象，包含支付结果通知
     */
    @PostMapping("/notify")
    public void returns(HttpServletRequest request) {
        log.info("进入回调notify");
        payService.notifyPayment(request);
    }
}
