#ifndef BASE_MANAGER_HPP_INCLUDED
#define BASE_MANAGER_HPP_INCLUDED

#include <vector>
#include <list>
#include <map>
#include <memory>
#include <exception>
#include <thread>
#include <mutex>
#include <atomic>
#include <service/runable.hpp>
#include <service/active_queue.hpp>
#include <util/copyable_atomic.hpp>
#include <util/logging.h>
#include <transport/app_message.h>
#include <boost/bind.hpp>

using zhicloud::transport::AppMessage;
using namespace zhicloud::util;
using zhicloud::service::ActiveQueue;

namespace zhicloud{
    namespace transaction{

        template < class T >
        class BaseManager: public zhicloud::service::Runable
        {
        public:
            typedef typename T::session_type::session_id_type session_id_type;
            typedef typename T::session_type session_type;
            typedef typename T::task_id_type task_id_type;
            typedef T task_type;
            BaseManager(const session_id_type& session_count, const uint32_t& queue_count):
                _session_count(session_count), _last_seed(0),
                _min_session(1), _max_session(session_count + _min_session - 1),
                _queue_count(queue_count)
            {
                logger = getLogger("BaseManager");
                for(session_id_type seed = 0; seed < _session_count; seed++){
                    session_id_type session_id = seed + _min_session;
                    _allocate_map.emplace(session_id, atomic< bool > (false));
                    _session_map.emplace(session_id, session_type(session_id));
                }
                logger->info(boost::format("<TaskManager>%d transaction session created")
                             %_session_count);
                for(uint32_t i = 0; i < _queue_count; i++){
                    _queue_vector.emplace_back(ActiveQueue< session_id_type, queue_size >() );
                }
                for(auto& active_queue:_queue_vector){
                    active_queue.bindHandler(boost::bind(&BaseManager< T >::onSessionInvoked, this, _1, _2, _3));
                }
                logger->info(boost::format("<TaskManager>%d work queue(s) ready")
                             %_queue_count);
            }
            virtual ~BaseManager(){
                _task_map.clear();
            }
            bool addTask(task_type* p_task){
                const task_id_type& task_id = p_task->getTaskID();
                if(_task_map.end() != _task_map.find(task_id)){
                    logger->warn(boost::format("<TaskManager>add task fail, task %d already exists")
                                 %(uint32_t)task_id);
                    return false;
                }
                _task_map[task_id] = std::unique_ptr< task_type > (p_task);
                logger->info(boost::format("<TaskManager>add task success, task id %d")
                             %(uint32_t)task_id);
                return true;
            }
            bool allocTransaction(const task_id_type& task_id, session_id_type& session_id){
                bool expect(false);
                session_id_type last_seed = _last_seed.load();
                for(session_id_type offset = 0; offset < _session_count; offset++){
                    session_id = (last_seed + offset)%_session_count + _min_session;
                    if(_allocate_map[session_id].compare_exchange_strong(expect, true)){
                        //unallocate
                        if(!_session_map[session_id].occupy(task_id)){
                            //occupy fail
                            _allocate_map[session_id].compare_exchange_strong(expect, false);
                            continue;
                        }
                        _last_seed.store((session_id)%_session_count);
                        return true;
                    }
                }
                return false;
            }
            bool deallocTransaction(const session_id_type& session_id){
                if(!isValid(session_id))
                    return false;
                bool expect(true);
                if(_allocate_map[session_id].compare_exchange_strong(expect, false)){
                    _session_map[session_id].reset();
//                    logger->info(boost::format("<TaskManager>debug:session[%08X]deallocated by thread[%x]")
//                                 %(uint32_t)session_id %this_thread::get_id());
                    return true;
                }
                return false;
            }
            void terminateTransaction(const session_id_type& session_id){
                if(!isValid(session_id))
                    return;
                if(_allocate_map[session_id].load()){
                    AppMessage msg(AppMessage::message_type::EVENT, EventEnum::terminate);
                    msg.session = session_id;
                    _session_map[session_id].insertMessage(msg);
                    invokeTransaction(session_id);
                }
            }
            void invokeTransaction(const session_id_type& session_id){
                uint32_t index = session_id % _queue_count;
                _queue_vector[index].put(session_id);
            }
            bool startTransaction(const session_id_type& session_id, AppMessage& msg){
                return appendMessage(session_id, msg);
            }
            bool processMessage(const session_id_type& session_id, AppMessage& msg){
                return appendMessage(session_id, msg);
            }
            bool containsTransaction(const session_id_type& session_id){
                if(!isValid(session_id))
                    return false;
                return _allocate_map[session_id].load();
            }
            bool appendMessage(const session_id_type& session_id, AppMessage& msg){
                if(!containsTransaction(session_id)){
                    logger->warn(boost::format("<TaskManager>append message to session fail, invalid task session [%08X]")
                                 %session_id);
                    return false;
                }
                _session_map[session_id].putMessage(msg);
                invokeTransaction(session_id);
                return true;
            }
        protected:
            virtual bool onStart() override{
                for(auto& active_queue:_queue_vector){
                    active_queue.start();
                }
                logger->info("<TaskManager>service started");
                return true;
            }
            virtual void onStopping() override{
                for(auto& active_queue:_queue_vector){
                    active_queue.stop();
                }
            }
            virtual void onWaitFinish() override{
            }
            virtual void onStopped() override{
            }
        private:
            void onSessionInvoked(session_id_type& session_id, uint64_t& pos, bool end_of_batch){
                session_type& session = _session_map[session_id];
                const task_id_type& task_id = session.getTaskID();
                if(task_id_type::invalid == task_id){
                    //session deallocated
                    return;
                }
                if(_task_map.end() == _task_map.find(task_id)){
                    logger->error(boost::format("<TaskManager>invoke session fail, invalid task %d for session [%08X]")
                                  %(uint32_t)task_id %session_id);
                    return;
                }
                task_type& task = *_task_map[task_id];
                list< AppMessage > message_list;
                if(!session.fetchMessage(message_list)){
//                    logger->warn(boost::format("<TaskManager>session [%08X] invoked, but no message available")
//                                        %session_id);
                    return;
                }
                for(AppMessage& msg:message_list)
                {
                    try{
                        if(!session.isInitialed()){
                            task.initialSession(msg, session);
                            task.invokeSession(session);
                        }
                        else{
                            task.processMessage(msg, session);
                        }
                        if(session.isFinished()){
                            task.releaseResource(session);
//                            logger->info(boost::format("<TaskManager>release finished session[%08X] by work thread[%x], last message %d, type %d")
//                                                %session_id %this_thread::get_id() %msg.id %(uint32_t)msg.type);
                            deallocTransaction(session_id);
                            return;
                        }
                    }
                    catch(std::exception& ex){
                        logger->error(boost::format("<TaskManager>process message exception in thread [%x], session[%08X], message %d, exception:%s")
                                      %this_thread::get_id() %session_id %msg.id %ex.what());
                        deallocTransaction(session_id);
                        return;
                    }
                    catch(...){
                        logger->error(boost::format("<TaskManager>process message unknown exception in thread [%x], session[%08X], message %d")
                                      %this_thread::get_id() %session_id %msg.id);
                        deallocTransaction(session_id);
                        return;
                    }
                }
            }

            bool isValid(const session_id_type& session_id){
                if((session_id < _min_session)||(session_id > _max_session))
                    return false;
                return true;
            }
        private:
            logger_type logger;
            session_id_type _session_count;
            atomic< session_id_type > _last_seed;
            session_id_type _min_session;
            session_id_type _max_session;
            uint32_t _queue_count;
            map< task_id_type, std::unique_ptr< task_type > > _task_map;
            map< session_id_type, session_type > _session_map;
            map< session_id_type, CopyableAtomic< bool > > _allocate_map;
            const static size_t queue_size = 1024;
            vector< ActiveQueue < session_id_type, queue_size > > _queue_vector;
        };
    }
}

#endif // BASE_MANAGER_HPP_INCLUDED
