package com.backend.careerplanningbackend.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.rabbit.retry.MessageRecoverer;
import org.springframework.amqp.rabbit.retry.RepublishMessageRecoverer;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 错误处理配置类，用于配置 RabbitMQ 消息重试和错误处理机制。
 * 当消息处理失败时，消息将被重新发布到指定的错误交换机和队列中，以便后续分析和处理。
 * 通过 @ConditionalOnProperty 注解，只有当 spring.rabbitmq.listener.simple.retry.enabled 属性设置为 true 时，才会加载此配置。
 * 主要功能：
 * 1. 定义错误交换机（error.direct）
 * 2. 定义错误队列（error.queue）
 * 3. 将错误队列绑定到错误交换机
 * 4. 配置消息恢复器，当消息处理失败时，将消息重新发布到
 */
@Slf4j
@ConditionalOnProperty(name = "spring.rabbitmq.listener.simple.retry.enabled", havingValue = "true")
@Configuration
public class ErrorConfiguration {

    @Bean
    public DirectExchange errorExchange(){
        return new DirectExchange("error.direct");
    }

    @Bean
    public Queue errorQueue(){
        return new Queue("error.queue");
    }

    @Bean
    public Binding errorBinding(Queue errorQueue, DirectExchange errorExchange){
        return BindingBuilder.bind(errorQueue).to(errorExchange).with("error");
    }

    //将失败处理策略改为RepublishMessageRecoverer:
    //①首先，定义接收失败消息的交换机、队列及其绑定关系，此处：
    //②然后，定义RepublishMessageRecoverer:
    @Bean
    public MessageRecoverer messageRecoverer(RabbitTemplate rabbitTemplate){
        log.debug("加载RepublishMessageRecoverer");
        return new RepublishMessageRecoverer(rabbitTemplate, "error.direct", "error");
    }
}
