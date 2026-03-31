package com.backend.careerplanningbackend.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.internal.util.AlipaySignature;
import com.alipay.api.request.AlipayTradePagePayRequest;
import com.alipay.api.request.AlipayTradePrecreateRequest;
import com.alipay.api.response.AlipayTradePrecreateResponse;
import com.backend.careerplanningbackend.config.AliPayConfig;
import com.backend.careerplanningbackend.domain.po.PaymentOrder;
import com.backend.careerplanningbackend.domain.po.PointsTransaction;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.mapper.PaymentOrderMapper;
import com.backend.careerplanningbackend.mapper.PointsTransactionMapper;
import com.backend.careerplanningbackend.service.PayService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class PayServiceImpl implements PayService {
    @Autowired
    private AlipayClient alipayClient;   // 前面配好的 Bean

    private static final String FORMAT = "json";

    private static final String CHARSET = "UTF-8";

    private static final String SIGN_TYPE = "RSA2";

    @Resource
    public AliPayConfig alipayConfig;

    @Resource
    public PointsTransactionMapper pointsTransactionMapper;
    
    @Resource
    public PaymentOrderMapper paymentOrderMapper;
    
    
//    @Override
//    public Result pay() throws AlipayApiException {
//        /* 2. 组装支付宝当面付请求 */
//        //支付宝开放平台里的“当面付-预下单接口”（也叫“扫码支付”）。
//        //调用成功后，支付宝会返回一个 qr_code 字符串，你们前端把它生成二维码，顾客用支付宝 App 扫这个码就能付款。
//        AlipayTradePrecreateRequest request = new AlipayTradePrecreateRequest();
//        request.setNotifyUrl(alipayConfig.getNotifyUrl());
//
//        JSONObject biz = new JSONObject();
//        String orderNumber=order.getOrderNumber();
//        biz.put("out_trade_no", orderNumber);
//        biz.put("total_amount", 0.01);
//        biz.put("total_amount", dbOrder.getTotalPrice().toString());
//        biz.put("subject", "外卖订单-" + orderNumber);
//        biz.put("timeout_express", "5m");
//        request.setBizContent(biz.toString());
//
//        /* 3. 发起调用 */
//        AlipayTradePrecreateResponse response = alipayClient.execute(request);
//        if (!response.isSuccess()) {
//            throw new RuntimeException("支付宝下单失败:" + response.getMsg());
//        }
//        log.info("【支付宝响应】{}", JSON.toJSONString(response));
//        return Result.ok(response.getQrCode());
//    }


    /**
     * 电脑网站支付（跳转支付宝收银台）
     */
    @Override
    public void orderNoPay(PaymentOrder paymentOrder, HttpServletResponse response) throws IOException {
//        PaymentOrder paymentOrder = paymentOrderMapper.selectOne(new LambdaQueryWrapper<PaymentOrder>()
//                .eq(PaymentOrder::getOrderNo, orderNumber)
//        );

        // 初始化配置
        AlipayClient alipayClient = new DefaultAlipayClient(alipayConfig.getGateway(), 
                alipayConfig.getAppId(), alipayConfig.getPrivateKey(), FORMAT, CHARSET,
                alipayConfig.getPublicKey(), SIGN_TYPE);

        AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();
        request.setReturnUrl(alipayConfig.getReturnUrl());
        request.setNotifyUrl(alipayConfig.getNotifyUrl());

        JSONObject biz = new JSONObject();
        biz.put("out_trade_no", paymentOrder.getOrderNo()); //这是payment_order的order_no, 亦是points_transaction 的主键 id
        biz.put("total_amount", paymentOrder.getAmount());
        biz.put("subject", "积分充值订单-" + paymentOrder.getId());
        biz.put("product_code", "FAST_INSTANT_TRADE_PAY"); // 电脑网站支付固定值
        request.setBizContent(biz.toString());

        String body=null;
        try {
            body = alipayClient.pageExecute(request).getBody();
        } catch (AlipayApiException e) {
            e.printStackTrace();
        }
        // 直接返回一段带表单的 html，前端浏览器会自动提交跳转
        response.setContentType("text/html;charset=UTF-8");
        response.getWriter().write(body);   // 自动提交表单
        response.getWriter().flush();
        response.getWriter().close();
        System.out.println("沙箱支付展示订单展示，回调");
    }
    
    @Override
    public void pagePay(Long orderNumber, HttpServletResponse response) throws IOException {
        PaymentOrder paymentOrder = paymentOrderMapper.selectOne(new LambdaQueryWrapper<PaymentOrder>()
                .eq(PaymentOrder::getOrderNo, orderNumber)
        );

        if (paymentOrder == null){
            log.error("订单不存在:{}", orderNumber);
            throw new RuntimeException("订单不存在");
        }
        // 初始化配置
        AlipayClient alipayClient = new DefaultAlipayClient(alipayConfig.getGateway(),
                alipayConfig.getAppId(), alipayConfig.getPrivateKey(), FORMAT, CHARSET,
                alipayConfig.getPublicKey(), SIGN_TYPE);

        AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();
        request.setReturnUrl(alipayConfig.getReturnUrl());
        request.setNotifyUrl(alipayConfig.getNotifyUrl());

        JSONObject biz = new JSONObject();
        biz.put("out_trade_no", paymentOrder.getOrderNo()); //这是payment_order的order_no, 亦是points_transaction 的主键 id
        biz.put("total_amount", paymentOrder.getAmount());
        biz.put("subject", "积分充值订单-" + paymentOrder.getId());
        biz.put("product_code", "FAST_INSTANT_TRADE_PAY"); // 电脑网站支付固定值
        request.setBizContent(biz.toString());

        String body=null;
        try {
            body = alipayClient.pageExecute(request).getBody();
        } catch (AlipayApiException e) {
            e.printStackTrace();
        }
        // 直接返回一段带表单的 html，前端浏览器会自动提交跳转
        response.setContentType("text/html;charset=UTF-8");
        response.getWriter().write(body);   // 自动提交表单
        response.getWriter().flush();
        response.getWriter().close();
        System.out.println("沙箱支付展示订单展示，回调");
    }

    @Override
    public void pagePayByUserId(Long orderNumber, HttpServletResponse response) throws AlipayApiException, IOException {
        PaymentOrder paymentOrder = paymentOrderMapper.selectOne(new LambdaQueryWrapper<PaymentOrder>()
                .eq(PaymentOrder::getUserId, orderNumber)
        );

        if (paymentOrder == null){
            log.error("订单不存在:{}", orderNumber);
            throw new RuntimeException("订单不存在");
        }
        // 初始化配置
        AlipayClient alipayClient = new DefaultAlipayClient(alipayConfig.getGateway(),
                alipayConfig.getAppId(), alipayConfig.getPrivateKey(), FORMAT, CHARSET,
                alipayConfig.getPublicKey(), SIGN_TYPE);

        AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();
        request.setReturnUrl(alipayConfig.getReturnUrl());
        request.setNotifyUrl(alipayConfig.getNotifyUrl());

        JSONObject biz = new JSONObject();
        biz.put("out_trade_no", paymentOrder.getOrderNo()); //这是payment_order的order_no, 亦是points_transaction 的主键 id
        biz.put("total_amount", paymentOrder.getAmount());
        biz.put("subject", "积分充值订单-" + paymentOrder.getId());
        biz.put("product_code", "FAST_INSTANT_TRADE_PAY"); // 电脑网站支付固定值
        request.setBizContent(biz.toString());

        String body=null;
        try {
            body = alipayClient.pageExecute(request).getBody();
        } catch (AlipayApiException e) {
            e.printStackTrace();
        }
        // 直接返回一段带表单的 html，前端浏览器会自动提交跳转
        response.setContentType("text/html;charset=UTF-8");
        response.getWriter().write(body);   // 自动提交表单
        response.getWriter().flush();
        response.getWriter().close();
        System.out.println("沙箱支付展示订单展示，回调");
    }

    @Override
    public void notifyPayment(HttpServletRequest request) {
        Map<String, String> params = convertRequestParams(request);

        /* 1. 验签 */
        boolean signVerified;
        try {
            signVerified = AlipaySignature.rsaCheckV1(
                    params, alipayConfig.getPublicKey(), "UTF-8", "RSA2");
        } catch (AlipayApiException e) {
            log.error("验签异常", e);
            return;
        }
        if (!signVerified) {
            log.warn("支付宝通知验签失败");
            return;
        }

        /* 2. 只处理成功/完结状态 */
        String tradeStatus = params.get("trade_status");
        if (!"TRADE_SUCCESS".equals(tradeStatus) && !"TRADE_FINISHED".equals(tradeStatus)) {
            return;
        }

        String outTradeNo = params.get("out_trade_no");

        /* 3. 幂等：已支付直接返回 success */
        PointsTransaction pointsTransaction = pointsTransactionMapper.selectById(outTradeNo);
        if (pointsTransaction == null) {
            log.warn("通知订单号不存在:{}", outTradeNo);
            return;
        }

        ///. todo 真正业务：改状态、扣库存、清购物车 /
        // todo 异步将状态修改了
//        pointsTransactionMapper.updateOrderAndPayStatus(outTradeNo,0);
//        paymentOrderMapper.updateStatus(outTradeNo, 1);

        log.info("订单{}支付完成", outTradeNo);
    }

    private Map<String, String> convertRequestParams(HttpServletRequest req) {
        Map<String, String> res = new HashMap<>();
        req.getParameterMap().forEach((k, v) -> res.put(k, v[0]));
        return res;
    }

    // todo ,上面那个不行才使用下面这个
//    public void notifyPayment(HttpServletRequest request, HttpServletResponse response) throws IOException {
//        Map<String, String> params = convertRequestParams(request);
//
//        try {
//            // 1. 验签
//            boolean signVerified = AlipaySignature.rsaCheckV1(
//                    params, alipayConfig.getPublicKey(), "UTF-8", "RSA2");
//            if (!signVerified) {
//                log.warn("支付宝通知验签失败");
//                response.getWriter().write("fail");
//                return;
//            }
//
//            // 2. 状态检查
//            String tradeStatus = params.get("trade_status");
//            if (!"TRADE_SUCCESS".equals(tradeStatus) && !"TRADE_FINISHED".equals(tradeStatus)) {
//                response.getWriter().write("success"); // 非成功状态也返回success，不再通知
//                return;
//            }
//
//            String outTradeNo = params.get("out_trade_no");
//
//            // 3. 幂等检查
//            PaymentOrder paymentOrder = paymentOrderMapper.selectOne(
//                    new LambdaQueryWrapper<PaymentOrder>()
//                            .eq(PaymentOrder::getOrderNo, outTradeNo)
//            );
//
//            if (paymentOrder == null) {
//                log.error("订单不存在:{}", outTradeNo);
//                response.getWriter().write("fail");
//                return;
//            }
//
//            if (paymentOrder.getStatus() == 1) { // 已支付
//                response.getWriter().write("success");
//                return;
//            }
//
//            // 4. 更新订单状态 + 加积分（需要加事务 @Transactional）
//            paymentOrder.setStatus(1);
//            paymentOrder.setTradeNo(params.get("trade_no")); // 支付宝交易号
//            paymentOrderMapper.updateById(paymentOrder);
//
//            // 更新积分交易记录
//            PointsTransaction pt = pointsTransactionMapper.selectById(paymentOrder.getPointsTransactionId());
//            if (pt != null && pt.getStatus() != 1) {
//                pt.setStatus(1);
//                pointsTransactionMapper.updateById(pt);
//                // TODO: 给用户账户加积分
//            }
//
//            log.info("订单{}支付成功处理完成", outTradeNo);
//            response.getWriter().write("success");
//
//        } catch (Exception e) {
//            log.error("支付回调处理异常", e);
//            response.getWriter().write("fail"); // 让支付宝重试
//        }
//    }
}
