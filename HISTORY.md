# History

## 0.8.1

* Utility function order_by_id uses GET with filtering to search for an order by a specific ID.

## 0.8.0

* Support for orderBookL2.

## 0.7.0

* Support for bulk order creation and amending was removed.  See - https://blog.bitmex.com/api_announcement/removal-of-bulk-order-rest-api-endpoints/
* Added single order amend.
* Update dependencies.

## 0.6.1

* Switch to orjson for serialization.

## 0.6.0

* Implement automatic asymptotically increasing throttling. As remaining requests approaches zero, the next request will automatically be delayed by an increasing value. The delay is relative to current time, meaning that if the user does not make additional api calls while the throttle is active, the delay runs out automatically and the next call will not be throttled. The throttling strategy will prevent 429 (Too many requests) errors, as long as this library is the sole user of the login/source IP-address.

## 0.5.0

* Add /user/walletHistory

## 0.4.4

* Make symbol parameter optional in funding api.

## 0.4.3

* Updated ujson to 4.0.1

## 0.4.2

* Fix incorrect reverse query parameter usage across all api calls.

## 0.4.1

* Add /execution

## 0.3.0

* Add /instrument

## 0.2.2

* Add /instrument/active

## 0.1.0

Initial commit