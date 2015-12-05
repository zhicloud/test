#ifndef LOGGING_EVENT_H
#define LOGGING_EVENT_H

#include <string>
#include <map>
#include <sstream>
#include <sys/time.h>
#include <mutex>
#include <queue>
#include <fstream>
#include <memory>
#include <boost/make_shared.hpp>
#include <boost/optional.hpp>
#include <boost/format.hpp>


namespace zhicloud {
namespace util {

class LoggingTime
{
public:
    LoggingTime() = default;

    LoggingTime(uint32_t year, uint32_t month, uint32_t day, uint32_t hour, uint32_t minute, uint32_t second, uint32_t usecond)
    {
        m_year = year;
        m_month = month;
        m_day = day;
        m_hour = hour;
        m_minute = minute;
        m_second = second;
        m_usecond = usecond;
    }

    uint32_t year() const
    {
        return m_year;
    }

    uint32_t month() const
    {
        return m_month;
    }

    uint32_t day() const
    {
        return m_day;
    }

    uint32_t hour() const
    {
        return m_hour;
    }

    uint32_t minute() const
    {
        return m_minute;
    }

    uint32_t second() const
    {
        return m_second;
    }

    uint32_t usecond() const
    {
        return m_usecond;
    }

private:
    uint32_t m_year;
    uint32_t m_month;
    uint32_t m_day;
    uint32_t m_hour;
    uint32_t m_minute;
    uint32_t m_second;
    uint32_t m_usecond;
};


class LoggingEvent
{
public:
    enum class EVENT_TYPE
    {
        NORMAL,
        STOP
    };

    LoggingEvent() = default;

    LoggingEvent(const std::string &level, const LoggingTime &time, const std::string &logger_name, const std::string &message)
    {
        m_level = level;
        m_time = time;
        m_logger_name = logger_name;
        m_message = message;
    }

    const std::string& level()const
    {
        return m_level;
    }

    const LoggingTime& time() const
    {
        return m_time;
    }

    const std::string& logger_name() const
    {
        return m_logger_name;
    }

    const std::string& message() const
    {
        return m_message;
    }

    EVENT_TYPE eventType() const
    {
        return m_event_type;
    }

    void eventType(EVENT_TYPE event_type)
    {
        m_event_type = event_type;
    }

private:
    std::string m_level;
    LoggingTime m_time;
    std::string m_logger_name;
    std::string m_message;
    EVENT_TYPE m_event_type = EVENT_TYPE::NORMAL;
};

}
}

#endif // LOGGING_EVENT_H
