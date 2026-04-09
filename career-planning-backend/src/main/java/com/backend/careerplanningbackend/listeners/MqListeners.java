package com.backend.careerplanningbackend.listeners;

import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.service.PointsReferService;
import com.backend.careerplanningbackend.util.MailUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.ExchangeTypes;
import org.springframework.amqp.rabbit.annotation.*;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class MqListeners {
    
    private final PointsReferService pointsReferService;
    private final MailUtil mailSender;

    /**
     * 交换 机队列 持久化
     * 懒队列
     * @param referralDTO
     * @throws InterruptedException
     */
    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "points.register.queue", durable = "true"),
            exchange = @Exchange(name = "career.direct", type = ExchangeTypes.DIRECT, durable = "true"),
            key = {"user.registered.points"}
    ))
    public void registerPointsReferService(ReferralDTO referralDTO) throws InterruptedException {
        log.info("消费者 收到了 user.registered.points 的消息：【{}】,listenDirectQueue1", referralDTO);
        
        try {
            
            Result register = pointsReferService.register(referralDTO);
            log.info("处理 user.registered.points 消息完成，用户ID: {}, Result 结果: {},listenDirectQueue1", referralDTO.getUserId(), register);
        }catch (Exception e) {
            log.info("error 处理 user.registered.points 消息失败，用户ID: {}, 错误信息: {},listenDirectQueue1", referralDTO.getUserId(), e.getMessage());
            // 可以选择抛出异常以触发重试机制，或者记录错误后继续
            throw e; // 这里选择抛出异常以触发重试
        }
    }

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "points.invite.queue", durable = "true"),
            exchange = @Exchange(name = "career.direct", type = ExchangeTypes.DIRECT, durable = "true"),
            key = {"user.invited.points"}
    ))
    public void receiverPointsReferService(ReferralDTO referralDTO) throws InterruptedException {
        log.info("消费者 收到了 user.invited.points 的消息：【{}】,listenDirectQueue1", referralDTO);

        try {
            Result register = pointsReferService.receiverPoints(referralDTO);
            log.info("处理 user.invited.points 消息完成，用户ID: {}, Result 结果: {},listenDirectQueue1", referralDTO.getUserId(), register);
        }catch (Exception e) {
            log.info("error 处理 user.invited.points 消息失败，用户ID: {}, 错误信息: {},listenDirectQueue1", referralDTO.getUserId(), e.getMessage());
            // 可以选择抛出异常以触发重试机制，或者记录错误后继续
            throw e; // 这里选择抛出异常以触发重试
        }
    }

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "membership.newinsert.queue", durable = "true"),
            exchange = @Exchange(name = "career.direct", type = ExchangeTypes.DIRECT),
            key = {"user.new.insert.membership"}
    ))
    public void giveInviteVIPGiftPoints(ReferralDTO referralDTO) throws InterruptedException {
        log.info("消费者 收到了 user.new.insert.membership 的消息：【{}】,listenDirectQueue1", referralDTO);

        try {
            Result register = pointsReferService.giveInviteVIPGiftPoints(referralDTO);
            log.info("处理 user.new.insert.membership 消息完成，用户ID: {}, Result 结果: {},listenDirectQueue1", referralDTO.getUserId(), register);
        }catch (Exception e) {
            log.info("error 处理 user.new.insert.membership 消息失败，用户ID: {}, 错误信息: {},listenDirectQueue1", referralDTO.getUserId(), e.getMessage());
            // 可以选择抛出异常以触发重试机制，或者记录错误后继续
            throw e; // 这里选择抛出异常以触发重试
        }
    }

    /**
     * 人工处理错误,并且告知错误在那里一块
     * error.direct 交换机
     * error.queue 队列
     * @param message
     * @throws InterruptedException
     */
    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "error.queue", durable = "true"),
            exchange = @Exchange(name = "error.direct", type = ExchangeTypes.DIRECT),
            key = {"error"}
    ))
    public void handleError(String message) throws InterruptedException {
        log.info("消费者 收到了 handleError 的消息：【{}】,message", message);

        try {
            mailSender.sendErrorNotification("错误消息需要人工处理",message);
        }catch (Exception e) {
            log.error("error 处理 handleError 消息失败，错误信息: {},message", e.getMessage());
            throw e;// 这里选择抛出异常以触发重试
        }
    }


}
