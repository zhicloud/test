#ifndef LOGGER_MANAGER_H
#define LOGGER_MANAGER_H

#include <util/singleton.h>
#include <util/logging.h>
#include <util/file_appender.h>
#include <unordered_map>
#include <thread>
#include <service/passive_queue.hpp>

namespace zhicloud {
namespace util {

class LoggerManager : public Singleton<LoggerManager>, public EventHandler
{
public:
    bool initialLogging(bool create_async_thread = false);
    bool finishLogging();
    bool setCollector(const std::string& path, const uint64_t& max_size);
    logger_type getLogger(const std::string& name, const log_level& level = level_info);
    void log(const LoggingEvent &event);

    bool addAsyncFileAppender(const std::string &appender_name,
                              const std::string& work_path,
                              const std::string& prefix,
                              const uint64_t& max_size,
                              bool immediateFlush = true);

    bool addSyncFileAppender(const std::string &appender_name,
                             const std::string& work_path,
                             const std::string& prefix,
                             const uint64_t& max_size,
                             bool immediateFlush = true);


private:
    bool addFileAppender(const Appender::WORK_MODE& workmode,
                         const std::string &appender_name,
                         const std::string& work_path,
                         const std::string& prefix,
                         const uint64_t& max_size,
                         const FileAppender::THREAD_MODE& thread,
                         bool immediateFlush = true);

    void dispatch();

    void transferEvent(const ASYNC_EVENT_TYPE &event)override;
    bool delPathTailSlash(const std::string &path, std::string &new_path);

    std::shared_ptr<Appender> findLatestAppender(const std::string &logger_name);
    std::vector<std::shared_ptr<Appender>> m_root_appenders;
    std::unordered_map<std::string, std::shared_ptr<Appender>> m_appenders;
    std::unordered_map<std::string, std::shared_ptr<Appender>> m_appender_path_infos;
    std::unordered_map<std::string, uint64_t> m_collector_infos;
    zhicloud::service::PassiveQueue<ASYNC_EVENT_TYPE, 8192> m_async_events;
    std::thread m_async_thread;
    bool _has_async_thread;
};

}
}

#endif // LOGGER_MANAGER_H
