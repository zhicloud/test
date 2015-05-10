#include <iostream>
#include <functional>
#include <boost/log/trivial.hpp>
#include <unistd.h>
#include "service/timer_service_test.h"


TimerServiceTest::TimerServiceTest(const int &num):timerCount(0), loopTimerCount(0),clearCount(0),timerCount1(0),loopTimerCount1(0),clearCount1(0),num(num) {
    timerService.bindHandler(std::bind(&TimerServiceTest::handler, this, std::placeholders::_1));
    timerService.bindHandler(std::bind(&TimerServiceTest::handler1, this, std::placeholders::_1));
    timerService.setTimer(timerOut, timerSession);
    timerService.setTimer(clearOut,  clearSession);
    timerService.setLoopTimer(loopTimerOut, loopTimerSession);
    timerService.start();
}
void TimerServiceTest::handler(zhicloud::service::TimerService::event_list_type list) {
    for(const zhicloud::transport::AppMessage &msg:list) {
        if(msg.session == timerSession) {
            timerCount++;
        } else if(msg.session == loopTimerSession) {
            loopTimerCount++;
        } else if(msg.session == clearSession) {
            clearCount++;
        }
        //BOOST_LOG_TRIVIAL(info) << "+++++++++++ " << msg.session;
    }
    //BOOST_LOG_TRIVIAL(info)<< "list size " << list.size() << " back element " << list.back().getInt(zhicloud::util::ParamEnum::domain) << std::endl;
}
void TimerServiceTest::handler1(zhicloud::service::TimerService::event_list_type list) {
    for(const zhicloud::transport::AppMessage &msg:list) {
        if(msg.session == timerSession) {
            timerCount1++;
        } else if(msg.session == loopTimerSession) {
            loopTimerCount1++;
        } else if(msg.session == clearSession) {
            clearCount1++;
        }
        //BOOST_LOG_TRIVIAL(info) << "--------------------- " << msg.session;
    }
    //BOOST_LOG_TRIVIAL(info) << "list1 size " << list.size() << " back element " << list.back().getInt(zhicloud::util::ParamEnum::domain);
}
TimerServiceTest::~TimerServiceTest() {
    timerService.stop();
}
bool TimerServiceTest::test() {
    zhicloud::transport::AppMessage timerMessage;
    zhicloud::transport::AppMessage loopTimerMessage;

    timerMessage.setInt(zhicloud::util::ParamEnum::domain, 0);
    loopTimerMessage.setInt(zhicloud::util::ParamEnum::domain, 1);

    timerService.setTimedEvent(timerMessage, timerOut);
    timerService.setTimedEvent(timerMessage, timerOut);
    timerService.setTimedEvent(timerMessage, timerOut);
    zhicloud::service::TimerService::timer_id_type timer_id = timerService.setTimedEvent(timerMessage, clearOut);
    timerService.clearTimer(timer_id);
    timerService.setLoopTimedEvent(loopTimerMessage, loopTimerOut);
    sleep(num *2);
    timerService.stop();
    //BOOST_LOG_TRIVIAL(info) << timerCount << "---------------" << loopTimerCount;

    return timerCount ==3 && loopTimerCount == num / loopTimerOut - 1 && clearCount == 0;
}


