---
title: 3GPP OpenAPIs
description: 3GPP 5G Core & APIs
sidebar_position: 1
---

# 3GPP OpenAPIs

The 3GPP, as the body responsible for the standards defining 5G, has outlined not only the radio interface used for 5G (called 5G New Radio, abbreviated as 5G-NR) but also the core network architecture for service providers. This new architecture is based on a Service-Based Architecture (SBA) composed of Network Functions (NFs), which are applications running on generic hardware, such as that provided by cloud infrastructure vendors.

These services communicate via APIs defined by the 3GPP and documented using OpenAPIs, a standard for API documentation. However, these APIs are designed for use only within the operator's core network and are not intended for third-party use, except for those offered by the Network Exposure Function (NEF).

The NEF is a specific NF designed to allow third parties to securely access the operator's network capabilities. The APIs provided by the NEF are referred to as the Northbound Interface, and their clients are known as Application Functions (AFs).

In conclusion, 3GPP OpenAPIs operate solely within the operator's domain and do not expose the operator’s network capabilities to third parties, except for the NEF, which explicitly aims to support third-party integration with the operator’s network.
