#ifndef BASE_MANAGER_HPP_INCLUDED
#define BASE_MANAGER_HPP_INCLUDED

#include <service/runable.hpp>
#include <util/logging.h>
#include <vector>
#include <list>
#include <map>
#include <memory>
#include <exception>
#include <transport/app_message.h>
#include <thread>
#include <mutex>
#include <service/event.hpp>

using zhicloud::transport::AppMessage;
using namespace zhicloud::util;
using zhicloud::service::Event;

namespace zhicloud{
    namespace transaction{

        template < class T >
        class BaseManager: public zhicloud::service::Runable
        {
        private:
            typedef std::unique_lock<std::recursive_mutex> lock_type;
            typedef std::unique_lock<std::mutex> task_lock_type;
        public:
            typedef typename T::session_type::session_id_type session_id_type;
            typedef typename T::session_type session_type;
            typedef typename T::task_id_type task_id_type;
            typedef T task_type;
            BaseManager(const session_id_type& session_count, const uint32_t& work_thread):
                session_count(session_count), last_seed(0),
                min_session(1), max_session(session_count + min_session - 1),
                thread_index(0), thread_count(work_thread)
            {
                logger = getLogger("BaseManager");
                for(session_id_type seed = 0; seed < session_count; seed++){
                    session_id_type session_id = seed + min_session;
                    allocate_map[session_id] = false;
                    session_map.insert(std::pair< session_id_type, session_type>(session_id,
                                                                                 std::move(session_type(session_id))));
                }
                logger->info(boost::format("<TaskManager>%d transaction session created")
                             %session_count);
                for(uint32_t i = 0; i < work_thread; i++){
                    task_mutex.emplace_back(std::unique_ptr< std::mutex>( new std::mutex()));
                    task_queue.emplace_back(std::move(list< session_id_type >()));
                    task_available.emplace_back(std::unique_ptr<  Event >(new Event()));
                }
                logger->info(boost::format("<TaskManager>%d work thread(s) ready")
                             %work_thread);
            }
            virtual ~BaseManager(){
                invoke_thread.clear();
                task_mutex.clear();
                task_available.clear();
                task_map.clear();
            }
            bool addTask(task_type* p_task){
                lock_type lock(session_mutex);
                task_id_type task_id = p_task->getTaskID();
                if(task_map.end() != task_map.find(task_id)){
                    logger->warn(boost::format("<TaskManager>add task fail, task %d already exists")
                                 %(uint32_t)task_id);
                    return false;
                }
                task_map[task_id] = std::unique_ptr< task_type > (p_task);
                logger->info(boost::format("<TaskManager>add task success, task id %d")
                             %(uint32_t)task_id);
                return true;
            }
            bool allocTransaction(const task_id_type& task_id, session_id_type& session_id){
                lock_type lock(session_mutex);

                for(session_id_type offset = 0; offset < session_count; offset++){
                    session_id = (last_seed + offset)%session_count + min_session;
                    if(!allocate_map[session_id]){
                        //unallocate
                        session_map[session_id].occupy(task_id);
                        allocate_map[session_id] = true;
                        last_seed = (session_id)%session_count;
                        return true;
                    }
                }
                return false;
            }
            bool deallocTransaction(const session_id_type& session_id){
                lock_type lock(session_mutex);
                if(!isValid(session_id))
                    return false;
                if(allocate_map[session_id]){
                    session_map[session_id].reset();
                    allocate_map[session_id] = false;
                    return true;
                }
                return false;
            }
            void terminateTransaction(const session_id_type& session_id){
                lock_type lock(session_mutex);
                if(!isValid(session_id))
                    return;
                if(allocate_map[session_id]){
                    AppMessage msg(AppMessage::message_type::EVENT, EventEnum::terminate);
                    msg.session = session_id;
                    session_map[session_id].insertMessage(msg);
                    invokeTransaction(session_id);
                }
            }
            void invokeTransaction(const session_id_type& session_id){
                uint32_t index = session_id % thread_count;
                task_lock_type lock(*task_mutex[index]);
                task_queue[index].push_back(session_id);
                task_available[index]->set();
            }
            bool startTransaction(const session_id_type& session_id, AppMessage& msg){
                return appendMessage(session_id, msg);
            }
            bool processMessage(const session_id_type& session_id, AppMessage& msg){
                return appendMessage(session_id, msg);
            }
            bool containsTransaction(const session_id_type& session_id){
                lock_type lock(session_mutex);
                if(!isValid(session_id))
                    return false;
                return allocate_map[session_id];
            }
            bool appendMessage(const session_id_type& session_id, AppMessage& msg){
                lock_type lock(session_mutex);
                if(!containsTransaction(session_id)){
                    logger->warn(boost::format("<TaskManager>append message to session fail, invalid task session [%08X]")
                                 %session_id);
                    return false;
                }
                session_map[session_id].putMessage(msg);
                invokeTransaction(session_id);
                return true;
            }
        protected:
            virtual bool onStart() override{
                for(uint32_t i = 0; i < thread_count; i++){
                    invoke_thread.emplace_back(std::unique_ptr< std::thread >(new std::thread(&BaseManager< T >::invokeProcess,
                                                                                                              this)));
                }
                logger->info("<TaskManager>service started");
                return true;
            }
            virtual void onStopping() override{

                for(uint32_t i = 0; i < thread_count; i++){
                    task_lock_type lock(*task_mutex[i]);
                    task_available[i]->set();
                }
            }
            virtual void onWaitFinish() override{
                for(uint32_t i = 0; i < thread_count; i++){
                    invoke_thread[i]->join();
                }
            }
            virtual void onStopped() override{
                for(uint32_t i = 0; i < thread_count; i++){
                    invoke_thread[i].reset();
                }
            }
        private:
            void invokeProcess(){
                uint32_t index = 0;
                {
                    lock_type lock(session_mutex);
                    index = thread_index;
                    thread_index++;
                }
                std::mutex& thread_mutex = *task_mutex[index];
                Event& thread_event = *task_available[index];
                list< session_id_type >& thread_queue = task_queue[index];

                list< session_id_type > request_queue;
                list< AppMessage > message_list;
                while(isRunning()){
                    {
                        thread_event.wait();
                        if(!isRunning())
                        {
                            thread_event.set();
                            break;
                        }
                        task_lock_type lock(thread_mutex);

                        if(thread_queue.empty())
                            continue;
                        request_queue.clear();
                        //move session id
                        request_queue = std::move(thread_queue);
                        thread_queue.clear();
                    }
                    request_queue.unique();
                    for(typename list< session_id_type >::iterator ir = request_queue.begin(); ir != request_queue.end(); ir++){
                        if(!containsTransaction(*ir)){
                            logger->warn(boost::format("<TaskManager>invoke session fail, invalid session [%08X]")
                                                %*ir);
                            ir = request_queue.erase(ir);
                        }
                    }

                    //process
                    for(session_id_type& session_id:request_queue){
                        session_type& session = session_map[session_id];
                        task_id_type task_id = session.getTaskID();
                        if(task_map.end() == task_map.find(task_id)){
                            logger->error(boost::format("<TaskManager>invoke session fail, invalid task %d for session [%08X]")
                                          %(uint32_t)task_id %session_id);
                            continue;
                        }
                        task_type& task = *task_map[task_id];
                        message_list.clear();
                        if(!session.fetchMessage(message_list)){
                            logger->warn(boost::format("<TaskManager>session [%08X] invoked, but no message available")
                                                %session_id);
                            continue;
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
                                    deallocTransaction(session_id);
                                    break;
                                }
                            }
                            catch(std::exception& ex){
                                logger->error(boost::format("<TaskManager>process message exception in thread %d, session[%08X], message %d, exception:%s")
                                              %index %session_id %msg.id %ex.what());
                                deallocTransaction(session_id);
                                break;
                            }
                            catch(...){
                                logger->error(boost::format("<TaskManager>process message unknown exception in thread %d, session[%08X], message %d")
                                              %index %session_id %msg.id);
                                deallocTransaction(session_id);
                                break;
                            }
                        }
                    }


                }
            }
            bool isValid(const session_id_type& session_id){
                if((session_id < min_session)||(session_id > max_session))
                    return false;
                return true;
            }
        private:

            logger_type logger;
            std::recursive_mutex session_mutex;
            session_id_type session_count;
            session_id_type last_seed;
            session_id_type min_session;
            session_id_type max_session;
            uint32_t thread_index;
            uint32_t thread_count;
            vector< std::unique_ptr< std::mutex > > task_mutex;
            vector< list< session_id_type > > task_queue;
            vector< std::unique_ptr< Event > > task_available;
            vector< std::unique_ptr< std::thread > > invoke_thread;
            map< task_id_type, std::unique_ptr< task_type > > task_map;
            map< session_id_type, session_type > session_map;
            map< session_id_type, bool > allocate_map;
        };
    }
}

#endif // BASE_MANAGER_HPP_INCLUDED
