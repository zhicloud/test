#ifndef LOGGING_H
#define LOGGING_H

#include "logger.h"

namespace zhicloud {
namespace util {

typedef boost::shared_ptr<Logger> logger_type;
bool initialLogging(bool create_async_thread = false);
bool finishLogging();
bool addFileAppender(const std::string& path_name, const std::string& prefix, const uint64_t& max_size,bool immediateFlush = true);
bool addAsyncFileAppender(const std::string& path_name, const std::string& prefix, const uint64_t& max_size,bool immediateFlush = true);
bool setCollector(const std::string& path_name, const uint64_t& max_size);
logger_type getLogger(const std::string& name, const log_level& level = level_info);

}
}

#endif // LOGGING_H
