#ifndef LOGGER_H
#define LOGGER_H

#include <boost/format.hpp>


namespace zhicloud {
namespace util {

enum log_level
{
    level_debug,
    level_info,
    level_warning,
    level_error,
    level_fatal
};

class Logger
{
public:
    Logger(const std::string& name, const log_level& level = level_info);
    virtual ~Logger();
    void debug(const std::string& content);
    void info(const std::string& content);
    void warn(const std::string& content);
    void error(const std::string& content);
    void fatal(const std::string& content);
    void debug(boost::format& input);
    void info(boost::format& input);
    void warn(boost::format& input);
    void error(boost::format& input);
    void fatal(boost::format& input);
    void hex(const log_level& level, const std::string& input);
    void hex(const log_level& level, const char* buf, const int& buf_length);

private:
    void log_impl(const std::string &level_str, const std::string &message);
    std::string m_name;
    log_level m_level;
    const static std::string _debug_str;
    const static std::string _info_str;
    const static std::string _warn_str;
    const static std::string _error_str;
    const static std::string _fatel_str;
};

}
}

#endif
