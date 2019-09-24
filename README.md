# cloudwatch_alarm_to_slack


Publish notifications from CloudWatch to Slack


Local development requires an environment variable `SLACK_HOOK` which references a Slack webhook uri.


To update function definition in AWS using Lambduh:

```
git clone https://github.com/scub/lambduh lambduh && cd $_
git clone https://github.com/linuxacademy/cloudwatch_slack_relay functions/cloudwatch_slack_relay
./sbin/build.sh
```
