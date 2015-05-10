#include <iostream>
#include "util/logging_test.h"

#include <util/define.hpp>
#include <util/network_utility.h>
#include <util/domain_utility.h>
#include <util/logger.h>
#include <util/logging.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <boost/log/trivial.hpp>

#include <transaction/base_session.hpp>
#include <transaction/base_task.hpp>
#include <transaction/process_rule.hpp>
#include <transaction/base_manager.hpp>
#include <transport/app_message.h>
#include <transport/command.h>


#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <zpl.hpp>

#include <semaphore.h>
#include <time.h>
#include <boost/filesystem.hpp>

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;
using namespace boost::filesystem;

LoggingTest::LoggingTest()
{
    //ctor
	logger = getLogger("LogTester");

	logger->info("<LogTester> service started.");
}

LoggingTest::~LoggingTest()
{
    //dtor
}
void LoggingTest::init()
{
	bIsRunning = true;

	/*if (true != initialLogging())
	{
		BOOST_LOG_TRIVIAL(info) <<"init logging failed.";
	}*/
	BOOST_LOG_TRIVIAL(info) <<"init logging success.";

	if (true != addFileAppender("/var/zhicloud/mylog", "wllog", 512))
	{
		BOOST_LOG_TRIVIAL(info) <<"addFileAppender failed.";
	}
	//BOOST_LOG_TRIVIAL(info) <<"addFileAppender success.";

	if (true != setCollector("/var/zhicloud/mylog", 512))
	{
		BOOST_LOG_TRIVIAL(info) <<"setCollector failed.";
	}
	//BOOST_LOG_TRIVIAL(info) <<"setCollector success.";


	//BOOST_LOG_TRIVIAL(info) <<"LoggingTest init finish.";
	//printf("LoggingTest init finish ..........\n");
    return;
}

bool LoggingTest::test()
{
	int idx = 0;

	while (idx < 10)
	{
		for (int i = 0 ; i < 5; i++)
		{
			BOOST_LOG_TRIVIAL(info) <<"wangli test log info................";
		}

		if (true != setCollector("/var/zhicloud/mylog", 512))
		{
			printf("test setCollector failed.\n");
			return false;
		}

		sleep(1);
		idx++;
	}
	sleep(3);
	/*if (true != finishLogging())
	{
		BOOST_LOG_TRIVIAL(warning) <<"finish logging failed.";

		return false;
	}
	sleep(3);*/

	directory_iterator end;
	for (directory_iterator pos("/var/zhicloud/mylog"); pos != end; ++pos)
	{
        if (is_regular_file(pos->status()))
        {
            filenames.push_back(pos->path().string());
        }
	}

	int filesize = 0;
	for ( int i = 0 ; i < filenames.size(); i++)
	{
		//BOOST_LOG_TRIVIAL(info) << boost::format("file %d:[%s]") %i %filenames[i].c_str() ;
		filesize = file_size(filenames[i].c_str());
		//BOOST_LOG_TRIVIAL(info) << boost::format("file %d size is %d") %i %filesize;
		if ( 512 < filesize)
		{
			BOOST_LOG_TRIVIAL(warning) <<"limit log size failed!.";
		    return false;
		}
	}

	BOOST_LOG_TRIVIAL(info) <<"Logging test all pass.";
	return true;
}




