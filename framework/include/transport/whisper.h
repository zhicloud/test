#ifndef WHISPER_H
#define WHISPER_H

#include <string>
#include <mutex>
#include <map>
#include <transport/endpoint_address.hpp>
#include <transport/packet_receiver.h>
#include <transport/packet_sender.h>
#include <transport/app_message.h>
#include <service/runable.hpp>
#include <service/timer_service.h>
#include <util/logging.h>
#include <util/generator.h>
#include <transport/whisper_task_manager.h>

using std::string;
using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transport{
    class Whisper:public zhicloud::service::Runable
    {
        public:
            typedef EndpointAddress address_type;
            typedef WhisperSession::session_id_type task_id_type;
            Whisper(const string& ip, const size_t& channel_count, const string& path, const size_t& work_thread = 2);
            virtual ~Whisper();
            const uint16_t& control_port() const;
            template <class T >
            void bindObserver(T* observer){
                _task_manager.bindObserver(observer);
            }
            void attachFile(const string& filename, string& file_id);
            void detachFile(const string& file_id);
            bool containsFile(const string& file_id);
            void getFilename(const string& file_id, string& filename);
            void generateFile(string& file_id, string& filename);
            void fetchFile(const string& file_id, const string& target_file);
            void beginWrite(const string& local_file_id, const address_type& remote_address, task_id_type& task_id);
            void beginRead(const string& remote_file_id, const address_type& remote_address, task_id_type& task_id);
            void sendMessage(AppMessage& msg, const string& ip, const uint16_t& port);
            void onPacketReceived(const string& packet_data, const string& from_ip, const uint16_t& from_port,
                                                const string& to_ip, const uint16_t& to_port,  int socket_id);
            void getReceivePorts(vector< uint64_t >& ports);
            int32_t  setTimer(const uint32_t& timeout, const task_id_type& task_id);
            int32_t  setLoopTimer(const uint32_t& interval, const task_id_type& task_id);
            bool clearTimer(const int32_t& timer_id);
        protected:
            virtual bool onStart();
            virtual void onStopping();
        private:
            bool initial();
            void serializeToPacket(AppMessage& msg, string& packet_data);
            void unserializeFromPacket(const string& packet_data, AppMessage& msg);
            bool setNonBlocking(int socket);
            void onTimeoutEvent(list< AppMessage >& event_list);
        private:
            typedef std::lock_guard< std::recursive_mutex > lock_type;
            enum class CommandTypeEnum: uint64_t{
                write = 1,
                read = 2,
                data = 3,
                finish = 4,
                write_ack = 5,
                read_ack = 6,
                data_ack = 7,
                ready = 8,
                finish_ack = 9,
            };

            const static uint64_t max_session_count;
            const static uint16_t min_port;
            const static uint16_t max_port;
            string _ip;
            uint16_t _port;
            size_t _channel;
            string _file_path;
            std::recursive_mutex _file_mutex;
            map< string, string > _file_map;
            zhicloud::util::logger_type logger;
            zhicloud::util::Generator _generator;
            WhisperTaskManager _task_manager;
            PacketSender _sender;
            PacketReceiver _receiver;
            vector< int > _sockets;
            vector< uint64_t > _local_port;
            TimerService _timer_service;
    };
}

}
#endif // WHISPER_H
