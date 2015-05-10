#ifndef BASE_SESSION_H
#define BASE_SESSION_H
#include <string>
#include <list>
#include <transport/app_message.h>
#include <boost/thread/lock_types.hpp>
#include <boost/thread/recursive_mutex.hpp>

using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transaction{
        template < typename T >
        class BaseSession
        {
        	private:
            protected:
                typedef boost::recursive_mutex::scoped_lock lock_type;

            public:
                typedef uint32_t session_id_type;
                typedef uint32_t state_type;
                typedef T task_id_type;
                typedef int32_t timer_id_type;

                BaseSession(const session_id_type& id):session_id(id){
                    reset();
                }
                BaseSession():BaseSession(0){
                }
                virtual ~BaseSession(){
                }
                void reset(){
                    task_id = T::invalid;
                    initialed = false;
                    current_state = (state_type)StateEnum::initial;
                    request_module.clear();
                    request_session = 0;
                    timer_id = 0;
                    blocked = false;
                    state_specified = false;
                    message_queue.clear();
                    onReset();
                }
                bool occupy(const T& task){
                    lock_type lock(mutex);
                    task_id = task;
                    return true;
                }
                bool isInitialed(){
                    lock_type lock(mutex);
                    return initialed;
                }
                void initial(const AppMessage& msg){
                    lock_type lock(mutex);
                    initial_message = msg;
                    current_state = (state_type)StateEnum::initial;
                    request_module = msg.sender;
                    request_session = msg.session;
                    initialed = true;
                }
                constexpr static state_type getInitialState(){
                	return (state_type)StateEnum::initial;
                }
                constexpr static state_type getFinishState(){
                    return (state_type)StateEnum::finish;
                }
                bool isFinished(){
                    lock_type lock(mutex);
                    return ((state_type)StateEnum::finish == current_state);
                }
                void finish(){
                    lock_type lock(mutex);
                    current_state = (state_type)StateEnum::finish;
                }
                void setState(const state_type& next_state){
                    lock_type lock(mutex);
                    if(current_state != (state_type)StateEnum::initial)
                    {
                        state_specified = true;
                    }
                    current_state = next_state;
                }
                void putMessage(AppMessage& msg){
                    lock_type lock(mutex);
                    message_queue.push_back(std::move(msg));
                }
                void insertMessage(AppMessage& msg){
                    lock_type lock(mutex);
                    message_queue.push_front(std::move(msg));
                }
                bool fetchMessage(list< AppMessage >& message_list){
                    lock_type lock(mutex);
                    if(message_queue.empty()){
                        return false;
                    }
                    message_list = std::move(message_queue);
                    message_queue.clear();
                    return true;
                }

                AppMessage& getInitialMessage(){
                    lock_type lock(mutex);
                    return initial_message;
                }

                state_type getCurrentState() const{
                    lock_type lock(mutex);
                    return current_state;
                }
                void next(const state_type& state){
                    lock_type lock(mutex);
                    if((state_type)StateEnum::finish != current_state){
                        if(state_specified)
                            state_specified = false;
                        else
                            current_state = state;
                    }
                }
                void setTimerID(const timer_id_type& id){
                    lock_type lock(mutex);
                    timer_id = id;
                }
                timer_id_type getTimerID() const{
                    lock_type lock(mutex);
                    return timer_id;
                }
                task_id_type getTaskID() const{
                    lock_type lock(mutex);
                    return task_id;
                }
                const session_id_type& getSessionID() const{
                    lock_type lock(mutex);
                    return session_id;
                }
                const string& getRequestModule() const{
                    lock_type lock(mutex);
                    return request_module;
                }
                const session_id_type& getRequestSession() const{
                    lock_type lock(mutex);
                    return request_session;
                }

                BaseSession(BaseSession&& other){
                    session_id = std::move(other.session_id);
                    task_id = std::move(other.task_id);
                    initialed = std::move(other.initialed);
                    current_state = std::move(other.current_state);
                    initial_message = std::move(other.initial_message);
                    request_module = std::move(other.request_module);
                    request_session = std::move(other.request_session);
                    timer_id = std::move(other.timer_id);
                    blocked = std::move(other.blocked);
                    state_specified = std::move(other.state_specified);
                    message_queue = std::move(other.message_queue);
                }
                BaseSession& operator=(BaseSession&& other){
                    session_id = std::move(other.session_id);
                    task_id = std::move(other.task_id);
                    initialed = std::move(other.initialed);
                    current_state = std::move(other.current_state);
                    initial_message = std::move(other.initial_message);
                    request_module = std::move(other.request_module);
                    request_session = std::move(other.request_session);
                    timer_id = std::move(other.timer_id);
                    blocked = std::move(other.blocked);
                    state_specified = std::move(other.state_specified);
                    message_queue = std::move(other.message_queue);
                    return *this;
                }
            protected:
                virtual void onReset(){
                    //reset member here
                }
                session_id_type session_id;
                T task_id;
                bool initialed;
                state_type current_state;
                AppMessage initial_message;
                string request_module;
                session_id_type request_session;
                timer_id_type timer_id;
                bool blocked;
                bool state_specified;
                mutable boost::recursive_mutex mutex;
                list< AppMessage > message_queue;
            private:
        		enum class StateEnum:state_type{
        			initial = 0,
        			finish = 0xFFFF,
        		};
        };
    }
}



#endif // BASE_SESSION_H
