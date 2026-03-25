package com.backend.careerplanningbackend.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.ExchangeTypes;
import org.springframework.amqp.rabbit.annotation.Exchange;
import org.springframework.amqp.rabbit.annotation.Queue;
import org.springframework.amqp.rabbit.annotation.QueueBinding;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class TestConnection {

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "direct.career1", durable = "true"),
            exchange = @Exchange(name = "career1.direct", type = ExchangeTypes.DIRECT),
            key = {"red", "blue"}
    ))
    public void listenDirectQueue1(String msg) throws InterruptedException {
        System.out.println("消费者1 收到了 direct.queue1的消息：【" + msg +"】");
    }

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "direct.career2", durable = "true"),
            exchange = @Exchange(name = "career2.direct", type = ExchangeTypes.DIRECT),
            key = {"red", "yellow"}
    ))
    public void listenDirectQueue2(String msg) throws InterruptedException {
        System.out.println("消费者2 收到了 direct.queue2的消息：【" + msg +"】");
    }

    
}
