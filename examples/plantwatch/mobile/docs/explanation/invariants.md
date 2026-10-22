# Invariants of mobile

What is true of the app at every moment, across all of its parts. A change that breaks one of these lines needs a decision.

- The screens take no data from the radio or from the network. They read from the store on the phone and write to it. Their one contact with the outside is `push-service`: registering the phone and receiving a tap.
- No part waits for another rhythm. A fetch does not wait for an upload, an upload does not wait for a fetch, a screen waits for neither.
- A reading is confirmed to the sensor stick only after it is stored durably on the phone. It is removed from the phone only after the server has confirmed it and it is older than the history the app keeps.
- A reading has its UTC time and its estimated flag before it is stored. Both never change afterwards.
- The app computes no alert. A plant "needs water" on a screen only because an open alert says so.
- Each thing in the [data model](../references/data-model.md) has one origin. The app changes only what the owner may change.
- At most one fetch runs at a time, and at most one upload.
- Code that exists once per platform belongs to the radio part and nowhere else. A second place needs a new decision.
