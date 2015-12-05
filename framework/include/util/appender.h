#ifndef APPENDER_H
#define APPENDER_H

#include <util/logging_event.h>


namespace zhicloud {
namespace util {


class Appender;

class EventHandler//Appender helper, asynchronous call doAppend
{
public:
    typedef std::pair<LoggingEvent, std::shared_ptr<Appender>> ASYNC_EVENT_TYPE;

    virtual void transferEvent(const ASYNC_EVENT_TYPE &event) = 0;
    virtual ~EventHandler() {}
};


class Appender : public std::enable_shared_from_this<Appender>
{
public:
    enum class WORK_MODE:uint32_t
    {
        LOG_SYNC = 0,
        LOG_ASYNC = 1
    };

    Appender(const std::string &name,const WORK_MODE& mode);
    virtual ~Appender() = default;

    void append(const LoggingEvent &event);
    void dispatch(const LoggingEvent &event);//only used by async

    const std::string& name() const;
    const WORK_MODE& workmode()const;

    void parent(std::shared_ptr<Appender> &parent);
    void setCollector(uint64_t size);
    void addEventHandler(EventHandler& listener);//only set when async mode

protected:
    virtual void doAppend(const LoggingEvent &event) = 0;

    boost::optional<EventHandler&> m_handler;

    std::shared_ptr<Appender> m_parent;
    uint64_t m_collector_size = 0;

    const std::string m_name;
    const WORK_MODE m_workmode;
};


}
}

#endif // APPENDER_h
