---
title: GSMA Open Gateway
description: GSMA Open Gateway vs. 3GPP
sidebar_position: 3
---

# GSMA Open Gateway

Similar to the NEF, the GSMA Open Gateway aims to expose various network operator capabilities to third parties. However, there are advantages to using the GSMA Open Gateway:

* **Simplification**: The NEF exposes highly complex interfaces with various details of the operator's network, requiring knowledge in mobile networks and 5G, which increases the cost of adopting these APIs.
* **Aggregation**: The NEF only provides access to the operator's network, while the GSMA Open Gateway envisions the existence of aggregators that offer APIs for multiple operators in a unified manner, requiring contact with only one aggregator instead of multiple operators.
* **Privacy management**: The GSMA Open Gateway includes mechanisms for managing end-user consent, which is often necessary for legal reasons.

This does not mean that the NEF is an inferior interface; it offers deeper integration with the operators’ networks. Additionally, it is possible to use the NEF to implement the GSMA Open Gateway by modeling it as an AF. In reality, the NEF and the GSMA Open Gateway are complementary technologies.

Nevertheless, it is important to highlight that the GSMA Open Gateway is a more convenient interface for most third-party application developers since, unlike direct interaction with the NEF, it does not require knowledge of mobile networks. The NEF still holds importance—not only by offering greater integration with the operator's network but also because it can serve as a foundation for implementing a GSMA Open Gateway.
