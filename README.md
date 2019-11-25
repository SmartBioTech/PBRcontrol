# PBRcontrol

The functionality of `PBRcontrol` can be divided to two general parts: 

* an API providing access to local DB of a node, execution of requested commands, and devices management
* turbidostat - a tool to maintain optical density in specified range

To start the `PBRcontrol`, use

```
python3 main.py
```

This will initialise database and its API. The available end points are the following:

* [Initiate node](Docs-(Initiation))
* [Initiate device](Docs-(Add-device))
* [Send command](Docs-(Command))
* [End device/node](Docs-(End))
* [Read log](Docs-(Log))
* [Ping](Docs-(Ping))

