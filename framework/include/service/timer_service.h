#ifndef TIMERSERVICE_H
#define TIMERSERVICE_H
#include <map>
#include <transport/app_message.h>
#include <service/timed_invoker.h>
#include <boost/thread/recursive_mutex.hpp>

namespace zhicloud{
    namespace service{
        using zhicloud::transport::AppMessage;
        using std::map;
        class TimerService
        {
            public:
                typedef int32_t timer_id_type;
                typedef uint32_t timeout_type;
                typedef uint32_t session_id_type;
                typedef list< AppMessage > event_list_type;
                typedef boost::signals2::signal< void (event_list_type&) > event_type;
                typedef event_type::slot_type event_handler;

                TimerService(const uint32_t& interval = 1);
                virtual ~TimerService();
                void bindHandler(const event_handler& handler);
                bool start();
                void stop();
                timer_id_type setTimer(const timeout_type& timeout, const session_id_type& session);
                timer_id_type setLoopTimer(const timeout_type& timeout, const session_id_type& session);
                timer_id_type setTimedEvent(const AppMessage& event, const timeout_type& timeout);
                timer_id_type setLoopTimedEvent(const AppMessage& event, const timeout_type& timeout);
                bool clearTimer(const timer_id_type& timer_id);

            private:
                event_type onTimeoutInvoked;
                void onCheckTimeout();

                typedef boost::recursive_mutex::scoped_lock lock_type;
                 struct TimerCounter{
                    timer_id_type timer_id;
                    session_id_type receive_session;
                    timeout_type timeout;
                    timeout_type count_down;
                    bool is_loop;
                    bool event_specified;
                    AppMessage event;
                    TimerCounter();
                    TimerCounter(TimerCounter&& other);
                };
                typedef map< timer_id_type, TimerCounter > map_type;

                static const timer_id_type max_timer = 1000;
                boost::recursive_mutex mutex;
                TimedInvoker invoker;
                timer_id_type seed;
                map_type timer_map;
        };
    }
}



#endif // TIMERSERVICE_H
