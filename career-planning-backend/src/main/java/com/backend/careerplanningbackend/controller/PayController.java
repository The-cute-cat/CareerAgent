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

@Slf4j
@RestController
@RequestMapping("/member")
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
     * 电脑网站支付：前端直接访问 /alipay/pagePay/{orderNumber}
     * 浏览器会 302 到支付宝沙箱收银台
     */
    @GetMapping("/pay/order")
    public void orderNoPay(PaymentOrder paymentOrder, HttpServletResponse response) throws Exception {
        log.info("paymentOrder: {}", paymentOrder);
        payService.orderNoPay(paymentOrder,response);
    }
    
    @GetMapping("/pay/{orderNumber}")
    public void pagePay(@PathVariable Long orderNumber, HttpServletResponse response) throws Exception {
        log.info("orderNumber: {}", orderNumber);
        payService.pagePay(orderNumber,response);
    }

    /**
     * 支付成功异步通知
     */
    @PostMapping("/notify")
    public void returns(HttpServletRequest request) {
        System.out.println("进入回调notify");
        payService.notifyPayment(request);
    }
}
