package com.backend.careerplanningbackend.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.alipay.api.AlipayApiException;
import com.backend.careerplanningbackend.domain.dto.AiChatResponse;
import com.backend.careerplanningbackend.domain.dto.PointsMembershipChangeDTO;
import com.backend.careerplanningbackend.domain.dto.ReferralDTO;
import com.backend.careerplanningbackend.domain.dto.StudentTrueDTO;
import com.backend.careerplanningbackend.domain.po.*;
import com.backend.careerplanningbackend.domain.vo.UserPointsVO;
import com.backend.careerplanningbackend.mapper.PointsTransactionMapper;
import com.backend.careerplanningbackend.mapper.UserMapper;
import com.backend.careerplanningbackend.mapper.UserPointsMapper;
import com.backend.careerplanningbackend.mapper.UserReferralMapper;
import com.backend.careerplanningbackend.service.PayService;
import com.backend.careerplanningbackend.service.PointsReferService;
import com.backend.careerplanningbackend.util.AiServiceClient;
import com.backend.careerplanningbackend.util.RedisIdWorker;
import com.backend.careerplanningbackend.util.ThreadLocalUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.AmqpException;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessagePostProcessor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.RequestBody;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import static com.backend.careerplanningbackend.util.PointsConstant.POINTS_FOR_REFERRAL;
import static com.backend.careerplanningbackend.util.PointsConstant.POINTS_FOR_REGISTRATION;
import static com.backend.careerplanningbackend.util.RedisConstant.*;
import static com.backend.careerplanningbackend.util.SystemActivityConstant.Activity_End_Time;

@Service
@RequiredArgsConstructor
@Slf4j
public class PointsReferServiceImpl implements PointsReferService {

    private final UserPointsMapper userpointsMapper;
    private final PointsTransactionMapper pointsTransactionMapper;
    private final UserReferralMapper userReferralMapper;
    private final UserMapper userMapper;
    private final RedisIdWorker redisIdWorker;
    private final RabbitTemplate rabbitTemplate;
    private final AiServiceClient aiServiceClient;
    private final PayService payService;
    
    /**
     * getAccountPoints 
     * 获取账户积分接口
     * @param userId
     * @return
     * 1. 根据用户ID查询UserPoints表，获取当前积分余额和相关信息
     * 2. 如果用户积分信息不存在，返回错误提示
     * 3. 将查询到的UserPoints信息转换为UserPointsVO对象，并返回给前端
     * 4. 返回UserPointsVO对象
     * 5. 返回积分信息
     */
    
    @Override
    public Result<UserPointsVO> getAccountPoints(Long userId) {
//        UserPoints accountPoints = userpointsMapper.getAccountPoints(id);
        Long currentUserId = ThreadLocalUtil.getCurrentUserId();
        UserPoints accountPoints = userpointsMapper.selectOne(
                new LambdaQueryWrapper<UserPoints>().eq(UserPoints::getUserId, currentUserId)
        );
        if(accountPoints == null) {
            log.error("用户 {} 的积分信息不存在", userId);
            return Result.fail("用户积分信息不存在");
        }
        UserPointsVO userPointsVO = BeanUtil.copyProperties(accountPoints, UserPointsVO.class);
        log.info("用户 {} 的积分信息: {}", userId, userPointsVO);
        return Result.ok(userPointsVO);
    }

    /**
     * register 
     * 新用户注册领取积分接口
     * @param referralDTO
     * @return 
     * 1. 校验邀请码是否存在且有效
     * 2. 更新UserReferral表，绑定用户ID，设置奖励积分和活动结束时间
     * 3. 在UserPoints表中为用户创建积分账户，初始积分为1000，设置状态和时间信息
     * 4. 在PointsTransaction表中记录这笔积分变动，类型为系统赠送，描述为新用户注册赠送积分
     * 5. 返回注册成功的积分信息
     */
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Object> register(@RequestBody ReferralDTO referralDTO) {
        /* 模拟延迟 */
//        try {
//            Thread.sleep(5000);
//        }catch (Exception e){
//            log.error("Thread.sleep--register 注册失败");
//            e.printStackTrace();
//        }
        Long userId = referralDTO.getUserId();
        String inviteCode = referralDTO.getInviteCode();
        UserReferral userReferral = null;
        if (StrUtil.isNotBlank(inviteCode)) {
            userReferral = userReferralMapper.selectOne(
                    new LambdaQueryWrapper<UserReferral>()
                            .select(UserReferral::getUserId, UserReferral::getStatus)
                            .eq(UserReferral::getInviteCode, inviteCode)
            );
        }
        User selectedOne = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .select(User::getId, User::getStatus)
                        .eq(User::getId, userId)
        );
//            User selectedOne = userMapper.selectOne(
//                    new LambdaQueryWrapper<User>()
//                            .eq(User::getId, userId)
//            );
        if (selectedOne == null) {
            log.error("用户 {} 还没有注册成功", userId);
            return Result.fail("用户还没有注册成功");
        }
        if (selectedOne.getStatus() != 1) {
            log.error("用户 {} 已经被封了", userId);
            return Result.fail("用户已经被封了");
        }

        /** 1 PointsTransaction insert */
        PointsTransaction pointsTransaction = new PointsTransaction();
        pointsTransaction.setUserId(userId);
        /* POINTS_FOR_REGISTRATION-新用户注册获得的积分-赠送积分 */
        pointsTransaction.setAmount(POINTS_FOR_REGISTRATION);
        /* 5-系统赠送 */
        pointsTransaction.setType(5);
        /* 新用户注册赠送积分 */
        pointsTransaction.setDescription("新用户注册赠送积分");

        int inserted = pointsTransactionMapper.insert(pointsTransaction);
        if (inserted == 0) {
            log.error("记录积分变动失败");
            return Result.fail("记录积分变动失败");
        }
        log.info("pointsTransactionMapper 表插入 userId{} 成功注册，inviteCode邀请码: {}, " +
                "pointsTransactionMapper 表更新成功", userId, inviteCode);

        /** 2 UserPoints insert */
        UserPoints userPoints = new UserPoints();
        userPoints.setUserId(userId);
        /* 初始积分 POINTS_FOR_REGISTRATION */
        userPoints.setPointsBalance(POINTS_FOR_REGISTRATION);
        userPoints.setPointsRemainAmount(POINTS_FOR_REGISTRATION);

        /* 创建-更新-开始-结束时间*/
        /* 积分有效期1年后结束 */
        userPoints.setEndTime(LocalDateTime.now().plusYears(1));
        userPoints.setActivityEndTime(Activity_End_Time);

        int insert = userpointsMapper.insert(userPoints);

        if (insert == 0) {
            log.error("创建用户积分账户失败");
            return Result.fail("创建用户积分账户失败");
        }
        log.info("userpointsMapper 表插入 userId {} 成功注册，inviteCode邀请码: {}, " +
                "userpointsMapper 表更新成功", userId, inviteCode);

        /** 3-UserReferral update */
        if(userReferral==null) {
            log.error("用户 {} 使用的邀请码 {} 无效", userId, inviteCode);
            return Result.fail("邀请码无效");
        }
        int updated = userReferralMapper.update(null, new LambdaUpdateWrapper<UserReferral>()
                .eq(UserReferral::getInviteCode, inviteCode)
                .set(UserReferral::getUserId, userId)
                .set(UserReferral::getRewardPoints, POINTS_FOR_REFERRAL)
                .set(UserReferral::getEndTime, LocalDateTime.now().plusYears(1))
                .set(UserReferral::getActivityEndTime, Activity_End_Time)
        );

        if (updated == 0) {
            log.error("修改用户信息失败");
            return Result.fail("修改用户信息失败");
        }
        log.info("userReferralMapper 表 插入 userId {} 成功注册，inviteCode 邀请码: {}, " +
                "UserReferral表更新成功", userId, inviteCode);

        // 2. 发送rabbitmq,积分表创建
        String exchange = "career.direct";
        String routingKey = "user.invited.points";
        ReferralDTO newReferralDTO = new ReferralDTO();
        newReferralDTO.setInviteCode(inviteCode);
        newReferralDTO.setUserId(userId); // 这里是对的,审核对了

        rabbitTemplate.convertAndSend(exchange, routingKey, newReferralDTO, new MessagePostProcessor() {
            @Override
            public Message postProcessMessage(Message message) throws AmqpException {
                message.getMessageProperties()
                        .setExpiration("10000");
                return message;
            }
        });

        log.info("消息发送成功！");
        return Result.ok("注册的积分已返回");
//        if (StrUtil.isNotBlank(inviteCode)) {
//            UserReferral userReferral = userReferralMapper.selectOne(
//                    new LambdaQueryWrapper<UserReferral>()
//                            .eq(UserReferral::getInviteCode, inviteCode)
//            );
//            if (userReferral == null) {
//                log.error("用户 {} 还没有注册成功", userId);
//                return Result.fail("用户还没有注册成功");
//            }
//            if (userReferral.getStatus() != 1) {
//                log.error("用户 {} 已经被封了", userId);
//                return Result.fail("用户已经被封了");
//            }
//
//            /** PointsTransaction insert */
//            PointsTransaction pointsTransaction = new PointsTransaction();
//            pointsTransaction.setUserId(userId);
//            /* POINTS_FOR_REGISTRATION-新用户注册获得的积分-赠送积分 */
//            pointsTransaction.setAmount(POINTS_FOR_REGISTRATION);
//            /* 5-系统赠送 */
//            pointsTransaction.setType(5);
//            /* 新用户注册赠送积分 */
//            pointsTransaction.setDescription("新用户注册赠送积分");
//
//            int inserted = pointsTransactionMapper.insert(pointsTransaction);
//            if (inserted == 0) {
//                log.error("记录积分变动失败");
//                return Result.fail("记录积分变动失败");
//            }
//            log.info("userReferralMapper 表插入 {} 成功注册，邀请码: {}, UserReferral表更新成功", userId, inviteCode);
//
//            /** UserPoints insert */
//            UserPoints userPoints = new UserPoints();
//            userPoints.setUserId(userId);
//            /* 初始积分 POINTS_FOR_REGISTRATION */
//            userPoints.setPointsBalance(POINTS_FOR_REGISTRATION);
//            userPoints.setPointsRemainAmount(POINTS_FOR_REGISTRATION);
//
//            /* 创建-更新-开始-结束时间*/
//            /* 积分有效期1年后结束 */
//            userPoints.setEndTime(LocalDateTime.now().plusYears(1));
//            userPoints.setEndActivityTime(Activity_End_Time);
//
//            int insert = userpointsMapper.insert(userPoints);
//
//            if (insert == 0) {
//                log.error("创建用户积分账户失败");
//                return Result.fail("创建用户积分账户失败");
//            }
//            log.info("userReferralMapper 表插入 {} 成功注册，邀请码: {}, UserReferral表更新成功", userId, inviteCode);
//
//            if (StrUtil.isBlank(inviteCode)) {
//                // 没有邀请码，直接返回积分
//                log.info("用户 {} 注册成功，没有邀请码，直接创建积分账户", userId);
//                return Result.ok("注册的积分已返回");
//            }
//
//            /** 1-UserReferral update */
//            int updated = userReferralMapper.update(null, new LambdaUpdateWrapper<UserReferral>()
//                    .eq(UserReferral::getInviteCode, inviteCode)
//                    .set(UserReferral::getUserId, userId)
//                    .set(UserReferral::getRewardPoints, POINTS_FOR_REFERRAL)
//                    .set(UserReferral::getEndTime, LocalDateTime.now().plusYears(1))
//                    .set(UserReferral::getActivityEndTime, Activity_End_Time)
//            );
//
//            if (updated == 0) {
//                log.error("修改用户信息失败");
//                return Result.fail("修改用户信息失败");
//            }
//            log.info("userReferralMapper 表插入 {} 成功注册，邀请码: {}, UserReferral表更新成功", userId, inviteCode);
//
//            // 2. 发送rabbitmq,积分表创建
//            String exchange = "career.direct";
//            String routingKey = "user.invited.points";
//            ReferralDTO newReferralDTO = new ReferralDTO();
//            referralDTO.setInviteCode(inviteCode);
//            referralDTO.setUserId(userId); // 注册没有推荐人，设置为0或null
//
//            rabbitTemplate.convertAndSend(exchange, routingKey, referralDTO, new MessagePostProcessor() {
//                @Override
//                public Message postProcessMessage(Message message) throws AmqpException {
//                    message.getMessageProperties()
//                            .setExpiration("10000");
//                    return message;
//                }
//            });
//
//            log.info("消息发送成功！");
//
//        } else {
//            User selectedOne = userMapper.selectOne(
//                    new LambdaQueryWrapper<User>()
//                            .eq(User::getId, userId)
//            );
//            if (selectedOne == null) {
//                log.error("用户 {} 还没有注册成功", userId);
//                return Result.fail("用户还没有注册成功");
//            }
//            if (selectedOne.getStatus() != 1) {
//                log.error("用户 {} 已经被封了", userId);
//                return Result.fail("用户已经被封了");
//            }
//
//            /** UserPoints insert */
//            UserPoints userPoints = new UserPoints();
//            userPoints.setUserId(userId);
//            /* 初始积分 POINTS_FOR_REGISTRATION */
//            userPoints.setPointsBalance(POINTS_FOR_REGISTRATION);
//            /* 1-正常 */
//            userPoints.setStatus(1);
//            /* 创建-更新-开始-结束时间*/
//            // to do 活动时间
//            userPoints.setCreateTime(Activity_Start_Time);
//            userPoints.setUpdateTime(Activity_End_Time);
//
//            userPoints.setStartTime(LocalDateTime.now());
//            /* 1年后结束 */
//            userPoints.setEndTime(LocalDateTime.now().plusYears(1));
//            int insert = userpointsMapper.insert(userPoints);
//
//            if (insert == 0) {
//                log.error("创建用户积分账户失败");
//                return Result.fail("创建用户积分账户失败");
//            }
//            log.info("userReferralMapper 表插入 {} 成功注册，邀请码: {}, UserReferral表更新成功", userId, inviteCode);
//
//            /** PointsTransaction insert */
//            PointsTransaction pointsTransaction = new PointsTransaction();
//            pointsTransaction.setUserId(userId);
//            /* POINTS_FOR_REGISTRATION-新用户注册获得的积分-赠送积分 */
//            pointsTransaction.setAmount(POINTS_FOR_REGISTRATION);
//            /* 5-系统赠送 */
//            pointsTransaction.setType(5);
//            /* 新用户注册赠送积分 */
//            pointsTransaction.setDescription("新用户注册赠送积分");
//            int inserted = pointsTransactionMapper.insert(pointsTransaction);
//
//            if (inserted == 0) {
//                log.error("记录积分变动失败");
//                return Result.fail("记录积分变动失败");
//            }
//            log.info("userReferralMapper 表插入 {} 成功注册，邀请码: {}, UserReferral表更新成功", userId, inviteCode);
//
//            if (StrUtil.isBlank(inviteCode)) {
//                log.info("用户 {} 注册成功，没有邀请码，直接创建积分账户", userId);
//                return Result.ok("注册的积分已返回");
//            }
//
//        }
    }

    /**
     * invite 生成邀请码
     * 邀请好友接口
     * @param referralDTO
     * @return
     * 1. 获取当前用户ID
     * 2. 生成一个新的邀请码，并保存到UserReferral表中
     * 3. 返回邀请码
     */
    @Override
    public Result<ReferralDTO> generateInvite(@RequestBody ReferralDTO referralDTO) {
        Long currentUserId = ThreadLocalUtil.getCurrentUserId();

        long nextId = redisIdWorker.nextId(INVITE_CODE_KEY_PREFIX);

        ReferralDTO data = new ReferralDTO();
        data.setInviteCode(String.valueOf(nextId));
        
        // referral 表示邀请大使
        data.setReferrerId(currentUserId);
        return Result.ok(data);
    }

    @Override
    public Result receiverPoints(ReferralDTO referralDTO) {
        Long userId = referralDTO.getUserId();
        String inviteCode = referralDTO.getInviteCode();

        /** UserReferral update */
        int updatedReferral = userReferralMapper.update(null, new LambdaUpdateWrapper<UserReferral>()
                .eq(UserReferral::getInviteCode, inviteCode)
                .set(UserReferral::getUserId, userId)
                .set(UserReferral::getRewardPoints, POINTS_FOR_REFERRAL)
                .set(UserReferral::getEndTime, LocalDateTime.now().plusYears(1))
                .set(UserReferral::getActivityEndTime, Activity_End_Time)
        );
        if(updatedReferral == 0) {
            log.error("更新用户推荐信息失败");
            return Result.fail("更新用户推荐信息失败");
        }
        return Result.ok("邀请好友注册赠送积分已到账");
    }

    /** todo 这里是给学生用户留着的 */
    @Override
    public Result<Object> registerStudent(@RequestBody StudentTrueDTO studentTrueDTO) {
        Map<String, Object> params =new HashMap<>();
        params.put("name", studentTrueDTO.getName());
        params.put("schoolName", studentTrueDTO.getSchoolName());
        params.put("major", studentTrueDTO.getMajor());
        params.put("grade",studentTrueDTO.getGrade());
        params.put("entranceTime", studentTrueDTO.getEntranceTime());
        params.put("graduatedTime", studentTrueDTO.getGraduatedTime());
        AiChatResponse aiChatResponse = aiServiceClient.chatWithOtherJson("/points/student/register", params,true);
        return Result.ok(aiChatResponse);
    }

    /**
     * 充值积分接口
     * @return
     * 1. 获取当前用户ID
     * 2. 根据用户ID查询UserPoints表，获取当前积分账户信息
     * 3. 如果用户积分账户不存在，返回错误提示
     * 4. 根据传入的积分变动值，计算新的积分余额，并更新UserPoints表中的积分余额和更新时间
     * 5. 在PointsTransaction表中记录这笔积分变动，类型为充值，描述为充值积分
     * 6. 返回充值成功的积分信息
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<UserPoints> recharge(@RequestBody @Valid PointsMembershipChangeDTO pointsMembershipChangeDTO, HttpServletResponse response) {
        
        UserPoints account = userpointsMapper.selectOne(
                new LambdaQueryWrapper<UserPoints>()
                        .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
        );
        
        if(account == null) {
            return Result.fail("用户积分信息不存在,可能是有人发起攻击来了,或者系统故障");
        }

        Integer amount = pointsMembershipChangeDTO.getAmount();
        int newAmount = account.getPointsBalance() + amount;
        account.setPointsBalance(newAmount);

        int updated = userpointsMapper.update(null, new LambdaUpdateWrapper<UserPoints>()
                .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
                .set(UserPoints::getPointsBalance, newAmount)
        );
        if(updated == 0) {
            return Result.fail("更新用户积分信息失败");
        }

        PointsTransaction paymentOrder = BeanUtil.copyProperties(pointsMembershipChangeDTO, PointsTransaction.class);
        paymentOrder.setAmount(newAmount);
        paymentOrder.setType(1);
        
//        redisIdWorker.nextId(POINTS_RECHARGE_KEY_PREFIX);
        paymentOrder.setDescription("充值积分");
        
        int insert = pointsTransactionMapper.insert(paymentOrder);
        if (insert == 0) {
            return Result.fail("记录积分变动失败");
        }

        try {
            payService.pagePay(paymentOrder.getId(), response);
        } catch (AlipayApiException e) {
            log.info("支付宝支付失败{}", e.getMessage());
            throw new RuntimeException(e);
        } catch (IOException e) {
            log.info("支付宝支付失败{}", e.getMessage());
            throw new RuntimeException(e);
        }

        // todo 支付宝
        return Result.ok(account);
    }

    /**
     * consumePoints 消耗积分接口
     * @return
     * 1. 获取当前用户ID
     * 2. 根据用户ID查询UserPoints表，获取当前积分账户信息
     * 3. 如果用户积分账户不存在，返回错误提示
     * 4. 根据传入的积分变动值，计算新的积分余额，并更新UserPoints表中的积分余额和更新时间
     * 5. 在PointsTransaction表中记录这笔积分变动，类型为消费，描述为消费积分
     * 6. 返回消费成功的积分信息
     */
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result consumePoints(PointsMembershipChangeDTO pointsMembershipChangeDTO) {

        UserPoints account = userpointsMapper.selectOne(
                new LambdaQueryWrapper<UserPoints>()
                        .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
        );

        if(account == null) {
            return Result.fail("用户积分信息不存在,可能是有人发起攻击来了,或者系统故障");
        }

        Integer amount = pointsMembershipChangeDTO.getAmount();
        int newAmount = account.getPointsBalance() - amount;
        account.setPointsBalance(newAmount);

        int updated = userpointsMapper.update(null, new LambdaUpdateWrapper<UserPoints>()
                .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
                .set(UserPoints::getPointsBalance, newAmount)
        );
        if(updated == 0) {
            return Result.fail("更新用户积分信息失败");
        }

        PointsTransaction entity = BeanUtil.copyProperties(pointsMembershipChangeDTO, PointsTransaction.class);
        entity.setAmount(newAmount);
        entity.setType(1);
        
        redisIdWorker.nextId(POINTS_CONSUME_KEY_PREFIX);
        entity.setDescription("消费积分积分");
        int insert = pointsTransactionMapper.insert(entity);
        
        if (insert == 0) {
            return Result.fail("记录积分变动失败");
        }

        return Result.ok(account);
    }

    @Override
    public Result<String> giveInviteVIPGiftPoints(ReferralDTO dto) {
        int updated = pointsTransactionMapper.update(null, new LambdaUpdateWrapper<PointsTransaction>()
                .eq(PointsTransaction::getUserId, dto.getUserId())
                .eq(PointsTransaction::getType, 4)
                .set(PointsTransaction::getAmount, POINTS_FOR_REFERRAL)
                .set(PointsTransaction::getDescription, "邀请好友注册赠送积分")
        );
        if(updated == 0) {
            log.error("更新用户推荐信息失败");
            return Result.fail("更新用户推荐信息失败");
        }
        return Result.ok("giveInviteVIPGiftPoints  邀请好友注册赠送积分已到账");
    }

    /**
     * deletePoints 删除积分接口
     * @param dto
     * @return
     * 1. 获取当前用户ID
     * 2. 根据用户ID查询UserPoints表，获取当前积分账户信息
     * 3. 如果用户积分账户不存在，返回错误提示
     * 4. 根据传入的积分变动值，计算新的积分余额，并更新UserPoints表中的积分余额和更新时间
     * 5. 在PointsTransaction表中记录这笔积分变动，类型为删除，描述为删除积分
     * 6. 返回删除成功的积分信息
     */
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Object> deletePoints(PointsMembershipChangeDTO dto) {

        UserPoints account = userpointsMapper.selectOne(
                new LambdaQueryWrapper<UserPoints>()
                        .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
        );

        if(account == null) {
            return Result.fail("用户积分信息不存在,可能是有人发起攻击来了,或者系统故障");
        }

        Integer amount = dto.getAmount();
        int newAmount = account.getPointsBalance() - amount;
        account.setPointsBalance(newAmount);

        int updated = userpointsMapper.update(null, new LambdaUpdateWrapper<UserPoints>()
                .eq(UserPoints::getUserId, ThreadLocalUtil.getCurrentUserId())
                .set(UserPoints::getPointsBalance, newAmount)
                .set(UserPoints::getUpdateTime, LocalDateTime.now())
                .set(UserPoints::getStatus, 0)
        );
        
        if(updated == 0) {
            return Result.fail("删除用户积分信息失败");
        }

        return null;
    }
}
