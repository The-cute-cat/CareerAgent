package com.backend.careerplanningbackend.service.impl;

import org.springframework.mail.javamail.JavaMailSender;
import cn.hutool.core.util.StrUtil;
import cn.hutool.extra.mail.MailException;
import com.backend.careerplanningbackend.domain.dto.LoginFormDTO;
import com.backend.careerplanningbackend.domain.dto.UserDTO;
import com.backend.careerplanningbackend.domain.po.Result;
import com.backend.careerplanningbackend.domain.po.User;
import com.backend.careerplanningbackend.domain.vo.LoginVO;
import com.backend.careerplanningbackend.mapper.UserMapper;
import com.backend.careerplanningbackend.service.UserService;
import com.backend.careerplanningbackend.util.*;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import io.jsonwebtoken.Claims;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import static com.backend.careerplanningbackend.util.RedisConstant.EXPIRE_TIME;
import static com.backend.careerplanningbackend.util.RedisConstant.SENT_TIME;

@Slf4j
@Service     
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    //导入application.yml里面的发件人邮箱
    @Value("${spring.mail.username}")
    private String fromEmail;
    @Autowired
    JavaMailSender sender;
    @Autowired
    private UserMapper userMapper;
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    @Autowired
    private AliOSSUtils aliOSSUtils;

    @Override
    public Result login(LoginFormDTO user) {
        String password = user.getPassword();
        String username = user.getUsername();
        if(StrUtil.isBlank(password)||StrUtil.isBlank(username)){
            return Result.fail("账号或密码不能为空");
        }
        if(RegexUtil.isPasswordInvalid(password)){
            return Result.fail("密码格式无效,4~32位有效数字");
        }
        if(RegexUtil.isUsernameInvalid(username)){
            return Result.fail("用户名格式无效,24位有效数字");
        }
        log.debug("用户登录请求: {}", user);
        
        User userByName = userMapper.selectByUsername(username);
        
        // 账号不存在或密码错误，返回相同的错误提示（防止账号枚举攻击）
        if (userByName == null || !PwdUtil.match(password, userByName.getPassword())) {
            log.warn("登录失败: 账号或密码错误 - {}", username);
            return Result.fail("账号或密码错误");
        }
        // 检查账号状态
        if (userByName.getStatus() == 0) {
            log.warn("登录失败: 账号被禁用 - {}", username);
            return Result.fail("账号已被禁用");
        }
        
        // 生成 Token
        String accessToken = JwtUtil.createToken(String.valueOf(userByName.getId()));
        String refreshToken = JwtUtil.createRefreshToken(String.valueOf(userByName.getId()));
        
        log.info("用户登录成功: {}, userId: {}", username, userByName.getId());
        LoginVO loginVO = new LoginVO(accessToken, refreshToken);
        return Result.ok(loginVO);
    }
    
    @Override
    public Result register(LoginFormDTO user) {
        log.debug("用户注册请求: {}", user);
        String password = user.getPassword();
        String username = user.getUsername();
        String email = user.getEmail();
        if(StrUtil.isBlank(password)||StrUtil.isBlank(username)){
            return Result.fail("账号或密码不能为空");
        }
        if (!password.equals(user.getPasswordConfirm())) {
            return Result.fail("两次输入的密码不一致");
        }
        if(RegexUtil.isPasswordInvalid(password)){
            return Result.fail("密码格式无效,4~32位有效数字");
        }
        if(RegexUtil.isUsernameInvalid(username)){
            return Result.fail("用户名格式无效,24位有效数字");
        }
        if (RegexUtil.isEmailInvalid(email)) {
            return Result.fail("邮箱格式无效");
        }
        User ByEmail = userMapper.selectByEmail(email);
        if(ByEmail!=null){
            return Result.fail("邮箱已经存在");
        }
        User userByName = userMapper.selectByUsername(user.getUsername());
        if(userByName!=null){
            return Result.fail("用户名已被占用");
        }

        // 2. 校验验证码 (直接调用本类重构后的方法)
        String codeKey = RedisConstant.EMAIL_CODE + ":" + username + ":" + email;
        String sentKey = RedisConstant.EMAIL_SENT + ":" + username + ":" + email;
        String cachedCode = stringRedisTemplate.opsForValue().get(codeKey);

        // 2. 校验是否存在（5分钟有效性）
        if (StrUtil.isBlank(cachedCode)) {
            return Result.fail("验证码已过期或未发送");
        }
        // 3. 校验正确性
        if (!cachedCode.equals(user.getCode())) {
            return Result.fail("验证码错误");
        }
       
        //加密
        String encode = PwdUtil.encode(password);
        user.setPassword(encode);

        //注册功能点实现
        int rows = userMapper.register(user);
        if (rows == 0) {
            return Result.fail("服务器开小差了，注册失败");
        }
        // 4. 验证成功后立即删除，防止同一验证码被二次使用（幂等性）
        stringRedisTemplate.delete(codeKey);
        stringRedisTemplate.delete(sentKey);
        return Result.ok();
    }

    @Override
    public Result forget(LoginFormDTO user) {
        log.debug("用户修改密码请求: {}", user);
        String username = user.getUsername();
        String password = user.getPassword();
        String email = user.getEmail();
        if (StrUtil.hasBlank(user.getUsername(), user.getEmail(), user.getPassword())) {
            return Result.fail("用户名、邮箱或密码不能为空");
        }
        if (!password.equals(user.getPasswordConfirm())) {
            return Result.fail("两次输入的密码不一致");
        }
        if (RegexUtil.isEmailInvalid(email)) {
            return Result.fail("邮箱格式无效");
        }
        User ByEmail = userMapper.selectByEmail(email);
        User userByName = userMapper.selectByUsername(user.getUsername());
        if (userByName == null||ByEmail==null||!userByName.getEmail().equals(email)) {
            return Result.fail("用户名或邮箱信息不匹配");
        }

        // 2. 校验验证码 (直接调用本类重构后的方法)
        String codeKey = RedisConstant.EMAIL_CODE + ":" + username + ":" + email;
        String sentKey = RedisConstant.EMAIL_SENT + ":" + username + ":" + email;
        String cachedCode = stringRedisTemplate.opsForValue().get(codeKey);

        // 2. 校验是否存在（5分钟有效性）
        if (StrUtil.isBlank(cachedCode)) {
            return Result.fail("验证码已过期或未发送");
        }
        // 3. 校验正确性
        if (!cachedCode.equals(user.getCode())) {
            return Result.fail("验证码错误");
        }
        //加密
        String encode = PwdUtil.encode(password);
        user.setPassword(encode);

        //忘记密码的功能实现
        int login = userMapper.forget(user);
        if (login == 0) {
            return Result.fail("重置失败，请稍后再试");
        }
        // 4. 验证成功后立即删除，防止同一验证码被二次使用（幂等性）
        stringRedisTemplate.delete(codeKey);
        stringRedisTemplate.delete(sentKey);
        
        return Result.ok();
    }

    /**
     * 发送验证码 （带防刷）
     * @param  user*(LoginFormDTO)
     * @return
     */
    @Override
    public Result sendCode(LoginFormDTO user) {
        String username = user.getUsername();
        String toEmail = user.getEmail();
        // 判断参数不合法
        if(StrUtil.isEmpty(username)){
            return Result.fail("用户名无效");
        }
        if (RegexUtil.isEmailInvalid(toEmail)) {
            return Result.fail("邮箱格式无效");
        }
        // 2. 防刷校验：使用 ":" 分隔符规范 Key 结构
        // 建议格式：项目名:模块:业务:标识 这个用来计算60秒内是否重置 
        String sentKey = RedisConstant.EMAIL_SENT + ":" + username + ":" + toEmail;
        if(Boolean.TRUE.equals(stringRedisTemplate.hasKey(sentKey))){
            return Result.fail("60秒之内已经发送了一条验证码");
        }
        try {
            String code= VerificationCode.generateVerificationCode();
            log.info("code:{}",code);
            System.out.println(code);
            //存入验证码到 redis 里面
            String codeKey= RedisConstant.EMAIL_CODE + ":" + username + ":" + toEmail;

            stringRedisTemplate.opsForValue().set(codeKey,code,EXPIRE_TIME, TimeUnit.SECONDS);
            //存入 防刷标记 到 redis 里面
            stringRedisTemplate.opsForValue().set(sentKey,"1",SENT_TIME,TimeUnit.SECONDS);

            //发送邮件验证码
            SimpleMailMessage msg = new SimpleMailMessage();
            msg.setFrom(fromEmail);
            msg.setTo(toEmail);
            msg.setSubject("AI 职业规划助手，助你开启未来之门！");
            msg.setText("您的验证码是：" + code + "，5分钟内有效，请勿泄露");
            sender.send(msg);
            return Result.ok();
        } catch (MailException e) {
            e.printStackTrace();
            return Result.fail("重置密码错误");
        }
    }

    /***
     * 修改用户的资料
     * @param user
     * @return
     */
    @Override
    public Result edit(User user) {
        if(user==null){
            return Result.fail("前端传输过来的是空的东西或者邮箱为空");
        }
        System.out.println("userinfo===="+user);
        String username = user.getUsername();
        String email = user.getEmail();
        String nickname = user.getNickname();
        if(StrUtil.isBlank(username)||StrUtil.isBlank(email)||StrUtil.isBlank(nickname)){
            return Result.fail("用户有一个值是空的东西");
        }
        User byUsername = userMapper.selectByUsername(username);
        if(byUsername!=null && !byUsername.getId().equals(user.getId())){
            return Result.fail("用户名已经存在");
        }
        User byEmail = userMapper.selectByEmail(email);
        if(byEmail!=null && !byEmail.getId().equals(user.getId())){
            return Result.fail("邮箱已经存在");
        }
        int rows = userMapper.edit(user);
        if(rows==0) {
            return Result.fail("userService.edit数据库更新失败");
        }
        log.info("用户ID: {} 的信息更新成功", user.getId());
        return Result.ok();
    }

    /**
     * 刷新短token
     * @param accessToken
     * @param response
     * @return
     */
    @Override
    public Result refreshToken(String refreshToken, HttpServletResponse response) {
        log.info("refreshToken={}",refreshToken);
        Claims claims = null;
        try {
            claims = JwtUtil.parseToken(refreshToken);
            System.out.println(claims);
        } catch (Exception e) {
            System.out.println(claims);
            System.out.println("长token过期了,token expired");
            return Result.fail(401,"长token过期了,token expired");
        }
        log.info("登录的账号为 : {}", claims.getId());
        Long id = Long.valueOf(claims.getSubject());
        System.out.println(id);
        User user = userMapper.getUserOneInfo(id);
        if(user==null){
            return Result.fail(401,"用户不存在,你竟然测试我");
        }
        //更新双 token 回去
        String AccessToken = JwtUtil.createToken(String.valueOf(id));
        String RefreshToken = JwtUtil.createRefreshToken(String.valueOf(id));
//        response.setHeader("AccessToken", AccessToken);
//        response.setHeader("RefreshToken",RefreshToken);
        log.info("AccessToken: {},RefreshToken: {}", AccessToken, RefreshToken);

        LoginVO loginVO = new LoginVO(AccessToken, RefreshToken);
        return Result.ok(loginVO);
    }

    /**
     * 获取用户的资料（只能自己获取）
     * @return
     */
    @Override
    public Result getUserInfo() {
        Long currentUserId = ThreadLocalUtil.getCurrentUserId();
        if(currentUserId == 0) {
            return Result.fail("id为空");
        }
        UserDTO user = userMapper.getUserInfo(currentUserId);
        if(user==null){
            return Result.fail("未查到id为"+currentUserId+"用户");
        }
        return Result.ok(user);
    }

    @Override
    public Result updateAvatar(MultipartFile avatar) throws IOException {
        Long currentUserId = ThreadLocalUtil.getCurrentUserId();
        String upload = aliOSSUtils.upload(avatar);
        int i = userMapper.updateAvatar(upload,currentUserId);
        if(i==0){
            throw new RuntimeException("未更新成功");
        }
        log.info("用户头像url {}",upload);
        return Result.ok(upload);
    }
    
}
