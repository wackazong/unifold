# Platform limits

What iOS and Android let the app do, as far as the design depends on it. The values are design assumptions for the system versions named here. None of them has been confirmed against the vendors' documentation or on a phone yet; confirm each one before code relies on it. The
[mobile-review-a-new-os-version](../skills/mobile-review-a-new-os-version/SKILL.md)
skill keeps this file current.

## Supported systems

| Platform | Oldest supported version | Designed for up to |
|---|---|---|
| iOS | 16 | 26 |
| Android | 12 (API level 31) | 16 (API level 36) |

## Waking the app when a paired sensor stick appears

| Topic | iOS | Android |
|---|---|---|
| Mechanism | A pending connection request to a known peripheral, with the background mode for BLE centrals and state restoration | A companion device association with presence observation |
| How long the request lasts | Until the app cancels it; it does not time out | Until the association is removed |
| What the system does | Connects when the peripheral advertises and starts or resumes the app | Starts the app's companion service when the device appears |
| Delay between appearing and waking | Seconds to a few minutes; the system scans less often for apps in the background | Seconds to a few minutes |
| Survives a restart of the phone | Yes, after the owner has unlocked the phone once | Yes |

## Run time in the background

| Topic | iOS | Android |
|---|---|---|
| Run time per wake-up | About 10 seconds; an extension can be requested and is not guaranteed | While the device is present; the system may still stop the process when memory is short |
| Design budget of the app | 10 seconds per wake-up on both platforms | |
| Scheduled work at a later time | A background task request; the system chooses the moment, often hours later | A work request with the constraint "network connected"; power saving delays it to maintenance windows |
| Earliest repetition of scheduled work | Not defined | 15 minutes |

## What stops background work

| Cause | iOS | Android |
|---|---|---|
| Owner removes the app from the app switcher | The system no longer wakes the app until the owner opens it | No effect on most phones |
| Owner chooses "Force stop" in the settings | Not available | The system no longer wakes the app until the owner opens it |
| Bluetooth switched off | No wake-up | No wake-up |
| Permission withdrawn | No wake-up | No wake-up |
| Battery saver of the phone's manufacturer | Not applicable | May stop the app on some phones; differs per manufacturer |

The app cannot notice any of these while it is stopped. It notices them when the owner opens it.

## Permissions

| Purpose | iOS | Android |
|---|---|---|
| Find and connect to sensor sticks | Bluetooth permission, asked at first use | "Nearby devices" permission, asked at run time |
| Associate a sensor stick for background wake-up | None beyond Bluetooth | A system dialog per sensor stick in which the owner confirms the device |
| Show notifications | Notification permission, asked at run time | Notification permission, asked at run time from Android 13 |
| Scan the code of another phone | Camera permission, asked at run time | Camera permission, asked at run time |
| Location | Not needed | Not needed; the app declares that it does not derive location from scans |

## BLE

| Topic | Value |
|---|---|
| Connections at a time | The app connects to one sensor stick at a time. Both systems allow more. |
| BLE in simulators | The phone simulators of both platforms have no BLE that reaches real hardware. |
| Address of a sensor stick | iOS hides the hardware address and gives the app an identifier that is valid on this phone only. The app recognises a sensor stick by its sensor id. |

## Notifications

| Topic | iOS | Android |
|---|---|---|
| Push service | APNs | FCM |
| Notification address | Device token, may change; the system tells the app | Registration token, may change; the system tells the app |
| Shown while the app is not running | Yes, by the system | Yes, by the system |
