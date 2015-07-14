# Github File Watcher

So, I was contributing stuff to [cocos2d-x](https://github.com/cocos2d/cocos2d-x), but I wanted to know if anyone made changes to my changes, so I can review them.

Instead of reviewing every single PR, we have this server receiving github PR webhooks, and checking if any of the files to be monitored have been changed.

## Usage

To use this app, simply clone, add a `config.py` file with two variables:

```python
# Webhook to deliver notifications to
SLACK_WEBHOOK = 'your-slack-webhook'

# Files to check for changes
FILES = ['filename-with-or-without-extension']
```
