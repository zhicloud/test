#ifndef FILE_APPENDER_H
#define FILE_APPENDER_H

#include <util/appender.h>


namespace zhicloud {
namespace util {

class FileAppender : public Appender
{
public:
    enum class THREAD_MODE:uint32_t
    {
        SINGLE_THREAD_MODE = 0,
        MULTI_THREAD_MODE = 1
    };

    FileAppender(const WORK_MODE& mode,
                 const std::string &name,
                 const std::string &path,
                 const std::string &prefix,
                 const uint64_t &size,
                 const THREAD_MODE& thread_mode,
                 bool immediateFlush = true);

    virtual ~FileAppender();

    virtual void doAppend(const LoggingEvent &event) override;

private:
    void write_file(const LoggingEvent &event);


    const THREAD_MODE m_thread_mode;
    const bool m_immediateFlush;

    std::string m_path;
    std::string m_prefix;
    std::string m_cur_file_name;
    std::fstream m_stream;
    std::mutex m_mutex;
    std::queue<std::pair<std::string, uint64_t>> m_file_infos;

    uint64_t m_file_size = 0;
    uint32_t m_year = 0;
    uint32_t m_month = 0;
    uint32_t m_day = 0;
    uint32_t m_seq = 0;
    uint32_t m_cur_file_size = 0;
    uint32_t m_all_file_size = 0;

};

}
}

#endif
