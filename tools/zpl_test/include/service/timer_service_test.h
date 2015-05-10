#ifndef TIMER_SERVICE_H_INCLUDED
#define TIMER_SERVICE_H_INCLUDED

#include <service/timer_service.h>

#define       timerSession  1
#define       loopTimerSession  2
#define       clearSession 3
#define        timerOut  2
#define        loopTimerOut  4
#define        clearOut 3

class TimerServiceTest{

    public:
        TimerServiceTest(const int &num);
        void handler(zhicloud::service::TimerService::event_list_type list);
        void handler1(zhicloud::service::TimerService::event_list_type list);
        ~TimerServiceTest();
        bool test();
    private:
        zhicloud::service::TimerService timerService;
        int timerCount;
        int loopTimerCount;
        int clearCount;
        int timerCount1;
        int loopTimerCount1;
        int clearCount1;
        int num;
};

#endif // TIMER_SERVICE_H_INCLUDED
