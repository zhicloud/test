#!/usr/bin/python

def elapsedMilliseconds(time_delta):
    return (float(time_delta.microseconds + (time_delta.seconds + time_delta.days * 24 * 3600) * 10**6) / 10**3)

def elapsedSeconds(time_delta):
    return (float(time_delta.microseconds + (time_delta.seconds + time_delta.days * 24 * 3600) * 10**6) / 10**6)
