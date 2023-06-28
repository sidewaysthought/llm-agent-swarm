# About Logging

## Log Files

Every event that takes place is logged, and a new log is created every session. If the swarm is active for more than 2 hours, a new log is created.

THe Python logging module is used for logging and debugging. For more information, refer to the [Python documentation on the logging module](https://docs.python.org/3/library/logging.html).

The following logs are created:

* ```conversations_<date>_<number>.log```
    * Conversations that agents have with each other
* ```info_<date>_<number>.log```
    * Contains Info and Warning messages
    * Info and warning message are also displayed to the console
* ```error_<date>_<number>.log```
    * Contains Error and Critical messages
    * Error and Critical messages are also displayed to the console
* ```debug_<date>_<number>.log```
    * Contains debug messages
    * Debug messages only shown on the console with --debug flag

Logs are tab delimited.

The Info, Error and Debug logs contain timestamp, event type, issuing agent (or System) and message. 

The conversations log contains the timestamp, a unique ID for each conversation item, the from agent, the to agent and the message body.

### Example Conversations Log Output
| Date/Time | ID | From | To | Message |
|----------|----------|----------|----------|----------|
| 2023-06-27 23:01:22 | acr3bd8m | ChiefExecAgent  | SystemAgent | Hello SystemAgent! It is nice to meet you. I am ready to work on the project! | 
| 2023-06-27 23:01:23 | 4md9g254 | SystemAgent  | ChiefExecAgent | Great to meet you. I have an idea on how to proceed. | 

### Example Info, Error and Debug Log Output
| Date/Time | Event Type | Issuer | Message |
|----------|----------|----------|----------|
| 2023-06-27 23:01:22 | Info  | System | Conversation Loop Started | 
| 2023-06-27 23:01:25 | Info  | System | Message acr3bd8m Redirected from System to SystemAgent  | 
| 2023-06-27 23:01:23 | Error  | ChiefExecAgent | Failed to save Memory: "Memory Message" | 