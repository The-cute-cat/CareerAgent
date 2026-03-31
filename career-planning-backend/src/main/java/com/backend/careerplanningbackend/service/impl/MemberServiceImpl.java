package com.backend.careerplanningbackend.service.impl;

import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.po.*;
import com.backend.careerplanningbackend.mapper.MemberMapper;
import com.backend.careerplanningbackend.mapper.PointsTransactionMapper;
import com.backend.careerplanningbackend.mapper.UserMapper;
import com.backend.careerplanningbackend.mapper.UserReferralMapper;
import com.backend.careerplanningbackend.service.MemberService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.AmqpException;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessagePostProcessor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Arrays;

@Service
@Slf4j
@RequiredArgsConstructor
public class MemberServiceImpl implements MemberService {

    private final UserMapper userMapper;
    private final MemberMapper memberMapper;
    private final PointsTransactionMapper pointsTransactionMapper;
    private final RabbitTemplate rabbitTemplate;
    private final UserReferralMapper userReferralMapper;

    @Override
    public Result<String> insertMember(PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        UserMembership userMembership = new UserMembership();
        userMembership.setUserId(pointsMembershipChangeDTO.getUserId());
        userMembership.setLevel(pointsMembershipChangeDTO.getVip());
        userMembership.setExpireTime(LocalDateTime.now().plusYears(1));

        int inserted = memberMapper.insert(userMembership);
        if (inserted > 0) {
            log.info("成功插入会员信息: {}", userMembership);
            return Result.ok();
        } else {
            log.error("插入会员信息失败: {}", userMembership);
            return Result.fail("插入会员信息失败");
        }
    }

    @Override
    public Result<String> insertNewMember(PointsMembershipChangeDTO pointsMembershipChangeDTO) {
//        // 30天前时间 -创建账号时间-now    useful
//        LocalDateTime beforeNowDays = LocalDateTime.now().minusDays(30);
//        LocalDateTime now = LocalDateTime.now();
//
//        // 0 表示新用户 , 1 表示老用户
//        Long selected = userMapper.selectCount(new LambdaQueryWrapper<User>()
//                .eq(User::getId, pointsMembershipChangeDTO.getUserId())
//                .between(User::getCreateTime, beforeNowDays, now)
//        );
//
//        // 检查用户是否已经存在积分交易记录，如果存在则不插入会员信息
//        Long selectCount = pointsTransactionMapper.selectCount(new LambdaQueryWrapper<PointsTransaction>()
//                        .eq(PointsTransaction::getUserId, pointsMembershipChangeDTO.getUserId())
//                        .in(PointsTransaction::getType, Arrays.asList(1, 0))
////                .ge(PointsTransaction::getCreateTime, LocalDateTime.now().minusMonths(1))
//                        .between(PointsTransaction::getCreateTime, beforeNowDays, now)
//        );
//        if(selectCount > 0 || selected > 0) {
//            log.info("用户 {} 已经存在积分交易记录，跳过插入会员信息", pointsMembershipChangeDTO.getUserId());
//            UserMembership userMembership = new UserMembership();
//            userMembership.setUserId(pointsMembershipChangeDTO.getUserId());
//            userMembership.setLevel(pointsMembershipChangeDTO.getVip());
//            userMembership.setExpireTime(LocalDateTime.now().plusYears(1));
//
//            int inserted = memberMapper.insert(userMembership);
//            if (inserted > 0) {
//                log.info("成功插入会员信息: {}", userMembership);
//                return Result.ok();
//            } else {
//                log.error("插入会员信息失败: {}", userMembership);
//                return Result.fail("插入会员信息失败");
//            }
//        }
        UserMembership userMembership = new UserMembership();
        userMembership.setUserId(pointsMembershipChangeDTO.getUserId());
        userMembership.setLevel(pointsMembershipChangeDTO.getVip());
        userMembership.setExpireTime(LocalDateTime.now().plusYears(1));

        int inserted = memberMapper.insert(userMembership);
        if (inserted > 0) {
            log.info("成功插入会员信息: {}", userMembership);
        } else {
            log.error("插入会员信息失败: {}", userMembership);
        }

        UserReferral userReferral = userReferralMapper.selectOne(new LambdaQueryWrapper<UserReferral>()
                .eq(UserReferral::getUserId, pointsMembershipChangeDTO.getUserId())
        );

        if(userReferral == null) {
            log.info("用户 {} 没有被邀请过，跳过转发积分消息", pointsMembershipChangeDTO.getUserId());
            return Result.ok();
        }
        
        // 4. 发送rabbitmq,积分表创建
        String exchange = "career.direct";
        String routingKey = "user.new.insert.membership";

        rabbitTemplate.convertAndSend(exchange, routingKey, userReferral, new MessagePostProcessor() {
            @Override
            public Message postProcessMessage(Message message) throws AmqpException {
                message.getMessageProperties()
                        .setExpiration("10000");
                return message;
            }
        });

        log.info("MemberServiceImpl insertNewMember 消息发送成功！");
        return Result.ok("Result MemberServiceImpl insertNewMember 消息发送成功！");
    }

    @Override
    public Result<UserMembership> getMember(Long userId) {
        UserMembership userMembership = memberMapper.selectOne(new LambdaQueryWrapper<UserMembership>()
                .eq(UserMembership::getUserId, userId)
        );
        return Result.ok(userMembership);
    }

    /**
     * 续费会员时更新积分交易记录的描述
     * @param pointsMembershipChangeDTO
     * @return
     */
    @Override
    public Result<String> updateMember(PointsMembershipChangeDTO pointsMembershipChangeDTO) {
        int updated = pointsTransactionMapper.update(null, new LambdaUpdateWrapper<PointsTransaction>()
                .eq(PointsTransaction::getUserId, pointsMembershipChangeDTO.getUserId())
                .eq(PointsTransaction::getType, 0)
                .set(PointsTransaction::getDescription, "会员续费")
        );
        if (updated == 0) {
            log.info("用户 {} 没有找到续费的积分交易记录，无法更新描述", pointsMembershipChangeDTO.getUserId());
            return Result.fail("没有找到续费的积分交易记录，无法更新描述");
        }

        int update = memberMapper.update(null, new LambdaUpdateWrapper<UserMembership>()
                .eq(UserMembership::getUserId, pointsMembershipChangeDTO.getUserId())
                .set(UserMembership::getExpireTime, LocalDateTime.now().plusYears(1))
                .set(UserMembership::getLevel, pointsMembershipChangeDTO.getVip())
        );
        if (update == 0) {
            log.info("用户 {} 没有找到会员信息，无法更新过期时间", pointsMembershipChangeDTO.getUserId());
            return Result.fail("没有找到会员信息，无法更新过期时间");
        }
        return Result.ok("成功更新会员信息和积分交易记录描述");
    }


}
